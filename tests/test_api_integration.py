"""
API integration test stub for Sentio
"""
import pytest
import sentio.core.config

class DummyBillingConfig:
    stripe_api_key = "test_key"
    enable_profit_sharing = False
    # Add other required billing config attributes here as needed

class DummyRiskConfig:
    def model_dump(self):
        return {}

class DummyStrategyConfig:
    max_concurrent_trades = 1

class DummyConfig:
    billing = DummyBillingConfig()
    risk_management = DummyRiskConfig()
    strategy = DummyStrategyConfig()

def test_health_endpoint(monkeypatch):
    monkeypatch.setattr(sentio.core.config, "get_config", lambda: DummyConfig())
    from fastapi.testclient import TestClient
    from sentio.api import main
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
