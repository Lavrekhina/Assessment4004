import logging
from datetime import datetime, timedelta
from database.db import Database, PolicyType, PolicyStatus, ClaimStatus
import random
import bcrypt
import sqlite3
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sample_data(db: Database):
    """Add sample data to the database"""
    try:
        # Get current date for dynamic date calculations
        current_date = datetime.now()
        # Generate unique timestamp for emails
        timestamp = int(time.time())

        # Check if admin user already exists
        db.cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not db.cursor.fetchone():
            # Add default user
            password = "admin123"  # Default password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            db.cursor.execute("""
                INSERT INTO users (username, password_hash, role, branch_id)
                VALUES (?, ?, ?, ?)
            """, ('admin', hashed_password.decode('utf-8'), 'admin', 1))
            db.conn.commit()
            logger.info("Created default admin user")
        else:
            logger.info("Admin user already exists")

        # Add sample customers
        customers = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': f'john.doe.{timestamp}@example.com',
                'phone': '555-0101',
                'address': '123 Main St, Anytown, USA',
                'dob': '1980-01-15',
                'ssn': '123-45-6789'
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': f'jane.smith.{timestamp}@example.com',
                'phone': '555-0102',
                'address': '456 Oak Ave, Somewhere, USA',
                'dob': '1985-05-20',
                'ssn': '234-56-7890'
            },
            {
                'first_name': 'Robert',
                'last_name': 'Johnson',
                'email': f'robert.j.{timestamp}@example.com',
                'phone': '555-0103',
                'address': '789 Pine Rd, Elsewhere, USA',
                'dob': '1975-11-30',
                'ssn': '345-67-8901'
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'email': f'sarah.w.{timestamp}@example.com',
                'phone': '555-0104',
                'address': '321 Elm St, Nowhere, USA',
                'dob': '1990-03-25',
                'ssn': '456-78-9012'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Brown',
                'email': f'michael.b.{timestamp}@example.com',
                'phone': '555-0105',
                'address': '654 Maple Dr, Anywhere, USA',
                'dob': '1988-07-12',
                'ssn': '567-89-0123'
            }
        ]

        customer_ids = []
        for customer in customers:
            try:
                customer_id = db.create_customer(
                    first_name=customer['first_name'],
                    last_name=customer['last_name'],
                    email=customer['email'],
                    phone=customer['phone'],
                    address=customer['address'],
                    dob=customer['dob'],
                    ssn=customer['ssn']
                )
                if customer_id:
                    customer_ids.append(customer_id)
                    logger.info(f"Created customer: {customer['first_name']} {customer['last_name']}")
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    logger.warning(f"Customer {customer['email']} already exists")
                else:
                    raise

        if not customer_ids:
            raise Exception("No customers were created. Cannot proceed with policy creation.")

        # Add sample policies
        policy_types = ['AUTO', 'HOME', 'LIFE', 'HEALTH', 'TRAVEL', 'PET', 'BUSINESS']
        policy_ids = []
        for policy_type in policy_types:
            try:
                policy_id = db.create_policy(
                    customer_id=random.choice(customer_ids),
                    policy_type=policy_type,
                    policy_number=f"POL-{timestamp}-{random.randint(1000, 9999)}",
                    start_date=current_date.strftime('%Y-%m-%d'),
                    end_date=(current_date + timedelta(days=365)).strftime('%Y-%m-%d'),
                    premium=random.uniform(500, 2000),
                    coverage_limit=random.uniform(10000, 100000),
                    status='active',
                    payment_schedule='Monthly',
                    beneficiary_info='Self',
                    exclusions='None'
                )
                if policy_id:
                    policy_ids.append(policy_id)
                    logger.info(f"Created policy: {policy_type}")
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    logger.warning(f"Policy number already exists")
                else:
                    raise

        if not policy_ids:
            raise Exception("No policies were created. Cannot proceed with claim creation.")

        # Add sample claims
        claim_statuses = ['pending', 'approved', 'paid', 'rejected']
        for status in claim_statuses:
            try:
                claim_id = db.create_claim(
                    policy_id=policy_ids[0],
                    claim_date=current_date.strftime('%Y-%m-%d'),
                    incident_date=current_date.strftime('%Y-%m-%d'),
                    incident_time=current_date.strftime('%H:%M:%S'),
                    incident_location='123 Main St',
                    description=f'Test claim with status: {status}',
                    claim_amount=random.uniform(1000, 5000),
                    status=status
                )
                if claim_id:
                    logger.info(f"Created claim: {claim_id}")
            except Exception as e:
                logger.error(f"Error creating claim: {e}")

        logger.info("Sample data added successfully")
        return True

    except Exception as e:
        logger.error(f"Error adding sample data: {e}")
        return False

if __name__ == "__main__":
    db = Database()
    add_sample_data(db)
    db.close() 