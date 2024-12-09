import logging
from typing import List
from ebay.models.item_model import Item
from ebay.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WishlistModel:
    """
    A class to manage a wishlist of ebay items.

    Attributes:
        

    """

    def __init__(self):
        """
        Initializes the WishlistModel with an empty playlist and the current track set to 1.
        """
        self.wishlist: List[Item] = []

    ##################################################
    # Wishlist Management Functions
    ##################################################

    #add item
    def add_item_to_wishlist(self, item: Item) -> None:
        """
        Adds an item to the wishlist.

        Args:
            item (Item): the item to add to the wishlist.

        Raises:
            TypeError: If the item is not a valid Item instance.
            ValueError: If an item with the same 'id' already exists.
        """
        logger.info("Adding new item to the wishlist")
        if not isinstance(item, Item):
            logger.error("Item is not a valid item")
            raise TypeError("Item is not a valid item")

        item_id = self.validate_item_id(item.id, check_in_wishlist=False)
        if item_id in [item_in_playlist.id for item_in_wishlist in self.wishlist]:
            logger.error("Item with ID %d already exists in the wishlist", item.id)
            raise ValueError(f"Item with ID {item.id} already exists in the playlist")

        self.wishlist.append(item)

    #remove item
    def remove_item_by_item_id(self, item_id: int) -> None:
        """
        Removes an item from the wishlist by its item ID.

        Args:
            item_id (int): The ID of the item to remove from the wishlist.

        Raises:
            ValueError: If the wishlist is empty or the item ID is invalid.
        """
        logger.info("Removing item with id %d from wishlist", item_id)
        self.check_if_empty()
        item_id = self.validate_item_id(item_id)
        self.wishlist = [item_in_wishlist for item_in_wishlist in self.wishlist if item_in_wishlist.id != item_id]
        logger.info("Item with id %d has been removed", item_id)

    #clear
    def clear_wishlist(self) -> None:
        """
        Clears all items from the wishlist. If the wishlist is already empty, logs a warning.
        """
        logger.info("Clearing playlist")
        if self.get_wishlist_length() == 0:
            logger.warning("Clearing an empty playlist")
        self.wishlist.clear()

    ##################################################
    # Playlist Retrieval Functions
    ##################################################

    #get all
    def get_all_songs(self) -> List[Song]:
        """
        Returns a list of all items in the wishlist.
        """
        self.check_if_empty()
        logger.info("Getting all items in the wishlist")
        return self.wishlist

    #get by id
    def get_item_by_item_id(self, item_id: int) -> Item:
        """
        Retrieves an item from the wishlist by its item ID.

        Args:
            item_id (int): The ID of the item to retrieve.

        Raises:
            ValueError: If the wishlist is empty or the item is not found.
        """
        self.check_if_empty()
        item_id = self.validate_item_id(item_id)
        logger.info("Getting item with id %d from wishlist", item_id)
        return next((item for item in self.wishlist if item.id == item_id), None)

    #get by price
    def get_item_by_price(self, price: int) -> Item:
        """
        Retrieves an item from the wishlist by its price (1-indexed).

        Args:
            price (int): The price of the item to retrieve.

        Raises:
            ValueError: If the wishlist is empty or the item is invalid.
        """
        self.check_if_empty()
        price = self.validate_price(price)
        #not sure abt this line under here come back if there is an error
        wishlist_index = id - 1
        logger.info("Getting item at price %d from wishlist", price)
        return self.wishlist[wishlist_index]


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
                                                If False, skips the check. Defaults to True.

        Raises:
            ValueError: If the item ID is not a valid non-negative integer.
        """
        try:
            item_id = int(item_id)
            if item_id < 0:
                logger.error("Invalid item id %d", item_id)
                raise ValueError(f"Invalid item id: {item_id}")
        except ValueError:
            logger.error("Invalid item id %s", item_id)
            raise ValueError(f"Invalid item id: {item_id}")

        if check_in_wishlist:
            if item_id not in [item_in_wishlist.id for item_in_wishlist in self.wishlist]:
                logger.error("Item with id %d not found in wishlist", item_id)
                raise ValueError(f"Item with id {item_id} not found in wishlist")

        return item_id

    def validate_price(self, price: int) -> int:
        """
        Validates the given price, ensuring it is a non-negative integer.

        Args:
            price (int): The price to validate.

        Raises:
            ValueError: If the price is not a valid non-negative integer.
        """
        try:
            price = int(price)
            if price < 1:
                logger.error("Invalid price %d", price)
                raise ValueError(f"Invalid price: {price}")
        except ValueError:
            logger.error("Invalid price %s", price)
            raise ValueError(f"Invalid price: {price}")

        return price

    def check_if_empty(self) -> None:
        """
        Checks if the wishlist is empty, logs an error, and raises a ValueError if it is.

        Raises:
            ValueError: If the wishlist is empty.
        """
        if not self.wishlist:
            logger.error("Wishlist is empty")
            raise ValueError("Wishlist is empty")