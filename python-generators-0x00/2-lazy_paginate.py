#!/usr/bin/env python3
import seed

def paginate_users(page_size, offset):
    """
    Fetch a single page of users from the database.
    """
    conn = seed.connect_to_prodev()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def lazy_pagination(page_size):
    """
    Generator that lazily fetches pages of users.
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
