import sqlite3
import bcrypt
import logging
from datetime import datetime
from .pool import pool

# Set up logging
logger = logging.getLogger(__name__)


def create_user(username, password, role):
    """Create a new user with hashed password."""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        # Hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        query = """
        INSERT INTO users (username, password_hash, role, created_at)
        VALUES (?, ?, ?, ?)
        """
        params = (
            username,
            hashed.decode('utf-8'),
            role,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        cursor.execute(query, params)
        user_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Created user {username} with role {role}")
        return user_id
    except sqlite3.Error as e:
        logger.error(f"Database error in create_user: {e}")
        return None
    finally:
        pool.return_connection(conn)


def verify_user(username, password):
    """Verify user credentials"""
    try:
        logger.info(f"Attempting to verify user: {username}")
        conn = pool.get_connection()
        cursor = conn.cursor()

        # Get the stored password hash
        cursor.execute('''
            SELECT password_hash FROM users 
            WHERE username = ?
        ''', (username,))

        row = cursor.fetchone()
        if not row:
            logger.warning(f"User not found: {username}")
            return None

        stored_hash = row[0].encode('utf-8')
        logger.info("Retrieved password hash")

        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            logger.info("Password verified successfully")
            # Get user role
            cursor.execute('''
                SELECT role FROM users 
                WHERE username = ?
            ''', (username,))
            role_row = cursor.fetchone()
            role = role_row[0] if role_row else None
            logger.info(f"User role: {role}")
            return role

        logger.warning("Password verification failed")
        return None
    except sqlite3.Error as e:
        logger.error(f"Database error in verify_user: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in verify_user: {e}")
        return None
    finally:
        pool.return_connection(conn)
        logger.info("Connection returned to pool")


def check_access(user_role, required_role):
    """Check if user has required role access."""
    role_hierarchy = {
        'admin': ['admin', 'claims_manager', 'adjuster', 'user'],
        'claims_manager': ['claims_manager', 'adjuster', 'user'],
        'adjuster': ['adjuster', 'user'],
        'user': ['user']
    }
    return required_role in role_hierarchy.get(user_role, [])