#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

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

def stream_users():
    """
    Generator that yields one user record at a time from the configured table.
    """
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(database=DB_NAME, **DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        for row in cursor:
            yield row
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
