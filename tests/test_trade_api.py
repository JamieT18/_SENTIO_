"""
Unit tests for trade execution API endpoints
Tests the API layer for automated trade execution
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from sentio.ui.api import app
from sentio.execution.trading_engine import OrderStatus


@pytest.mark.unit
@pytest.mark.api
class TestTradeExecutionAPI:
    """Test trade execution API endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, mock_api_token):
        """Create authentication headers"""
        return {"Authorization": f"Bearer {mock_api_token}"}

    @pytest.fixture
    def mock_order_filled(self):
        """Mock filled order"""
        return {
            "order_id": "paper_123456",
            "symbol": "AAPL",
            "side": "buy",
            "quantity": 10,
            "price": 150.0,
            "filled_price": 150.0,
            "filled_qty": 10,
            "status": OrderStatus.FILLED,
            "timestamp": datetime.now(),
            "message": "Order filled (simulated)",
        }

    @pytest.fixture
    def mock_order_rejected(self):
        """Mock rejected order"""
        return {
            "order_id": None,
            "symbol": "AAPL",
            "status": OrderStatus.REJECTED,
            "message": "Insufficient funds",
            "timestamp": datetime.now(),
        }

    def test_execute_trade_success(self, client, auth_headers, mock_order_filled):
        """Test successful trade execution"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine

            # Mock analyze_symbol
            mock_voting_result = Mock()
            mock_voting_result.final_signal.value = "buy"
            mock_voting_result.confidence = 0.8
            mock_voting_result.to_dict.return_value = {
                "signal": "buy",
                "confidence": 0.8,
            }
            mock_engine.analyze_symbol.return_value = mock_voting_result

            # Mock execute_signal to return filled order
            mock_engine.execute_signal.return_value = mock_order_filled

            response = client.post(
                "/api/v1/trade",
                json={"symbol": "AAPL", "action": "buy", "quantity": 10},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "order_details" in data
            assert data["order_details"]["order_id"] == "paper_123456"
            assert data["order_details"]["symbol"] == "AAPL"

    def test_execute_trade_rejection(self, client, auth_headers, mock_order_rejected):
        """Test trade rejection handling"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine

            # Mock analyze_symbol
            mock_voting_result = Mock()
            mock_voting_result.final_signal.value = "buy"
            mock_voting_result.confidence = 0.8
            mock_engine.analyze_symbol.return_value = mock_voting_result

            # Mock execute_signal to return rejected order
            mock_engine.execute_signal.return_value = mock_order_rejected

            response = client.post(
                "/api/v1/trade",
                json={"symbol": "AAPL", "action": "buy", "quantity": 10},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert "Insufficient funds" in data["message"]

    def test_execute_trade_conflict_warning(self, client, auth_headers):
        """Test warning when manual action conflicts with strategy"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine

            # Mock analyze_symbol to return SELL but user wants BUY
            mock_voting_result = Mock()
            mock_voting_result.final_signal.value = "sell"
            mock_voting_result.confidence = 0.8
            mock_voting_result.to_dict.return_value = {
                "signal": "sell",
                "confidence": 0.8,
            }
            mock_engine.analyze_symbol.return_value = mock_voting_result

            response = client.post(
                "/api/v1/trade",
                json={
                    "symbol": "AAPL",
                    "action": "buy",  # Conflicts with 'sell'
                    "quantity": 10,
                },
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "warning"
            assert "conflicts" in data["message"]
            assert "recommendation" in data

    def test_close_position_success(self, client, auth_headers):
        """Test closing a position"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine
            mock_engine.open_positions = {"AAPL": {"symbol": "AAPL"}}

            response = client.post(
                "/api/v1/trade",
                json={"symbol": "AAPL", "action": "close"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            mock_engine.close_position.assert_called_once_with("AAPL", reason="manual")

    def test_close_position_not_found(self, client, auth_headers):
        """Test closing non-existent position"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine
            mock_engine.open_positions = {}

            response = client.post(
                "/api/v1/trade",
                json={"symbol": "AAPL", "action": "close"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert "No open position" in data["message"]


@pytest.mark.unit
@pytest.mark.api
class TestOrderStatusAPI:
    """Test order status API endpoints"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, mock_api_token):
        """Create authentication headers"""
        return {"Authorization": f"Bearer {mock_api_token}"}

    def test_get_order_status_success(self, client, auth_headers):
        """Test retrieving order status"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine

            mock_order = {
                "order_id": "paper_123456",
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10,
                "price": 150.0,
                "filled_price": 150.0,
                "filled_qty": 10,
                "status": OrderStatus.FILLED,
                "timestamp": datetime.now(),
                "message": "Order filled",
            }
            mock_engine.get_order_status.return_value = mock_order

            response = client.get("/api/v1/orders/paper_123456", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "order" in data
            assert data["order"]["order_id"] == "paper_123456"

    def test_get_order_status_not_found(self, client, auth_headers):
        """Test retrieving non-existent order"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine
            mock_engine.get_order_status.return_value = None

            response = client.get("/api/v1/orders/nonexistent", headers=auth_headers)

            assert response.status_code == 404

    def test_get_all_orders(self, client, auth_headers):
        """Test retrieving all orders"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine

            mock_orders = [
                {
                    "order_id": "paper_123456",
                    "symbol": "AAPL",
                    "side": "buy",
                    "quantity": 10,
                    "price": 150.0,
                    "status": OrderStatus.FILLED,
                    "timestamp": datetime.now(),
                },
                {
                    "order_id": "paper_123457",
                    "symbol": "GOOGL",
                    "side": "buy",
                    "quantity": 5,
                    "price": 2800.0,
                    "status": OrderStatus.FILLED,
                    "timestamp": datetime.now(),
                },
            ]
            mock_engine.get_all_orders.return_value = mock_orders

            response = client.get("/api/v1/orders", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "orders" in data
            assert data["count"] == 2

    def test_get_orders_filtered_by_symbol(self, client, auth_headers):
        """Test retrieving orders filtered by symbol"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine

            mock_orders = [
                {
                    "order_id": "paper_123456",
                    "symbol": "AAPL",
                    "side": "buy",
                    "quantity": 10,
                    "price": 150.0,
                    "status": OrderStatus.FILLED,
                    "timestamp": datetime.now(),
                }
            ]
            mock_engine.get_all_orders.return_value = mock_orders

            response = client.get("/api/v1/orders?symbol=AAPL", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert "orders" in data
            mock_engine.get_all_orders.assert_called_once()

    def test_get_orders_with_limit(self, client, auth_headers):
        """Test retrieving orders with limit"""
        with patch("sentio.ui.api.get_trading_engine") as mock_engine_factory:
            mock_engine = Mock()
            mock_engine_factory.return_value = mock_engine
            mock_engine.get_all_orders.return_value = []

            response = client.get("/api/v1/orders?limit=50", headers=auth_headers)

            assert response.status_code == 200
            mock_engine.get_all_orders.assert_called_once()
