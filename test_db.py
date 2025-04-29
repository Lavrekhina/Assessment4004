import unittest
import os
import tempfile
from db_operations import (
    setup_database,
    create_customer,
    get_customer,
    update_customer,
    delete_customer,
    create_policy,
    create_claim,
    POLICY_TYPES,
    CLAIM_STATUSES
)


def test_customer_crud():
    # Create a temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    db_path = temp_db.name

    try:
        # Setup database
        setup_database(db_path)

        # Create a customer
        customer_id = create_customer({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'date_of_birth': '1990-01-01',
            'password': 'securepassword123'
        }, db_path)
        assert customer_id is not None

        # Retrieve the customer
        customer = get_customer(customer_id, db_path)
        assert customer['first_name'] == 'John'
        assert customer['last_name'] == 'Doe'

        # Update the customer
        update_customer(customer_id, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '0987654321',
            'address': '123 Main St',
            'date_of_birth': '1990-01-01'
        }, db_path)

        # Verify update
        updated_customer = get_customer(customer_id, db_path)
        assert updated_customer['phone'] == '0987654321'

        # Delete the customer
        delete_customer(customer_id, db_path)
        deleted_customer = get_customer(customer_id, db_path)
        assert deleted_customer is None

        print("Customer CRUD test passed successfully!")
    finally:
        # Clean up
        os.unlink(db_path)


def test_policy_creation():
    # Create a temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    db_path = temp_db.name

    try:
        # Setup database
        setup_database(db_path)

        # Create a customer first
        customer_id = create_customer({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'date_of_birth': '1990-01-01',
            'password': 'securepassword123'
        }, db_path)

        # Create a policy
        policy_id = create_policy({
            'customer_id': customer_id,
            'policy_number': 'POL123',
            'policy_type': POLICY_TYPES['AUTO'],
            'start_date': '2024-01-01',
            'end_date': '2025-01-01',
            'premium_amount': 1000.00,
            'coverage_details': 'Full coverage',
            'status': 'active'
        }, db_path)
        assert policy_id is not None

        print("Policy creation test passed successfully!")
    finally:
        # Clean up
        os.unlink(db_path)


def test_claim_creation():
    # Create a temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    db_path = temp_db.name

    try:
        # Setup database
        setup_database(db_path)

        # Create a customer and policy first
        customer_id = create_customer({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'date_of_birth': '1990-01-01',
            'password': 'securepassword123'
        }, db_path)

        policy_id = create_policy({
            'customer_id': customer_id,
            'policy_number': 'POL123',
            'policy_type': POLICY_TYPES['AUTO'],
            'start_date': '2024-01-01',
            'end_date': '2025-01-01',
            'premium_amount': 1000.00,
            'coverage_details': 'Full coverage',
            'status': 'active'
        }, db_path)

        # Create a claim
        claim_id = create_claim({
            'policy_id': policy_id,
            'claim_number': 'CLM123',
            'claim_type': 'auto',
            'description': 'Car accident',
            'incident_date': '2024-01-15',
            'claim_date': '2024-01-16',
            'status': CLAIM_STATUSES['PENDING'],
            'estimated_amount': 5000.00
        }, db_path)
        assert claim_id is not None

        print("Claim creation test passed successfully!")
    finally:
        # Clean up
        os.unlink(db_path)


if __name__ == '__main__':
    print("Running tests...")
    test_customer_crud()
    test_policy_creation()
    test_claim_creation()
    print("All tests completed!")