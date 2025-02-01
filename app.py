from flask import Flask, request, redirect, session, render_template, jsonify, send_from_directory
import os
import logging
import requests
from dotenv import load_dotenv
from shopify import ShopifyApi
from barcode import Code128
from barcode.writer import SVGWriter
import io
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

SHOPIFY_CLIENT_ID = os.getenv('P_API_KEY')
SHOPIFY_CLIENT_SECRET = os.getenv('P_API_SECRET')
SHOPIFY_SCOPE = "read_orders,read_products,read_customers"
REDIRECT_URI = os.getenv('P_REDIRECT_URI')
api = None


def get_order_id(order_name):
    global api
    response = api.orders(order_name=order_name)
    
    return response['data']['orders']['edges'][0]['node']['id']


@app.after_request
def add_headers(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Content-Security-Policy'] = (
        "frame-ancestors 'self' https://*.myshopify.com https://admin.shopify.com"
    )
    response.headers['Access-Control-Allow-Origin'] = '*'  # For development, restrict in production

    return response


@app.route('/')
def install():
    shop = request.args.get('shop')
    if not shop:

        return "Missing shop parameter", 400
    install_url = f"https://{shop}/admin/oauth/authorize"

    return redirect(
        f"{install_url}?client_id={SHOPIFY_CLIENT_ID}&scope={SHOPIFY_SCOPE}&redirect_uri={REDIRECT_URI}&embedded_app=true"
    )


@app.route('/api/init', methods=['GET'])
def init_app():
    shop_origin = request.args.get('shop')
    if not shop_origin:
        return jsonify({'error': 'Shop parameter is missing!'}), 400

    return jsonify({'apiKey': SHOPIFY_CLIENT_ID, 'shopOrigin': shop_origin})


@app.route('/callback')
def callback():
    shop = request.args.get('shop')
    code = request.args.get('code')
    if not shop or not code:

        return "Missing shop or code parameter", 400

    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {
        "client_id": SHOPIFY_CLIENT_ID,
        "client_secret": SHOPIFY_CLIENT_SECRET,
        "code": code,
    }
    response = requests.post(token_url, json=payload)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        logger.info(f"Access token retrieved for {shop}")
        token_file_path = "shopify_tokens.json"

        if os.path.exists(token_file_path):
            with open(token_file_path, "r") as token_file:
                all_tokens = json.load(token_file)
        else:
            all_tokens = {}

        all_tokens[shop] = access_token
        with open(token_file_path, "w") as token_file:
            json.dump(all_tokens, token_file, indent=4)

        session['shop'] = shop
        session['access_token'] = access_token

        return redirect(f"/index?shop={shop}")

    return "Failed to get access token", 400


@app.route('/index')
def index():
    global api

    shop = session.get('shop')
    access_token = session.get('access_token')

    if not shop or not access_token:
        token_file_path = "shopify_tokens.json"
        if os.path.exists(token_file_path):
            with open(token_file_path, "r") as token_file:
                all_tokens = json.load(token_file)
                shop = request.args.get('shop')
                access_token = all_tokens.get(shop)

    if not shop or not access_token:
        return "Unauthorized", 401

    # Fetch orders from Shopify
    api = ShopifyApi(store_name=shop.split('.')[0], access_token=access_token, version='2025-01')
    api.create_session()
    orders_data = api.orders()

    orders = []
    for edge in orders_data['data']['orders']['edges']:
        node = edge['node']
        orders.append({
            "no": node['name'],
            "date": node['createdAt'],
            "customer": f"{node['customer']['firstName']} {node['customer']['lastName']}" if node['customer'] else "Guest",
            "totalPrice": f"${node['totalPriceSet']['shopMoney']['amount']}",
            "paymentStatus": node['displayFinancialStatus'],
            "fulfillmentStatus": node['displayFulfillmentStatus'],
            "shippingAddress": (
                f"{node['shippingAddress']['address1']}, {node['shippingAddress']['city']}, {node['shippingAddress']['country']}, {node['shippingAddress']['zip']}"
                if node['shippingAddress'] else "No Address"
            ),
            "actions": "View"
        })

    return render_template('index.html', shop=shop, orders=orders, )


