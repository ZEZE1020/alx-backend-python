#!/usr/bin/env python3
"""
Database seeding module for ALX_prodev project.

This module provides functionality to:
- Connect to MySQL database server
- Create the ALX_prodev database
- Create user_data table with required schema
- Populate the table with data from CSV file

Author: Ogembo Godfrey
Date: 07/2025
"""

import mysql.connector
from mysql.connector import Error
import csv
import uuid
import logging
from typing import Optional, Any, Dict, List
import os
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update with your MySQL password
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

DB_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'


def connect_db() -> Optional[mysql.connector.MySQLConnection]:
    """
    Connect to the MySQL database server.
    
    Returns:
        mysql.connector.MySQLConnection: Database connection object if successful
        None: If connection fails
        
    Raises:
        mysql.connector.Error: If connection fails
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.info("Successfully connected to MySQL server")
            return connection
        else:
            logger.error("Failed to connect to MySQL server")
            return None
            
    except Error as e:
        logger.error(f"Error connecting to MySQL server: {e}")
        return None


def create_database(connection: mysql.connector.MySQLConnection) -> bool:
    """
    Create the ALX_prodev database if it does not exist.
    
    Args:
        connection: Active MySQL connection object
        
    Returns:
        bool: True if database was created or already exists, False otherwise
        
    Raises:
        mysql.connector.Error: If database creation fails
    """
    try:
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
            "WHERE SCHEMA_NAME = %s", (DB_NAME,)
        )
        
        if cursor.fetchone():
            logger.info(f"Database {DB_NAME} already exists")
        else:
            # Create database with proper charset and collation
            cursor.execute(
                f"CREATE DATABASE {DB_NAME} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            logger.info(f"Database {DB_NAME} created successfully")
            
        cursor.close()
        return True
        
    except Error as e:
        logger.error(f"Error creating database: {e}")
        return False


def connect_to_prodev() -> Optional[mysql.connector.MySQLConnection]:
    """
    Connect to the ALX_prodev database in MySQL.
    
    Returns:
        mysql.connector.MySQLConnection: Database connection object if successful
        None: If connection fails
        
    Raises:
        mysql.connector.Error: If connection fails
    """
    try:
        config = DB_CONFIG.copy()
        config['database'] = DB_NAME
        
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            logger.info(f"Successfully connected to {DB_NAME} database")
            return connection
        else:
            logger.error(f"Failed to connect to {DB_NAME} database")
            return None
            
    except Error as e:
        logger.error(f"Error connecting to {DB_NAME} database: {e}")
        return None


def create_table(connection: mysql.connector.MySQLConnection) -> bool:
    """
    Create the user_data table if it does not exist.
    
    Args:
        connection: Active MySQL connection object
        
    Returns:
        bool: True if table was created or already exists, False otherwise
        
    Raises:
        mysql.connector.Error: If table creation fails
    """
    try:
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
            (DB_NAME, TABLE_NAME)
        )
        
        if cursor.fetchone():
            logger.info(f"Table {TABLE_NAME} already exists")
        else:
            # Create table with proper constraints and indexes
            create_table_query = f"""
            CREATE TABLE {TABLE_NAME} (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(3,0) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_email (email),
                INDEX idx_age (age)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """
            
            cursor.execute(create_table_query)
            logger.info(f"Table {TABLE_NAME} created successfully")
            
        cursor.close()
        return True
        
    except Error as e:
        logger.error(f"Error creating table: {e}")
        return False


def _is_valid_uuid(uuid_string: str) -> bool:
    """
    Validate if a string is a valid UUID.
    
    Args:
        uuid_string: String to validate
        
    Returns:
        bool: True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def _validate_row_data(row: Dict[str, Any], has_user_id: bool = True) -> bool:
    """
    Validate a single row of data before insertion.
    
    Args:
        row: Dictionary containing row data
        has_user_id: Whether the row contains user_id field
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    if has_user_id:
        required_fields = ['user_id', 'name', 'email', 'age']
    else:
        required_fields = ['name', 'email', 'age']
    
    # Check if all required fields are present
    if not all(field in row for field in required_fields):
        logger.warning(f"Missing required fields in row: {row}")
        return False
    
    # Validate user_id is a valid UUID if present
    if has_user_id and 'user_id' in row:
        if not _is_valid_uuid(row['user_id']):
            logger.warning(f"Invalid UUID format for user_id: {row['user_id']}")
            return False
    
    # Validate name and email are not empty
    if not row['name'].strip() or not row['email'].strip():
        logger.warning(f"Empty name or email in row: {row}")
        return False
    
    # Validate age is numeric and reasonable
    try:
        age = float(row['age'])
        if age < 0 or age > 150:
            logger.warning(f"Invalid age value: {age}")
            return False
    except ValueError:
        logger.warning(f"Non-numeric age value: {row['age']}")
        return False
    
    return True


def insert_data(connection: mysql.connector.MySQLConnection, csv_file: str) -> bool:
    """
    Insert data from CSV file into the user_data table.
    
    Args:
        connection: Active MySQL connection object
        csv_file: Path to the CSV file containing user data
        
    Returns:
        bool: True if data was inserted successfully, False otherwise
        
    Raises:
        FileNotFoundError: If CSV file is not found
        mysql.connector.Error: If database operation fails
    """
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if data already exists (skip insertion if table has data)
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.info(f"Table {TABLE_NAME} already contains {count} records, skipping insertion")
            cursor.close()
            return True
        
        # Read and insert data from CSV
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """
        
        inserted_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Validate CSV headers - user_id is optional and will be generated if missing
            required_headers = {'name', 'email', 'age'}
            csv_headers = set(csv_reader.fieldnames)
            
            if not required_headers.issubset(csv_headers):
                logger.error(f"CSV file missing required headers: {required_headers}")
                cursor.close()
                return False
            
            # Check if user_id column exists
            has_user_id = 'user_id' in csv_headers
            if not has_user_id:
                logger.info("user_id column not found in CSV, UUIDs will be generated automatically")
            
            # Process data in batches for better performance
            batch_size = 1000
            batch_data = []
            
            for row in csv_reader:
                if _validate_row_data(row, has_user_id):
                    # Generate UUID if not present
                    if not has_user_id:
                        user_id = str(uuid.uuid4())
                    else:
                        user_id = row['user_id']
                    
                    batch_data.append((
                        user_id,
                        row['name'].strip(),
                        row['email'].strip(),
                        float(row['age'])
                    ))
                    
                    if len(batch_data) >= batch_size:
                        cursor.executemany(insert_query, batch_data)
                        connection.commit()
                        inserted_count += len(batch_data)
                        batch_data = []
                        logger.info(f"Inserted {inserted_count} records...")
                else:
                    skipped_count += 1
            
            # Insert remaining data
            if batch_data:
                cursor.executemany(insert_query, batch_data)
                connection.commit()
                inserted_count += len(batch_data)
        
        logger.info(
            f"Data insertion completed: {inserted_count} records inserted, "
            f"{skipped_count} records skipped"
        )
        
        cursor.close()
        return True
        
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_file}")
        return False
    except Error as e:
        logger.error(f"Error inserting data: {e}")
        connection.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error during data insertion: {e}")
        connection.rollback()
        return False


