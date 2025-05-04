-- Users table for authentication and role-based access
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'agent', 'adjuster')),
    branch_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    last_login TEXT,
    is_active BOOLEAN DEFAULT 1
);

-- Branches table for multi-branch support
CREATE TABLE branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- Customers table with enhanced security
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    address TEXT,
    date_of_birth TEXT,
    ssn_encrypted TEXT,  -- Encrypted sensitive data
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- Policies table with comprehensive coverage details
CREATE TABLE policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    policy_type TEXT NOT NULL CHECK(policy_type IN ('AUTO', 'HOME', 'LIFE', 'HEALTH', 'TRAVEL', 'PET', 'BUSINESS')),
    policy_number TEXT UNIQUE NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    premium DECIMAL(10,2) NOT NULL,
    coverage_limit DECIMAL(10,2) NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active', 'inactive', 'cancelled', 'expired')),
    payment_schedule TEXT NOT NULL,
    beneficiary_info TEXT,
    exclusions TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Premium payments table
CREATE TABLE premium_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'completed', 'failed')),
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (policy_id) REFERENCES policies(id)
);

-- Claims table with comprehensive tracking
CREATE TABLE claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    claim_number TEXT UNIQUE NOT NULL,
    claim_date TEXT NOT NULL,
    incident_date TEXT NOT NULL,
    incident_time TEXT NOT NULL,
    incident_location TEXT NOT NULL,
    description TEXT NOT NULL,
    claim_amount DECIMAL(10,2) NOT NULL,
    approved_amount DECIMAL(10,2),
    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected', 'paid')),
    adjuster_id INTEGER,
    resolution_notes TEXT,
    settlement_date TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    updated_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (policy_id) REFERENCES policies(id),
    FOREIGN KEY (adjuster_id) REFERENCES users(id)
);

-- Claim payments table
CREATE TABLE claim_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'completed', 'failed')),
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (claim_id) REFERENCES claims(id)
);

-- Communication logs for tracking all communications
CREATE TABLE communication_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER,
    policy_id INTEGER,
    user_id INTEGER NOT NULL,
    communication_type TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (claim_id) REFERENCES claims(id),
    FOREIGN KEY (policy_id) REFERENCES policies(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Assessment reports for claims
CREATE TABLE assessment_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    adjuster_id INTEGER NOT NULL,
    report_date TEXT NOT NULL,
    findings TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (claim_id) REFERENCES claims(id),
    FOREIGN KEY (adjuster_id) REFERENCES users(id)
);

-- Audit log for tracking all changes
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    user_id INTEGER,
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for better query performance
CREATE INDEX idx_policies_customer_id ON policies(customer_id);
CREATE INDEX idx_claims_policy_id ON claims(policy_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_incident_date ON claims(incident_date);
CREATE INDEX idx_premium_payments_policy_id ON premium_payments(policy_id);
CREATE INDEX idx_claim_payments_claim_id ON claim_payments(claim_id);
CREATE INDEX idx_communication_logs_claim_id ON communication_logs(claim_id);
CREATE INDEX idx_assessment_reports_claim_id ON assessment_reports(claim_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);