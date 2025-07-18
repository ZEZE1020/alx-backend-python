#!/usr/bin/env python3
"""Module for implementing retry mechanism for database operations."""
import time
import sqlite3
import functools


def with_db_connection(func):
    """Decorator that handles database connection lifecycle."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function that manages the database connection."""
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper


def retry_on_failure(retries=3, delay=2):
    """Decorator that implements retry logic for database operations."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function that handles retry logic."""
            last_error = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < retries - 1:  # Don't sleep on last attempt
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """Function to fetch all users with retry mechanism."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    # Example usage
    users = fetch_users_with_retry()
    print(users)
