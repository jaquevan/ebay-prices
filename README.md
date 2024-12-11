  
Project Description: What the application does at a high level

This application manages a wishlist for eBay items. It uses the eBay API allowing users to add, remove, and retrieve items from their wishlist. Using an SQLite db, we store wishlist items and users.   
Built using Python and Flask with executables for building the docker container and virtual environment. Users can execute various actions through defined routes/API endpoints, making interacting with eBay’s catalog easy. This is ideal for frequent shoppers and eBay scalpers\!

With love, 

Evan, Zhi, and Jorge ;3

Routes

* Search  
  * Request Type: GET  
  * Purpose: Searches for the items on eBay and gives the user search results  
  * Request Body:  
    * query (str): The search keyword.  
    * limit (int, optional): The maximum number of items to retrieve. Default is 5\.  
  * Response Format: JSON  
    * Success Response Example:  
    * items \= \[ {ebay\_item\_id 1….}, ebay\_item\_id 2….}\]  
  * Example Request:  
    * { query: computer, limit(): 5 }  
  * Example Response:   
    * "items": \[  
    *         {  
    *             "ebay\_item\_id": "v1|205157122545|0",  
    *             "price": 334.99,  
    *             "title": "DELL PRECISION 5540 | CORE I9-9980HK | 512GB | 32GB RAM | NO OS/NO PWR ADAPTER"  
    *         },  
    *         {  
    *             "ebay\_item\_id": "v1|326323962677|0",  
    *             "price": 105.0,  
    *             "title": "Dell Latitude 7390 Laptop 13.3\\" Laptop Intel Core i5 8GB 128GB SSD Windows 11"  
    *         },  
* Get\_top\_search\_result  
  * Request Type: GET  
  * Purpose: For a given keyword, show the top result, based off the search route  
  * Request Body:  
    * query (str): The search keyword.  
    * limit (int, optional): The maximum number of items to retrieve. Default is 5\.  
  * Response Format: JSON  
    * Success Response Example:  
    * items \= \[ {ebay\_item\_id 1….}, ebay\_item\_id 2….}\]  
  * Example Request:  
    * { query: computer, limit(): 5 }  
  * Example Response:   
    * {  
    *     "top\_item": {  
    *         "ebay\_item\_id": "v1|205157122545|0",  
    *         "price": 334.99,  
    *         "title": "DELL PRECISION 5540 | CORE I9-9980HK | 512GB | 32GB RAM | NO OS/NO PWR ADAPTER"  
    *     }  
    * }

* Search\_ebay\_id  
  * Request Type: GET  
  * Purpose: Search for an item on eBay given the eBay item id.  
  * Request Body:  
    * ebay\_item\_id (str): The eBay item ID of the item to search for.  
  * Response Format: JSON  
    * Success Response Example:  
    * { available\_quantity:..., ebay\_item\_id:..., price:...., …. }  
  * Example Request:  
    * { ebay\_item\_id: ‘2’ }  
  * Example Response:   
    * {  
    *     "available\_quantity": null,  
    *     "ebay\_item\_id": "v1|254582474636|0",  
    *     "price": 140.47,  
    *     "sold\_quantity": 790,  
    *     "title": "HP X360 11 G4 2-in-1 Touch Laptop PC 11.6\\" Windows 11 Core i5 8GB RAM 128GB SSD"  
    * }

* Get\_sold\_quantity  
  * Request Type: GET  
  * Purpose: Get the sold quantity for a specific item on eBay  
  * Request Body:  
    * ebay\_item\_id (str): The eBay item ID of the item to search for.  
  * Response Format: JSON  
    * Success Response Example:  
    * { Ebay\_item\_id:..., sold\_quantity:..., Title:....}  
  * Example Request:  
    * { ebay\_item\_id: ‘2’ }  
  * Example Response:   
    * {  
    *     "Ebay Item ID": "v1|254582474636|0",  
    *     "Sold quantity: ": 790,  
    *     "Title": "HP X360 11 G4 2-in-1 Touch Laptop PC 11.6\\" Windows 11 Core i5 8GB RAM 128GB SSD"  
    * }

* Get\_available\_quantity  
  * Request Type: GET  
  * Purpose: Get the available quantity for a specific item on eBay.  
  * Request Body:  
    * ebay\_item\_id (str): The eBay item ID of the item to search for.  
  * Response Format: JSON  
    * Success Response Example:  
    * { available\_quantity:..., ebay\_item\_id:..., Title:....}  
  * Example Request:  
    * { ebay\_item\_id: ‘2’ }  
  * Example Response:   
    * {  
    *     "Available quantity: ": 0,  
    *     "Ebay Item ID": "v1|254582474636|0",  
    *     "Title": "HP X360 11 G4 2-in-1 Touch Laptop PC 11.6\\" Windows 11 Core i5 8GB RAM 128GB SSD"  
    * }

* Add\_item\_to\_wishlist  
  * Request Type: POST  
  * Purpose: Route to add an item to the wishlist by its unique attributes.  
  * Request Body:  
    * ebay\_item\_id (str): The eBay item ID.  
    * title (str): The title of the item.  
    * price (float): The price of the item.  
    * available\_quantity (int): The available quantity of the item.  
    * sold\_quantity (int): The sold quantity of the item.  
    * alert\_price (float): The alert price for the item.  
  * Response Format: JSON  
    * Success Response Example:  
    * {'status': 'success', 'message': 'Item added to wishlist'}  
  * Example Request:  
    * { ebay\_item\_id: ‘2’, title: ‘Dell Computer’, price: 23.99, available\_quantity: 20, sold\_quantity: 10, alert\_price: 4}  
  * Example Response:   
    * {'status': 'success', 'message': 'Item added to wishlist'}

* Remove\_item\_from\_wishlist  
  * Request Type: DELETE  
  * Purpose: Route to remove an item from the wishlist by its item ID.  
  * Request Body:  
    * item\_id (int): The ID of the item to remove.  
  * Response Format: JSON  
    * Success Response Example:  
    * {'status': 'success', 'message': 'Item removed from wishlist'}  
  * Example Request:  
    * { item\_id: 3 }  
      * {item\_id: v1|254582474636|0} ( not in DB )  
  * Example Response:   
    * {'status': 'success', 'message': 'Item removed from wishlist'}  
      *  "error": "Item with eBay item ID v1|254582474636|0 not found in the wishlist"

* Get\_wishlist  
  * Request Type: GET  
  * Purpose: Route to retrieve all non-deleted items from the wishlist.  
  * Request Body:  
    * N/A  
  * Response Format: JSON  
    * Success Response Example:  
    * { available\_quantity:..., ebay\_item\_id:..., Title:....}  
  * Example Request:  
    * { ebay\_item\_id: ‘2’ }  
  * Example Response:   
    * {  
    *     "Available quantity: ": 0,  
    *     "Ebay Item ID": "v1|254582474636|0",  
    *     "Title": "HP X360 11 G4 2-in-1 Touch Laptop PC 11.6\\" Windows 11 Core i5 8GB RAM 128GB SSD"  
    * }

   
