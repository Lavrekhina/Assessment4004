import logging
from datetime import datetime, timedelta
from database.db import Database, PolicyType, PolicyStatus, ClaimStatus
import random
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sample_data(db: Database):
    """Add sample data to the database"""
    try:
        # Get current date for dynamic date calculations
        current_date = datetime.now()

        # Add default user
        password = "admin123"  # Default password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        db.cursor.execute("""
            INSERT INTO users (username, password_hash, role, branch_id)
            VALUES (?, ?, ?, ?)
        """, ('admin', hashed_password.decode('utf-8'), 'admin', 1))
        db.conn.commit()
        logger.info("Created default admin user")

        # Add sample customers
        customers = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '555-0101',
                'address': '123 Main St, Anytown, USA',
                'dob': '1980-01-15',
                'ssn': '123-45-6789'
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@example.com',
                'phone': '555-0102',
                'address': '456 Oak Ave, Somewhere, USA',
                'dob': '1985-05-20',
                'ssn': '234-56-7890'
            },
            {
                'first_name': 'Robert',
                'last_name': 'Johnson',
                'email': 'robert.j@example.com',
                'phone': '555-0103',
                'address': '789 Pine Rd, Elsewhere, USA',
                'dob': '1975-11-30',
                'ssn': '345-67-8901'
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'email': 'sarah.w@example.com',
                'phone': '555-0104',
                'address': '321 Elm St, Nowhere, USA',
                'dob': '1990-03-25',
                'ssn': '456-78-9012'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Brown',
                'email': 'michael.b@example.com',
                'phone': '555-0105',
                'address': '654 Maple Dr, Anywhere, USA',
                'dob': '1988-07-12',
                'ssn': '567-89-0123'
            }
        ]

        customer_ids = []
        for customer in customers:
            customer_id = db.create_customer(
                first_name=customer['first_name'],
                last_name=customer['last_name'],
                email=customer['email'],
                phone=customer['phone'],
                address=customer['address'],
                dob=customer['dob'],
                ssn=customer['ssn']
            )
            customer_ids.append(customer_id)
            logger.info(f"Created customer: {customer['first_name']} {customer['last_name']}")

        # Add sample policies with dynamic dates
        policies = [
            {
                'customer_id': customer_ids[0],
                'policy_type': PolicyType.AUTO.value,
                'policy_number': 'AUTO',
                'start_date': (current_date - timedelta(days=180)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=180)).strftime('%Y-%m-%d'),
                'premium': 1200.00,
                'coverage_limit': 50000.00,
                'status': PolicyStatus.ACTIVE.value,
                'payment_schedule': 'Monthly',
                'beneficiary_info': 'Self',
                'exclusions': 'Racing, Commercial use'
            },
            {
                'customer_id': customer_ids[1],
                'policy_type': PolicyType.HOME.value,
                'policy_number': 'HOME',
                'start_date': (current_date - timedelta(days=90)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=275)).strftime('%Y-%m-%d'),
                'premium': 2500.00,
                'coverage_limit': 300000.00,
                'status': PolicyStatus.ACTIVE.value,
                'payment_schedule': 'Quarterly',
                'beneficiary_info': 'Family',
                'exclusions': 'Flood damage'
            },
            {
                'customer_id': customer_ids[2],
                'policy_type': PolicyType.LIFE.value,
                'policy_number': 'LIFE',
                'start_date': (current_date - timedelta(days=45)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=3650)).strftime('%Y-%m-%d'),
                'premium': 5000.00,
                'coverage_limit': 1000000.00,
                'status': PolicyStatus.ACTIVE.value,
                'payment_schedule': 'Annual',
                'beneficiary_info': 'Spouse and Children',
                'exclusions': 'Suicide within first year'
            },
            {
                'customer_id': customer_ids[3],
                'policy_type': PolicyType.HEALTH.value,
                'policy_number': 'HEALTH',
                'start_date': (current_date - timedelta(days=30)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=335)).strftime('%Y-%m-%d'),
                'premium': 3500.00,
                'coverage_limit': 500000.00,
                'status': PolicyStatus.INACTIVE.value,
                'payment_schedule': 'Monthly',
                'beneficiary_info': 'Self and Dependents',
                'exclusions': 'Pre-existing conditions'
            },
            {
                'customer_id': customer_ids[4],
                'policy_type': PolicyType.TRAVEL.value,
                'policy_number': 'TRAVEL',
                'start_date': (current_date - timedelta(days=15)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=45)).strftime('%Y-%m-%d'),
                'premium': 500.00,
                'coverage_limit': 25000.00,
                'status': PolicyStatus.ACTIVE.value,
                'payment_schedule': 'Single Payment',
                'beneficiary_info': 'Self',
                'exclusions': 'Extreme sports, War zones'
            },
            {
                'customer_id': customer_ids[0],
                'policy_type': PolicyType.PET.value,
                'policy_number': 'PET',
                'start_date': (current_date - timedelta(days=60)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=305)).strftime('%Y-%m-%d'),
                'premium': 800.00,
                'coverage_limit': 10000.00,
                'status': PolicyStatus.CANCELLED.value,
                'payment_schedule': 'Monthly',
                'beneficiary_info': 'Dog: Max',
                'exclusions': 'Pre-existing conditions'
            },
            {
                'customer_id': customer_ids[1],
                'policy_type': PolicyType.BUSINESS.value,
                'policy_number': 'BUSINESS',
                'start_date': (current_date - timedelta(days=45)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=320)).strftime('%Y-%m-%d'),
                'premium': 5000.00,
                'coverage_limit': 1000000.00,
                'status': PolicyStatus.EXPIRED.value,
                'payment_schedule': 'Quarterly',
                'beneficiary_info': 'Business: Smith Consulting LLC',
                'exclusions': 'Cyber attacks, Employee fraud'
            }
        ]

        policy_ids = []
        for policy in policies:
            policy_id = db.create_policy(
                customer_id=policy['customer_id'],
                policy_type=policy['policy_type'],
                policy_number=policy['policy_number'],
                start_date=policy['start_date'],
                end_date=policy['end_date'],
                premium=policy['premium'],
                coverage_limit=policy['coverage_limit'],
                status=policy['status'],
                payment_schedule=policy['payment_schedule'],
                beneficiary_info=policy['beneficiary_info'],
                exclusions=policy['exclusions']
            )
            policy_ids.append(policy_id)
            logger.info(f"Created policy: {policy['policy_number']}")

        # Add sample claims with dynamic dates
        claims = [
            {
                'policy_id': policy_ids[0],
                'claim_date': (current_date - timedelta(days=15)).strftime('%Y-%m-%d'),
                'incident_date': (current_date - timedelta(days=16)).strftime('%Y-%m-%d'),
                'incident_time': '14:30:00',
                'incident_location': 'Main St and 1st Ave, Anytown',
                'description': 'Rear-end collision at traffic light',
                'claim_amount': 5000.00,
                'status': 'pending'  # New claim, under review
            },
            {
                'policy_id': policy_ids[1],
                'claim_date': (current_date - timedelta(days=10)).strftime('%Y-%m-%d'),
                'incident_date': (current_date - timedelta(days=11)).strftime('%Y-%m-%d'),
                'incident_time': '02:15:00',
                'incident_location': '456 Oak Ave, Somewhere',
                'description': 'Water damage from burst pipe',
                'claim_amount': 15000.00,
                'status': 'approved'  # Claim approved but not yet paid
            },
            {
                'policy_id': policy_ids[3],
                'claim_date': (current_date - timedelta(days=5)).strftime('%Y-%m-%d'),
                'incident_date': (current_date - timedelta(days=5)).strftime('%Y-%m-%d'),
                'incident_time': '09:45:00',
                'incident_location': 'City Hospital',
                'description': 'Emergency appendectomy',
                'claim_amount': 25000.00,
                'status': 'paid'  # Claim processed and paid
            },
            {
                'policy_id': policy_ids[4],
                'claim_date': (current_date - timedelta(days=3)).strftime('%Y-%m-%d'),
                'incident_date': (current_date - timedelta(days=4)).strftime('%Y-%m-%d'),
                'incident_time': '16:45:00',
                'incident_location': 'Vet Emergency Clinic',
                'description': 'Emergency treatment for dog after eating chocolate',
                'claim_amount': 800.00,
                'status': 'rejected'  # Claim rejected as it's a pre-existing condition
            }
        ]

        for claim in claims:
            claim_id = db.create_claim(
                policy_id=claim['policy_id'],
                claim_date=claim['claim_date'],
                incident_date=claim['incident_date'],
                incident_time=claim['incident_time'],
                incident_location=claim['incident_location'],
                description=claim['description'],
                claim_amount=claim['claim_amount'],
                status=claim['status']
            )
            if claim_id:
                logger.info(f"Created claim: {claim_id}")

        logger.info("Sample data added successfully")
        return True
    except Exception as e:
        logger.error(f"Error adding sample data: {e}")
        return False

if __name__ == "__main__":
    db = Database()
    add_sample_data(db)
    db.close() 