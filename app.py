from dotenv import load_dotenv
import requests
from flask import Flask, jsonify, make_response, Response, request


# from flask_cors import CORS

from ebay.models.item_model import Item
from ebay.utils.sql_utils import check_database_connection, check_table_exists
from ebay.services.ebay_client import get_access_token, search_items, search_item_by_id

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
@app.route('/api/search/summary', methods=['GET'])
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
    
    ####################################################################################
    #
    # example curl: curl -X GET "http://localhost:5000/api/search/summary?query=laptop"
    #
    ###################################################################################

# Top search result given the category or keyword
@app.route('/api/search/top-search', methods=['GET'])
def get_top_search_result():
    """
    Get the top search result for a given keyword. Based on the above function which gets a search
    """
    query = request.args.get('query')
    limit = int(request.args.get('limit', 5))
    if not query:
        return make_response(jsonify({'error': 'Query parameter is required'}), 400)

    try:
        items = search_items(query, limit)

        if not items:
            return make_response(jsonify({'error': 'No items found for the given query'}), 404)
        
        top_item = items[0]

        # Create a summary for the top item
        summary = {
            "ebay_item_id": top_item.get("ebay_item_id"),
            "title": top_item.get("title"),
            "price": top_item.get("price"),
        }

        return make_response(jsonify({"top_item": summary}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    
    ####################################################################################
    #
    # example curl: curl -X GET "http://localhost:5000/api/search/top-search?query=laptop"
    #
    ###################################################################################


# Search using ebay_item_id
@app.route('/api/search/item/ebay_id', methods=['GET'])
def search_ebay_id():
    """
    Search for an item on eBay given the ebay item id.
    """
    ebay_item_id = request.args.get('ebay_item_id')

    if not ebay_item_id:
        return make_response(jsonify({'error': 'Ebay item id parameter is required'}), 400)

    try:
        item_data = search_item_by_id(ebay_item_id)
        
        if not item_data:
            return make_response(jsonify({'error': 'No item found for the given eBay item ID'}), 404)

        title = item_data.get("title")
        if not title:
            raise ValueError("Title is missing from item data")
        
        price_info = item_data.get("price", {})
        price = float(price_info.get("value", 0))
        if price <= 0:
            raise ValueError(f"Invalid price: {price}")

        estimated_availabilities = item_data.get("estimatedAvailabilities", [])
        if estimated_availabilities:
            available_quantity = estimated_availabilities[0].get("estimatedAvailableQuantity")
            sold_quantity = estimated_availabilities[0].get("estimatedSoldQuantity")
        else:
            available_quantity = 0
            sold_quantity = 0

        return make_response(jsonify({
            "ebay_item_id": ebay_item_id,
            "title": title,
            "price": price,
            "available_quantity": available_quantity,
            "sold_quantity": sold_quantity
        }), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    
    ####################################################################################
    #
    # example curl: curl -X GET "http://localhost:5000/api/search/item/ebay_id?ebay_item_id=v1|254582474636|0"
    #
    ###################################################################################

@app.route('/api/search/item/sold_quantity', methods=['GET'])
def get_sold_quantity():
    """
    Get the sold quantity for a specific item.
    """
    ebay_item_id = request.args.get('ebay_item_id')

    if not ebay_item_id:
        return make_response(jsonify({'error': 'Ebay item id parameter is required'}), 400)

    try:
        item_data = search_item_by_id(ebay_item_id)
        
        if not item_data:
            return make_response(jsonify({'error': 'No item found for the given eBay item ID'}), 404)

        title = item_data.get("title", "Unknown Title")

        estimated_availabilities = item_data.get("estimatedAvailabilities", [])
        sold_quantity = (
            estimated_availabilities[0].get("estimatedSoldQuantity", 0)
            if estimated_availabilities else 0
        )

    
        return make_response(jsonify({
            "Ebay Item ID": ebay_item_id,
            "Title": title,
            "Sold quantity: ": sold_quantity
        }), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    

    ####################################################################################
    #
    # example curl: curl -X GET "http://localhost:5000/api/search/item/sold_quantity?ebay_item_id=v1|254582474636|0"
    #
    ###################################################################################

# this function gets the number of items available for a specific item and is similar to the above function
@app.route('/api/search/item/available_quantity', methods=['GET'])
def get_available_quantity(ebay_item_id):
    """
    Get the available quantity for a specific item.
    """
    ebay_item_id = request.args.get('ebay_item_id')

    if not ebay_item_id:
        return make_response(jsonify({'error': 'Ebay item id parameter is required'}), 400)

    try:
        item_data = search_item_by_id(ebay_item_id)
        
        if not item_data:
            return make_response(jsonify({'error': 'No item found for the given eBay item ID'}), 404)

        title = item_data.get("title", "Unknown Title")

        estimated_availabilities = item_data.get("estimatedAvailabilities", [])
        available_quantity = (
            estimated_availabilities[0].get("estimatedAvailableQuantity", 0)
            if estimated_availabilities else 0
        )
       
    
        return make_response(jsonify({
            "Ebay Item ID": ebay_item_id,
            "Title": title,
            "Available quantity: ": available_quantity
        }), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)
    
    ####################################################################################
    #
    # example curl: curl -X GET "http://localhost:5000/api/search/item/available_quantity?ebay_item_id=v1|254582474636|0"
    #
    ###################################################################################
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