@contextmanager
def get_db_connection(database: str = None):
    """
    Context manager for database connections.
    
    Args:
        database: Database name to connect to (optional)
        
    Yields:
        mysql.connector.MySQLConnection: Database connection object
    """
    connection = None
    try:
        if database:
            config = DB_CONFIG.copy()
            config['database'] = database
            connection = mysql.connector.connect(**config)
        else:
            connection = connect_db()
        
        yield connection
        
    except Error as e:
        logger.error(f"Database connection error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed")


def main():
    """
    Main function to demonstrate the seeding process.
    This function is called when the script is run directly.
    """
    try:
        # Connect to MySQL server
        connection = connect_db()
        if not connection:
            logger.error("Failed to connect to MySQL server")
            return
        
        # Create database
        if create_database(connection):
            logger.info("Database setup completed")
        else:
            logger.error("Database setup failed")
            return
        
        connection.close()
        
        # Connect to ALX_prodev database
        connection = connect_to_prodev()
        if not connection:
            logger.error("Failed to connect to ALX_prodev database")
            return
        
        # Create table
        if create_table(connection):
            logger.info("Table setup completed")
        else:
            logger.error("Table setup failed")
            return
        
        # Insert data (assuming user_data.csv exists)
        csv_file = 'user_data.csv'
        if insert_data(connection, csv_file):
            logger.info("Data seeding completed successfully")
        else:
            logger.error("Data seeding failed")
        
        connection.close()
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")


if __name__ == "__main__":
    main()