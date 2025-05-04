import sqlite3
import os
from database.sample_data import add_sample_data
from database.db import Database


def init_db():
    try:
        # Remove existing database if it exists
        if os.path.exists('insurance.db'):
            os.remove('insurance.db')

        # Create new database
        conn = sqlite3.connect('insurance.db')
        cursor = conn.cursor()

        # Read and execute schema
        with open('schema.sql', 'r') as f:
            schema = f.read()
            cursor.executescript(schema)

        conn.commit()
        print("Database initialized successfully!")

        # Add sample data
        db = Database()
        add_sample_data(db)
        print("Sample data added successfully!")

        # Add test user
        import bcrypt
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        password_hash_str = password_hash.decode('utf-8')

        cursor.execute("""
            INSERT INTO branches (name, address, phone, email)
            VALUES ('Test Branch', '123 Test St', '555-0000', 'test@example.com')
        """)

        cursor.execute("SELECT id FROM branches WHERE name = 'Test Branch'")
        branch_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO users (username, password_hash, role, branch_id)
            VALUES (?, ?, 'admin', ?)
        """, ('admin', password_hash_str, branch_id))

        conn.commit()
        print("Test user created successfully!")
        print("Username: admin")
        print("Password: admin123")

    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()