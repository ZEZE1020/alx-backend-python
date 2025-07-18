#!/usr/bin/env python3
"""Module for handling database connections using a decorator."""
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


@with_db_connection
def get_user_by_id(conn, user_id):
    """Function to get a user by their ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


if __name__ == "__main__":
    # Example usage
    user = get_user_by_id(user_id=1)
    print(user)
