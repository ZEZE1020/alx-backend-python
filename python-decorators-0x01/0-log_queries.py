#!/usr/bin/env python3
"""Module for logging database queries using a decorator."""
import sqlite3
import functools


def log_queries():
    """Decorator that logs SQL queries before execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(query, *args, **kwargs):
            """Wrapper function that logs the query and executes the function."""
            print(f"Query: {query}")
            return func(query, *args, **kwargs)
        return wrapper
    return decorator


@log_queries()
def fetch_all_users(query):
    """Function to fetch all users from the database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    # Example usage
    users = fetch_all_users(query="SELECT * FROM users")
