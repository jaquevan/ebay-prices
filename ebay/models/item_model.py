import sqlite3
import logging
from dataclasses import dataclass
from ebay.utils.logger import configure_logger
from ebay.utils.sql_utils import get_db_connection
from ebay.services.ebay_client import search_item_by_id


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Item:
    id: int
    ebay_item_id: str
    title: str
    price: float
    available_quantity: int
    sold_quantity: int
    alert_price: float


    def __post_init__(self):
        if self.price < 0:
           raise ValueError(f"Price must be non-negative, got {self.price}")
        if self.available_quantity < 0:
            raise ValueError(f"Available quantity must be non-negative, got {self.available_quantity}")
        if self.sold_quantity < 0:
            raise ValueError(f"Sold quantity must be non-negative, got {self.sold_quantity}")

        # Set default alert_price to 60% of the original price if not provided
        self.alert_price = self.price * 0.6

def create_item(ebay_item_id: str, 
                title: str, 
                price: float, 
                available_quantity: int,
                sold_quantity: int,
                alert_price: float) -> None:
   
   if not isinstance(price, (int, float)) or price <= 0:
       raise ValueError(f"Invalid price: {price} (must be a positive number).")
   if not isinstance(available_quantity, int) or available_quantity < 0:
       raise ValueError(f"Invalid quantity: {available_quantity} (must be a non-negative integer).")


   try:
       with get_db_connection() as conn:
           cursor = conn.cursor()
           cursor.execute("""
               INSERT INTO items (ebay_item_id, title, price, available_quantity, sold_quantity, alert_price)
               VALUES (?, ?, ?, ?, ?, ?)
           """, (ebay_item_id, title, price, available_quantity, sold_quantity, alert_price))
           conn.commit()
           logger.info("Item created successfully: %s - %s", ebay_item_id, title)
   except sqlite3.IntegrityError as e:
       logger.error("Item with ebay id '%s' and title '%s' already exists.", ebay_item_id, title)
       raise ValueError(f"Item with ebay id '{ebay_item_id}' and title '{title}' already exists.") from e
   except sqlite3.Error as e:
       logger.error("Database error while creating item: %s", str(e))
       raise sqlite3.Error(f"Database error: {str(e)}")

def create_item_ebay_id(ebay_item_id):
    data = search_item_by_id(ebay_item_id=ebay_item_id)
    if not data:
        raise ValueError(f"No data found for ebay item id: {ebay_item_id}")

    try:

        # Getting and parsing the data from the json
        title = data.get("title")
        if not title:
            raise ValueError("Title is missing from item data")
        
        price_info = data.get("price", {})
        price = float(price_info.get("value", 0))
        if price <= 0:
            raise ValueError(f"Invalid price: {price}")

        estimated_availabilities = data.get("estimatedAvailabilities", [])
        if estimated_availabilities:
            available_quantity = estimated_availabilities[0].get("estimatedAvailableQuantity")
            sold_quantity = estimated_availabilities[0].get("estimatedSoldQuantity")
        else:
            available_quantity = None
            sold_quantity = None

        alert_price = price * 0.6

   
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO items (ebay_item_id, title, price, available_quantity, sold_quantity, alert_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ebay_item_id, title, price, available_quantity, sold_quantity, alert_price))
            conn.commit()
            logger.info("Item created successfully: %s - %s", ebay_item_id, title)


            # Get the auto id
            item_id = cursor.lastrowid

        # Create and return the Item intance
        return Item(
            id=item_id,
            ebay_item_id = ebay_item_id,
            title = title,
            price = price,
            available_quantity = available_quantity,
            sold_quantity = sold_quantity,
            alert_price = alert_price
        )
    except sqlite3.IntegrityError as e:
        logger.error("Item with ebay id '%s' and title '%s' already exists.", ebay_item_id, title)
        raise ValueError(f"Item with ebay id '{ebay_item_id}' and title '{title}' already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating item: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")

