"""
Basic compliance dashboard tests for Sentio
"""
import pytest
from sentio.compliance.dashboard import ComplianceDashboard

def test_compliance_check_trade():
    dashboard = ComplianceDashboard()
    result = dashboard.check_trade({"id": 1, "symbol": "AAPL", "amount": 100})
    assert result["compliant"] is True
