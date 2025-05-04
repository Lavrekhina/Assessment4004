# Insurance Management System

A Python-based insurance management system with a Tkinter GUI interface and SQLite database backend.

## Features

- User authentication with role-based access control
- Customer management
- Policy management (AUTO, HOME, LIFE, HEALTH, TRAVEL)
- Claims processing
- Payment tracking
- Audit logging

## Setup

1. Clone the repository
2. Install required packages:
   ```bash
   pip install bcrypt
   ```
3. Initialize the database:
   ```bash
   python init_db.py
   ```
4. Run the application:
   ```bash
   python gui/main.py
   ```

## Default Login

- Username: test
- Password: test123
- Role: admin

## Project Structure

```
.
├── database/           # Database operations and models
│   ├── auth.py        # Authentication functions
│   ├── claims.py      # Claims management
│   ├── customers.py   # Customer management
│   ├── policies.py    # Policy management
│   └── __init__.py    # Database initialization
├── gui/               # GUI interface
│   └── main.py        # Main application window
├── init_db.py         # Database initialization script
└── schema.sql         # Database schema
```

## Database Schema

The system uses SQLite with the following main tables:

- users
- customers
- policies
- claims
- payments
- audit_logs

## Development

To modify the database schema:

1. Update schema.sql
2. Delete insurance.db
3. Run init_db.py

To add new features:

1. Add database functions in the appropriate module
2. Update the GUI in gui/main.py
3. Add any necessary audit logging
