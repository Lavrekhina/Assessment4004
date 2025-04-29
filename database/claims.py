from database import execute_query
from datetime import datetime
from .pool import pool
from .auth import check_access
from .audit import log_action
import logging
import sqlite3

# Set up logging
logger = logging.getLogger(__name__)


def create_claim(user_id, policy_id, description, incident_date, amount):
    """Create a new claim."""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        # First verify the policy exists
        cursor.execute('SELECT id FROM policies WHERE id = ?', (policy_id,))
        if not cursor.fetchone():
            logger.error(f"Policy {policy_id} not found")
            return None

        cursor.execute('''
            INSERT INTO claims (policy_id, description, incident_date, amount, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (policy_id, description, incident_date, amount))

        claim_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Created claim {claim_id}")
        return claim_id
    except sqlite3.Error as e:
        logger.error(f"Database error in create_claim: {e}")
        return None
    finally:
        pool.return_connection(conn)


def update_claim_status(claim_id, status):
    """Update claim status."""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE claims 
            SET status = ?
            WHERE id = ?
        ''', (status, claim_id))

        conn.commit()
        logger.info(f"Updated claim {claim_id} status to {status}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error in update_claim_status: {e}")
        return False
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


def get_claim_details(claim_id):
    """Get detailed information about a claim."""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM claims 
            WHERE id = ?
        ''', (claim_id,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        logger.warning(f"Claim {claim_id} not found")
        return None
    except sqlite3.Error as e:
        logger.error(f"Database error in get_claim_details: {e}")
        return None
    finally:
        pool.return_connection(conn)


def get_claims_by_status(status):
    """Get all claims with a specific status."""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT * FROM claims 
            WHERE status = ?
        ''', (status,))

        claims = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Found {len(claims)} claims with status {status}")
        return claims
    except sqlite3.Error as e:
        logger.error(f"Database error in get_claims_by_status: {e}")
        return []
    finally:
        pool.return_connection(conn)