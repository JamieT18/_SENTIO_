"""
Sentio Integrity Test Suite
Ensures all major modules and features are importable and basic calls succeed
"""
import pytest

def test_import_portfolio_rebalancer():
    from sentio.portfolio.rebalancer import PortfolioRebalancer
    r = PortfolioRebalancer()
    assert hasattr(r, 'rebalance')

def test_import_alert_manager():
    from sentio.notifications.alerts import AlertManager
    a = AlertManager()
    assert hasattr(a, 'push_alert')

def test_import_community_manager():
    from sentio.social.community import CommunityManager
    c = CommunityManager()
    assert hasattr(c, 'share_strategy')

def test_import_explainability_engine():
    from sentio.explainability.shap_lime import ExplainabilityEngine
    class DummyModel:
        def predict(self, X): return [0]*len(X)
    e = ExplainabilityEngine(DummyModel())
    assert hasattr(e, 'explain_shap')

def test_import_broker_manager():
    from sentio.brokers.broker_manager import BrokerManager
    b = BrokerManager()
    assert hasattr(b, 'register_broker')

def test_import_compliance_dashboard():
    from sentio.compliance.dashboard import ComplianceDashboard
    d = ComplianceDashboard()
    assert hasattr(d, 'check_trade')
