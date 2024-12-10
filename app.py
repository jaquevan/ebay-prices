from dotenv import load_dotenv
import requests
from flask import Flask, jsonify, make_response, Response, request


# from flask_cors import CORS

from ebay.models.item_model import Item
from ebay.utils.sql_utils import check_database_connection, check_table_exists
from ebay.services.ebay_client import get_access_token, search_items

# Load environment variables from .env file
load_dotenv()
load_dotenv(dotenv_path="./secrets.env", override=True)

app = Flask(__name__)
# This bypasses standard security stuff we'll talk about later
# If you get errors that use words like cross origin or flight,
# uncomment this
# CORS(app)

# Initialize model for route /

@app.route('/')
def index():
    return "Welcome to our eBay API item service!"

####################################################
#
# Healthchecks
#
####################################################


@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and wishlist table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if wishlist table exists...")
        check_table_exists("wishlist")
        app.logger.info("wishlist table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

#####################################################
# Token Management
#####################################################
@app.route('/api/token', methods=['GET'])
def get_token():
    """
    Generate and return an eBay API token.
    """
    try:
        token = get_access_token()
        return make_response(jsonify({'token': token}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

#####################################################
# Item Search Routes
#####################################################
@app.route('/api/search', methods=['GET'])
def search():
    """
    Search for items on eBay.
    """
    query = request.args.get('query')
    limit = int(request.args.get('limit', 5))
    if not query:
        return make_response(jsonify({'error': 'Query parameter is required'}), 400)

    try:
        items = search_items(query, limit)
        return make_response(jsonify({'items': items}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

##########################################################
#
# ebay items (eq. to meals in meal max)
#
##########################################################

##########################################################
# Function to search for an item by keyword or category
##########################################################
@app.route('/api/items/search', methods=['GET'])
def browse_items():
    """
    Search for items by category or keyword.

    """
    query = request.args.get('query')
    if not query:
        return make_response(jsonify({'error': 'Query parameter is required'}), 400)

    try:
        token = get_access_token()
        url = f'https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        items = response.json().get('itemSummaries', [])

        return make_response(jsonify({'items': items}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

##########################################################
# Function to get the top item of an ebay search since
# it returns alot of searches with the above method
##########################################################
@app.route('/api/items/top-search', methods=['GET'])
def get_top_search_result():
    """
    Get the top search result for a given keyword. Based on the above function which gets a search
    """
    query = request.args.get('query')
    if not query:
        return make_response(jsonify({'error': 'Query parameter is required'}), 400)

    try:
        token = get_access_token()
        url = f'https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=1'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        items = response.json().get('itemSummaries', [])

        if not items:
            return make_response(jsonify({'message': 'No results found'}), 200)

        # Simplify the output for the top item
        top_item = items[0]
        simplified_top_item = {
            'title': top_item.get('title'),
            'price': top_item.get('price', {}).get('value'),
            'currency': top_item.get('price', {}).get('currency'),
            'item_id': top_item.get('itemId'),
            'item_web_url': top_item.get('itemWebUrl'),
            'condition': top_item.get('condition'),
            'image_url': top_item.get('image', {}).get('imageUrl')
        }

        return make_response(jsonify({'top_item': simplified_top_item}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

# this function gets the number of items sold for a specific item
# for testing this function and function below use this test itemid:
# http://127.0.0.1:5001/api/items/v1|110567362227|0/sold-quantity (available for other function)
@app.route('/api/items/<item_id>/sold-quantity', methods=['GET'])
def get_sold_quantity(item_id):
    """
    Get the sold quantity for a specific item.
    """
    try:
        token = get_access_token()
        url = f'https://api.ebay.com/buy/browse/v1/item/{item_id}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        sold_count = response.json().get('estimatedSalesCount', 0)

        return make_response(jsonify({'item_id': item_id, 'sold_quantity': sold_count}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

# this function gets the number of items available for a specific item and is similar to the above function
@app.route('/api/items/<item_id>/available-quantity', methods=['GET'])
def get_available_quantity(item_id):
    """
    Get the available quantity for a specific item.
    """
    try:
        token = get_access_token()
        url = f'https://api.ebay.com/buy/browse/v1/item/{item_id}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        available_count = response.json().get('estimatedAvailableQuantity', 0)

        return make_response(jsonify({'item_id': item_id, 'available_quantity': available_count}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/orders/<item_id>', methods=['GET'])
##########################################################
# Function to get the number of orders
##########################################################

def number_of_orders(item_id):
    try:
        token = get_access_token()
        if not token:
            app.logger.error("Failed to retrieve access token.")
            return 0

        url = f'https://api.ebay.com/buy/browse/v1/item/{item_id}'
        app.logger.info(f"Requesting eBay API for item ID: {item_id}")

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        sales_count = data.get('estimatedSalesCount', 0)
        return sales_count

    except requests.RequestException as e:
        app.logger.error(f"Request error: {e}")
        return 0
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return 0

##########################################################
# Route to get number of orders for an item
##########################################################
# http://127.0.0.1:5000/api/orders/123

@app.route('/api/orders/<item_id>', methods=['GET'])
def get_number_of_orders(item_id):
    """
    API endpoint to get the number of orders for a specific item.

    Args:
        item_id (str): The eBay item ID.

    Returns:
        JSON response with the number of orders or an error message.
    """
    try:
        orders_count = number_of_orders(item_id)  # This returns an int
        return jsonify({'item_id': item_id, 'orders_count': orders_count})
    except Exception as e:
        app.logger.error(f"Error in get_number_of_orders: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
