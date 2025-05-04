import unittest
import tkinter as tk
from gui.main import InsuranceSystem
from tests.config import setup_test_db, teardown_test_db, TEST_DB_PATH


class TestInsuranceSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_test_db()
        cls.root = tk.Tk()
        cls.app = InsuranceSystem()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        teardown_test_db()

    def test_login_window_exists(self):
        """Test if login window is properly initialized"""
        self.assertIsNotNone(self.app.login_window)
        self.assertTrue(self.app.login_window.winfo_exists())

    def test_login_fields_exist(self):
        """Test if login fields are properly initialized"""
        self.assertIsNotNone(self.app.username_entry)
        self.assertIsNotNone(self.app.password_entry)

    def test_login_success(self):
        """Test successful login"""
        # Set test credentials
        self.app.username_entry.insert(0, 'test_user')
        self.app.password_entry.insert(0, 'test123')

        # Perform login
        self.app.login()

        # Verify main window is created
        self.assertIsNotNone(self.app.main_window)
        self.assertTrue(self.app.main_window.winfo_exists())

    def test_login_failure(self):
        """Test failed login"""
        # Set invalid credentials
        self.app.username_entry.delete(0, tk.END)
        self.app.password_entry.delete(0, tk.END)
        self.app.username_entry.insert(0, 'invalid_user')
        self.app.password_entry.insert(0, 'wrong_password')

        # Perform login
        self.app.login()

        # Verify main window is not created
        self.assertIsNone(getattr(self.app, 'main_window', None))

    def test_main_window_tabs(self):
        """Test if main window tabs are properly initialized"""
        # Login first
        self.app.username_entry.delete(0, tk.END)
        self.app.password_entry.delete(0, tk.END)
        self.app.username_entry.insert(0, 'test_user')
        self.app.password_entry.insert(0, 'test123')
        self.app.login()

        # Verify tabs exist
        self.assertIsNotNone(self.app.notebook)
        self.assertIsNotNone(self.app.customers_tab)
        self.assertIsNotNone(self.app.policies_tab)
        self.assertIsNotNone(self.app.claims_tab)
        self.assertIsNotNone(self.app.reports_tab)

    def test_customer_creation(self):
        """Test customer creation functionality"""
        # Login first
        self.app.username_entry.delete(0, tk.END)
        self.app.password_entry.delete(0, tk.END)
        self.app.username_entry.insert(0, 'test_user')
        self.app.password_entry.insert(0, 'test123')
        self.app.login()

        # Set test values
        self.app.first_name_entry.insert(0, 'New')
        self.app.last_name_entry.insert(0, 'Customer')
        self.app.email_entry.insert(0, 'new@example.com')
        self.app.phone_entry.insert(0, '9876543210')
        self.app.address_entry.insert(0, '456 New St')
        self.app.dob_entry.insert(0, '1995-01-01')
        self.app.ssn_entry.insert(0, '987-65-4321')

        # Create customer
        self.app.create_customer()

        # Verify customer list is updated
        self.assertGreater(len(self.app.customer_tree.get_children()), 0)


if __name__ == '__main__':
    unittest.main()