import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.claims import create_claim, get_claims_by_status, get_claim_details
from database.policies import create_policy, get_policy_details, get_customer_policies
from database.auth import verify_user


class InsuranceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Insurance Management System")
        self.root.geometry("800x600")

        # Login frame
        self.login_frame = ttk.Frame(root, padding="10")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0)
        self.username = ttk.Entry(self.login_frame)
        self.username.grid(row=0, column=1)

        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0)
        self.password = ttk.Entry(self.login_frame, show="*")
        self.password.grid(row=1, column=1)

        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2)

        # Main frame (initially hidden)
        self.main_frame = ttk.Frame(root, padding="10")

        # Create tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Claims tab
        self.claims_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.claims_frame, text="Claims")
        self.setup_claims_tab()

        # Policies tab
        self.policies_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.policies_frame, text="Policies")
        self.setup_policies_tab()

        # Reports tab
        self.reports_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.reports_frame, text="Reports")
        self.setup_reports_tab()

    def login(self):
        username = self.username.get()
        password = self.password.get()
        role = verify_user(username, password)

        if role:
            self.login_frame.grid_remove()
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def setup_claims_tab(self):
        # Claim form
        ttk.Label(self.claims_frame, text="New Claim").grid(row=0, column=0, columnspan=2)

        ttk.Label(self.claims_frame, text="Policy ID:").grid(row=1, column=0)
        self.policy_id = ttk.Entry(self.claims_frame)
        self.policy_id.grid(row=1, column=1)

        ttk.Label(self.claims_frame, text="Description:").grid(row=2, column=0)
        self.description = ttk.Entry(self.claims_frame)
        self.description.grid(row=2, column=1)

        ttk.Label(self.claims_frame, text="Amount:").grid(row=3, column=0)
        self.amount = ttk.Entry(self.claims_frame)
        self.amount.grid(row=3, column=1)

        ttk.Button(self.claims_frame, text="Submit Claim",
                   command=self.submit_claim).grid(row=4, column=0, columnspan=2)

        # Claims table
        self.claims_tree = ttk.Treeview(self.claims_frame,
                                        columns=("ID", "Policy", "Date", "Amount", "Status"))
        self.claims_tree.grid(row=5, column=0, columnspan=2)
        self.claims_tree.heading("ID", text="ID")
        self.claims_tree.heading("Policy", text="Policy")
        self.claims_tree.heading("Date", text="Date")
        self.claims_tree.heading("Amount", text="Amount")
        self.claims_tree.heading("Status", text="Status")

    def setup_policies_tab(self):
        # Policy form
        ttk.Label(self.policies_frame, text="New Policy").grid(row=0, column=0, columnspan=2)

        ttk.Label(self.policies_frame, text="Customer ID:").grid(row=1, column=0)
        self.customer_id = ttk.Entry(self.policies_frame)
        self.customer_id.grid(row=1, column=1)

        ttk.Label(self.policies_frame, text="Policy Type:").grid(row=2, column=0)
        self.policy_type = ttk.Entry(self.policies_frame)
        self.policy_type.grid(row=2, column=1)

        ttk.Label(self.policies_frame, text="Premium:").grid(row=3, column=0)
        self.premium = ttk.Entry(self.policies_frame)
        self.premium.grid(row=3, column=1)

        ttk.Button(self.policies_frame, text="Create Policy",
                   command=self.create_policy).grid(row=4, column=0, columnspan=2)

        # Policies table
        self.policies_tree = ttk.Treeview(self.policies_frame,
                                          columns=("ID", "Customer", "Type", "Premium", "Status"))
        self.policies_tree.grid(row=5, column=0, columnspan=2)
        self.policies_tree.heading("ID", text="ID")
        self.policies_tree.heading("Customer", text="Customer")
        self.policies_tree.heading("Type", text="Type")
        self.policies_tree.heading("Premium", text="Premium")
        self.policies_tree.heading("Status", text="Status")

    def setup_reports_tab(self):
        # Report options
        ttk.Label(self.reports_frame, text="Generate Report").grid(row=0, column=0)

        self.report_type = ttk.Combobox(self.reports_frame,
                                        values=["Claims by Status", "Policy Summary", "Financial Report"])
        self.report_type.grid(row=0, column=1)

        ttk.Button(self.reports_frame, text="Generate",
                   command=self.generate_report).grid(row=1, column=0, columnspan=2)

        # Report display
        self.report_text = tk.Text(self.reports_frame, height=20, width=60)
        self.report_text.grid(row=2, column=0, columnspan=2)

    def submit_claim(self):
        try:
            claim_id = create_claim(
                1,  # user_id
                int(self.policy_id.get()),
                self.description.get(),
                datetime.now(),
                float(self.amount.get())
            )
            messagebox.showinfo("Success", f"Claim created with ID: {claim_id}")
            self.refresh_claims()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_policy(self):
        try:
            policy_id = create_policy(
                1,  # user_id
                int(self.customer_id.get()),
                self.policy_type.get(),
                datetime.now(),
                datetime.now().replace(year=datetime.now().year + 1),
                float(self.premium.get()),
                100000  # coverage_limit
            )
            messagebox.showinfo("Success", f"Policy created with ID: {policy_id}")
            self.refresh_policies()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_claims(self):
        for item in self.claims_tree.get_children():
            self.claims_tree.delete(item)
        claims = get_claims_by_status(1, "pending")  # user_id
        for claim in claims:
            self.claims_tree.insert("", "end", values=(
                claim["id"],
                claim["policy_id"],
                claim["claim_date"],
                claim["amount"],
                claim["status"]
            ))

    def refresh_policies(self):
        for item in self.policies_tree.get_children():
            self.policies_tree.delete(item)
        policies = get_customer_policies(int(self.customer_id.get()))
        for policy in policies:
            self.policies_tree.insert("", "end", values=(
                policy["id"],
                policy["customer_id"],
                policy["policy_type"],
                policy["premium"],
                policy["status"]
            ))

    def generate_report(self):
        report_type = self.report_type.get()
        self.report_text.delete(1.0, tk.END)

        if report_type == "Claims by Status":
            claims = get_claims_by_status(1, "pending")  # user_id
            for claim in claims:
                self.report_text.insert(tk.END,
                                        f"Claim {claim['id']}: ${claim['amount']} - {claim['status']}\n")
        elif report_type == "Policy Summary":
            policies = get_customer_policies(int(self.customer_id.get()))
            for policy in policies:
                self.report_text.insert(tk.END,
                                        f"Policy {policy['id']}: {policy['policy_type']} - ${policy['premium']}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = InsuranceApp(root)
    root.mainloop()