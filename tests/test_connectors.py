"""
Integration tests for external service connectors
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from sentio.connectors import (
    ConnectorFactory,
    HealthMonitor,
    ConnectorStatus,
    ConnectorError,
    ConnectionError,
    APIError,
    RateLimitError,
)


class TestConnectorFactory:
    """Test connector factory"""

    def test_list_registered_connectors(self):
        """Test listing registered connectors"""
        brokers = ConnectorFactory.list_registered_brokers()
        data_providers = ConnectorFactory.list_registered_data_providers()
        notifications = ConnectorFactory.list_registered_notifications()

        assert "alpaca" in brokers
        assert "polygon" in data_providers
        assert "email" in notifications
        assert "webhook" in notifications

    def test_create_alpaca_broker_without_config(self):
        """Test creating Alpaca broker without required config fails"""
        with pytest.raises(ValueError):
            ConnectorFactory.create_broker("alpaca", {})

    def test_create_polygon_data_without_config(self):
        """Test creating Polygon data provider without required config fails"""
        with pytest.raises(ValueError):
            ConnectorFactory.create_data_provider("polygon", {})

    def test_create_email_notification_without_config(self):
        """Test creating email notification without required config fails"""
        with pytest.raises(ValueError):
            ConnectorFactory.create_notification("email", {})

    def test_create_webhook_notification_without_config(self):
        """Test creating webhook notification without required config fails"""
        with pytest.raises(ValueError):
            ConnectorFactory.create_notification("webhook", {})

    def test_create_unknown_connector(self):
        """Test creating unknown connector type fails"""
        with pytest.raises(ValueError):
            ConnectorFactory.create_broker("unknown_broker", {})


class TestAlpacaBroker:
    """Test Alpaca broker connector"""

    @pytest.fixture
    def alpaca_config(self):
        """Alpaca configuration"""
        return {
            "api_key": "test_key",
            "api_secret": "test_secret",
            "base_url": "https://paper-api.alpaca.markets",
            "max_retries": 2,
            "retry_delay": 0.1,
        }

    @pytest.fixture
    def alpaca_broker(self, alpaca_config):
        """Create Alpaca broker instance"""
        return ConnectorFactory.create_broker("alpaca", alpaca_config)

    def test_initialization(self, alpaca_broker):
        """Test broker initialization"""
        assert alpaca_broker.name == "alpaca"
        assert alpaca_broker.status == ConnectorStatus.DISCONNECTED

    @patch("requests.Session.get")
    def test_connect_success(self, mock_get, alpaca_broker):
        """Test successful connection"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"account_number": "123"}
        mock_get.return_value = mock_response

        result = alpaca_broker.connect()
        assert result is True
        assert alpaca_broker.status == ConnectorStatus.CONNECTED

    @patch("requests.Session.get")
    def test_connect_failure(self, mock_get, alpaca_broker):
        """Test connection failure"""
        mock_get.side_effect = Exception("Connection failed")

        result = alpaca_broker.connect()
        assert result is False

    @patch("requests.Session.get")
    def test_health_check(self, mock_get, alpaca_broker):
        """Test health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        health = alpaca_broker.health_check()
        assert "healthy" in health
        assert "timestamp" in health

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_place_order(self, mock_get, mock_post, alpaca_broker):
        """Test placing order"""
        # Mock connection
        mock_get.return_value = Mock(status_code=200, json=lambda: {})
        alpaca_broker.connect()

        # Mock order response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "order_123",
            "symbol": "AAPL",
            "qty": 100,
            "side": "buy",
        }
        mock_post.return_value = mock_response

        order = alpaca_broker.place_order("AAPL", 100, "buy")
        assert order["id"] == "order_123"
        assert order["symbol"] == "AAPL"

    @patch("requests.Session.post")
    @patch("requests.Session.get")
    def test_rate_limit_error(self, mock_get, mock_post, alpaca_broker):
        """Test rate limit handling"""
        # Mock connection
        mock_get.return_value = Mock(status_code=200, json=lambda: {})
        alpaca_broker.connect()

        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "1"}
        mock_post.return_value = mock_response

        with pytest.raises(RateLimitError):
            alpaca_broker.place_order("AAPL", 100, "buy")


class TestPolygonData:
    """Test Polygon data provider connector"""

    @pytest.fixture
    def polygon_config(self):
        """Polygon configuration"""
        return {"api_key": "test_api_key", "max_retries": 2, "retry_delay": 0.1}

    @pytest.fixture
    def polygon_data(self, polygon_config):
        """Create Polygon data provider instance"""
        return ConnectorFactory.create_data_provider("polygon", polygon_config)

    def test_initialization(self, polygon_data):
        """Test data provider initialization"""
        assert polygon_data.name == "polygon"
        assert polygon_data.status == ConnectorStatus.DISCONNECTED

    @patch("requests.Session.get")
    def test_get_quote(self, mock_get, polygon_data):
        """Test getting quote"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "ticker": {
                "lastTrade": {"p": 150.0},
                "lastQuote": {"p": 149.9, "P": 150.1},
                "day": {"h": 152.0, "l": 148.0, "v": 1000000},
                "prevDay": {"c": 149.0},
            },
        }
        mock_get.return_value = mock_response

        quote = polygon_data.get_quote("AAPL")
        assert quote["symbol"] == "AAPL"
        assert quote["price"] == 150.0
        assert "timestamp" in quote


