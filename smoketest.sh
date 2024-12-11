#!/bin/bash

BASE_URL="http://localhost:5000/api"

ECHO_JSON=false

while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##############################################
#
# User management
#
##############################################

# Function to create a user
create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

# Function to log in a user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to log out a user
logout_user() {
  echo "Logging out user..."
  response=$(curl -s -X POST "$BASE_URL/logout" -H "Content-Type: application/json" \
    -d '{"username":"testuser"}')
  if echo "$response" | grep -q '"message": "User testuser logged out successfully."'; then
    echo "User logged out successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Logout Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log out user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to initialize the database
init_db() {
  echo "Initializing the database..."
  response=$(curl -s -X POST "$BASE_URL/init-db")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Database initialized successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Initialization Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initialize the database."
    exit 1
  fi
}

check_number_of_orders() {
  item_id=$1
  echo "Checking the number of orders for item ID: $item_id..."
  response=$(curl -s -X GET "$BASE_URL/orders/$item_id")

  if echo "$response" | grep -q '"orders_count"'; then
    echo "Number of orders retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Order Count Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve the number of orders for item ID: $item_id."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to request eBay token
request_ebay_token() {
  echo "Requesting eBay token..."
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/token)
  if [ "$response" -eq 200 ]; then
    echo "Token generated successfully"
  else
    echo "Token generation failed with status code $response"
  fi
}

# Function to search for summary
search_summary() {
  local query=$1
  echo "Searching for '$query' summary..."
  response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/api/search/summary?query=$query")
  if [ "$response" -eq 200 ]; then
    echo "Search summary test passed"
  else
    echo "Search summary test failed with status code $response"
  fi
}

# Function to search for top search result
search_top_result() {
  local query=$1
  echo "Getting top search result for '$query'..."
  response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/api/search/top-search?query=$query")
  if [ "$response" -eq 200 ]; then
    echo "Top search test passed"
  else
    echo "Top search test failed with status code $response"
  fi
}

# Function to search item by eBay ID
search_item_by_ebay_id() {
  local ebay_item_id=$1
  echo "Searching for item by eBay ID '$ebay_item_id'..."
  response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/api/search/item/ebay_id?ebay_item_id=$ebay_item_id")
  if [ "$response" -eq 200 ]; then
    echo "Search by eBay ID test passed"
  else
    echo "Search by eBay ID test failed with status code $response"
  fi
}

# Function to check sold quantity for an item
check_sold_quantity() {
  local ebay_item_id=$1
  echo "Getting sold quantity for item by eBay ID '$ebay_item_id'..."
  response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/api/search/item/sold_quantity?ebay_item_id=$ebay_item_id")
  if [ "$response" -eq 200 ]; then
    echo "Sold quantity test passed"
  else
    echo "Sold quantity test failed with status code $response"
  fi
}

# Function to check available quantity for an item
check_available_quantity() {
  local ebay_item_id=$1
  echo "Getting available quantity for item by eBay ID '$ebay_item_id'..."
  response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/api/search/item/available_quantity?ebay_item_id=$ebay_item_id")
  if [ "$response" -eq 200 ]; then
    echo "Available quantity test passed"
  else
    echo "Available quantity test failed with status code $response"
  fi
}

# Function to add item to wishlist
add_item_to_wishlist() {
  local ebay_item_id=$1
  echo "Adding item '$ebay_item_id' to wishlist..."
  response=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:5000/api/add-item-to-wishlist -H "Content-Type: application/json" -d '{
    "ebay_item_id": "'$ebay_item_id'",
    "title": "Laptop",
    "price": 299.99,
    "available_quantity": 10,
    "sold_quantity": 5,
    "alert_price": 250.00
  }')
  if [ "$response" -eq 201 ]; then
    echo "Add item to wishlist test passed"
  else
    echo "Add item to wishlist test failed with status code $response"
  fi
}

# Function to remove item from wishlist
remove_item_from_wishlist() {
  local item_id=$1
  echo "Removing item '$item_id' from wishlist..."
  response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE http://localhost:5000/api/remove-item-from-wishlist/$item_id)
  if [ "$response" -eq 200 ]; then
    echo "Remove item from wishlist test passed"
  else
    echo "Remove item from wishlist test failed with status code $response"
  fi
}

# Function to get wishlist
get_wishlist() {
  echo "Retrieving wishlist..."
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/get-wishlist)
  if [ "$response" -eq 200 ]; then
    echo "Get wishlist test passed"
  else
    echo "Get wishlist test failed with status code $response"
  fi
}


check_health
check_db
request_ebay_token
create_user
login_user
check_number_of_orders "$ITEM_ID"
search_summary "laptop"
search_top_result "laptop"
search_item_by_ebay_id "v1|254582474636|0"
check_sold_quantity "v1|254582474636|0"
check_available_quantity "v1|254582474636|0"
add_item_to_wishlist "v1|254582474636|0"
remove_item_from_wishlist 1
get_wishlist

echo "All tests passed successfully!"

