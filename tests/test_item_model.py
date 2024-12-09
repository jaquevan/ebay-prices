from contextlib import contextmanager
import re
import sqlite3
import sys
import os
import pytest


# Add the root directory of the project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from ebay.models.item_model import (
   WishlistItem,
   create_item,
   delete_item,
   get_item_by_id,
   get_all_items,
   update_item_quantity
)


######################################################
#
#    Fixtures
#
######################################################


def normalize_whitespace(sql_query: str) -> str:
   return re.sub(r'\s+', ' ', sql_query).strip()


# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
   mock_conn = mocker.Mock()
   mock_cursor = mocker.Mock()


   # Mock the connection's cursor
   mock_conn.cursor.return_value = mock_cursor
   mock_cursor.fetchone.return_value = None  # Default return for queries
   mock_cursor.fetchall.return_value = []
   mock_conn.commit.return_value = None


   # Mock the get_db_connection context manager from sql_utils
   @contextmanager
   def mock_get_db_connection():
       yield mock_conn  # Yield the mocked connection object


   mocker.patch("ebay.models.item_model.get_db_connection", mock_get_db_connection)


   return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################


def test_create_item(mock_cursor):
   """Test creating a new item in the catalog."""


   # Call the function to create a new item
   create_item(seller="Seller Name", title="Item Title", price=100.0, category="Electronics", quantity=10)


   expected_query = normalize_whitespace("""
       INSERT INTO items (seller, title, price, category, quantity)
       VALUES (?, ?, ?, ?, ?)
   """)


   actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])


   # Assert that the SQL query was correct
   assert actual_query == expected_query, "The SQL query did not match the expected structure."


   # Extract the arguments used in the SQL call (second element of call_args)
   actual_arguments = mock_cursor.execute.call_args[0][1]


   # Assert that the SQL query was executed with the correct arguments
   expected_arguments = ("Seller Name", "Item Title", 100.0, "Electronics", 10)
   assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_item_duplicate(mock_cursor):
   """Test creating an item with a duplicate seller and title (should raise an error)."""


   # Simulate that the database will raise an IntegrityError due to a duplicate entry
   mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: items.seller, items.title")


   # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
   with pytest.raises(ValueError, match=r"Item with seller 'Seller Name' and title 'Item Title' already exists."):
       create_item(seller="Seller Name", title="Item Title", price=100.0, category="Electronics", quantity=10)


def test_create_item_invalid_price():
   """Test error when trying to create an item with an invalid price (e.g., negative price)"""


   # Attempt to create an item with a negative price
   with pytest.raises(ValueError, match=r"Invalid price: -100.0 \(must be a positive number\)."):
       create_item(seller="Seller Name", title="Item Title", price=-100.0, category="Electronics", quantity=10)


   # Attempt to create an item with a non-numeric price
   with pytest.raises(ValueError, match=r"Invalid price: invalid \(must be a positive number\)."):
       create_item(seller="Seller Name", title="Item Title", price="invalid", category="Electronics", quantity=10)


def test_create_item_invalid_quantity():
   """Test error when trying to create an item with an invalid quantity (e.g., negative quantity)."""


   # Attempt to create an item with a negative quantity
   with pytest.raises(ValueError, match=r"Invalid quantity: -10 \(must be a non-negative integer\)."):
       create_item(seller="Seller Name", title="Item Title", price=100.0, category="Electronics", quantity=-10)


   # Attempt to create an item with a non-integer quantity
   with pytest.raises(ValueError, match=r"Invalid quantity: invalid \(must be a non-negative integer\)."):
       create_item(seller="Seller Name", title="Item Title", price=100.0, category="Electronics", quantity="invalid")


def test_delete_item(mock_cursor):
   """Test soft deleting an item from the catalog by item ID."""


   # Simulate that the item exists (id = 1)
   mock_cursor.fetchone.return_value = ([False])


   # Call the delete_item function
   delete_item(1)


   # Normalize the SQL for both queries (SELECT and UPDATE)
   expected_select_sql = normalize_whitespace("SELECT deleted FROM items WHERE id = ?")
   expected_update_sql = normalize_whitespace("UPDATE items SET deleted = TRUE WHERE id = ?")


   # Access both calls to `execute()` using `call_args_list`
   actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
   actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])


   # Ensure the correct SQL queries were executed
   assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
   assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."


   # Ensure the correct arguments were used in both SQL queries
   expected_select_args = (1,)
   expected_update_args = (1,)


   actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
   actual_update_args = mock_cursor.execute.call_args_list[1][0][1]


   assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
   assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_delete_item_bad_id(mock_cursor):
   """Test error when trying to delete a non-existent item."""


   # Simulate that no item exists with the given ID
   mock_cursor.fetchone.return_value = None


   # Expect a ValueError when attempting to delete a non-existent item
   with pytest.raises(ValueError, match="Item with ID 999 not found"):
       delete_item(999)


