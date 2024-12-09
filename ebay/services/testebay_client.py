from services.tokenGeneration import get_access_token, search_items

if __name__ == "__main__":
    # Test the access token generation
    try:
        print("Testing access token generation...")
        token = get_access_token()
        if token:
            print(f"Access Token: {token}")
        else:
            print("Failed to generate access token.")
    except Exception as e:
        print(f"Error during token generation: {e}")

    # Test the search functionality
    try:
        print("\nTesting item search...")
        query = "laptop"  # Replace with a query of your choice
        items = search_items(query=query, limit=5)
        if items:
            print("Search Results:")
            for item in items:
                print(f"Title: {item['title']}, Price: {item['price']['value']} {item['price']['currency']}")
        else:
            print("No items found.")
    except Exception as e:
        print(f"Error during item search: {e}")