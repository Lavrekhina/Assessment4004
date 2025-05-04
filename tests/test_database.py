import unittest
import sqlite3
from datetime import datetime
from database.db import Database, UserRole, PolicyType, ClaimStatus
from tests.config import setup_test_db, teardown_test_db, TEST_DB_PATH


class TestDatabaseOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_test_db()
        cls.db = Database(TEST_DB_PATH)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        teardown_test_db()

    def test_verify_user(self):
        """Test user verification"""
        # Test valid credentials
        result = self.db.verify_user('test_user', 'test123')
        self.assertIsNotNone(result)
        self.assertEqual(result['role'], 'admin')
        self.assertEqual(result['branch_id'], 1)

        # Test invalid credentials
        result = self.db.verify_user('invalid_user', 'wrong_password')
        self.assertIsNone(result)

    def test_create_customer(self):
        """Test customer creation"""
        customer_id = self.db.create_customer(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            address='123 Main St',
            dob='1990-01-01',
            ssn='123-45-6789'
        )
        self.assertIsNotNone(customer_id)

        # Verify customer was created
        customer = self.db.get_customer(customer_id)
        self.assertIsNotNone(customer)
        self.assertEqual(customer[1], 'John')  # first_name
        self.assertEqual(customer[2], 'Doe')   # last_name
        self.assertEqual(customer[3], 'john.doe@example.com')  # email

    def test_create_policy(self):
        """Test policy creation"""
        policy_id = self.db.create_policy(
            customer_id=1,
            policy_type=PolicyType.AUTO.value,
            policy_number='POL002',
            start_date='2024-01-01',
            end_date='2025-01-01',
            premium=1000.00,
            coverage_limit=50000.00,
            status='active',
            payment_schedule='monthly'
        )
        self.assertIsNotNone(policy_id)

        # Verify policy was created
        policy = self.db.get_policy(policy_id)
        self.assertIsNotNone(policy)
        self.assertEqual(policy['policy_type'], PolicyType.AUTO.value)
        self.assertEqual(policy['policy_number'], 'POL002')

    def test_create_claim(self):
        """Test claim creation"""
        claim_id = self.db.create_claim(
            policy_id=1,
            claim_date='2024-01-15',
            incident_date='2024-01-14',
            incident_time='14:30:00',
            incident_location='123 Main St',
            description='Test claim',
            claim_amount=1000.00,
            status=ClaimStatus.PENDING.value
        )
        self.assertIsNotNone(claim_id)

        # Verify claim was created
        claims = self.db.get_claims(policy_id=1)
        self.assertIsNotNone(claims)
        self.assertGreater(len(claims), 0)
        self.assertEqual(claims[0]['status'], ClaimStatus.PENDING.value)

    def test_update_claim_status(self):
        """Test claim status update"""
        # Create a claim first
        claim_id = self.db.create_claim(
            policy_id=1,
            claim_date='2024-01-15',
            incident_date='2024-01-14',
            incident_time='14:30:00',
            incident_location='123 Main St',
            description='Test claim',
            claim_amount=1000.00,
            status=ClaimStatus.PENDING.value
        )

        # Update claim status
        success = self.db.update_claim_status(claim_id, ClaimStatus.APPROVED.value)
        self.assertTrue(success)

        # Verify status was updated
        claims = self.db.get_claims(policy_id=1)
        self.assertEqual(claims[0]['status'], ClaimStatus.APPROVED.value)


if __name__ == '__main__':
    unittest.main() 