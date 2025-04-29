import sqlite3
import os
import bcrypt
import logging
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
POLICY_TYPES = {
    'AUTO': 'AUTO',
    'HOME': 'HOME',
    'LIFE': 'LIFE',
    'HEALTH': 'HEALTH'
}

CLAIM_STATUSES = {
    'PENDING': 'PENDING',
    'APPROVED': 'APPROVED',
    'REJECTED': 'REJECTED',
    'PAID': 'PAID'
}


def get_connection(db_path: str = 'insurance.db') -> sqlite3.Connection:
    """Get a database connection."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def setup_database(db_path: str = 'insurance.db'):
    """Initialize the database with all required tables."""
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()

        # Execute SQL script to create tables
        with open('schema.sql', 'r') as f:
            sql_script = f.read()
            cursor.executescript(sql_script)

        conn.commit()
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Database setup error: {e}")
        raise
    finally:
        conn.close()


def execute_query(query: str, params: tuple = None, fetch: bool = False, db_path: str = 'insurance.db') -> Optional[
    Dict]:
    """Execute a query with proper error handling."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            result = cursor.fetchall()
            return [dict(row) for row in result] if result else None
        conn.commit()
        return None
    except sqlite3.Error as e:
        logger.error(f"Query execution error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# Customer operations
def create_customer(data: Dict[str, Any], db_path: str = 'insurance.db') -> int:
    """Create a new customer record."""
    try:
        # Hash the password
        hashed_password = hash_password(data['password'])

        query = '''
            INSERT INTO customers (first_name, last_name, email, phone, address, date_of_birth, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            data['first_name'],
            data['last_name'],
            data['email'],
            data['phone'],
            data['address'],
            data['date_of_birth'],
            hashed_password
        )
        execute_query(query, params, db_path=db_path)

        # Log the creation
        customer_id = execute_query('SELECT last_insert_rowid()', fetch=True, db_path=db_path)[0]['last_insert_rowid()']
        log_audit('customers', customer_id, 'CREATE', None, f"Created customer {data['email']}")

        return customer_id
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise


def get_customer(customer_id: int, db_path: str = 'insurance.db') -> Optional[Dict]:
    """Retrieve a customer by ID."""
    try:
        query = 'SELECT * FROM customers WHERE id = ?'
        result = execute_query(query, (customer_id,), fetch=True, db_path=db_path)
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error retrieving customer: {e}")
        raise


def update_customer(customer_id: int, data: Dict[str, Any], db_path: str = 'insurance.db') -> bool:
    """Update a customer record."""
    try:
        query = '''
            UPDATE customers
            SET first_name = ?, last_name = ?, email = ?, phone = ?, address = ?, date_of_birth = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (
            data['first_name'],
            data['last_name'],
            data['email'],
            data['phone'],
            data['address'],
            data['date_of_birth'],
            customer_id
        )
        execute_query(query, params, db_path=db_path)

        # Log the update
        log_audit('customers', customer_id, 'UPDATE', None, f"Updated customer {data['email']}")

        return True
    except Exception as e:
        logger.error(f"Error updating customer: {e}")
        raise


def delete_customer(customer_id: int, db_path: str = 'insurance.db') -> bool:
    """Delete a customer record."""
    try:
        # Get customer details for logging
        customer = get_customer(customer_id, db_path)
        if not customer:
            return False

        query = 'DELETE FROM customers WHERE id = ?'
        execute_query(query, (customer_id,), db_path=db_path)

        # Log the deletion
        log_audit('customers', customer_id, 'DELETE', None, f"Deleted customer {customer['email']}")

        return True
    except Exception as e:
        logger.error(f"Error deleting customer: {e}")
        raise


# Policy operations
def create_policy(data: Dict[str, Any], db_path: str = 'insurance.db') -> int:
    """Create a new policy record."""
    try:
        query = '''
            INSERT INTO policies (customer_id, policy_number, policy_type, start_date, end_date, 
                                premium_amount, coverage_details, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            data['customer_id'],
            data['policy_number'],
            data['policy_type'],
            data['start_date'],
            data['end_date'],
            data['premium_amount'],
            data['coverage_details'],
            data['status']
        )
        execute_query(query, params, db_path=db_path)

        # Log the creation
        policy_id = execute_query('SELECT last_insert_rowid()', fetch=True, db_path=db_path)[0]['last_insert_rowid()']
        log_audit('policies', policy_id, 'CREATE', None, f"Created policy {data['policy_number']}")

        return policy_id
    except Exception as e:
        logger.error(f"Error creating policy: {e}")
        raise


# Claim operations
def create_claim(data: Dict[str, Any], db_path: str = 'insurance.db') -> int:
    """Create a new claim record."""
    try:
        query = '''
            INSERT INTO claims (policy_id, claim_number, claim_type, description, incident_date,
                              claim_date, status, estimated_amount, approved_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            data['policy_id'],
            data['claim_number'],
            data['claim_type'],
            data['description'],
            data['incident_date'],
            data['claim_date'],
            data['status'],
            data['estimated_amount'],
            data.get('approved_amount')
        )
        execute_query(query, params, db_path=db_path)

        # Log the creation
        claim_id = execute_query('SELECT last_insert_rowid()', fetch=True, db_path=db_path)[0]['last_insert_rowid()']
        log_audit('claims', claim_id, 'CREATE', None, f"Created claim {data['claim_number']}")

        return claim_id
    except Exception as e:
        logger.error(f"Error creating claim: {e}")
        raise


def log_audit(table_name: str, record_id: int, action: str, user_id: Optional[int], details: str,
              db_path: str = 'insurance.db'):
    """Log an audit entry."""
    try:
        query = '''
            INSERT INTO audit_logs (table_name, record_id, action, user_id, details)
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (table_name, record_id, action, user_id, details)
        execute_query(query, params, db_path=db_path)
    except Exception as e:
        logger.error(f"Error logging audit: {e}")
        raise