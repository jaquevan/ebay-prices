from dotenv import load_dotenv
import requests
from flask import Flask, jsonify, make_response, Response, request
import logging as logger
import sqlite3

# from flask_cors import CORS

from ebay.models.item_model import Item
from ebay.utils.sql_utils import check_database_connection, check_table_exists, get_db_connection
from ebay.services.ebay_client import get_access_token, search_items, search_item_by_id
from ebay.models.item_model import create_item

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

    Parameters:
        query (str): The search keyword.
        limit (int, optional): The maximum number of items to retrieve. Default is 5.

    Returns:
        Response: A JSON response containing the search results, or an error message.

    Example:
        curl -X GET "http://localhost:5000/api/search/summary?query=laptop"

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

    Parameters:
        query (str): The search keyword.
        limit (int, optional): The maximum number of items to retrieve. Default is 5.

    Returns:
        Response: A JSON response containing the top search result, or an error message.

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

    Parameters:
        ebay_item_id (str): The eBay item ID of the item to search for.

    Returns:
        Response: A JSON response containing the item details, or an error message.

    Example:
        curl -X GET "http://localhost:5000/api/search/item/ebay_id?ebay_item_id=v1|254582474636|0"

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
    Get the sold quantity for a specific item on eBay.

    This endpoint retrieves the sold quantity of an item based on its eBay item ID.

    Parameters:
        ebay_item_id (str): The eBay item ID of the item to search for.

    Returns:
        Response: A JSON response containing the sold quantity of the item, or an error message.

    Example:
        curl -X GET "http://localhost:5000/api/search/item/sold_quantity?ebay_item_id=v1|254582474636|0"
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
def get_available_quantity():
    """
    Get the available quantity for a specific item on eBay.
    This endpoint retrieves the available quantity of an item based on its eBay item ID.

    Parameters:
        ebay_item_id (str): The eBay item ID of the item to search for.

    Returns:
        Response: A JSON response containing the available quantity of the item, or an error message.

    Example:
        curl -X GET "http://localhost:5000/api/search/item/available_quantity?ebay_item_id=v1|254582474636|0"
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
    
#
# Wishlist Management
#

# Route to add an item to the wishlist
@app.route('/api/add-item-to-wishlist', methods=['POST'])
def add_item_to_wishlist() -> Response:
    """
    Route to add an item to the wishlist by its unique attributes.

    Expected JSON Input:
        - ebay_item_id (str): The eBay item ID.
        - title (str): The title of the item.
        - price (float): The price of the item.
        - available_quantity (int): The available quantity of the item.
        - sold_quantity (int): The sold quantity of the item.
        - alert_price (float): The alert price for the item.

    Returns:
        JSON response indicating success of the addition or error message.
    """
    try:
        data = request.get_json()

        ebay_item_id = data.get('ebay_item_id')
        title = data.get('title')
        price = data.get('price')
        available_quantity = data.get('available_quantity')
        sold_quantity = data.get('sold_quantity')
        alert_price = data.get('alert_price')

        if not ebay_item_id or not title or not isinstance(price, (int, float)) or price <= 0 or available_quantity < 0 or sold_quantity < 0:
            return make_response(jsonify({'error': 'Invalid input data'}), 400)

        # Create the item in the wishlist
        create_item(ebay_item_id, title, price, available_quantity, sold_quantity, alert_price)

        logger.info(f"Item {title} added to wishlist")
        return make_response(jsonify({'status': 'success', 'message': 'Item added to wishlist'}), 201)

    except Exception as e:
        logger.error(f"Error adding item to wishlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


# Function to remove an item from the wishlist by its item id
def remove_item_from_wishlist(item_id: int) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM wishlist WHERE id = ?", (item_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Item with ID %s has already been deleted", item_id)
                    raise ValueError(f"Item with ID {item_id} has already been deleted")
            except TypeError:
                logger.info("Item with ID %s not found", item_id)
                raise ValueError(f"Item with ID {item_id} not found")

            cursor.execute("UPDATE wishlist SET deleted = TRUE WHERE id = ?", (item_id,))
            conn.commit()
            logger.info("Item with ID %s marked as deleted in wishlist.", item_id)
    except sqlite3.Error as e:
        logger.error("Database error while deleting item from wishlist: %s", str(e))
        raise e


# Route to remove an item from the wishlist by item id
@app.route('/api/remove-item-from-wishlist/<int:item_id>', methods=['DELETE'])
def remove_item(item_id: int) -> Response:
    """
    Route to remove an item from the wishlist by its item ID.

    Path Parameter:
        - item_id (int): The ID of the item to remove.

    Returns:
        JSON response indicating success or error message.
    """
    try:
        remove_item_from_wishlist(item_id)
        return make_response(jsonify({'status': 'success', 'message': 'Item removed from wishlist'}), 200)

    except Exception as e:
        logger.error(f"Error removing item from wishlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


# Route to get all items in the wishlist
@app.route('/api/get-wishlist', methods=['GET'])
def get_wishlist() -> Response:
    """
    Route to retrieve all non-deleted items from the wishlist.

    Returns:
        JSON response with a list of items in the wishlist.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ebay_item_id, title, price, available_quantity, sold_quantity, alert_price
                FROM wishlist
                WHERE deleted = FALSE
            """)
            rows = cursor.fetchall()

            items = [
                {
                    "id": row[0],
                    "ebay_item_id": row[1],
                    "title": row[2],
                    "price": row[3],
                    "available_quantity": row[4],
                    "sold_quantity": row[5],
                    "alert_price": row[6]
                }
                for row in rows
            ]

            logger.info(f"Retrieved {len(items)} items from the wishlist")
            return make_response(jsonify(items), 200)

    except sqlite3.Error as e:
        logger.error("Database error while retrieving wishlist items: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0", port=5000)



