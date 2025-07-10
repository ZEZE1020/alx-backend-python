#!/usr/bin/env python3
import mysql.connector

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

def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from the user_data table in batches.
    Yields a list of up to `batch_size` user dicts each time.
    """
    conn = mysql.connector.connect(database=DB_NAME, **DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        yield rows

    cursor.close()
    conn.close()

def batch_processing(batch_size):
    """
    Processes each batch from the generator, printing users older than 25.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user.get('age', 0) > 25:
                print(user)
