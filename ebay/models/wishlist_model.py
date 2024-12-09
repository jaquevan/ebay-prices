import logging
from typing import List, Optional
from ebay.models.item_model import Item
from ebay.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WishlistModel:
    """
    A class to manage a wishlist of eBay items.

    This class provides methods to add, remove, and retrieve items 
    from a wishlist. It also includes utility functions for validating
    item attributes and handling wishlist state.
    """

    def __init__(self):
        """
        Initializes the WishlistModel with an empty wishlist.
        """
        self.wishlist: List[Item] = []


    ##################################################
    # Wishlist Management Functions
    ##################################################

    def add_item_to_wishlist(self, item: Item) -> None:
        """
        Adds an item to the wishlist.

        Args:
            item (Item): The item to add to the wishlist.

        Raises:
            TypeError: If the item is not a valid Item instance.
            ValueError: If an item with the same 'id' already exists.
        """
        logger.info("Adding new item to the wishlist")
        if not isinstance(item, Item):
            logger.error("Item is not a valid Item instance")
            raise TypeError("Item is not a valid Item instance")

        if item.id in [existing_item.id for existing_item in self.wishlist]:
            logger.error("Item with ID %d already exists in the wishlist", item.id)
            raise ValueError(f"Item with ID {item.id} already exists in the wishlist")

        self.wishlist.append(item)
        logger.info("Item with ID %d added to the wishlist", item.id)

    def remove_item_by_item_id(self, item_id: int) -> None:
        """
        Removes an item from the wishlist by its item ID.

        Args:
            item_id (int): The ID of the item to remove from the wishlist.

        Raises:
            ValueError: If the wishlist is empty or the item ID is not found.
        """
        logger.info("Removing item with ID %d from wishlist", item_id)
        self.check_if_empty()
        item_id = self.validate_item_id(item_id)

        initial_length = len(self.wishlist)
        self.wishlist = [item for item in self.wishlist if item.id != item_id]
        
        if len(self.wishlist) == initial_length:
            logger.error("Item with ID %d not found in the wishlist", item_id)
            raise ValueError(f"Item with ID {item_id} not found in the wishlist")
        
        logger.info("Item with ID %d removed from the wishlist", item_id)

    def clear_wishlist(self) -> None:
        """
        Clears all items from the wishlist. If the wishlist is already empty, logs a warning.
        """
        logger.info("Clearing wishlist")
        if self.get_wishlist_length() == 0:
            logger.warning("Clearing an already empty wishlist")
        self.wishlist.clear()
        logger.info("Wishlist has been cleared")

    ##################################################
    # Wishlist Retrieval Functions
    ##################################################

    def get_all_items(self) -> List[Item]:
        """
        Returns a list of all items in the wishlist.

        Raises:
            ValueError: If the wishlist is empty.
        """
        self.check_if_empty()
        logger.info("Getting all items in the wishlist")
        return self.wishlist

    def get_item_by_item_id(self, item_id: int) -> Optional[Item]:
        """
        Retrieves an item from the wishlist by its item ID.

        Args:
            item_id (int): The ID of the item to retrieve.

        Raises:
            ValueError: If the wishlist is empty or the item is not found.
        """
        self.check_if_empty()
        item_id = self.validate_item_id(item_id)
        logger.info("Getting item with ID %d from the wishlist", item_id)
        return next((item for item in self.wishlist if item.id == item_id), None)

    def get_item_by_price(self, price: int) -> List[Item]:
        """
        Retrieves all items from the wishlist with the specified price.

        Args:
            price (int): The price of the items to retrieve.

        Raises:
            ValueError: If the wishlist is empty or no items match the price.
        """
        self.check_if_empty()
        price = self.validate_price(price)

        matching_items = [item for item in self.wishlist if item.price == price]
        if not matching_items:
            logger.error("No items found with price %d", price)
            raise ValueError(f"No items found with price {price}")
        
        logger.info("Found %d item(s) with price %d", len(matching_items), price)
        return matching_items

    def get_wishlist_length(self) -> int:
        """
        Returns the number of items in the wishlist.
        """
        return len(self.wishlist)

    ##################################################
    # Utility Functions
    ##################################################

    def validate_item_id(self, item_id: int, check_in_wishlist: bool = True) -> int:
        """
        Validates the given item ID, ensuring it is a non-negative integer.

        Args:
            item_id (int): The item ID to validate.
            check_in_wishlist (bool, optional): If True, checks if the item ID exists in the wishlist.

        Raises:
            ValueError: If the item ID is invalid or not found (when `check_in_wishlist` is True).
        """
        try:
            item_id = int(item_id)
            if item_id < 0:
                logger.error("Invalid item ID: %d", item_id)
                raise ValueError(f"Invalid item ID: {item_id}")
        except ValueError:
            logger.error("Invalid item ID: %s", item_id)
            raise ValueError(f"Invalid item ID: {item_id}")

        if check_in_wishlist and item_id not in [item.id for item in self.wishlist]:
            logger.error("Item with ID %d not found in wishlist", item_id)
            raise ValueError(f"Item with ID {item_id} not found in wishlist")

        return item_id

    def validate_price(self, price: int) -> int:
        """
        Validates the given price, ensuring it is a positive integer.

        Args:
            price (int): The price to validate.

        Raises:
            ValueError: If the price is invalid.
        """
        try:
            price = int(price)
            if price <= 0:
                logger.error("Invalid price: %d", price)
                raise ValueError(f"Invalid price: {price}")
        except ValueError:
            logger.error("Invalid price: %s", price)
            raise ValueError(f"Invalid price: {price}")

        return price

    def check_if_empty(self) -> Boolean:
        """
        Checks if the wishlist is empty. Logs an error and raises a ValueError if it is.

        Raises:
            Boolean: If the wishlist is empty.
        """
        if not self.wishlist:
            logger.error("Wishlist is empty")
            raise ValueError("Wishlist is empty")
