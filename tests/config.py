import os
import sqlite3
from datetime import datetime

# Test database path
TEST_DB_PATH = 'test_insurance.db'


def setup_test_db():
    """Set up test database with sample data"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    # Read and execute schema
    with open('schema.sql', 'r') as f:
        schema = f.read()
    cursor.executescript(schema)

    # Insert test data
    cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES ('test_user', 'test_hash', 'admin')
    """)

    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email, phone)
        VALUES ('Test', 'Customer', 'test@example.com', '1234567890')
    """)

    cursor.execute("""
        INSERT INTO policies (customer_id, policy_number, policy_type, start_date, end_date, premium, coverage_limit, status)
        VALUES (1, 'POL001', 'auto', '2024-01-01', '2025-01-01', 1000.00, 50000.00, 'active')
    """)

    conn.commit()
    conn.close()


def teardown_test_db():
    """Clean up test database"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)