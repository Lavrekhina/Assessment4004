import sqlite3
import bcrypt
from datetime import datetime
from .pool import pool


def create_user(username, password, role):
    """Create a new user with hashed password."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

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
    conn.commit()
    conn.close()


def verify_user(username, password):
    """Verify user credentials"""
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT role FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password))

        row = cursor.fetchone()
        return row['role'] if row else None
    finally:
        pool.return_connection(conn)


def check_access(user_role, required_role):
    """Check if user has required role access."""
    role_hierarchy = {
        'admin': ['admin', 'claims_manager', 'adjuster', 'user'],
        'claims_manager': ['claims_manager', 'adjuster', 'user'],
        'adjuster': ['adjuster', 'user'],
        'user': ['user']
    }
    return required_role in role_hierarchy.get(user_role, [])