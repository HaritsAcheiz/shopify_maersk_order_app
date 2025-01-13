from flask import Flask, request, redirect, session, url_for, render_template, jsonify
from shopify import ShopifyApi
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")

# Shopify App Config
API_KEY = "your-shopify-app-api-key"
API_SECRET = "your-shopify-app-api-secret"
SCOPES = "read_products,write_products"
REDIRECT_URI = "https://your-app-domain.com/auth/callback"


def init_shopify():
    global shopify_api
    if not shopify_api:
        try:
            shopify_api = ShopifyApi(
                store_name=os.getenv('STORE_NAME'),
                access_token=os.getenv('ACCESS_TOKEN'),
                version='2024-01'
            )
            shopify_api.create_session()

            return shopify_api

        except Exception as e:
            logger.error(f"Failed to initialize Shopify API: {e}")
            raise


@app.route("/")
def index():
    """Redirect to order shipping label page"""
    return redirect(url_for('order_shipping_label'))


@app.route("/order-shipping-label")
def order_shipping_label():
    """Render the order shipping label page"""
    try:
        # Initialize Shopify connection
        init_shopify()
        return render_template("order-shipping-label.html")
    except Exception as e:
        logger.error(f"Error accessing order shipping label page: {e}")
        return render_template("error.html", error=str(e))


@app.route("/api/orders")
def get_orders():
    """API endpoint to fetch orders"""
    try:
        api = init_shopify()
        cursor = request.args.get('cursor')

        # Get orders from Shopify
        response = api.orders(cursor) if cursor else api.orders()

        if 'errors' in response:
            logger.error(f"Shopify API error: {response['errors']}")
            return jsonify({'error': response['errors']}), 400

        return jsonify(response)
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html', error="Internal server error"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
