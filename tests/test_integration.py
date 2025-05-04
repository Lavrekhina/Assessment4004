import unittest
import os
import sqlite3
from datetime import datetime, timedelta
from tests.config import setup_test_db, teardown_test_db, TEST_DB_PATH
from database.claims import create_claim, get_claims_by_status
from database.policies import create_policy, get_policy_details
from database.auth import verify_user
from db_operations import (
    create_customer,
    get_customer,
    update_customer,
    delete_customer,
    create_policy,
    get_policy,
    update_policy,
    delete_policy,
    create_claim,
    get_claim,
    update_claim,
    delete_claim
)
import database.pool

class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test database and connection"""
        setup_test_db()
        self.db = database.pool.get_connection()
        self.cursor = self.db.cursor()

    def tearDown(self):
        """Clean up test database"""
        teardown_test_db()
        database.pool.return_connection(self.db)

    def test_customer_policy_claim_flow(self):
        """Test the complete flow from customer creation to claim processing"""
        # Create a customer
        customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'ssn': '123-45-6789'
        }
        customer_id = create_customer(self.db, customer_data)
        self.assertIsNotNone(customer_id)

        # Create a policy for the customer
        policy_data = {
            'customer_id': customer_id,
            'policy_type': 'AUTO',
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'premium': 1000.00,
            'status': 'active'
        }
        policy_id = create_policy(self.db, policy_data)
        self.assertIsNotNone(policy_id)

        # Create a claim for the policy
        claim_data = {
            'policy_id': policy_id,
            'claim_date': datetime.now().strftime('%Y-%m-%d'),
            'incident_date': datetime.now().strftime('%Y-%m-%d'),
            'incident_time': datetime.now().strftime('%H:%M:%S'),
            'incident_location': '123 Main St',
            'description': 'Car accident',
            'claim_amount': 5000.00,
            'status': 'pending'
        }
        claim_id = create_claim(self.db, claim_data)
        self.assertIsNotNone(claim_id)

        # Verify the claim was created
        claim = get_claim(self.db, claim_id)
        self.assertIsNotNone(claim)
        self.assertEqual(claim['status'], 'pending')

        # Update the claim status
        update_claim(self.db, claim_id, {'status': 'approved'})
        claim = get_claim(self.db, claim_id)
        self.assertEqual(claim['status'], 'approved')

        # Clean up
        delete_claim(self.db, claim_id)
        delete_policy(self.db, policy_id)
        delete_customer(self.db, customer_id)

if __name__ == '__main__':
    unittest.main()