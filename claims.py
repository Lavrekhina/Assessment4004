from database import execute_query
from datetime import datetime
import sqlite3

def create_claim(policy_id, description, incident_date, amount):
    """Create a new claim."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    query = """
    INSERT INTO claims (policy_id, claim_date, description, amount, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, 'pending', ?, ?)
    """
    now = datetime.now()
    params = (
        policy_id,
        incident_date.strftime("%Y-%m-%d"),
        description,
        amount,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        now.strftime("%Y-%m-%d %H:%M:%S")
    )
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return cursor.lastrowid

def update_claim_status(claim_id, status, adjuster_details=None):
    """Update claim status and adjuster details."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    query = """
    UPDATE claims 
    SET status = ?, adjuster_details = ?, updated_at = ?
    WHERE id = ?
    """
    params = (
        status,
        adjuster_details,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        claim_id
    )
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def add_claim_payment(claim_id, amount, payment_date):
    """Record a claim payment."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    query = """
    INSERT INTO claim_payments (claim_id, amount, payment_date, created_at)
    VALUES (?, ?, ?, ?)
    """
    params = (
        claim_id,
        amount,
        payment_date.strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def get_claim_details(claim_id):
    """Get detailed information about a claim."""
    return execute_query(
        """
        SELECT c.*, p.policy_type, p.premium, 
               (SELECT SUM(amount) FROM claim_payments WHERE claim_id = c.id) as total_payments
        FROM claims c
        JOIN policies p ON c.policy_id = p.id
        WHERE c.id = ?
        """,
        (claim_id,)
    )

def get_claims_by_status(status):
    """Get all claims with a specific status."""
    return execute_query(
        "SELECT * FROM claims WHERE status = ?",
        (status,)
    )