"""
Edge case tests for Sentio risk manager
"""
import pytest
from sentio.risk.risk_manager import RiskManager

def test_risk_manager_default():
    manager = RiskManager()
    assert manager is not None
