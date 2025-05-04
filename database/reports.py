import logging
from datetime import datetime, timedelta
import os
from .db import Database


class ReportGenerator:
    def __init__(self, db: Database):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def get_claims_by_status(self):
        """Get claims grouped by status"""
        try:
            claims = self.db.get_all_claims()
            if not claims:
                return "No claims found"

            status_groups = {}
            for claim in claims:
                status = claim['status']
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(claim)

            report = "Claims by Status Report\n"
            report += "=====================\n\n"

            for status, claims in status_groups.items():
                report += f"Status: {status}\n"
                report += "-" * 50 + "\n"
                for claim in claims:
                    report += f"Claim #{claim['claim_number']} - Amount: £{claim['claim_amount']:.2f}\n"
                report += "\n"

            return report
        except Exception as e:
            self.logger.error(f"Error generating claims by status report: {e}")
            return "Error generating report"

    def get_claims_by_policy_type(self):
        """Get claims grouped by policy type"""
        try:
            claims = self.db.get_all_claims()
            if not claims:
                return "No claims found"

            policy_groups = {}
            for claim in claims:
                policy = self.db.get_policy(claim['policy_id'])
                if not policy:
                    continue

                policy_type = policy['policy_type']
                if policy_type not in policy_groups:
                    policy_groups[policy_type] = []
                policy_groups[policy_type].append(claim)

            report = "Claims by Policy Type Report\n"
            report += "=========================\n\n"

            for policy_type, claims in policy_groups.items():
                report += f"Policy Type: {policy_type}\n"
                report += "-" * 50 + "\n"
                for claim in claims:
                    report += f"Claim #{claim['claim_number']} - Amount: £{claim['claim_amount']:.2f}\n"
                report += "\n"

            return report
        except Exception as e:
            self.logger.error(f"Error generating claims by policy type report: {e}")
            return "Error generating report"

    def get_financial_summary(self):
        """Get financial summary of premiums and claims"""
        try:
            policies = self.db.get_all_policies()
            claims = self.db.get_all_claims()

            if not policies and not claims:
                return "No financial data found"

            total_premiums = sum(policy['premium'] for policy in policies)
            total_claims = sum(claim['claim_amount'] for claim in claims)

            report = "Financial Summary Report\n"
            report += "=====================\n\n"
            report += f"Total Premiums: £{total_premiums:.2f}\n"
            report += f"Total Claims: £{total_claims:.2f}\n"
            report += f"Net Income: £{(total_premiums - total_claims):.2f}\n"

            return report
        except Exception as e:
            self.logger.error(f"Error generating financial summary report: {e}")
            return "Error generating report"

    def export_to_csv(self, data, filename):
        """Export data to CSV file"""
        try:
            if not filename.endswith('.csv'):
                filename += '.csv'

            with open(filename, 'w') as f:
                # Write header
                if data and isinstance(data, list) and data[0]:
                    headers = list(data[0].keys())
                    f.write(','.join(headers) + '\n')

                    # Write data
                    for row in data:
                        values = [str(row.get(header, '')) for header in headers]
                        f.write(','.join(values) + '\n')

            self.logger.info(f"Data exported to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return False

    def get_claim_timeline(self, claim_number):
        """Get timeline for a specific claim"""
        try:
            claim = self.db.get_claim(claim_number)
            if not claim:
                return "Claim not found"

            report = f"Claim Timeline Report - Claim #{claim_number}\n"
            report += "==================================\n\n"
            report += f"Date Filed: {claim['claim_date']}\n"
            report += f"Incident Date: {claim['incident_date']}\n"
            report += f"Status: {claim['status']}\n"
            report += f"Amount: £{claim['claim_amount']:.2f}\n"

            return report
        except Exception as e:
            self.logger.error(f"Error generating claim timeline report: {e}")
            return "Error generating report"