import unittest
import sqlite3
from datetime import datetime
from database.claims import create_claim, get_claims_by_status, get_claim_details
from database.policies import create_policy, get_policy_details, get_customer_policies
from database.auth import verify_user
from tests.config import setup_test_db, teardown_test_db, TEST_DB_PATH


class TestDatabaseOperations(unittest.TestCase):
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

    def test_create_claim(self):
        """Test claim creation"""
        claim_id = create_claim(
            user_id=1,
            policy_id=1,
            description="Test claim",
            incident_date=datetime.now(),
            amount=1000.00
        )
        self.assertIsNotNone(claim_id)

        # Verify claim was created
        self.cursor.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
        claim = self.cursor.fetchone()
        self.assertIsNotNone(claim)
        self.assertEqual(claim[3], "Test claim")  # description
        self.assertEqual(claim[5], 1000.00)  # amount

    def test_get_claims_by_status(self):
        """Test retrieving claims by status"""
        claims = get_claims_by_status(1, "pending")
        self.assertIsInstance(claims, list)

    def test_create_policy(self):
        """Test policy creation"""
        policy_id = create_policy(
            user_id=1,
            customer_id=1,
            policy_type="auto",
            start_date=datetime.now(),
            end_date=datetime.now().replace(year=datetime.now().year + 1),
            premium=1000.00,
            coverage_limit=50000.00
        )
        self.assertIsNotNone(policy_id)

    def test_get_customer_policies(self):
        """Test retrieving customer policies"""
        policies = get_customer_policies(1)
        self.assertIsInstance(policies, list)
        self.assertGreater(len(policies), 0)

    def test_verify_user(self):
        """Test user verification"""
        role = verify_user("test_user", "test_hash")
        self.assertEqual(role, "admin")

    def test_invalid_credentials(self):
        """Test invalid login attempt"""
        role = verify_user("invalid_user", "wrong_password")
        self.assertIsNone(role)


if __name__ == '__main__':
    unittest.main() 