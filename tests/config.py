import os
import sqlite3
from datetime import datetime
import bcrypt

# Test database path
TEST_DB_PATH = 'test_insurance.db'


def setup_test_db():
    """Set up test database with sample data"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema = f.read()
    cursor.executescript(schema)

    # Insert test branch
    cursor.execute("""
        INSERT INTO branches (name, address, phone, email)
        VALUES ('Test Branch', '123 Test St', '555-0000', 'test@example.com')
    """)

    # Insert test user with hashed password
    password_hash = bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, branch_id)
        VALUES (?, ?, ?, ?)
    """, ('test_user', password_hash.decode('utf-8'), 'admin', 1))

    # Insert test customer
    cursor.execute("""
        INSERT INTO customers (first_name, last_name, email, phone, address, date_of_birth)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Test', 'Customer', 'test@example.com', '1234567890', '123 Test St', '1990-01-01'))

    # Insert test policy
    cursor.execute("""
        INSERT INTO policies (customer_id, policy_type, policy_number, start_date, end_date, 
                            premium, coverage_limit, status, payment_schedule)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (1, 'AUTO', 'POL001', '2024-01-01', '2025-01-01', 1000.00, 50000.00, 'active', 'monthly'))

    conn.commit()
    conn.close()


def teardown_test_db():
    """Clean up test database"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH) 