import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch credentials from environment
client_id = os.getenv("EBAY_CLIENT_ID")
client_secret = os.getenv("EBAY_CLIENT_SECRET")
environment = os.getenv("EBAY_ENVIRONMENT", "sandbox")


def get_access_token(client_id, client_secret):
    print("Starting token generation...")  # Debugging print
    url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"  # Use the production URL for production
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    print("Sending request to:", url)  # Debugging print

    try:
        response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
        print("Request sent. Status code:", response.status_code)  # Debugging print
    except Exception as e:
        print(f"Failed to make the request: {e}")
        return None

    if response.status_code == 200:
        print("Token generation successful.")  # Debugging print
        access_token = response.json()["access_token"]
        try:
            with open("access_token.txt", "w") as f:
                f.write(access_token)
                print("Access token saved to access_token.txt")
        except Exception as e:
            print(f"Failed to save access token: {e}")
        return access_token
    else:
        print("Error:", response.status_code, response.text)
        return None

if __name__ == "__main__":
    token = get_access_token(client_id, client_secret)
    if token:
        print("Token generated and saved successfully.")
    else:
        print("Failed to generate token.")
