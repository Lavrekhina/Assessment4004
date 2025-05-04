import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, timedelta
import os
import logging
from database.db import Database, UserRole
from database.reports import ReportGenerator
from tkcalendar import DateEntry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsuranceSystem:
    def __init__(self):
        self.db = Database()
        self.report_generator = ReportGenerator(self.db)
        self.current_user = None
        self.setup_login_window()

    def setup_login_window(self):
        """Create the login window"""
        self.login_window = tk.Tk()
        self.login_window.title("Global Insurance System - Login")
        self.login_window.geometry("400x300")
        self.login_window.configure(bg="#f0f0f0")

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#2196F3")
        style.configure("TLabel", padding=6, background="#f0f0f0")
        style.configure("TEntry", padding=6)

        # Title
        title_label = ttk.Label(
            self.login_window,
            text="Global Insurance System",
            font=("Helvetica", 16, "bold"),
            background="#f0f0f0"
        )
        title_label.pack(pady=20)

        # Login frame
        login_frame = ttk.Frame(self.login_window, style="TFrame")
        login_frame.pack(pady=20, padx=20, fill="x")

        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=0, column=1, sticky="ew", pady=5)

        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # Login button
        login_button = ttk.Button(
            self.login_window,
            text="Login",
            command=self.login,
            style="TButton"
        )
        login_button.pack(pady=20)

        # Configure grid weights
        login_frame.columnconfigure(1, weight=1)

    def login(self):
        """Handle login"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        user_info = self.db.verify_user(username, password)
        if user_info:
            self.current_user = {
                "username": username,
                "role": user_info["role"],
                "branch_id": user_info["branch_id"]
            }
            self.login_window.destroy()
            self.setup_main_window()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def setup_main_window(self):
        """Create the main application window"""
        self.main_window = tk.Tk()
        self.main_window.title(f"Global Insurance System - {self.current_user['role'].title()}")
        self.main_window.geometry("1200x800")
        self.main_window.configure(bg="#f0f0f0")

        # Create menu bar
        self.create_menu_bar()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_window)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create tabs
        self.customers_tab = ttk.Frame(self.notebook)
        self.policies_tab = ttk.Frame(self.notebook)
        self.claims_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.customers_tab, text="Customers")
        self.notebook.add(self.policies_tab, text="Policies")
        self.notebook.add(self.claims_tab, text="Claims")
        self.notebook.add(self.reports_tab, text="Reports")

        # Setup each tab
        self.setup_customers_tab()
        self.setup_policies_tab()
        self.setup_claims_tab()
        self.setup_reports_tab()

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.main_window)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.main_window.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.main_window.config(menu=menubar)

    def setup_customers_tab(self):
        """Setup the customers tab"""
        # Search frame
        search_frame = ttk.Frame(self.customers_tab)
        search_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky='ew')

        ttk.Label(search_frame, text="Search by Name :").pack(side='left', padx=5)
        self.customer_search_var = tk.StringVar()
        self.customer_search_var.trace('w', self.filter_customers)
        search_entry = ttk.Entry(search_frame, textvariable=self.customer_search_var)
        search_entry.pack(side='left', padx=5, fill='x', expand=True)

        # Filter frame
        filter_frame = ttk.Frame(self.customers_tab)
        filter_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')

        ttk.Label(filter_frame, text="Filter by:").pack(side='left', padx=5)
        self.customer_filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.customer_filter_var,
                                    values=['All', 'With Policies', 'Without Policies'],
                                    state='readonly')
        filter_combo.pack(side='left', padx=5)
        filter_combo.set('All')
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_customers())

        # Clear filter button
        ttk.Button(filter_frame, text="Clear Filter",
                   command=self.clear_customers_filter).pack(side='left', padx=5)

        # Customer form
        form_frame = ttk.LabelFrame(self.customers_tab, text="New Customer")
        form_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky='ew')

        # Form fields
        row = 0
        # First Name
        ttk.Label(form_frame, text="First Name:*").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.first_name_entry = ttk.Entry(form_frame)
        self.first_name_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')

        # Last Name
        row += 1
        ttk.Label(form_frame, text="Last Name:*").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.last_name_entry = ttk.Entry(form_frame)
        self.last_name_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')

        # Email
        row += 1
        ttk.Label(form_frame, text="Email:*").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')

        # Phone
        row += 1
        ttk.Label(form_frame, text="Phone:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.phone_entry = ttk.Entry(form_frame)
        self.phone_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')

        # Address
        row += 1
        ttk.Label(form_frame, text="Address:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.address_entry = ttk.Entry(form_frame)
        self.address_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')

        # Date of Birth
        row += 1
        ttk.Label(form_frame, text="Date of Birth (YYYY-MM-DD):").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.dob_entry = ttk.Entry(form_frame)
        self.dob_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')

        # SSN
        row += 1
        ttk.Label(form_frame, text="SSN (XXX-XX-XXXX):").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.ssn_entry = ttk.Entry(form_frame)
        self.ssn_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')

        # Required fields note
        row += 1
        ttk.Label(form_frame, text="* Required fields", font=('Helvetica', 8, 'italic')).grid(
            row=row, column=0, columnspan=2, pady=(0, 5), sticky='w')

        # Create button
        row += 1
        ttk.Button(form_frame, text="Create Customer",
                   command=self.create_customer).grid(row=row, column=0, columnspan=2, pady=10)

        # Configure form grid
        form_frame.columnconfigure(1, weight=1)

        # Customer list
        list_frame = ttk.LabelFrame(self.customers_tab, text="Customer List")
        list_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky='nsew')

        # Treeview for customer list
        self.customer_tree = ttk.Treeview(list_frame,
                                          columns=("ID", "First Name", "Last Name", "Email", "Phone", "Address", "DOB",
                                                   "Created At"),
                                          show="headings",
                                          selectmode="browse")

        # Define column headings and widths
        columns = [
            ("ID", 50),
            ("First Name", 100),
            ("Last Name", 100),
            ("Email", 150),
            ("Phone", 100),
            ("Address", 200),
            ("DOB", 100),
            ("Created At", 150)
        ]

        for col, width in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=width)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)

        # Grid the treeview and scrollbar
        self.customer_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Configure list frame grid
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Configure customers tab grid
        self.customers_tab.columnconfigure(0, weight=1)
        self.customers_tab.rowconfigure(3, weight=1)

        # Refresh customer list
        self.refresh_customers()

    def setup_policies_tab(self):
        """Setup the policies tab"""
        # Search and filter frame
        filter_frame = ttk.Frame(self.policies_tab)
        filter_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky='ew')

        # Search
        ttk.Label(filter_frame, text="Search by Policy Type:").pack(side='left', padx=5)
        self.policy_search_var = tk.StringVar()
        self.policy_search_var.trace('w', self.filter_policies)
        search_entry = ttk.Entry(filter_frame, textvariable=self.policy_search_var)
        search_entry.pack(side='left', padx=5, fill='x', expand=True)

        # Filter by type
        ttk.Label(filter_frame, text="Type:").pack(side='left', padx=5)
        self.policy_type_filter_var = tk.StringVar()
        type_combo = ttk.Combobox(filter_frame, textvariable=self.policy_type_filter_var,
                                  values=['All'] + ['AUTO', 'HOME', 'LIFE', 'HEALTH', 'TRAVEL', 'PET', 'BUSINESS'],
                                  state='readonly')
        type_combo.pack(side='left', padx=5)
        type_combo.set('All')
        type_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_policies())

        # Filter by status
        ttk.Label(filter_frame, text="Status:").pack(side='left', padx=5)
        self.policy_status_filter_var = tk.StringVar()
        status_combo = ttk.Combobox(filter_frame, textvariable=self.policy_status_filter_var,
                                    values=['All', 'active', 'inactive', 'cancelled', 'expired'],
                                    state='readonly')
        status_combo.pack(side='left', padx=5)
        status_combo.set('All')
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_policies())

        # Clear filter button
        ttk.Button(filter_frame, text="Clear Filter",
                   command=self.clear_policies_filter).pack(side='left', padx=5)

        # Policy form
        ttk.Label(self.policies_tab, text="New Policy").grid(row=1, column=0, columnspan=2, pady=10)

        # Customer selection
        ttk.Label(self.policies_tab, text="Customer:").grid(row=2, column=0, padx=5, pady=5)
        self.policy_customer_var = tk.StringVar()
        self.policy_customer_combo = ttk.Combobox(self.policies_tab,
                                                  textvariable=self.policy_customer_var,
                                                  state="readonly")
        self.policy_customer_combo.grid(row=2, column=1, padx=5, pady=5)

        # Policy type
        ttk.Label(self.policies_tab, text="Policy Type:").grid(row=3, column=0, padx=5, pady=5)
        self.policy_type_var = tk.StringVar()
        policy_types = ['AUTO', 'HOME', 'LIFE', 'HEALTH', 'TRAVEL', 'PET', 'BUSINESS']
        self.policy_type_combo = ttk.Combobox(self.policies_tab,
                                              textvariable=self.policy_type_var,
                                              values=policy_types,
                                              state="readonly")
        self.policy_type_combo.grid(row=3, column=1, padx=5, pady=5)
        self.policy_type_combo.set(policy_types[0])

        # Premium
        ttk.Label(self.policies_tab, text="Premium:").grid(row=4, column=0, padx=5, pady=5)
        self.premium_entry = ttk.Entry(self.policies_tab)
        self.premium_entry.grid(row=4, column=1, padx=5, pady=5)

        # Coverage limit
        ttk.Label(self.policies_tab, text="Coverage Limit:").grid(row=5, column=0, padx=5, pady=5)
        self.coverage_limit_entry = ttk.Entry(self.policies_tab)
        self.coverage_limit_entry.grid(row=5, column=1, padx=5, pady=5)

        # Status
        ttk.Label(self.policies_tab, text="Status:").grid(row=6, column=0, padx=5, pady=5)
        self.policy_status_var = tk.StringVar()
        status_combo = ttk.Combobox(self.policies_tab,
                                    textvariable=self.policy_status_var,
                                    values=['active', 'inactive', 'cancelled', 'expired'],
                                    state='readonly')
        status_combo.grid(row=6, column=1, padx=5, pady=5)
        status_combo.set('active')

        # Create button
        ttk.Button(self.policies_tab, text="Create Policy",
                   command=self.create_policy).grid(row=7, column=0, columnspan=2, pady=10)

        # Policy list
        self.policy_tree = ttk.Treeview(self.policies_tab,
                                        columns=("ID", "Customer", "Type", "Premium", "Coverage", "Status"),
                                        show="headings")
        self.policy_tree.grid(row=8, column=0, columnspan=2, padx=5, pady=5)
        self.policy_tree.heading("ID", text="ID")
        self.policy_tree.heading("Customer", text="Customer")
        self.policy_tree.heading("Type", text="Type")
        self.policy_tree.heading("Premium", text="Premium")
        self.policy_tree.heading("Coverage", text="Coverage")
        self.policy_tree.heading("Status", text="Status")

        # Refresh customer list in policy tab
        self.refresh_policy_customers()

        # Refresh policies list
        self.refresh_policies()

    def setup_claims_tab(self):
        """Setup the claims tab"""
        # Search and filter frame
        filter_frame = ttk.Frame(self.claims_tab)
        filter_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky='ew')

        # Search
        ttk.Label(filter_frame, text="Search by ID:").pack(side='left', padx=5)
        self.claim_search_var = tk.StringVar()
        self.claim_search_var.trace('w', self.filter_claims)
        search_entry = ttk.Entry(filter_frame, textvariable=self.claim_search_var)
        search_entry.pack(side='left', padx=5, fill='x', expand=True)

        # Filter by status
        ttk.Label(filter_frame, text="Status:").pack(side='left', padx=5)
        self.claim_status_filter_var = tk.StringVar()
        status_combo = ttk.Combobox(filter_frame, textvariable=self.claim_status_filter_var,
                                    values=['All', 'pending', 'approved', 'rejected', 'paid'],
                                    state='readonly')
        status_combo.pack(side='left', padx=5)
        status_combo.set('All')
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_claims())

        # Clear filter button
        ttk.Button(filter_frame, text="Clear Filter",
                   command=self.clear_claims_filter).pack(side='left', padx=5)

        # Claim form
        form_frame = ttk.LabelFrame(self.claims_tab, text="New Claim")
        form_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # Policy selection
        ttk.Label(form_frame, text="Policy:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.claim_policy_var = tk.StringVar()
        self.claim_policy_combo = ttk.Combobox(form_frame,
                                               textvariable=self.claim_policy_var,
                                               state="readonly")
        self.claim_policy_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Claim Date
        ttk.Label(form_frame, text="Claim Date:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.claim_date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2)
        self.claim_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Incident Date
        ttk.Label(form_frame, text="Incident Date:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.incident_date_entry = DateEntry(form_frame, width=12, background='darkblue',
                                             foreground='white', borderwidth=2)
        self.incident_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # Incident Time
        ttk.Label(form_frame, text="Incident Time:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        time_frame = ttk.Frame(form_frame)
        time_frame.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        # Hours (1-12)
        self.hours_var = tk.StringVar()
        hours = ttk.Combobox(time_frame, textvariable=self.hours_var, width=3, state="readonly")
        hours['values'] = [f"{i:02d}" for i in range(1, 13)]
        hours.set("12")
        hours.pack(side="left", padx=2)

        ttk.Label(time_frame, text=":").pack(side="left")

        # Minutes (00-59)
        self.minutes_var = tk.StringVar()
        minutes = ttk.Combobox(time_frame, textvariable=self.minutes_var, width=3, state="readonly")
        minutes['values'] = [f"{i:02d}" for i in range(60)]
        minutes.set("00")
        minutes.pack(side="left", padx=2)

        # AM/PM
        self.period_var = tk.StringVar()
        period = ttk.Combobox(time_frame, textvariable=self.period_var, width=3, state="readonly")
        period['values'] = ["AM", "PM"]
        period.set("AM")
        period.pack(side="left", padx=2)

        # Incident Location
        ttk.Label(form_frame, text="Incident Location:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.incident_location_entry = ttk.Entry(form_frame)
        self.incident_location_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.description_entry = ttk.Entry(form_frame)
        self.description_entry.grid(row=5, column=1, padx=5, pady=5, sticky='ew')

        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=6, column=1, padx=5, pady=5, sticky='ew')

        # Status
        ttk.Label(form_frame, text="Status:").grid(row=7, column=0, padx=5, pady=5, sticky='w')
        self.claim_status_var = tk.StringVar()
        self.claim_status_combo = ttk.Combobox(form_frame,
                                               textvariable=self.claim_status_var,
                                               values=['pending', 'approved', 'rejected', 'paid'],
                                               state='readonly')
        self.claim_status_combo.grid(row=7, column=1, padx=5, pady=5, sticky='ew')
        self.claim_status_combo.set('pending')  # Set initial selection

        # Create button
        ttk.Button(form_frame, text="Create Claim",
                   command=self.create_claim).grid(row=8, column=0, columnspan=2, pady=10)

        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

        # Claims Tree
        tree_frame = ttk.LabelFrame(self.claims_tab, text="Claims List")
        tree_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.claim_tree = ttk.Treeview(tree_frame, columns=(
            "ID", "Policy ID", "Claim Number", "Claim Date", "Incident Date",
            "Incident Time", "Incident Location", "Description", "Amount", "Status"
        ), show="headings")
        self.claim_tree.grid(row=0, column=0, sticky='nsew')

        # Configure columns
        self.claim_tree.heading("ID", text="ID")
        self.claim_tree.heading("Policy ID", text="Policy ID")
        self.claim_tree.heading("Claim Number", text="Claim Number")
        self.claim_tree.heading("Claim Date", text="Claim Date")
        self.claim_tree.heading("Incident Date", text="Incident Date")
        self.claim_tree.heading("Incident Time", text="Incident Time")
        self.claim_tree.heading("Incident Location", text="Incident Location")
        self.claim_tree.heading("Description", text="Description")
        self.claim_tree.heading("Amount", text="Amount")
        self.claim_tree.heading("Status", text="Status")

        # Set column widths
        self.claim_tree.column("ID", width=50)
        self.claim_tree.column("Policy ID", width=70)
        self.claim_tree.column("Claim Number", width=100)
        self.claim_tree.column("Claim Date", width=100)
        self.claim_tree.column("Incident Date", width=100)
        self.claim_tree.column("Incident Time", width=100)
        self.claim_tree.column("Incident Location", width=150)
        self.claim_tree.column("Description", width=200)
        self.claim_tree.column("Amount", width=100)
        self.claim_tree.column("Status", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.claim_tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.claim_tree.configure(yscrollcommand=scrollbar.set)

        # Add right-click menu for status updates
        self.claim_tree.bind("<Button-3>", self.show_claim_context_menu)

        # Configure grid weights for the main tab
        self.claims_tab.columnconfigure(0, weight=1)
        self.claims_tab.rowconfigure(2, weight=1)

        # Refresh policy list in claims tab
        self.refresh_claim_policies()

        # Refresh claims list
        self.refresh_claims()

    def setup_reports_tab(self):
        """Setup the reports tab"""
        # Report type selection
        ttk.Label(self.reports_tab, text="Report Type:").grid(row=0, column=0, padx=5, pady=5)
        self.report_type_var = tk.StringVar()
        report_types = [
            "Claims by Status",
            "Claims by Policy Type",
            "Financial Summary"
        ]
        self.report_type_combo = ttk.Combobox(self.reports_tab,
                                              textvariable=self.report_type_var,
                                              values=report_types,
                                              state="readonly")
        self.report_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.report_type_combo.set(report_types[0])

        # Generate and Export buttons
        button_frame = ttk.Frame(self.reports_tab)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(button_frame, text="Generate Report",
                   command=self.generate_report).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export to CSV",
                   command=self.export_report).pack(side='left', padx=5)

        # Report display
        self.report_text = tk.Text(self.reports_tab, height=20, width=80)
        self.report_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def filter_customers(self, *args):
        """Filter customers based on search and filter criteria"""
        search_term = self.customer_search_var.get().lower()
        filter_type = self.customer_filter_var.get()

        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)

        # Get and filter customers
        customers = self.db.get_customers()
        for customer in customers:
            customer_id = customer[0]
            first_name = customer[1]
            last_name = customer[2]
            email = customer[3]
            phone = customer[4]
            address = customer[5]
            dob = customer[6]
            created_at = customer[8]

            name = f"{first_name} {last_name}".lower()

            # Apply search filter
            if search_term and search_term not in name and search_term not in email.lower():
                continue

            # Apply type filter
            if filter_type == 'With Policies':
                policies = self.db.get_policies(customer_id)
                if not policies:
                    continue
            elif filter_type == 'Without Policies':
                policies = self.db.get_policies(customer_id)
                if policies:
                    continue

            self.customer_tree.insert("", "end", values=(
                customer_id,
                first_name,
                last_name,
                email,
                phone,
                address,
                dob,
                created_at
            ))

    def filter_policies(self, *args):
        """Filter policies based on search and filter criteria"""
        search_term = self.policy_search_var.get().lower()
        type_filter = self.policy_type_filter_var.get()
        status_filter = self.policy_status_filter_var.get()

        # Clear existing items
        for item in self.policy_tree.get_children():
            self.policy_tree.delete(item)

        # Get and filter policies
        policies = self.db.get_policies()
        for policy in policies:
            try:
                policy_id = policy[0]
                customer_id = policy[1]
                policy_number = policy[2]
                policy_type = policy[3]
                premium = float(policy[6])
                coverage = float(policy[7])
                status = policy[8]

                # Get customer information
                customers = self.db.get_customers()
                customer = next((c for c in customers if c[0] == customer_id), None)
                if not customer:
                    continue

                # Apply search filter
                if search_term and search_term not in policy_number.lower():
                    continue

                # Apply type filter
                if type_filter != 'All' and policy_type != type_filter:
                    continue

                # Apply status filter
                if status_filter != 'All' and status != status_filter:
                    continue

                self.policy_tree.insert("", "end", values=(
                    policy_id,
                    f"{customer[1]} {customer[2]}",
                    policy_type,
                    f"£{premium:.2f}",
                    f"£{coverage:.2f}",
                    status
                ))
            except (IndexError, ValueError) as e:
                logger.error(f"Error processing policy: {e}")
                continue

    def filter_claims(self, *args):
        """Filter claims based on search and filter criteria"""
        search_term = self.claim_search_var.get().lower()
        status_filter = self.claim_status_filter_var.get()

        # Clear existing items
        for item in self.claim_tree.get_children():
            self.claim_tree.delete(item)

        # Get and filter claims
        claims = self.db.get_claims()
        for claim in claims:
            try:
                # Access claim fields using dictionary keys
                claim_id = claim['id']
                policy_id = claim['policy_id']
                claim_number = claim['claim_number']
                claim_date = claim['claim_date']
                incident_date = claim['incident_date']
                incident_time = claim['incident_time']
                incident_location = claim['incident_location']
                description = claim['description']
                amount = float(claim['claim_amount'])
                status = claim['status']

                # Get policy information
                policies = self.db.get_policies()
                policy = next((p for p in policies if p[0] == policy_id), None)
                if not policy:
                    continue

                # Apply search filter - search in claim number, description, and location
                if search_term:
                    search_text = f"{claim_number} {description} {incident_location}".lower()
                    if search_term not in search_text:
                        continue

                # Apply status filter
                if status_filter != 'All' and status != status_filter:
                    continue

                self.claim_tree.insert("", "end", values=(
                    claim_id,
                    policy_id,
                    claim_number,
                    claim_date,
                    incident_date,
                    incident_time,
                    incident_location,
                    description,
                    f"£{amount:.2f}",
                    status
                ))
            except (KeyError, ValueError) as e:
                logger.error(f"Error processing claim {claim}: {e}")
                continue

    def create_customer(self):
        """Create a new customer"""
        try:
            # Get values from the main form
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            email = self.email_entry.get()
            phone = self.phone_entry.get()
            address = self.address_entry.get()
            dob = self.dob_entry.get()
            ssn = self.ssn_entry.get()

            # Validate required fields
            if not first_name or not last_name or not email:
                messagebox.showerror("Error", "First Name, Last Name, and Email are required fields")
                return

            # Create the customer
            customer_id = self.db.create_customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                dob=dob,
                ssn=ssn
            )

            if customer_id:
                messagebox.showinfo("Success", "Customer created successfully")
                # Clear form fields
                self.first_name_entry.delete(0, tk.END)
                self.last_name_entry.delete(0, tk.END)
                self.email_entry.delete(0, tk.END)
                self.phone_entry.delete(0, tk.END)
                self.address_entry.delete(0, tk.END)
                self.dob_entry.delete(0, tk.END)
                self.ssn_entry.delete(0, tk.END)
                # Refresh the customer list and policy customer dropdown
                self.refresh_customers()
                self.refresh_policy_customers()
            else:
                messagebox.showerror("Error", "Failed to create customer")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_policy(self):
        """Create a new policy"""
        try:
            # Get values from form
            customer_id = int(self.policy_customer_var.get().split(":")[0])
            policy_type = self.policy_type_var.get()
            premium = float(self.premium_entry.get())
            coverage_limit = float(self.coverage_limit_entry.get())
            status = self.policy_status_var.get()

            # Generate policy number
            policy_number = f"POL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Set dates
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

            # Create the policy
            policy_id = self.db.create_policy(
                customer_id=customer_id,
                policy_type=policy_type,
                policy_number=policy_number,
                start_date=start_date,
                end_date=end_date,
                premium=premium,
                coverage_limit=coverage_limit,
                payment_schedule='Monthly',
                beneficiary_info='Self',
                exclusions='None'
            )

            if policy_id:
                messagebox.showinfo("Success", "Policy created successfully")
                self.refresh_policies()

                # Clear form fields
                self.premium_entry.delete(0, tk.END)
                self.coverage_limit_entry.delete(0, tk.END)
                self.policy_status_var.set('active')
            else:
                messagebox.showerror("Error", "Failed to create policy")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def create_claim(self):
        """Create a new claim"""
        try:
            # Get values from form
            policy_id = int(self.claim_policy_var.get().split(":")[0])
            claim_date = self.claim_date_entry.get_date().strftime('%Y-%m-%d')
            incident_date = self.incident_date_entry.get_date().strftime('%Y-%m-%d')

            # Format time in 24-hour format
            hours = int(self.hours_var.get())
            minutes = self.minutes_var.get()
            period = self.period_var.get()

            if period == "PM" and hours < 12:
                hours += 12
            elif period == "AM" and hours == 12:
                hours = 0

            incident_time = f"{hours:02d}:{minutes}:00"

            incident_location = self.incident_location_entry.get()
            description = self.description_entry.get()
            amount = float(self.amount_entry.get())
            status = self.claim_status_combo.get()  # Get status directly from combo box

            # Log the status we're about to set
            logger.info(f"Creating claim with status: {status}")

            # Validate required fields
            if not incident_location or not description or not amount:
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            # Create the claim
            claim_id = self.db.create_claim(
                policy_id=policy_id,
                claim_date=claim_date,
                incident_date=incident_date,
                incident_time=incident_time,
                incident_location=incident_location,
                description=description,
                claim_amount=amount,
                status=status
            )

            if claim_id:
                messagebox.showinfo("Success", "Claim created successfully")
                self.refresh_claims()

                # Clear form fields
                self.incident_location_entry.delete(0, tk.END)
                self.description_entry.delete(0, tk.END)
                self.amount_entry.delete(0, tk.END)
                # Keep the current status selection
            else:
                messagebox.showerror("Error", "Failed to create claim")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def refresh_customers(self):
        """Refresh the customers list"""
        try:
            customers = self.db.get_all_customers()
            self.customer_tree.delete(*self.customer_tree.get_children())
            for customer in customers:
                self.customer_tree.insert("", "end", values=(
                    customer[0],  # ID
                    customer[1],  # First Name
                    customer[2],  # Last Name
                    customer[3],  # Email
                    customer[4],  # Phone
                    customer[5],  # Address
                    customer[6],  # Date of Birth
                    customer[8]  # Created At
                ))
        except Exception as e:
            logger.error(f"Error refreshing customers: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def refresh_policy_customers(self):
        """Refresh the customer list in the policy tab"""
        try:
            # Clear existing items
            self.policy_customer_combo['values'] = []

            # Get customers from database
            customers = self.db.get_customers()
            customer_list = [f"{c[0]}: {c[1]} {c[2]}" for c in customers]
            self.policy_customer_combo['values'] = customer_list
            if customer_list:
                self.policy_customer_combo.set(customer_list[0])
        except Exception as e:
            logger.error(f"Error refreshing policy customers: {e}")
            messagebox.showerror("Error", f"Failed to refresh customers: {str(e)}")

    def refresh_policies(self):
        """Refresh the policies list"""
        try:
            policies = self.db.get_all_policies()
            self.policy_tree.delete(*self.policy_tree.get_children())
            for policy in policies:
                # Get customer information
                customer = self.db.get_customer(policy[1])  # policy[1] is customer_id
                customer_name = f"{customer[1]} {customer[2]}" if customer else "Unknown"

                self.policy_tree.insert("", "end", values=(
                    policy[0],  # policy_id
                    customer_name,  # customer name
                    policy[3],  # policy_type
                    f"£{float(policy[6]):.2f}",  # premium
                    f"£{float(policy[7]):.2f}",  # coverage_limit
                    policy[8]  # status
                ))
        except Exception as e:
            logger.error(f"Error refreshing policies: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def refresh_claim_policies(self):
        """Refresh the policy list in the claims tab"""
        try:
            # Clear existing items
            self.claim_policy_combo['values'] = []

            # Get policies from database
            policies = self.db.get_policies()
            policy_list = [f"{p[0]}: {p[2]} - £{p[6]:.2f}" for p in policies]
            self.claim_policy_combo['values'] = policy_list
            if policy_list:
                self.claim_policy_combo.set(policy_list[0])
        except Exception as e:
            logger.error(f"Error refreshing claim policies: {e}")
            messagebox.showerror("Error", f"Failed to refresh policies: {str(e)}")

    def refresh_claims(self):
        """Refresh the claims list"""
        try:
            # Clear existing items
            for item in self.claim_tree.get_children():
                self.claim_tree.delete(item)

            # Get all claims
            claims = self.db.get_claims()
            if claims is None:
                logger.error("Failed to retrieve claims from database")
                return

            # Insert claims into tree
            for claim in claims:
                try:
                    # Access claim fields using dictionary keys
                    claim_id = claim.get('id')
                    policy_id = claim.get('policy_id')
                    claim_number = claim.get('claim_number')
                    claim_date = claim.get('claim_date')
                    incident_date = claim.get('incident_date')
                    incident_time = claim.get('incident_time')
                    incident_location = claim.get('incident_location')
                    description = claim.get('description')
                    amount = float(claim.get('claim_amount', 0))
                    status = claim.get('status', 'pending')

                    # Log the status we're about to display
                    logger.info(f"Displaying claim {claim_id} with status: {status}")

                    self.claim_tree.insert("", "end", values=(
                        claim_id, policy_id, claim_number, claim_date, incident_date,
                        incident_time, incident_location, description, f"£{amount:.2f}", status
                    ))
                except (KeyError, ValueError) as e:
                    logger.error(f"Error processing claim {claim}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error refreshing claims: {e}")
            messagebox.showerror("Error", "Failed to refresh claims list")

    def generate_report(self):
        """Generate a report"""
        try:
            report_type = self.report_type_var.get()
            if not report_type:
                messagebox.showwarning("Warning", "Please select a report type")
                return

            # Initialize report generator
            report_gen = ReportGenerator(self.db)

            # Generate report based on type
            if report_type == "Claims by Status":
                report_data = report_gen.get_claims_by_status()

            elif report_type == "Claims by Policy Type":
                report_data = report_gen.get_claims_by_policy_type()

            elif report_type == "Financial Summary":
                report_data = report_gen.get_financial_summary()

            # Display the report
            if report_data:
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, report_data)
            else:
                messagebox.showinfo("Info", "No data available for the selected report type")

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def export_report(self):
        """Export the current report to a file"""
        try:
            # Get filename from user
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not filename:
                return

            # Get current report content
            report_content = self.report_text.get(1.0, tk.END)
            if not report_content.strip():
                messagebox.showerror("Error", "No report data to export")
                return

            # Write report to file
            with open(filename, "w") as f:
                f.write(report_content)

            messagebox.showinfo("Success", f"Report exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_claim_context_menu(self, event):
        """Show context menu for claim status update"""
        # Select the item under the cursor
        item = self.claim_tree.identify_row(event.y)
        if not item:
            return

        self.claim_tree.selection_set(item)

        # Create menu
        menu = tk.Menu(self.claims_tab, tearoff=0)
        menu.add_command(label="Update Status", command=self.update_claim_status)
        menu.post(event.x_root, event.y_root)

    def update_claim_status(self):
        """Update the status of a selected claim"""
        try:
            # Get selected claim
            selection = self.claim_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a claim to update")
                return

            item = selection[0]
            claim_id = self.claim_tree.item(item)['values'][0]
            current_status = self.claim_tree.item(item)['values'][9]

            # Create status selection dialog
            dialog = tk.Toplevel(self.main_window)
            dialog.title("Update Claim Status")
            dialog.geometry("300x150")
            dialog.transient(self.main_window)
            dialog.grab_set()

            # Status selection
            ttk.Label(dialog, text="Select new status:").pack(pady=10)
            status_var = tk.StringVar(value=current_status)
            status_combo = ttk.Combobox(dialog, textvariable=status_var,
                                        values=['pending', 'approved', 'rejected', 'paid'],
                                        state='readonly')
            status_combo.pack(pady=10)

            def on_update():
                new_status = status_var.get()
                if new_status != current_status:
                    if self.db.update_claim_status(claim_id, new_status):
                        messagebox.showinfo("Success", "Claim status updated successfully")
                        self.refresh_claims()
                    else:
                        messagebox.showerror("Error", "Failed to update claim status")
                dialog.destroy()

            ttk.Button(dialog, text="Update", command=on_update).pack(pady=10)
        except Exception as e:
            logger.error(f"Error updating claim status: {e}")
            messagebox.showerror("Error", "Failed to update claim status")

    def update_policy_status(self):
        """Update the status of a selected policy"""
        selected = self.policy_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a policy first")
            return

        policy_id = self.policy_tree.item(selected[0])['values'][0]
        policy = self.db.get_policy(policy_id)
        if not policy:
            messagebox.showerror("Error", "Policy not found")
            return

        # Create a dialog for status update
        dialog = tk.Toplevel(self.main_window)
        dialog.title("Update Policy Status")
        dialog.geometry("300x200")

        # Status options
        status_var = tk.StringVar(value=policy[8])  # Current status
        status_frame = ttk.LabelFrame(dialog, text="New Status")
        status_frame.pack(padx=10, pady=10, fill="x")

        statuses = ["active", "inactive", "cancelled", "expired"]
        for status in statuses:
            ttk.Radiobutton(status_frame, text=status.capitalize(),
                            value=status, variable=status_var).pack(anchor="w")

        # Update button
        def on_update():
            try:
                self.db.update_policy_status(policy_id, status_var.get())
                self.refresh_policies()
                dialog.destroy()
                messagebox.showinfo("Success", "Policy status updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status: {str(e)}")

        ttk.Button(dialog, text="Update Status", command=on_update).pack(pady=10)

    def delete_claim(self):
        """Delete a selected claim"""
        selected = self.claim_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a claim first")
            return

        claim_id = self.claim_tree.item(selected[0])['values'][0]
        claim = self.db.get_claim(claim_id)
        if not claim:
            messagebox.showerror("Error", "Claim not found")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete claim #{claim[2]}?"):
            return

        try:
            self.db.delete_claim(claim_id)
            self.refresh_claims()
            messagebox.showinfo("Success", "Claim deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete claim: {str(e)}")

    def delete_policy(self):
        """Delete a selected policy"""
        selected = self.policy_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a policy first")
            return

        policy_id = self.policy_tree.item(selected[0])['values'][0]
        policy = self.db.get_policy(policy_id)
        if not policy:
            messagebox.showerror("Error", "Policy not found")
            return

        # Check if policy has claims
        claims = self.db.get_claims_by_policy(policy_id)
        if claims:
            if not messagebox.askyesno("Warning",
                                       f"This policy has {len(claims)} associated claims. "
                                       "Deleting the policy will also delete all claims. "
                                       "Are you sure you want to continue?"):
                return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete policy #{policy[2]}?"):
            return

        try:
            self.db.delete_policy(policy_id)
            self.refresh_policies()
            self.refresh_claims()  # Refresh claims as they might be affected
            messagebox.showinfo("Success", "Policy deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete policy: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "Global Insurance System\nVersion 1.0\n\nA comprehensive insurance management system."
        )

    def clear_claims_filter(self):
        """Clear all claim filters"""
        # Clear search
        self.claim_search_var.set("")

        # Clear status filter
        self.claim_status_filter_var.set("All")

        # Refresh claims list
        self.refresh_claims()

    def clear_customers_filter(self):
        """Clear all customer filters"""
        self.customer_search_var.set("")
        self.customer_filter_var.set("All")
        self.filter_customers()

    def clear_policies_filter(self):
        """Clear all policy filters"""
        self.policy_search_var.set("")
        self.policy_type_filter_var.set("All")
        self.policy_status_filter_var.set("All")
        self.filter_policies()

    def run(self):
        """Run the application"""
        self.login_window.mainloop()
        if self.current_user:
            self.main_window.mainloop()


if __name__ == "__main__":
    app = InsuranceSystem()
    app.run()