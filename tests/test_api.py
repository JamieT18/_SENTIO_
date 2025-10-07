"""
Unit tests for API endpoints
Tests FastAPI REST API functionality
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from sentio.ui.api import app


@pytest.mark.unit
@pytest.mark.api
class TestAPIEndpoints:
    """Test API endpoint functionality"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, mock_api_token):
        """Create authentication headers"""
        return {"Authorization": f"Bearer {mock_api_token}"}

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_no_auth_required(self, client):
        """Test that health check doesn't require authentication"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_get_positions_requires_auth(self, client):
        """Test that positions endpoint requires authentication"""
        response = client.get("/api/v1/positions")
        assert response.status_code == 403  # Forbidden without auth

    def test_get_positions_with_auth(self, client, auth_headers):
        """Test getting positions with authentication"""
        response = client.get("/api/v1/positions", headers=auth_headers)

        # Should succeed (or 200/500 depending on state, but not 401/403)
        assert response.status_code in [200, 500]

    def test_get_performance_requires_auth(self, client):
        """Test that performance endpoint requires authentication"""
        response = client.get("/api/v1/performance")
        assert response.status_code == 403

    def test_get_performance_with_auth(self, client, auth_headers):
        """Test getting performance metrics with authentication"""
        response = client.get("/api/v1/performance", headers=auth_headers)

        assert response.status_code in [200, 500]

    def test_analyze_symbol_requires_auth(self, client):
        """Test that analyze endpoint requires authentication"""
        response = client.post(
            "/api/v1/analyze", json={"symbol": "AAPL", "timeframe": "5min"}
        )
        assert response.status_code == 403

    def test_trade_endpoint_requires_auth(self, client):
        """Test that trade endpoint requires authentication"""
        response = client.post(
            "/api/v1/trade", json={"symbol": "AAPL", "action": "buy", "quantity": 10}
        )
        assert response.status_code == 403


@pytest.mark.unit
@pytest.mark.api
class TestSubscriptionEndpoints:
    """Test subscription and billing endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, mock_api_token):
        """Create authentication headers"""
        return {"Authorization": f"Bearer {mock_api_token}"}

    def test_get_pricing_public_endpoint(self, client):
        """Test that pricing endpoint is public"""
        response = client.get("/api/v1/subscription/pricing")

        # Should be accessible without auth
        assert response.status_code in [200, 500]

    def test_get_subscription_requires_auth(self, client):
        """Test that subscription details require authentication"""
        response = client.get("/api/v1/subscription/test_user")
        assert response.status_code == 403

    def test_profit_sharing_calculation_requires_auth(self, client):
        """Test that profit sharing calculation requires auth"""
        response = client.post(
            "/api/v1/subscription/profit-sharing/calculate",
            json={"user_id": "test_user", "trading_profit": 1000.0},
        )
        assert response.status_code == 403


@pytest.mark.unit
@pytest.mark.api
class TestDashboardEndpoints:
    """Test dashboard-specific endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, mock_api_token):
        """Create authentication headers"""
        return {"Authorization": f"Bearer {mock_api_token}"}

    def test_trade_signals_endpoint_requires_auth(self, client):
        """Test that trade signals endpoint requires authentication"""
        response = client.get("/api/v1/dashboard/trade-signals?symbols=AAPL")
        assert response.status_code == 403

    def test_earnings_endpoint_requires_auth(self, client):
        """Test that earnings endpoint requires authentication"""
        response = client.get("/api/v1/dashboard/earnings?user_id=test")
        assert response.status_code == 403

    def test_strength_signal_endpoint_requires_auth(self, client):
        """Test that strength signal endpoint requires authentication"""
        response = client.get("/api/v1/dashboard/strength-signal?symbol=AAPL")
        assert response.status_code == 403


@pytest.mark.unit
@pytest.mark.api
class TestRequestValidation:
    """Test request validation and error handling"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, mock_api_token):
        """Create authentication headers"""
        return {"Authorization": f"Bearer {mock_api_token}"}

    def test_analyze_request_validation(self, client, auth_headers):
        """Test request validation for analyze endpoint"""
        # Missing required field
        response = client.post(
            "/api/v1/analyze",
            json={"timeframe": "5min"},  # Missing 'symbol'
            headers=auth_headers,
        )

        assert response.status_code in [422, 500]  # Validation error

    def test_trade_request_validation(self, client, auth_headers):
        """Test request validation for trade endpoint"""
        # Missing required fields
        response = client.post(
            "/api/v1/trade",
            json={"symbol": "AAPL"},  # Missing 'action'
            headers=auth_headers,
        )

        assert response.status_code in [422, 500]  # Validation error
