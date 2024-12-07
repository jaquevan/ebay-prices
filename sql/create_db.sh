#!/bin/bash

# Check if the database file already exists
if [ -f "$DB_PATH" ]; then
    echo "Recreating database at $DB_PATH."
    sqlite3 "$DB_PATH" < "$SQL_CREATE_USER_TABLE_PATH"
    sqlite3 "$DB_PATH" < "$SQL_CREATE_WISHLIST_TABLE_PATH"
    echo "Database recreated successfully."
else
    echo "Creating database at $DB_PATH."
    sqlite3 "$DB_PATH" < "$SQL_CREATE_USER_TABLE_PATH"
    sqlite3 "$DB_PATH" < "$SQL_CREATE_WISHLIST_TABLE_PATH"
    echo "Database created successfully."
fi
