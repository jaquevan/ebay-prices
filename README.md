# ebay-prices


## Project Description: What the application does at a high level

This application manages a wishlist for eBay items. It uses the eBay API allowing users to add, remove, and retrieve items from their wishlist. Using an SQLite db, we store wishlist items and users. 
Built using Python and Flask with executables for building the docker container and virtual environment. Users can execute various actions through defined routes/API endpoints, making interacting with eBay’s catalog easy. This is ideal for frequent shoppers and eBay scalpers!

With love, 

Evan, Zhi, and Jorge ;3



## Routes

### 1. **Search**

- **Request Type:** `GET`  
- **Purpose:** Searches for items on eBay and returns search results.

#### **Request Body:**
  - `query` (str): The search keyword.
  - `limit` (int, optional): The maximum number of items to retrieve. Default is 5.
  - 
Success Response Example:
items = [ {ebay_item_id 1….}, ebay_item_id 2….}]
Example Request:
{ query: computer, limit(): 5 }

#### **Response Format:** JSON  
- **Success Response Example:**
  ```json
  {
      "items": [
          {
              "ebay_item_id": "v1|205157122545|0",
              "price": 334.99,
              "title": "DELL PRECISION 5540 | CORE I9-9980HK | 512GB | 32GB RAM | NO OS/NO PWR ADAPTER"
          },
          {
              "ebay_item_id": "v1|326323962677|0",
              "price": 105.0,
              "title": "Dell Latitude 7390 Laptop 13.3\" Laptop Intel Core i5 8GB 128GB SSD Windows 11"
          }
      ]
  }
  
Get_top_search_result
Request Type: GET
Purpose: For a given keyword, show the top result, based off the search route
Request Body:
query (str): The search keyword.
limit (int, optional): The maximum number of items to retrieve. Default is 5.
Response Format: JSON
Success Response Example:
items = [ {ebay_item_id 1….}, ebay_item_id 2….}]
Example Request:
{ query: computer, limit(): 5 }
Example Response: 
{
    "top_item": {
        "ebay_item_id": "v1|205157122545|0",
        "price": 334.99,
        "title": "DELL PRECISION 5540 | CORE I9-9980HK | 512GB | 32GB RAM | NO OS/NO PWR ADAPTER"
    }
}

Search_ebay_id
Request Type: GET
Purpose: Search for an item on eBay given the eBay item id.
Request Body:
ebay_item_id (str): The eBay item ID of the item to search for.
Response Format: JSON
Success Response Example:
{ available_quantity:..., ebay_item_id:..., price:...., …. }
Example Request:
{ ebay_item_id: ‘2’ }
Example Response: 
{
    "available_quantity": null,
    "ebay_item_id": "v1|254582474636|0",
    "price": 140.47,
    "sold_quantity": 790,
    "title": "HP X360 11 G4 2-in-1 Touch Laptop PC 11.6\" Windows 11 Core i5 8GB RAM 128GB SSD"
}

Get_sold_quantity
Request Type: GET
Purpose: Get the sold quantity for a specific item on eBay
Request Body:
ebay_item_id (str): The eBay item ID of the item to search for.
Response Format: JSON
Success Response Example:
{ Ebay_item_id:..., sold_quantity:..., Title:....}
Example Request:
{ ebay_item_id: ‘2’ }
Example Response: 
{
    "Ebay Item ID": "v1|254582474636|0",
    "Sold quantity: ": 790,
    "Title": "HP X360 11 G4 2-in-1 Touch Laptop PC 11.6\" Windows 11 Core i5 8GB RAM 128GB SSD"
}


Get_available_quantity
Request Type: GET
Purpose: Get the available quantity for a specific item on eBay.
Request Body:
ebay_item_id (str): The eBay item ID of the item to search for.
Response Format: JSON
Success Response Example:
{ available_quantity:..., ebay_item_id:..., Title:....}
Example Request:
{ ebay_item_id: ‘2’ }
Example Response: 
{
    "Available quantity: ": 0,
    "Ebay Item ID": "v1|254582474636|0",
    "Title": "HP X360 11 G4 2-in-1 Touch Laptop PC 11.6\" Windows 11 Core i5 8GB RAM 128GB SSD"
}


Add_item_to_wishlist
Request Type: POST
Purpose: Route to add an item to the wishlist by its unique attributes.
Request Body:
ebay_item_id (str): The eBay item ID.
title (str): The title of the item.
price (float): The price of the item.
available_quantity (int): The available quantity of the item.
sold_quantity (int): The sold quantity of the item.
alert_price (float): The alert price for the item.
Response Format: JSON
Success Response Example:
{'status': 'success', 'message': 'Item added to wishlist'}
Example Request:
{ ebay_item_id: ‘2’, title: ‘Dell Computer’, price: 23.99, available_quantity: 20, sold_quantity: 10, alert_price: 4}
Example Response: 
{'status': 'success', 'message': 'Item added to wishlist'}

Remove_item_from_wishlist
Request Type: DELETE
Purpose: Route to remove an item from the wishlist by its item ID.
Request Body:
item_id (int): The ID of the item to remove.
Response Format: JSON
Success Response Example:
{'status': 'success', 'message': 'Item removed from wishlist'}
Example Request:
{ item_id: 3 }
{item_id: v1|254582474636|0} ( not in DB )
Example Response: 
{'status': 'success', 'message': 'Item removed from wishlist'}
 "error": "Item with eBay item ID v1|254582474636|0 not found in the wishlist"
