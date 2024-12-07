#!/bin/bash

# Load the environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Load the secret environment variables from .secrets.env file
if [ -f .secrets.env ]; then
    echo "Loading secrets.env file..."
    export $(cat .secrets.env | xargs)
fi

# Debugging: Print the CREATE_DB value
echo "CREATE_DB is set to: $CREATE_DB"

# Check if CREATE_DB is true, and run the database creation script if so
if [ "$CREATE_DB" = "true" ]; then
    echo "Creating the database..."
    ./sql/create_db.sh
else
    echo "Skipping database creation."
fi

# Start the Python application
exec python3 app.py