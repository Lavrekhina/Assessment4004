import sqlite3
import os
from datetime import datetime
import logging
import bcrypt
import secrets
import string
from enum import Enum
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base class for database exceptions"""
    pass


class UserRole(Enum):
    ADMIN = 'admin'
    AGENT = 'agent'
    ADJUSTER = 'adjuster'


class PolicyType(Enum):
    AUTO = 'AUTO'
    HOME = 'HOME'
    LIFE = 'LIFE'
    HEALTH = 'HEALTH'
    TRAVEL = 'TRAVEL'
    PET = 'PET'
    BUSINESS = 'BUSINESS'


class PolicyStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'


class ClaimStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PAID = 'paid'


class PaymentStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'


class Database:
    def __init__(self, db_path='insurance.db', encryption_key=None):
        # Get the absolute path to the database file
        if not os.path.isabs(db_path):
            # Use the workspace root directory
            workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(workspace_root, db_path)
        else:
            self.db_path = db_path

        self.conn = None
        self.cursor = None
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.connect()

    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.conn.row_factory = sqlite3.Row  # Enable row factory for named access
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def _generate_encryption_key(self):
        """Generate a secure encryption key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    def _xor_encrypt(self, text):
        """Simple XOR encryption for sensitive data"""
        if not text:
            return None
        try:
            key = self.encryption_key.encode()
            text_bytes = text.encode()
            encrypted = bytes(a ^ b for a, b in zip(text_bytes, key * (len(text_bytes) // len(key) + 1)))
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return None

    def _xor_decrypt(self, encrypted_text):
        """Simple XOR decryption for sensitive data"""
        if not encrypted_text:
            return None
        try:
            key = self.encryption_key.encode()
            encrypted = base64.b64decode(encrypted_text.encode())
            decrypted = bytes(a ^ b for a, b in zip(encrypted, key * (len(encrypted) // len(key) + 1)))
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return None

    def encrypt_ssn(self, ssn):
        """Encrypt SSN using XOR encryption"""
        return self._xor_encrypt(ssn)

    def decrypt_ssn(self, encrypted_ssn):
        """Decrypt SSN using XOR encryption"""
        return self._xor_decrypt(encrypted_ssn)

    def get_customers(self):
        """Get all customers"""
        try:
            self.cursor.execute("SELECT * FROM customers")
            customers = self.cursor.fetchall()
            # Decrypt SSNs for all customers
            decrypted_customers = []
            for customer in customers:
                # Convert to list to modify the SSN field
                customer = list(customer)
                if customer[7]:  # SSN is at index 7
                    customer[7] = self.decrypt_ssn(customer[7])
                decrypted_customers.append(customer)
            return decrypted_customers
        except Exception as e:
            logger.error(f"Error getting customers: {e}")
            return []

    def get_all_customers(self):
        """Alias for get_customers"""
        return self.get_customers()

    def get_policies(self, customer_id=None):
        """Get all policies or policies for a specific customer"""
        try:
            if customer_id:
                self.cursor.execute("SELECT * FROM policies WHERE customer_id = ?", (customer_id,))
            else:
                self.cursor.execute("SELECT * FROM policies")
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting policies: {e}")
            return []

    def get_all_policies(self):
        """Alias for get_policies"""
        return self.get_policies()

    def get_claims(self, policy_id=None):
        """Get all claims or claims for a specific policy"""
        try:
            if policy_id:
                self.cursor.execute("SELECT * FROM claims WHERE policy_id = ? ORDER BY id", (policy_id,))
            else:
                self.cursor.execute("SELECT * FROM claims ORDER BY id")
            claims = self.cursor.fetchall()

            # Convert to list of dictionaries for easier access
            result = []
            for claim in claims:
                claim_dict = dict(claim)
                status = claim_dict['status']
                logger.info(f"Retrieved claim {claim_dict['id']} with status: {status}")

                # If status is None, update it to pending
                if status is None:
                    logger.warning(f"Claim {claim_dict['id']} has None status, updating to 'pending'")
                    self.update_claim_status(claim_dict['id'], 'pending')
                    claim_dict['status'] = 'pending'

                result.append(claim_dict)

            return result
        except Exception as e:
            logger.error(f"Error getting claims: {e}")
            return None

    def get_all_claims(self):
        """Alias for get_claims"""
        return self.get_claims()

    def create_customer(self, first_name, last_name, email, phone=None, address=None, dob=None, ssn=None):
        """Create a new customer"""
        try:
            # Encrypt SSN before storing
            encrypted_ssn = self.encrypt_ssn(ssn) if ssn else None

            self.cursor.execute("""
                INSERT INTO customers (first_name, last_name, email, phone, address, date_of_birth, ssn_encrypted)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (first_name, last_name, email, phone, address, dob, encrypted_ssn))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None

    def create_policy(self, customer_id, policy_type, policy_number, start_date, end_date,
                      premium, coverage_limit, status='active', payment_schedule=None, beneficiary_info=None,
                      exclusions=None):
        """Create a new policy"""
        try:
            self.cursor.execute("""
                INSERT INTO policies (customer_id, policy_type, policy_number, start_date, end_date,
                                    premium, coverage_limit, status, payment_schedule, beneficiary_info, exclusions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, policy_type, policy_number, start_date, end_date,
                  premium, coverage_limit, status, payment_schedule, beneficiary_info, exclusions))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating policy: {e}")
            return None

    def get_next_claim_number(self):
        """Generate the next claim number in sequence"""
        try:
            # Get the highest claim number
            self.cursor.execute("SELECT MAX(claim_number) FROM claims")
            result = self.cursor.fetchone()
            if not result or not result[0]:
                return "CLM-001"

            # Extract the number part and increment
            last_number = int(result[0].split('-')[1])
            next_number = last_number + 1
            return f"CLM-{next_number:03d}"
        except Exception as e:
            logger.error(f"Error generating claim number: {e}")
            return None

    def create_claim(self, policy_id, claim_date, incident_date, incident_time,
                     incident_location, description, claim_amount, status):
        """Create a new claim"""
        try:
            # Generate claim number
            claim_number = self.get_next_claim_number()
            if not claim_number:
                return None

            # Ensure status is one of the valid values
            valid_statuses = ['pending', 'approved', 'rejected', 'paid']
            if status not in valid_statuses:
                logger.warning(f"Invalid status: {status}, defaulting to 'pending'")
                status = 'pending'

            # Log the status we're about to insert
            logger.info(f"Creating claim with status: {status}")

            # Insert the claim with the status
            self.cursor.execute("""
                INSERT INTO claims (policy_id, claim_number, claim_date, incident_date, incident_time,
                                  incident_location, description, claim_amount, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (policy_id, claim_number, claim_date, incident_date, incident_time,
                  incident_location, description, claim_amount, status))
            self.conn.commit()

            # Verify the status was inserted correctly
            claim_id = self.cursor.lastrowid
            self.cursor.execute("SELECT status FROM claims WHERE id = ?", (claim_id,))
            inserted_status = self.cursor.fetchone()[0]
            logger.info(f"Verified claim {claim_id} status: {inserted_status}")

            return claim_id
        except Exception as e:
            logger.error(f"Error creating claim: {e}")
            return None

    def update_claim_status(self, claim_id, new_status):
        """Update claim status"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute("""
                UPDATE claims SET status = ?, updated_at = ?
                WHERE id = ?
            """, (new_status, current_time, claim_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating claim status: {e}")
            return False

    def get_claim_by_number(self, claim_number):
        """Get claim by claim number"""
        try:
            self.cursor.execute("SELECT * FROM claims WHERE claim_number = ?", (claim_number,))
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting claim: {e}")
            return None

    def get_claim_audit_logs(self, claim_id):
        """Get audit logs for a claim"""
        try:
            self.cursor.execute("""
                SELECT * FROM audit_log 
                WHERE table_name = 'claims' AND record_id = ?
                ORDER BY created_at
            """, (claim_id,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting claim audit logs: {e}")
            return []

    def verify_user(self, username, password):
        """Verify user credentials"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = self.cursor.fetchone()
            if user:
                # Convert the stored password hash from string to bytes
                stored_hash = user[2].encode('utf-8')
                # Check if the provided password matches
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    return {"role": user[3], "branch_id": user[4]}
            return None
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return None

    def get_customer(self, customer_id):
        """Get a single customer by ID"""
        try:
            self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            customer = self.cursor.fetchone()
            if customer:
                # Convert to list to modify the SSN field
                customer = list(customer)
                # Decrypt SSN if it exists
                if customer[7]:  # SSN is at index 7
                    customer[7] = self.decrypt_ssn(customer[7])
            return customer
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            return None

    def get_policy(self, policy_id):
        """Get a single policy by ID"""
        try:
            self.cursor.execute("""
                SELECT * FROM policies 
                WHERE id = ?
            """, (policy_id,))
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting policy: {str(e)}")
            return None

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")