def delete_item(item_id: int) -> None:
   try:
       with get_db_connection() as conn:
           cursor = conn.cursor()
           cursor.execute("SELECT deleted FROM items WHERE id = ?", (item_id,))
           try:
               deleted = cursor.fetchone()[0]
               if deleted:
                   logger.info("Item with ID %s has already been deleted", item_id)
                   raise ValueError(f"Item with ID {item_id} has already been deleted")
           except TypeError:
               logger.info("Item with ID %s not found", item_id)
               raise ValueError(f"Item with ID {item_id} not found")


           cursor.execute("UPDATE items SET deleted = TRUE WHERE id = ?", (item_id,))
           conn.commit()
           logger.info("Item with ID %s marked as deleted.", item_id)
   except sqlite3.Error as e:
       logger.error("Database error while deleting item: %s", str(e))
       raise e


def get_item_by_id(item_id: int) -> Item:
   try:
       with get_db_connection() as conn:
           cursor = conn.cursor()
           logger.info("Attempting to retrieve item with ID %s", item_id)
           cursor.execute("""
               SELECT id, ebay_item_id, title, price, available_quantity, sold_quantity, alert_price, deleted
               FROM items
               WHERE id = ?
           """, (item_id,))
           row = cursor.fetchone()


           if row:
               if row[7]:  # deleted is True
                   raise ValueError(f"Item with ID {item_id} has been deleted")

               return Item(
                   id=row[0],
                   ebay_item_id=row[1],
                   title=row[2],
                   price=row[3],
                   available_quantity=row[4],
                   sold_quantity = row[5],
                   alert_price=row[6]
               )


           # This line only executes if 'if row:' was False
           logger.info("Item with ID %s not found", item_id)
           raise ValueError(f"Item with ID {item_id} not found")


   except sqlite3.Error as e:
       logger.error("Database error while retrieving item by ID %s: %s", item_id, str(e))
       raise e




def get_all_items() -> list[dict]:
   try:
       with get_db_connection() as conn:
           cursor = conn.cursor()
           logger.info("Attempting to retrieve all non-deleted items from the catalog")
           cursor.execute("""
               SELECT id, seller, title, price, category, quantity
               FROM items
               WHERE deleted = FALSE
           """)
           rows = cursor.fetchall()


           if not rows:
               logger.warning("The item catalog is empty.")
               return []


           items = [
               {
                   "id"=row[0],
                   "ebay_item_id"=row[1],
                   "title"=row[2],
                   "price"=row[3],
                   "available_quantity"=row[4],
                   "sold_quantity" = row[5],
                   "alert_price"=row[6]
               }
               for row in rows
           ]
           logger.info("Retrieved %d items from the catalog", len(items))
           return items
   except sqlite3.Error as e:
       logger.error("Database error while retrieving all items: %s", str(e))
       raise e


def update_item_quantity(item_id: int, quantity: int) -> None:
   if not isinstance(quantity, int) or quantity < 0:
       raise ValueError(f"Invalid quantity: {quantity} (must be a non-negative integer).")


   try:
       with get_db_connection() as conn:
           cursor = conn.cursor()
           logger.info("Attempting to update quantity for item with ID %d", item_id)
           cursor.execute("SELECT deleted FROM items WHERE id = ?", (item_id,))
           try:
               deleted = cursor.fetchone()[0]
               if deleted:
                   logger.info("Item with ID %d has been deleted", item_id)
                   raise ValueError(f"Item with ID {item_id} has been deleted")
           except TypeError:
               logger.info("Item with ID %d not found", item_id)
               raise ValueError(f"Item with ID {item_id} not found")


           cursor.execute("UPDATE items SET quantity = ? WHERE id = ?", (quantity, item_id))
           conn.commit()
           logger.info("Quantity updated for item with ID: %d", item_id)
   except sqlite3.Error as e:
       logger.error("Database error while updating quantity for item with ID %d: %s", item_id, str(e))
       raise e
