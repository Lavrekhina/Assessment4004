import unittest
import tkinter as tk
from gui.main import InsuranceApp
from tests.config import setup_test_db, teardown_test_db, TEST_DB_PATH


class TestInsuranceApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_test_db()
        cls.root = tk.Tk()
        cls.app = InsuranceApp(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        teardown_test_db()

    def test_login_frame_exists(self):
        """Test if login frame is properly initialized"""
        self.assertIsNotNone(self.app.login_frame)
        self.assertTrue(self.app.login_frame.winfo_exists())

    def test_main_frame_hidden_initially(self):
        """Test if main frame is hidden initially"""
        self.assertFalse(self.app.main_frame.winfo_ismapped())

    def test_claims_tab_exists(self):
        """Test if claims tab is properly initialized"""
        self.assertIsNotNone(self.app.claims_frame)
        self.assertIsNotNone(self.app.claims_tree)

    def test_policies_tab_exists(self):
        """Test if policies tab is properly initialized"""
        self.assertIsNotNone(self.app.policies_frame)
        self.assertIsNotNone(self.app.policies_tree)

    def test_reports_tab_exists(self):
        """Test if reports tab is properly initialized"""
        self.assertIsNotNone(self.app.reports_frame)
        self.assertIsNotNone(self.app.report_text)

    def test_submit_claim(self):
        """Test claim submission functionality"""
        # Set test values
        self.app.policy_id.insert(0, "1")
        self.app.description.insert(0, "Test claim")
        self.app.amount.insert(0, "1000.00")

        # Submit claim
        self.app.submit_claim()

        # Verify claims tree is updated
        self.assertGreater(len(self.app.claims_tree.get_children()), 0)

    def test_create_policy(self):
        """Test policy creation functionality"""
        # Set test values
        self.app.customer_id.insert(0, "1")
        self.app.policy_type.insert(0, "auto")
        self.app.premium.insert(0, "1000.00")

        # Create policy
        self.app.create_policy()

        # Verify policies tree is updated
        self.assertGreater(len(self.app.policies_tree.get_children()), 0)

    def test_generate_report(self):
        """Test report generation functionality"""
        # Set report type
        self.app.report_type.set("Claims by Status")

        # Generate report
        self.app.generate_report()

        # Verify report text is updated
        self.assertNotEqual(self.app.report_text.get("1.0", tk.END).strip(), "")


if __name__ == '__main__':
    unittest.main()