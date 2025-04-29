from datetime import datetime
from .pool import pool


def create_policy(user_id, customer_id, policy_type, start_date, end_date, premium, coverage_limit):
    """Create a new policy"""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO policies (customer_id, policy_type, start_date, end_date, premium, coverage_limit, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
        ''', (customer_id, policy_type, start_date, end_date, premium, coverage_limit))

        policy_id = cursor.lastrowid
        conn.commit()
        return policy_id
    finally:
        pool.return_connection(conn)


def update_policy_details(policy_id, coverage_limit=None, premium=None):
    """Update policy details."""
    conn = pool.get_connection()
    cursor = conn.cursor()

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

    pool.return_connection(conn)


def add_policy_payment(policy_id, amount, payment_date):
    """Record a policy payment."""
    conn = pool.get_connection()
    cursor = conn.cursor()

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
    conn.commit()
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
        return dict(row) if row else None
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

        return [dict(row) for row in cursor.fetchall()]
    finally:
        pool.return_connection(conn)