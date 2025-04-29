import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dict_factory(cursor, row):
    """Convert database rows to dictionaries."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def execute_query(query: str, params: tuple = None):
    """Execute a query and return results as a list of dictionaries."""
    conn = sqlite3.connect('insurance.db')
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    cursor.execute(query, params or ())
    results = cursor.fetchall()

    conn.close()
    return results


def execute_update(query: str, params: tuple = None):
    """Execute an update query and return the number of affected rows."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    cursor.execute(query, params or ())
    conn.commit()
    conn.close()
    return cursor.rowcount


def format_date(date: datetime) -> str:
    """Format a datetime object as a string for SQLite."""
    return date.strftime("%Y-%m-%d")


def format_datetime(dt: datetime) -> str:
    """Format a datetime object as a string for SQLite."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")