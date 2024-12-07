#!/bin/bash

DB_PATH="users.db"
SQL_USER_PATH="./sql/create_user_table.sql"
SQL_WISHLIST_PATH="./sql/create_wishlist_table.sql"

echo "DB_PATH is: $DB_PATH"
echo "SQL_USER_PATH is: $SQL_USER_PATH"
echo "SQL_WISHLIST_PATH is: $SQL_WISHLIST_PATH"

# Check if the database file already exists
if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    sqlite3 "$DB_PATH" < "$SQL_USER_PATH"
    sqlite3 "$DB_PATH" < "$SQL_WISHLIST_PATH"
    echo "Database recreated successfully."
else
    echo "Creating database at $DB_PATH."
    sqlite3 "$DB_PATH" < "$SQL_USER_PATH"
    sqlite3 "$DB_PATH" < "$SQL_WISHLIST_PATH"
    echo "Database created successfully."
fi
