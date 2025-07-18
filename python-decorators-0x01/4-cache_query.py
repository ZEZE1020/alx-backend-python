#!/usr/bin/env python3
"""Module for implementing query caching using decorators."""
import time
import sqlite3
import functools


query_cache = {}


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


def cache_query(func):
    """Decorator that caches query results."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function that implements query caching."""
        query = kwargs.get('query')
        if query in query_cache:
            return query_cache[query]
        
        result = func(*args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Function to fetch users with caching mechanism."""
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call will cache the result
    users = fetch_users_with_cache(query="SELECT * FROM users")
    
    # Second call will use the cached result
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
