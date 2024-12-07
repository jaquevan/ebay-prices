import requests
import os
import time
from dotenv import load_dotenv

from  services.tokenGeneration import get_access_token

# Load environment variables
load_dotenv()
load_dotenv(dotenv_path="../.secrets.env", override=True)


def search_items(query, limit=5):
    """
    Searches for items on eBay using the Browse API.

    Args:
        query (str): The search query.
        limit (int): The number of results to return.

    Returns:
        list[dict]: A list of items matching the search query.
    """
    token = get_access_token()  # Ensure a valid token is available

    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit={limit}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Check if items are returned
        items = data.get("itemSummaries", [])
        if items:
            print("Search Results!")
            for item in items:
                print(f"Item ID: {item['itemId']}, Title: {item['title']}, "
                      f"Price: {item['price']}")
        else:
            print("No items found.")
        return items
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error searching for items: {e}")


