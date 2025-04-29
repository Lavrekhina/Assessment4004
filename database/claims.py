from database import execute_query
from datetime import datetime
from .pool import pool
from .auth import check_access
from .audit import log_action


def create_claim(user_id, policy_id, description, incident_date, amount):
    """Create a new claim."""
    if not check_access(user_id, 'adjuster'):
        return None

    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO claims (policy_id, description, incident_date, amount, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (policy_id, description, incident_date, amount))

        claim_id = cursor.lastrowid
        conn.commit()
        return claim_id
    finally:
        pool.return_connection(conn)


def update_claim_status(user_id, claim_id, status, adjuster_details=None):
    """Update claim status and adjuster details."""
    if not check_access(user_id, 'claims_manager'):
        return None

    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
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

        # Log the action
        log_action(user_id, 'update', 'claims', claim_id, {'status': status})
    finally:
        pool.return_connection(conn)


def add_claim_payment(user_id, claim_id, amount, payment_date):
    """Record a claim payment."""
    if not check_access(user_id, 'claims_manager'):
        return None

    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO payments (claim_id, amount, payment_date, status, created_at)
        VALUES (?, ?, ?, 'completed', ?)
        """
        params = (
            claim_id,
            amount,
            payment_date.strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        cursor.execute(query, params)
        payment_id = cursor.lastrowid
        conn.commit()

        # Log the action
        log_action(user_id, 'create', 'payments', payment_id, {'claim_id': claim_id, 'amount': amount})
        return payment_id
    finally:
        pool.return_connection(conn)


def get_claim_details(user_id, claim_id):
    """Get detailed information about a claim."""
    if not check_access(user_id, 'adjuster'):
        return None

    # Log the action
    log_action(user_id, 'view', 'claims', claim_id)

    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM claims 
            WHERE id = ?
        ''', (claim_id,))

        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        pool.return_connection(conn)


def get_claims_by_status(user_id, status):
    """Get all claims with a specific status."""
    if not check_access(user_id, 'adjuster'):
        return None

    # Log the action
    log_action(user_id, 'view', 'claims', None, {'status': status})

    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM claims 
            WHERE status = ?
        ''', (status,))

        return [dict(row) for row in cursor.fetchall()]
    finally:
        pool.return_connection(conn)