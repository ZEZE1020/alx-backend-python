# ALX Backend Python - Generators 0x00

## Project Overview

This project implements a Python-based database seeding system for the ALX_prodev MySQL database. The system is designed to create and populate a user data table with sample data from a CSV file, following professional best practices and implementing proper error handling.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)

## Features

- **Database Management**: Automated creation of MySQL database and tables
- **Data Validation**: Comprehensive validation of CSV data before insertion
- **Error Handling**: Robust error handling with detailed logging
- **Batch Processing**: Efficient batch insertion for large datasets
- **UUID Validation**: Proper UUID format validation for user IDs
- **Connection Management**: Context managers for safe database connections
- **Logging**: Comprehensive logging for debugging and monitoring

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.7 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

### Required Python Packages

```bash
pip install mysql-connector-python
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/alx-backend-python.git
cd alx-backend-python/python-generators-0x00
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure MySQL server is running on your system.

## Configuration

### Database Configuration

Update the database configuration in `seed.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # Update with your MySQL password
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
```

### CSV File Format

Ensure your `user_data.csv` file has the following format:

```csv
user_id,name,email,age
00234e50-34eb-4ce2-94ec-26e3fa749796,Dan Altenwerth Jr.,Molly59@gmail.com,67
006bfede-724d-4cdd-a2a6-59700f40d0da,Glenda Wisozk,Miriam21@gmail.com,119
```

## Usage

### Basic Usage

Run the seeding script directly:

```bash
python3 seed.py
```

### Using with Main Script

```bash
python3 0-main.py
```

### Programmatic Usage

```python
#!/usr/bin/env python3
import seed

# Connect to MySQL server
connection = seed.connect_db()
if connection:
    # Create database
    seed.create_database(connection)
    connection.close()
    
    # Connect to ALX_prodev database
    connection = seed.connect_to_prodev()
    if connection:
        # Create table and insert data
        seed.create_table(connection)
        seed.insert_data(connection, 'user_data.csv')
        connection.close()
```

## Database Schema

### Database: ALX_prodev

#### Table: user_data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | CHAR(36) | PRIMARY KEY, INDEXED | UUID format user identifier |
| name | VARCHAR(255) | NOT NULL | User's full name |
| email | VARCHAR(255) | NOT NULL, INDEXED | User's email address |
| age | DECIMAL(3,0) | NOT NULL, INDEXED | User's age |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Record update timestamp |

### Indexes

- Primary key on `user_id`
- Index on `user_id` for faster lookups
- Index on `email` for email-based queries
- Index on `age` for age-based filtering

## API Documentation

### Core Functions

#### `connect_db()`
Establishes connection to MySQL database server.

**Returns:**
- `mysql.connector.MySQLConnection`: Database connection object
- `None`: If connection fails

#### `create_database(connection)`
Creates the ALX_prodev database if it doesn't exist.

**Parameters:**
- `connection`: Active MySQL connection object

**Returns:**
- `bool`: True if successful, False otherwise

#### `connect_to_prodev()`
Connects specifically to the ALX_prodev database.

**Returns:**
- `mysql.connector.MySQLConnection`: Database connection object
- `None`: If connection fails

#### `create_table(connection)`
Creates the user_data table with proper schema.

**Parameters:**
- `connection`: Active MySQL connection object

**Returns:**
- `bool`: True if successful, False otherwise

#### `insert_data(connection, csv_file)`
Inserts data from CSV file into the database.

**Parameters:**
- `connection`: Active MySQL connection object
- `csv_file`: Path to CSV file containing user data

**Returns:**
- `bool`: True if successful, False otherwise

## Testing

### Manual Testing

1. Verify database creation:
```sql
SHOW DATABASES LIKE 'ALX_prodev';
```

2. Verify table creation:
```sql
USE ALX_prodev;
DESCRIBE user_data;
```

3. Verify data insertion:
```sql
SELECT COUNT(*) FROM user_data;
SELECT * FROM user_data LIMIT 5;
```

### Expected Output

When running `0-main.py`, you should see:

```
connection successful
Table user_data created successfully
Database ALX_prodev is present 
[('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67), ...]
```

## Error Handling

The system includes comprehensive error handling for:

- Database connection failures
- Invalid CSV file formats
- Missing required fields
- Invalid UUID formats
- Age validation (0-150 range)
- Duplicate data insertion prevention

## Logging

All operations are logged with appropriate levels:

- `INFO`: Successful operations
- `WARNING`: Data validation issues
- `ERROR`: Critical failures

## Performance Considerations

- **Batch Processing**: Data is inserted in batches of 1000 records
- **Indexing**: Proper indexes on frequently queried columns
- **Connection Management**: Efficient connection pooling and cleanup
- **Memory Usage**: Streaming CSV processing to handle large files

## Security Considerations

- **Input Validation**: All input data is validated before insertion
- **SQL Injection Prevention**: Uses parameterized queries
- **Error Information**: Sensitive information is not exposed in error messages

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Commit Message Guidelines

- Use imperative mood: "Add feature" not "Added feature"
- Keep first line under 50 characters
- Include detailed description if necessary
- Reference issues: "Fix #123: Add validation for user emails"


## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section below

## Troubleshooting

### Common Issues

1. **Connection Refused Error**
   - Ensure MySQL server is running
   - Check host and port configuration
   - Verify credentials

2. **CSV File Not Found**
   - Ensure `user_data.csv` exists in the project directory
   - Check file permissions
   - Verify file format

3. **Permission Denied**
   - Ensure MySQL user has necessary privileges
   - Check database and table creation permissions

### Debug Mode

Enable debug logging by setting:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Project Structure

```
python-generators-0x00/
├── seed.py                 # Main seeding script
├── 0-main.py              # Test/demo script
├── user_data.csv          # Sample data file
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## Version History

- v1.0.0: Initial release with basic seeding functionality
- v1.1.0: Added batch processing and improved error handling
- v1.2.0: Added comprehensive logging and validation

---

**Author:** Ogembo Godfrey 
**Last Updated:** 2025  
**Version:** 1.2.0