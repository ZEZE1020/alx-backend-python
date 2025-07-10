#!/usr/bin/env python3
import seed

def stream_user_ages():
    """
    Generator that yields one user age at a time from user_data.
    """
    conn = seed.connect_to_prodev()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:
        yield row['age']

    cursor.close()
    conn.close()

def main():
    """
    Compute and print the average age using the age-stream generator.
    """
    total = 0
    count = 0
    for age in stream_user_ages():
        total += age
        count += 1

    average = total / count if count else 0
    print(f"Average age of users: {average}")

if __name__ == '__main__':
    main()
gut