import unittest
import os
import tempfile
import sqlite3
from datetime import datetime
from tests.config import setup_test_db, teardown_test_db, TEST_DB_PATH
from database.claims import create_claim, get_claims_by_status
from database.policies import create_policy, get_policy_details
from database.auth import verify_user
from db_operations import (
    setup_database,
    create_customer,
    get_customer,
    update_customer,
    delete_customer,
    POLICY_TYPES,
    CLAIM_STATUSES
)


class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_test_db()
        # Override database path for testing
        import database.pool
        database.pool.DB_PATH = TEST_DB_PATH

    @classmethod
    def tearDownClass(cls):
        teardown_test_db()

    def setUp(self):
        self.conn = sqlite3.connect(TEST_DB_PATH)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_customer_crud_flow(self):
        """Test complete customer CRUD operations"""
        # Create customer
        customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'date_of_birth': '1990-01-01',
            'password': 'securepassword123'
        }
        customer_id = create_customer(customer_data, TEST_DB_PATH)
        self.assertIsNotNone(customer_id)

        # Retrieve customer
        customer = get_customer(customer_id, TEST_DB_PATH)
        self.assertEqual(customer['first_name'], 'John')
        self.assertEqual(customer['last_name'], 'Doe')

        # Update customer
        updated_data = customer_data.copy()
        updated_data['phone'] = '0987654321'
        update_customer(customer_id, updated_data, TEST_DB_PATH)

        # Verify update
        updated_customer = get_customer(customer_id, TEST_DB_PATH)
        self.assertEqual(updated_customer['phone'], '0987654321')

        # Delete customer
        delete_customer(customer_id, TEST_DB_PATH)
        deleted_customer = get_customer(customer_id, TEST_DB_PATH)
        self.assertIsNone(deleted_customer)

    def test_policy_creation_flow(self):
        """Test policy creation and retrieval"""
        # Create customer
        customer_id = create_customer({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'date_of_birth': '1990-01-01',
            'password': 'securepassword123'
        }, TEST_DB_PATH)

        # Create policy using both methods
        # Method 1: Using db_operations
        policy_id1 = create_policy({
            'customer_id': customer_id,
            'policy_number': 'POL123',
            'policy_type': POLICY_TYPES['AUTO'],
            'start_date': '2024-01-01',
            'end_date': '2025-01-01',
            'premium_amount': 1000.00,
            'coverage_details': 'Full coverage',
            'status': 'active'
        }, TEST_DB_PATH)
        self.assertIsNotNone(policy_id1)

        # Method 2: Using database module
        policy_id2 = create_policy(
            user_id=1,
            customer_id=customer_id,
            policy_type="auto",
            start_date=datetime.now(),
            end_date=datetime.now().replace(year=datetime.now().year + 1),
            premium=1000.00,
            coverage_limit=50000.00
        )
        self.assertIsNotNone(policy_id2)

        # Verify policies exist
        policy1 = get_policy_details(policy_id1)
        self.assertIsNotNone(policy1)
        policy2 = get_policy_details(policy_id2)
        self.assertIsNotNone(policy2)

    def test_claim_creation_flow(self):
        """Test claim creation and retrieval"""
        # Create customer and policy first
        customer_id = create_customer({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'date_of_birth': '1990-01-01',
            'password': 'securepassword123'
        }, TEST_DB_PATH)

        policy_id = create_policy(
            user_id=1,
            customer_id=customer_id,
            policy_type="auto",
            start_date=datetime.now(),
            end_date=datetime.now().replace(year=datetime.now().year + 1),
            premium=1000.00,
            coverage_limit=50000.00
        )

        # Create claim
        claim_id = create_claim(
            user_id=1,
            policy_id=policy_id,
            description="Test claim",
            incident_date=datetime.now(),
            amount=1000.00
        )
        self.assertIsNotNone(claim_id)

        # Verify claim exists
        claims = get_claims_by_status(1, "pending")
        self.assertGreater(len(claims), 0)
        self.assertEqual(claims[0]['policy_id'], policy_id)

    def test_user_authentication_flow(self):
        """Test user authentication and role-based access"""
        # Verify test user exists
        role = verify_user("test_user", "test_hash")
        self.assertEqual(role, "admin")

        # Test invalid credentials
        role = verify_user("invalid_user", "wrong_password")
        self.assertIsNone(role)


if __name__ == '__main__':
    unittest.main()