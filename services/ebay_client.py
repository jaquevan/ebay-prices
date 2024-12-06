import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("EBAY_PROD_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_PROD_CLIENT_SECRET")
ENVIRONMENT = os.getenv("EBAY_ENVIRONMENT", "production")

# Global variables to store token and expiration time
_access_token = None
_token_expiry = None


def get_access_token():
    """
    Fetches a new access token if none exists or if the token is expired.

    Returns:
        str: A valid eBay access token.
    """
    global _access_token, _token_expiry

    # If the token is still valid, reuse it
    if _access_token and _token_expiry and time.time() < _token_expiry:
        return _access_token

    # Generate a new token
    url = f"https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    try:
        response = requests.post(url, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()

        # Save the token and expiration time
        _access_token = response_data["access_token"]
        expires_in = response_data.get("expires_in", 7200)  # Default to 2 hours if not provided
        _token_expiry = time.time() + expires_in

        return _access_token
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch access token: {e}")


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


