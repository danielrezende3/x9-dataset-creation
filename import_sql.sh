#!/bin/bash

# Define database name
DB_NAME="code4bench"

# Step 1: Check if DB_PASSWORD is set, otherwise prompt for password
if [[ -z "$DB_PASSWORD" ]]; then
    echo "Enter MySQL password for root:"
    read -s DB_PASSWORD
else
    echo "Using environment variable DB_PASSWORD."
fi

# Step 2: Create the database (if it doesn't exist)
echo "Checking if MySQL database '$DB_NAME' exists..."
DB_EXISTS=$(mysql -u root -p"$DB_PASSWORD" -e "SHOW DATABASES LIKE '$DB_NAME';" | grep "$DB_NAME")

if [ -z "$DB_EXISTS" ]; then
    echo "Creating MySQL database '$DB_NAME'..."
    mysql -u root -p"$DB_PASSWORD" -e "CREATE DATABASE $DB_NAME;"

    # Step 3: Check if the file exists before downloading
    if [ -f "code4bench.rar" ]; then
        echo "code4bench.rar already exists. Skipping download."
    else
        echo "Downloading code4bench.rar..."
        wget -O code4bench.rar "https://zenodo.org/records/2582968/files/code4bench.rar?download=1"
    fi

    # Step 4: Check if the directory exists before extracting
    if [ -d "code4bench12-12-97" ]; then
        echo "Directory code4bench12-12-97 already exists. Skipping extraction."
    else
        echo "Extracting code4bench.rar..."
        unrar x code4bench.rar
    fi

    # Step 5: Import SQL files into MySQL (only if the database was just created)
    for file in code4bench12-12-97/*.sql; do
        echo "Importing $file..."
        mysql -u root -p"$DB_PASSWORD" $DB_NAME < "$file"
    done
else
    echo "Database '$DB_NAME' already exists. Skipping import step."
fi

# Step 6: Check if the tables have been created
mysql -u root -p"$DB_PASSWORD" -e "USE code4bench; SHOW TABLES;"

# Step 7: Run the scripts/process_codeforces_database.py script
echo "Running scripts/process_codeforces_database.py..."
python scripts/process_codeforces_database.py

if [ $? -ne 0 ]; then
    echo "Error: process_codeforces_database.py failed. Halting execution."
    exit 1
fi

# Step 8: Cleanup - Delete the downloaded and extracted files
echo "Cleaning up..."
rm -f code4bench.rar
rm -rf code4bench12-12-97

echo "All SQL files have been imported successfully, and cleanup is complete."