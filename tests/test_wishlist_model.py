import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ebay.models.wishlist_model import WishlistModel
from ebay.models.item_model import Item
from ebay.models.item_model import create_item


@pytest.fixture
def wishlist_model():
    """Fixture to provide a fresh WishlistModel for each test."""
    return WishlistModel()


@pytest.fixture
def sample_item():
    """Fixture to provide a sample Item using the new create_item method."""
    return create_item(ebay_item_id="2", title="Shoes", price=100, available_quantity=20, sold_quantity=10, alert_price=3)


@pytest.fixture
def another_item():
    """Fixture to provide another sample Item using the new create_item method."""
    return create_item(ebay_item_id="3", title="Pillow", price=200, available_quantity=40, sold_quantity=20, alert_price=4)


def test_add_item_to_wishlist(wishlist_model, sample_item):
    """Test adding a valid item to the wishlist."""
    wishlist_model.add_item_to_wishlist(sample_item)
    assert len(wishlist_model.get_all_items()) == 1
    assert wishlist_model.get_all_items()[0] == sample_item


def test_add_duplicate_item_to_wishlist(wishlist_model, sample_item):
    """Test that adding a duplicate item raises a ValueError."""
    wishlist_model.add_item_to_wishlist(sample_item)
    with pytest.raises(ValueError, match="Item with ID 1 already exists in the wishlist"):
        wishlist_model.add_item_to_wishlist(sample_item)


def test_add_invalid_item(wishlist_model):
    """Test that adding an invalid item raises a TypeError."""
    with pytest.raises(TypeError, match="Item is not a valid Item instance"):
        wishlist_model.add_item_to_wishlist("invalid_item")


def test_remove_item_by_item_id(wishlist_model, sample_item):
    """Test removing an item from the wishlist by item ID."""
    wishlist_model.add_item_to_wishlist(sample_item)
    wishlist_model.remove_item_by_item_id(1)
    assert len(wishlist_model.get_all_items()) == 0


def test_remove_nonexistent_item(wishlist_model):
    """Test that removing an item with a non-existent ID raises a ValueError."""
    with pytest.raises(ValueError, match="Item with ID 1 not found in the wishlist"):
        wishlist_model.remove_item_by_item_id(1)


def test_get_all_items(wishlist_model, sample_item, another_item):
    """Test retrieving all items from the wishlist."""
    wishlist_model.add_item_to_wishlist(sample_item)
    wishlist_model.add_item_to_wishlist(another_item)
    items = wishlist_model.get_all_items()
    assert len(items) == 2
    assert sample_item in items
    assert another_item in items


def test_get_item_by_item_id(wishlist_model, sample_item):
    """Test retrieving an item by its item ID."""
    wishlist_model.add_item_to_wishlist(sample_item)
    item = wishlist_model.get_item_by_item_id(1)
    assert item == sample_item


def test_get_item_by_invalid_item_id(wishlist_model):
    """Test that retrieving an item with a non-existent ID raises a ValueError."""
    with pytest.raises(ValueError, match="Item with ID 1 not found in the wishlist"):
        wishlist_model.get_item_by_item_id(1)


def test_get_item_by_price(wishlist_model, sample_item, another_item):
    """Test retrieving items by their price."""
    wishlist_model.add_item_to_wishlist(sample_item)
    wishlist_model.add_item_to_wishlist(another_item)
    items = wishlist_model.get_item_by_price(100)
    assert len(items) == 1
    assert items[0] == sample_item


def test_get_item_by_nonexistent_price(wishlist_model, sample_item):
    """Test that retrieving items with a non-existent price raises a ValueError."""
    wishlist_model.add_item_to_wishlist(sample_item)
    with pytest.raises(ValueError, match="No items found with price 200"):
        wishlist_model.get_item_by_price(200)


def test_clear_wishlist(wishlist_model, sample_item, another_item):
    """Test clearing the wishlist."""
    wishlist_model.add_item_to_wishlist(sample_item)
    wishlist_model.add_item_to_wishlist(another_item)
    wishlist_model.clear_wishlist()
    assert len(wishlist_model.get_all_items()) == 0


def test_clear_empty_wishlist(wishlist_model):
    """Test clearing an already empty wishlist."""
    wishlist_model.clear_wishlist()
    assert len(wishlist_model.get_all_items()) == 0


def test_wishlist_length(wishlist_model, sample_item, another_item):
    """Test getting the length of the wishlist."""
    wishlist_model.add_item_to_wishlist(sample_item)
    wishlist_model.add_item_to_wishlist(another_item)
    assert wishlist_model.get_wishlist_length() == 2