class TestEmailNotification:
    """Test email notification connector"""

    @pytest.fixture
    def email_config(self):
        """Email configuration"""
        return {
            "smtp_host": "smtp.test.com",
            "smtp_port": 587,
            "username": "test@test.com",
            "password": "test_password",
            "max_retries": 2,
            "retry_delay": 0.1,
        }

    @pytest.fixture
    def email_connector(self, email_config):
        """Create email notification connector instance"""
        return ConnectorFactory.create_notification("email", email_config)

    def test_initialization(self, email_connector):
        """Test email connector initialization"""
        assert email_connector.name == "email"
        assert email_connector.status == ConnectorStatus.DISCONNECTED

    @patch("smtplib.SMTP")
    def test_connect(self, mock_smtp, email_connector):
        """Test connecting to SMTP server"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        result = email_connector.connect()
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()


class TestWebhookNotification:
    """Test webhook notification connector"""

    @pytest.fixture
    def webhook_config(self):
        """Webhook configuration"""
        return {
            "webhook_url": "https://hooks.test.com/webhook",
            "auth_token": "test_token",
            "max_retries": 2,
            "retry_delay": 0.1,
        }

    @pytest.fixture
    def webhook_connector(self, webhook_config):
        """Create webhook notification connector instance"""
        return ConnectorFactory.create_notification("webhook", webhook_config)

    def test_initialization(self, webhook_connector):
        """Test webhook connector initialization"""
        assert webhook_connector.name == "webhook"
        assert webhook_connector.status == ConnectorStatus.DISCONNECTED

    @patch("requests.Session.post")
    def test_send_notification(self, mock_post, webhook_connector):
        """Test sending webhook notification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.content = b'{"status": "success"}'
        mock_post.return_value = mock_response

        result = webhook_connector.send_notification(
            "test_channel", "Test Subject", "Test message"
        )
        assert result is True

    @patch("requests.Session.post")
    def test_send_alert(self, mock_post, webhook_connector):
        """Test sending webhook alert"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.content = b'{"status": "success"}'
        mock_post.return_value = mock_response

        result = webhook_connector.send_alert(
            "trade_alert", "Trade executed", priority="high"
        )
        assert result is True


class TestHealthMonitor:
    """Test health monitoring"""

    @pytest.fixture
    def health_monitor(self):
        """Create health monitor instance"""
        return HealthMonitor(check_interval=60)

    @pytest.fixture
    def mock_connector(self):
        """Create mock connector"""
        connector = Mock()
        connector.name = "test_connector"
        connector.status = ConnectorStatus.CONNECTED
        connector.circuit_open = False
        connector.health_check.return_value = {"healthy": True, "message": "OK"}
        connector.get_status.return_value = {
            "name": "test_connector",
            "status": "connected",
        }
        return connector

    def test_register_connector(self, health_monitor, mock_connector):
        """Test registering connector for monitoring"""
        health_monitor.register_connector("test_conn", mock_connector)
        assert "test_conn" in health_monitor.connectors

    def test_check_health(self, health_monitor, mock_connector):
        """Test checking connector health"""
        health_monitor.register_connector("test_conn", mock_connector)
        health = health_monitor.check_health("test_conn")

        assert "healthy" in health
        assert "name" in health

    def test_check_all(self, health_monitor, mock_connector):
        """Test checking all connectors"""
        health_monitor.register_connector("test_conn", mock_connector)
        results = health_monitor.check_all()

        assert "test_conn" in results
        assert results["test_conn"]["healthy"] is True

    def test_get_summary(self, health_monitor, mock_connector):
        """Test getting health summary"""
        health_monitor.register_connector("test_conn", mock_connector)
        summary = health_monitor.get_summary()

        assert summary["total_connectors"] == 1
        assert summary["healthy"] == 1
        assert summary["unhealthy"] == 0

    def test_get_unhealthy_connectors(self, health_monitor, mock_connector):
        """Test getting unhealthy connectors"""
        # Set connector as unhealthy
        mock_connector.status = ConnectorStatus.ERROR
        health_monitor.register_connector("test_conn", mock_connector)

        unhealthy = health_monitor.get_unhealthy_connectors()
        assert "test_conn" in unhealthy


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    @pytest.fixture
    def connector_config(self):
        """Connector config with circuit breaker settings"""
        return {
            "api_key": "test_key",
            "max_errors": 3,
            "error_reset_time": 1,  # 1 second for testing
            "max_retries": 1,
            "retry_delay": 0.1,
        }

    def test_circuit_breaker_opens(self, connector_config):
        """Test circuit breaker opens after max errors"""
        from sentio.connectors.base import BaseConnector, ConnectorError

        # Create a test connector
        class TestConnector(BaseConnector):
            def connect(self):
                return True

            def disconnect(self):
                return True

            def health_check(self):
                return {}

        connector = TestConnector("test", connector_config)

        # Simulate errors
        for i in range(3):
            error = ConnectorError(f"Error {i}", "test")
            connector._record_error(error)

        # Circuit should be open
        assert connector.circuit_open is True
        assert connector.error_count >= 3

    def test_circuit_breaker_resets(self, connector_config):
        """Test circuit breaker resets after timeout"""
        import time
        from sentio.connectors.base import BaseConnector, ConnectorError

        class TestConnector(BaseConnector):
            def connect(self):
                return True

            def disconnect(self):
                return True

            def health_check(self):
                return {}

        connector = TestConnector("test", connector_config)

        # Open circuit
        for i in range(3):
            error = ConnectorError(f"Error {i}", "test")
            connector._record_error(error)

        assert connector.circuit_open is True

        # Wait for reset time
        time.sleep(1.5)

        # Check circuit breaker - should reset
        can_proceed = connector._check_circuit_breaker()
        assert can_proceed is True
        assert connector.circuit_open is False
