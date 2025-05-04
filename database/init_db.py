import sqlite3
import os
import logging
from database.sample_data import add_sample_data
from database.db import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database by creating tables and adding sample data"""
    try:
        # Get absolute path for database file
        workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(workspace_root, 'insurance.db')

        # Remove existing database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info("Removed existing database")

        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Read and execute schema from database folder
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
        logger.info(f"Loading schema from: {schema_path}")

        try:
            with open(schema_path, 'r') as f:
                schema = f.read()
                cursor.executescript(schema)
                conn.commit()
                logger.info("Schema loaded successfully")
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
            raise

        # Add test branch
        cursor.execute("""
            INSERT INTO branches (name, address, phone, email)
            VALUES ('Test Branch', '123 Test St', '555-0000', 'test@example.com')
        """)
        conn.commit()
        logger.info("Test branch created")

        # Close initial connection
        conn.close()

        # Create database instance and add sample data
        db = Database(db_path)
        if add_sample_data(db):
            logger.info("Sample data added successfully")
        else:
            logger.error("Failed to add sample data")

        return True

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    init_db()