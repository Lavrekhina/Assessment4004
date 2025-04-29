from database import execute_query
from datetime import datetime
import sqlite3


def create_policy(customer_id, policy_type, start_date, end_date, premium, coverage_limit):
    """Create a new policy."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    query = """
    INSERT INTO policies (customer_id, policy_type, start_date, end_date, premium, coverage_limit, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?)
    """
    now = datetime.now()
    params = (
        customer_id, policy_type,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d"),
        premium,
        coverage_limit,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        now.strftime("%Y-%m-%d %H:%M:%S")
    )
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return cursor.lastrowid


def update_policy_details(policy_id, coverage_limit=None, premium=None):
    """Update policy details."""
    conn = sqlite3.connect('insurance.db')
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

    conn.close()


def add_policy_payment(policy_id, amount, payment_date):
    """Record a policy payment."""
    conn = sqlite3.connect('insurance.db')
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
    conn.close()


def get_policy_details(policy_id):
    """Get detailed information about a policy."""
    return execute_query(
        """
        SELECT p.*, c.first_name, c.last_name, c.email,
               (SELECT SUM(amount) FROM payments WHERE policy_id = p.id) as total_payments
        FROM policies p
        JOIN customers c ON p.customer_id = c.id
        WHERE p.id = ?
        """,
        (policy_id,)
    )


def get_customer_policies(customer_id):
    """Get all policies for a customer."""
    return execute_query(
        "SELECT * FROM policies WHERE customer_id = ?",
        (customer_id,)
    )