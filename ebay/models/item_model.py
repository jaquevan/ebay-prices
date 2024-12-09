import sqlite3
import logging
from dataclasses import dataclass
from ebay.utils.logger import configure_logger
from ebay.utils.sql_utils import get_db_connection


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Item:
   id: int
   seller: str
   title: str
   price: float
   category: str
   quantity: int


   def __post_init__(self):
       if self.price < 0:
           raise ValueError(f"Price must be non-negative, got {self.price}")


def create_item(seller: str, title: str, price: float, category: str, quantity: int) -> None:
   if not isinstance(price, (int, float)) or price <= 0:
       raise ValueError(f"Invalid price: {price} (must be a positive number).")
   if not isinstance(quantity, int) or quantity < 0:
       raise ValueError(f"Invalid quantity: {quantity} (must be a non-negative integer).")


   try:
       with get_db_connection() as conn:
           cursor = conn.cursor()
           cursor.execute("""
               INSERT INTO items (seller, title, price, category, quantity)
               VALUES (?, ?, ?, ?, ?)
           """, (seller, title, price, category, quantity))
           conn.commit()
           logger.info("Item created successfully: %s - %s", seller, title)
   except sqlite3.IntegrityError as e:
       logger.error("Item with seller '%s' and title '%s' already exists.", seller, title)
       raise ValueError(f"Item with seller '{seller}' and title '{title}' already exists.") from e
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
               SELECT id, seller, title, price, category, quantity, deleted
               FROM items
               WHERE id = ?
           """, (item_id,))
           row = cursor.fetchone()


           if row:
               if row[6]:  # deleted is True
                   raise ValueError(f"Item with ID {item_id} has been deleted")


               return Item(
                   id=row[0],
                   seller=row[1],
                   title=row[2],
                   price=row[3],
                   category=row[4],
                   quantity=row[5]
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
                   "id": row[0],
                   "seller": row[1],
                   "title": row[2],
                   "price": row[3],
                   "category": row[4],
                   "quantity": row[5],
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
