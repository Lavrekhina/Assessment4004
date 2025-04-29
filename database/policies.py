from datetime import datetime
import sqlite3
import logging
from .pool import pool

# Set up logging
logger = logging.getLogger(__name__)


def create_policy(user_id, customer_id, policy_type, start_date, end_date, premium, coverage_limit):
    """Create a new policy"""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        # Verify customer exists
        cursor.execute('SELECT id FROM customers WHERE id = ?', (customer_id,))
        if not cursor.fetchone():
            logger.error(f"Customer {customer_id} not found")
            return None

        cursor.execute('''
            INSERT INTO policies (customer_id, policy_type, start_date, end_date, premium, coverage_limit, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
        ''', (customer_id, policy_type, start_date, end_date, premium, coverage_limit))

        policy_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Created policy {policy_id}")
        return policy_id
    except sqlite3.Error as e:
        logger.error(f"Database error in create_policy: {e}")
        return None
    finally:
        pool.return_connection(conn)


def update_policy_details(policy_id, coverage_limit=None, premium=None):
    """Update policy details."""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        updates = []
        params = []
        if coverage_limit is not None:
            updates.append("coverage_limit = ?")
            params.append(coverage_limit)
        if premium is not None:
            updates.append("premium = ?")
            params.append(premium)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            params.append(policy_id)

            query = f"UPDATE policies SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            logger.info(f"Updated policy {policy_id} details")
            return True
        return False
    except sqlite3.Error as e:
        logger.error(f"Database error in update_policy_details: {e}")
        return False
    finally:
        pool.return_connection(conn)


def add_policy_payment(policy_id, amount, payment_date):
    """Record a policy payment."""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO payments (policy_id, amount, payment_date, status, created_at)
        VALUES (?, ?, ?, 'completed', ?)
        """
        params = (
            policy_id,
            amount,
            payment_date.strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        cursor.execute(query, params)
        payment_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Added payment {payment_id} for policy {policy_id}")
        return payment_id
    except sqlite3.Error as e:
        logger.error(f"Database error in add_policy_payment: {e}")
        return None
    finally:
        pool.return_connection(conn)


def get_policy_details(policy_id):
    """Get policy details"""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM policies 
            WHERE id = ?
        ''', (policy_id,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        logger.warning(f"Policy {policy_id} not found")
        return None
    except sqlite3.Error as e:
        logger.error(f"Database error in get_policy_details: {e}")
        return None
    finally:
        pool.return_connection(conn)


def get_customer_policies(customer_id):
    """Get all policies for a customer"""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM policies 
            WHERE customer_id = ?
        ''', (customer_id,))

        policies = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Found {len(policies)} policies for customer {customer_id}")
        return policies
    except sqlite3.Error as e:
        logger.error(f"Database error in get_customer_policies: {e}")
        return []
    finally:
        pool.return_connection(conn)