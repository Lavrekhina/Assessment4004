import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_database():
    """Initialize the database with required tables."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    logger.info("Database setup completed successfully")


def execute_query(query, params=None, fetch=True):
    """Execute a query and return results if fetch is True."""
    conn = sqlite3.connect('insurance.db')
    cursor = conn.cursor()

    cursor.execute(query, params or ())

    if fetch:
        columns = [col[0] for col in cursor.description] if cursor.description else []
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results

    conn.commit()
    conn.close()

