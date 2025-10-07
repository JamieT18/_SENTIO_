"""
External Service Connectors
Modular integration layer for brokers, data providers, and notification services
"""

from .base import (
    BaseConnector,
    BrokerConnector,
    DataProviderConnector,
    NotificationConnector,
    ConnectorStatus,
    ConnectorError,
    ConnectionError,
    APIError,
    RateLimitError,
)
from .factory import ConnectorFactory
from .health import HealthMonitor
from .alpaca_broker import AlpacaBrokerConnector
from .polygon_data import PolygonDataConnector
from .email_notification import EmailNotificationConnector
from .webhook_notification import WebhookNotificationConnector

# Register connectors
ConnectorFactory.register_broker("alpaca", AlpacaBrokerConnector)
ConnectorFactory.register_data_provider("polygon", PolygonDataConnector)
ConnectorFactory.register_notification("email", EmailNotificationConnector)
ConnectorFactory.register_notification("webhook", WebhookNotificationConnector)

__all__ = [
    "BaseConnector",
    "BrokerConnector",
    "DataProviderConnector",
    "NotificationConnector",
    "ConnectorStatus",
    "ConnectorError",
    "ConnectionError",
    "APIError",
    "RateLimitError",
    "ConnectorFactory",
    "HealthMonitor",
    "AlpacaBrokerConnector",
    "PolygonDataConnector",
    "EmailNotificationConnector",
    "WebhookNotificationConnector",
]
