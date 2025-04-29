import sqlite3
from database.claims import create_claim, get_claims_by_status
from database.policies import create_policy, get_policy_details
from database.auth import verify_user


def setup_test_db():
    conn = sqlite3.connect('test_insurance.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password_hash TEXT,
            role TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            policy_type TEXT,
            status TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY,
            policy_id INTEGER,
            description TEXT,
            amount REAL,
            status TEXT
        )
    ''')

    # Add test user
    cursor.execute('''
        INSERT INTO users (username, password_hash, role)
        VALUES ('test', 'test123', 'admin')
    ''')

    conn.commit()
    return conn, cursor


def cleanup_test_db(conn, cursor):
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS policies')
    cursor.execute('DROP TABLE IF EXISTS claims')
    conn.close()


def test_login():
    print("Testing login...")
    # Test valid login
    role = verify_user('test', 'test123')
    assert role == 'admin', "Valid login failed"

    # Test invalid login
    role = verify_user('wrong', 'wrong')
    assert role is None, "Invalid login failed"
    print("Login tests passed!")


def test_policy():
    print("Testing policy creation...")
    # Create policy
    policy_id = create_policy(
        user_id=1,
        customer_id=1,
        policy_type='auto',
        start_date='2024-01-01',
        end_date='2025-01-01',
        premium=1000.00,
        coverage_limit=50000.00
    )
    assert policy_id is not None, "Policy creation failed"

    # Check policy
    policy = get_policy_details(policy_id)
    assert policy is not None, "Policy not found"
    assert policy['policy_type'] == 'auto', "Wrong policy type"
    print("Policy tests passed!")


def test_claim():
    print("Testing claim creation...")
    # Create policy first
    policy_id = create_policy(
        user_id=1,
        customer_id=1,
        policy_type='auto',
        start_date='2024-01-01',
        end_date='2025-01-01',
        premium=1000.00,
        coverage_limit=50000.00
    )

    # Create claim
    claim_id = create_claim(
        user_id=1,
        policy_id=policy_id,
        description='Test claim',
        incident_date='2024-01-01',
        amount=1000.00
    )
    assert claim_id is not None, "Claim creation failed"

    # Check claim
    claims = get_claims_by_status(1, 'pending')
    assert len(claims) > 0, "No claims found"
    print("Claim tests passed!")


def main():
    print("Starting tests...")
    conn, cursor = setup_test_db()

    try:
        test_login()
        test_policy()
        test_claim()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {str(e)}")
    finally:
        cleanup_test_db(conn, cursor)


if __name__ == '__main__':
    main()