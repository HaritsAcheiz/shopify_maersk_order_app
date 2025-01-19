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

SHOPIFY_CLIENT_ID = os.getenv('API_KEY')
SHOPIFY_CLIENT_SECRET = os.getenv('API_SECRET')
SHOPIFY_SCOPE = "read_products,write_products,read_all_orders,read_orders,write_orders"
REDIRECT_URI = os.getenv('REDIRECT_URI')


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
    print(orders_data)

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