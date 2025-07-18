# ALX Backend Python

This repository contains Python backend development projects focusing on advanced Python concepts, particularly decorators for database operations.

## Python Decorators Project (`python-decorators-0x01`)

This project implements various database operation decorators that showcase different aspects of database management and optimization using Python decorators.

### Features

1. **SQL Query Logging** (`0-log_queries.py`)
   - Decorator: `@log_queries()`
   - Logs SQL queries with timestamps before execution
   - Useful for debugging and monitoring database operations

2. **Database Connection Management** (`1-with_db_connection.py`)
   - Decorator: `@with_db_connection`
   - Automatically handles database connection lifecycle
   - Ensures proper connection closure even in case of errors

3. **Transaction Management** (`2-transactional.py`)
   - Decorator: `@transactional`
   - Manages database transactions with automatic commit/rollback
   - Ensures data consistency in database operations

4. **Operation Retry Mechanism** (`3-retry_on_failure.py`)
   - Decorator: `@retry_on_failure(retries=3, delay=2)`
   - Implements retry logic for failed database operations
   - Configurable retry count and delay between attempts

5. **Query Result Caching** (`4-cache_query.py`)
   - Decorator: `@cache_query`
   - Caches query results to improve performance
   - Avoids redundant database calls for identical queries

### Usage Examples

#### 1. SQL Query Logging
```python
@log_queries()
def fetch_all_users(query):
    # Function implementation
    pass

users = fetch_all_users(query="SELECT * FROM users")
# Output: [2025-07-18 10:30:15] Query: SELECT * FROM users
```

#### 2. Database Connection Management
```python
@with_db_connection
def get_user_by_id(conn, user_id):
    # Function implementation using provided connection
    pass

user = get_user_by_id(user_id=1)
```

#### 3. Transaction Management
```python
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    # Function implementation with automatic transaction handling
    pass

update_user_email(user_id=1, new_email='new@example.com')
```

#### 4. Retry Mechanism
```python
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    # Function implementation with retry capability
    pass

users = fetch_users_with_retry()
```

#### 5. Query Caching
```python
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    # Function implementation with result caching
    pass

users = fetch_users_with_cache(query="SELECT * FROM users")
```

### Requirements
- Python 3.x
- SQLite3 (included in Python standard library)

### Installation
No additional installation required. The project uses Python's standard library modules:
- `sqlite3` for database operations
- `functools` for decorator utilities
- `datetime` for timestamp logging
- `time` for retry delays

### Project Structure
```
python-decorators-0x01/
├── 0-log_queries.py
├── 1-with_db_connection.py
├── 2-transactional.py
├── 3-retry_on_failure.py
└── 4-cache_query.py
```

## Author
- ZEZE1020

## License
This project is part of the ALX Backend Python curriculum.