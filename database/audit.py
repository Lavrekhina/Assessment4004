import sqlite3
from datetime import datetime


def log_action(user_id, action, table_name, record_id, details=None):
    """Log a database action."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    query = """
    INSERT INTO audit_logs (user_id, action, table_name, record_id, details, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (
        user_id,
        action,
        table_name,
        record_id,
        str(details) if details else None,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    cursor.execute(query, params)
    conn.commit()
    conn.close()


def get_user_actions(user_id):
    """Get all actions performed by a user."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM audit_logs 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user_id,))

    results = cursor.fetchall()
    conn.close()
    return results