def test_delete_item_already_deleted(mock_cursor):
   """Test error when trying to delete an item that's already marked as deleted."""


   # Simulate that the item exists but is already marked as deleted
   mock_cursor.fetchone.return_value = ([True])


   # Expect a ValueError when attempting to delete an item that's already been deleted
   with pytest.raises(ValueError, match="Item with ID 999 has already been deleted"):
       delete_item(999)


######################################################
#
#    Get Item
#
######################################################


def test_get_item_by_id(mock_cursor):


   # Simulate that the item exists (id = 1) and is not deleted
   # Expected result based on the simulated fetchone return value


   mock_cursor.fetchone.return_value = (1, "Seller A", "Item A", 100.0, "Category A", 10, False)


   expected_result = WishlistItem(
       id=1,
       seller="Seller A",
       title="Item A",
       price=100.0,
       category="Category A",
       quantity=10
   )
   result = get_item_by_id(1)
   # Ensure the result matches the expected output
   assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_get_item_by_id_bad_id(mock_cursor):
   # Simulate that no item exists for the given ID
   mock_cursor.fetchone.return_value = None


   # Expect a ValueError when the item is not found
   with pytest.raises(ValueError, match="Item with ID 999 not found"):
       get_item_by_id(999)


def test_get_all_items(mock_cursor):
   """Test retrieving all items that are not marked as deleted."""


   # Simulate that there are multiple items in the database
   mock_cursor.fetchall.return_value = [
       (1, "Seller A", "Item A", 100.0, "Electronics", 10),
       (2, "Seller B", "Item B", 200.0, "Books", 5),
       (3, "Seller C", "Item C", 300.0, "Clothing", 2)
   ]


   # Call the get_all_items function
   items = get_all_items()


   # Ensure the results match the expected output
   expected_result = [
       {"id": 1, "seller": "Seller A", "title": "Item A", "price": 100.0, "category": "Electronics", "quantity": 10},
       {"id": 2, "seller": "Seller B", "title": "Item B", "price": 200.0, "category": "Books", "quantity": 5},
       {"id": 3, "seller": "Seller C", "title": "Item C", "price": 300.0, "category": "Clothing", "quantity": 2}
   ]


   assert items == expected_result, f"Expected {expected_result}, but got {items}"


   # Ensure the SQL query was executed correctly
   expected_query = normalize_whitespace("""
       SELECT id, seller, title, price, category, quantity
       FROM items
       WHERE deleted = FALSE
   """)
   actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])


   assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_all_items_empty_catalog(mock_cursor, caplog):
   """Test that retrieving all items returns an empty list when the catalog is empty and logs a warning."""


   # Simulate that the catalog is empty (no items)
   mock_cursor.fetchall.return_value = []


   # Call the get_all_items function
   result = get_all_items()


   # Ensure the result is an empty list
   assert result == [], f"Expected empty list, but got {result}"


   # Ensure that a warning was logged
   assert "The item catalog is empty." in caplog.text, "Expected warning about empty catalog not found in logs."


   # Ensure the SQL query was executed correctly
   expected_query = normalize_whitespace("SELECT id, seller, title, price, category, quantity FROM items WHERE deleted = FALSE")
   actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])


   # Assert that the SQL query was correct
   assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_update_item_quantity(mock_cursor):
   """Test updating the quantity of an item."""


   # Simulate that the item exists and is not deleted (id = 1)
   mock_cursor.fetchone.return_value = [False]


   # Call the update_item_quantity function with a sample item ID
   item_id = 1
   update_item_quantity(item_id, 20)


   # Normalize the expected SQL query
   expected_query = normalize_whitespace("""
       UPDATE items SET quantity = ? WHERE id = ?
   """)


   # Ensure the SQL query was executed correctly
   actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])


   # Assert that the SQL query was correct
   assert actual_query == expected_query, "The SQL query did not match the expected structure."


   # Extract the arguments used in the SQL call
   actual_arguments = mock_cursor.execute.call_args_list[1][0][1]


   # Assert that the SQL query was executed with the correct arguments (item ID and new quantity)
   expected_arguments = (20, item_id)
   assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


### Test for Updating a Deleted Item:
def test_update_item_quantity_deleted_item(mock_cursor):
   """Test error when trying to update quantity for a deleted item."""


   # Simulate that the item exists but is marked as deleted (id = 1)
   mock_cursor.fetchone.return_value = [True]


   # Expect a ValueError when attempting to update a deleted item
   with pytest.raises(ValueError, match="Item with ID 1 has been deleted"):
       update_item_quantity(1, 20)


   # Ensure that no SQL query for updating quantity was executed
   mock_cursor.execute.assert_called_once_with("SELECT deleted FROM items WHERE id = ?", (1,))

