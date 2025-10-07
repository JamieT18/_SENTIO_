"""
Regulatory/Compliance Dashboard for Sentio
Automated compliance checks and reporting
"""
from typing import List, Dict, Any

class ComplianceDashboard:
    def __init__(self):
        self.reports: List[Dict[str, Any]] = []

    def check_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        # Stub: Replace with real compliance logic
        result = {"trade_id": trade.get("id"), "compliant": True, "issues": []}
        self.reports.append(result)
        return result

    def get_reports(self) -> List[Dict[str, Any]]:
        return self.reports[-20:]