@app.route('/search_order')
def search_order():
    global api

    token_file_path = "shopify_tokens.json"
    if os.path.exists(token_file_path):
        with open(token_file_path, "r") as token_file:
            data = json.load(token_file)
            for key, value in data.items():
                shop = key
                access_token = value

    order_name = request.args.get('orderid')

    if not order_name:
        return jsonify({"error": "Order ID is required"}), 400

    try:
        order_id = get_order_id(order_name)
        response = api.order(order_id, mode='search')  # Assuming you have a method to get a specific order
        
        order_data = response['data']['order']
        if not order_data:
            return jsonify({"error": "Order not found"}), 404

        # Prepare the order data for rendering
        order = {
            "no": order_data['name'],
            "date": order_data['createdAt'],
            "customer": f"{order_data['customer']['firstName']} {order_data['customer']['lastName']}" if order_data['customer'] else "Guest",
            "totalPrice": f"${order_data['totalPriceSet']['shopMoney']['amount']}",
            "paymentStatus": order_data['displayFinancialStatus'],
            "fulfillmentStatus": order_data['displayFulfillmentStatus'],
            "shippingAddress": (
                f"{order_data['shippingAddress']['address1']}, {order_data['shippingAddress']['city']}, {order_data['shippingAddress']['country']}, {order_data['shippingAddress']['zip']}"
                if order_data['shippingAddress'] else "No Address"
            ),
            "actions": "View"
        }

        # Render the index.html with the specific order data
        return render_template('index.html', shop=shop, orders=[order])  # Pass the order as a list

    except Exception as e:
        # print(order_data)
        return jsonify({"error": str(e)}), 500


@app.route('/order-details')
def order_details():
    order_name = request.args.get('ordername')
    if not order_name:
        return jsonify({'error': 'Order ID is required'}), 400

    order_id = get_order_id(order_name)
    json_data = api.order(order_id, mode='details')

    order_data = json_data['data']['order']
    print(order_data)

    _items = []
    products = order_data['lineItems']['edges']
    for product in products:
        _items.append(product['node'])

    # tax_lines = []
    # if len(order_data['taxLines']) > 0:
    #     taxes = order_data['taxLines']['edges']
    #     for tax in taxes:
    #         tax_lines.append(tax['node'])

    order = {
        "no": order_data['name'],
        "date": order_data['createdAt'],
        "fulfillmentStatus": order_data['displayFulfillmentStatus'],
        "_items": _items,
        "subtotal": order_data['currentSubtotalPriceSet']['shopMoney']['amount'],
        "additional": order_data['currentTotalAdditionalFeesSet']['shopMoney']['amount'] if order_data['currentTotalAdditionalFeesSet'] else "0.0",
        # "tax": tax_lines,
        "tax": order_data['currentTotalTaxSet']['shopMoney']['amount'],
        "shipping": order_data['currentShippingPriceSet']['shopMoney']['amount'],
        "duties": order_data['currentTotalDutiesSet']['shopMoney']['amount'] if order_data['currentTotalDutiesSet'] else "0.0",
        "discount": order_data['currentTotalDiscountsSet']['shopMoney']['amount'],
        "total": order_data['currentTotalPriceSet']['shopMoney']['amount'],
        "paid": order_data['totalReceivedSet']['shopMoney']['amount'],
        "customer": {
            "name": f"{order_data['customer']['firstName']} {order_data['customer']['lastName']}" if order_data['customer'] else "Guest",
            "email": order_data['customer']['email'] if order_data['customer'] else "None",
            "phone": order_data['customer']['phone'] if order_data['customer'] else "None"
        },
        "shippingAddress": (
            f"{order_data['shippingAddress']['address1']}, {order_data['shippingAddress']['city']}, {order_data['shippingAddress']['country']}, {order_data['shippingAddress']['zip']}"
            if order_data['shippingAddress'] else "No Address"
        ),
        "paymentStatus": order_data['displayFinancialStatus']
    }

    # Render the order details page or return JSON data
    return render_template('order-details.html', order_data=order)


@app.route('/get-shipping-options')
def get_shipping_options():
    zipcode = request.args.get('zipcode', '90001')  # Default ZIP code if not provided

    # Load existing shipping services
    with open('shipping_services.json', 'r') as file:
        shipping_services = json.load(file)

    # You can add filtering logic based on `zipcode` if needed.
    available_services = shipping_services["dsQuote"]["Quote"]

    return jsonify(available_services)


@app.route('/get-label/<order_id>')
def get_label(order_id):
    # In practice, you would fetch the label data from your database
    ean = Code128(order_id, writer=SVGWriter())
    barcode_buffer = io.BytesIO()
    ean.write(barcode_buffer)
    barcode_svg = barcode_buffer.getvalue().decode('utf-8')

    label_data = {
        'order_number': order_id,
        'date_created': '12-07-2022',
        'tracking_number': 'TYPQW050000026',
        'weight': '50g',
        'carrier': 'PARCELPLUS',
        'barcode_svg': barcode_svg
    }
    return jsonify(label_data)


@app.errorhandler(404)
def not_found_error(error):
    """
    Handles 404 errors.
    """
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handles 500 errors.
    """
    return render_template('error.html', error="Internal server error"), 500


@app.route('/favicon.ico')
def favicon():
    """
    Handles favicon requests.
    """
    return '', 204


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


if __name__ == "__main__":
    # Ensure app is running in HTTPS using ngrok or other tunneling tools for local development
    app.run(host="0.0.0.0", port=5000, debug=True)