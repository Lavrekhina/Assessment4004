import sqlite3
import os
import bcrypt
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    try:
        # Get the absolute path to the database using os
        db_path = os.path.join(os.getcwd(), 'insurance.db')
        logger.info(f"Database will be created at: {db_path}")

        # Remove existing database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info("Removed existing database")

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logger.info("Connected to database")

        # Enable foreign keys
        cursor.execute('PRAGMA foreign_keys = ON;')
        logger.info("Enabled foreign keys")

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        logger.info("Created users table")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address TEXT
            )
        ''')
        logger.info("Created customers table")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                policy_type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                premium REAL NOT NULL,
                coverage_limit REAL NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        logger.info("Created policies table")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                incident_date TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (policy_id) REFERENCES policies(id)
            )
        ''')
        logger.info("Created claims table")

        # Hash password using bcrypt
        password = 'test123'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        logger.info("Hashed password created")

        # Add test user
        cursor.execute('''
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, 'admin')
        ''', ('test', hashed_password.decode('utf-8')))
        logger.info("Added test user")

        # Add test customer
        try:
            cursor.execute('''
                INSERT INTO customers (first_name, last_name, email, phone)
                VALUES (?, ?, ?, ?)
            ''', ('Test', 'Customer', 'test@example.com', '1234567890'))
            customer_id = cursor.lastrowid
            logger.info(f"Added test customer with ID: {customer_id}")

            # Verify customer was created
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            customer = cursor.fetchone()
            logger.info(f"Verified customer: {customer}")

            # Add test policy
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                next_year = datetime.now().replace(year=datetime.now().year + 1).strftime("%Y-%m-%d")

                policy_data = (customer_id, 'auto', today, next_year, 1000.00, 50000.00, 'active')
                logger.info(f"Attempting to insert policy with data: {policy_data}")

                cursor.execute('''
                    INSERT INTO policies 
                    (customer_id, policy_type, start_date, end_date, premium, coverage_limit, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', policy_data)

                policy_id = cursor.lastrowid
                logger.info(f"Added test policy with ID: {policy_id}")

                # Verify policy was created
                cursor.execute("SELECT * FROM policies WHERE id = ?", (policy_id,))
                policy = cursor.fetchone()
                logger.info(f"Verified policy: {policy}")

            except sqlite3.Error as e:
                logger.error(f"Error creating policy: {e}")
                raise

        except sqlite3.Error as e:
            logger.error(f"Error creating customer: {e}")
            raise

        conn.commit()
        logger.info(f"Database setup completed successfully at {db_path}")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    setup_database()