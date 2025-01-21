from flask import Flask, request, redirect, session, render_template, jsonify
import os
import logging
import requests
from dotenv import load_dotenv
from shopify import ShopifyApi
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

SHOPIFY_CLIENT_ID = os.getenv('D_API_KEY')
SHOPIFY_CLIENT_SECRET = os.getenv('D_API_SECRET')
SHOPIFY_SCOPE = "read_orders,read_products"
REDIRECT_URI = os.getenv('D_REDIRECT_URI')
api = None


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

    print(f"{install_url}?client_id={SHOPIFY_CLIENT_ID}&scope={SHOPIFY_SCOPE}&redirect_uri={REDIRECT_URI}&embedded_app=true")
    return redirect(
        f"{install_url}?client_id={SHOPIFY_CLIENT_ID}&scope={SHOPIFY_SCOPE}&redirect_uri={REDIRECT_URI}&embedded_app=true"
    )


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
    # orders_data = api.orders()
    orders = [
        {
            "no": "001",
            "date": "2025-01-20",
            "customer": "John Doe",
            "totalPrice": "$150.00",
            "paymentStatus": "Paid",
            "fulfillmentStatus": "Shipped",
            "shippingAddress": "123 Main St, New York, NY",
            "actions": "Print"
        },
        {
            "no": "002",
            "date": "2025-01-21",
            "customer": "Jane Smith",
            "totalPrice": "$230.00",
            "paymentStatus": "Pending",
            "fulfillmentStatus": "Processing",
            "shippingAddress": "456 Oak St, Los Angeles, CA",
            "actions": "Print"
        },
        {
            "no": "003",
            "date": "2025-01-22",
            "customer": "Michael Johnson",
            "totalPrice": "$320.00",
            "paymentStatus": "Failed",
            "fulfillmentStatus": "Unfulfilled",
            "shippingAddress": "789 Pine St, Chicago, IL",
            "actions": "Print"
        }
    ]

    # orders = []
    # for edge in orders_data['data']['orders']['edges']:
    #     node = edge['node']
    #     orders.append({
    #         "no": node['name'],
    #         "date": node['createdAt'],
    #         "customer": f"{node['customer']['firstName']} {node['customer']['lastName']}" if node['customer'] else "Guest",
    #         "totalPrice": f"${node['totalPriceSet']['shopMoney']['amount']}",
    #         "paymentStatus": node['displayFinancialStatus'],
    #         "fulfillmentStatus": node['displayFulfillmentStatus'],
    #         "shippingAddress": (
    #             f"{node['shippingAddress']['address1']}, {node['shippingAddress']['city']}, {node['shippingAddress']['country']}, {node['shippingAddress']['zip']}"
    #             if node['shippingAddress'] else "No Address"
    #         ),
    #         "actions": "View"
    #     })

    return render_template('index.html', shop=shop, orders=orders, )


@app.route('/order-details')
def order_details():
    order_id = request.args.get('order_id')
    if not order_id:
        return jsonify({'error': 'Order ID is required'}), 400

    # response = api.order(order_id)
    # if response.status_code != 200:
    #     return jsonify({'error': 'Failed to fetch order details'}), response.status_code

    # json_data = response.json()
    # order_data = json_data['data']['orders']['edges']['node']
    # order = {
    #     "no": order_data['name'],
    #     "date": order_data['createdAt'],
    #     "customer": f"{order_data['customer']['firstName']} {order_data['customer']['lastName']}" if order_data['customer'] else "Guest",
    #     "totalPrice": f"${order_data['totalPriceSet']['shopMoney']['amount']}",
    #     "paymentStatus": order_data['displayFinancialStatus'],
    #     "fulfillmentStatus": order_data['displayFulfillmentStatus'],
    #     "shippingAddress": (
    #         f"{order_data['shippingAddress']['address1']}, {order_data['shippingAddress']['city']}, {order_data['shippingAddress']['country']}, {order_data['shippingAddress']['zip']}"
    #         if order_data['shippingAddress'] else "No Address"
    #     ),
    #     "actions": "View"
    # }

    order_data = {
        "id": order_id,
        "date": "2025-01-22",
        "status": "Fulfilled",
        "_items": [
            {"title": "Product A", "quantity": 2, "price": "$20.00"},
            {"title": "Product B", "quantity": 1, "price": "$15.00"},
            {"title": "Product C", "quantity": 3, "price": "$10.00"}
        ],
        "subtotal": "$85.00",
        "tax": "$8.50",
        "total": "$93.50",
        "paid": "$93.50",
        "customer": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890"
        },
        "shipping_address": "123 Shopify Lane, Commerce City, CO, 80022"
    }

    # Render the order details page or return JSON data
    return render_template('order-details.html', order_data=order_data)


@app.route('/products')
def fetch_products():
    """
    Fetches the products from the Shopify store.
    """
    shop = request.args.get('shop')
    if not shop:
        return "Missing shop parameter", 400

    # Retrieve the access token from your database
    token = "stored_access_token_for_this_shop"  # Replace with your database retrieval logic
    url = f"https://{shop}/admin/api/2025-01/products.json"
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json",  # Add Content-Type header
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    return "Failed to fetch products", response.status_code


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


if __name__ == "__main__":
    # Ensure app is running in HTTPS using ngrok or other tunneling tools for local development
    app.run(host="0.0.0.0", port=5000, debug=True)