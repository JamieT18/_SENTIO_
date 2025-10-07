"""
Webhook notification connector implementation
"""

from typing import Dict, Any
from datetime import datetime
import requests
from .base import NotificationConnector, APIError, ConnectionError, RateLimitError
from ..core.logger import get_logger

logger = get_logger(__name__)


class WebhookNotificationConnector(NotificationConnector):
    """
    Webhook notification connector

    Provides webhook notification capabilities for external integrations
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize webhook notification connector

        Args:
            name: Connector name
            config: Configuration with webhook_url, headers, auth_token
        """
        super().__init__(name, config)

        self.webhook_url = config.get("webhook_url")
        self.auth_token = config.get("auth_token")
        self.custom_headers = config.get("headers", {})

        if not self.webhook_url:
            raise ValueError("Webhook URL is required")

        self.session = requests.Session()

        # Set up headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Sentio-Webhook-Connector/2.0",
        }

        # Add auth token if provided
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        # Add custom headers
        headers.update(self.custom_headers)

        self.session.headers.update(headers)

    def connect(self) -> bool:
        """
        Establish connection to webhook endpoint

        Returns:
            True if connection successful
        """
        try:
            # Test webhook with a ping
            response = self._retry_with_backoff(
                self._send_webhook,
                {"event": "ping", "timestamp": datetime.now().isoformat()},
            )

            self.status = self.status.CONNECTED
            logger.info(f"Connected to webhook: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to webhook: {e}")
            return False

    def disconnect(self) -> bool:
        """
        Close connection to webhook endpoint

        Returns:
            True if disconnection successful
        """
        try:
            self.session.close()
            self.status = self.status.DISCONNECTED
            logger.info(f"Disconnected from webhook: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting from webhook: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Check connector health

        Returns:
            Health status dictionary
        """
        try:
            # Send a health check ping
            response = self.session.post(
                self.webhook_url,
                json={"event": "health_check", "timestamp": datetime.now().isoformat()},
                timeout=10,
            )

            if response.status_code in [200, 201, 202, 204]:
                return {
                    "healthy": True,
                    "message": "Webhook accessible",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "healthy": False,
                    "message": f"Webhook returned status {response.status_code}",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "healthy": False,
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def _send_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send webhook request

        Args:
            payload: Webhook payload

        Returns:
            Response data

        Raises:
            APIError, RateLimitError, ConnectionError
        """
        response = self.session.post(self.webhook_url, json=payload, timeout=30)

        if response.status_code in [200, 201, 202, 204]:
            # Successful webhook
            try:
                return response.json() if response.content else {}
            except:
                return {"status": "success"}

        elif response.status_code == 429:
            # Rate limited
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                "Webhook rate limit exceeded", self.name, retry_after=retry_after
            )

        elif response.status_code in [500, 502, 503, 504]:
            # Server error
            raise ConnectionError(
                f"Webhook server error: {response.status_code}",
                self.name,
                {"status_code": response.status_code},
            )

        else:
            # Other error
            raise APIError(
                f"Webhook error: {response.status_code}",
                self.name,
                status_code=response.status_code,
                response=response.text,
            )

    def send_notification(
        self, recipient: str, subject: str, message: str, **kwargs
    ) -> bool:
        """
        Send webhook notification

        Args:
            recipient: Notification recipient (channel, user, etc.)
            subject: Notification subject/title
            message: Notification message
            **kwargs: Additional parameters

        Returns:
            True if successful
        """

        def _send():
            payload = {
                "event": "notification",
                "recipient": recipient,
                "subject": subject,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }

            # Add any additional data
            if kwargs:
                payload["data"] = kwargs

            self._send_webhook(payload)
            logger.info(f"Webhook notification sent to {recipient}: {subject}")
            return True

        return self._retry_with_backoff(_send)

    def send_alert(
        self, alert_type: str, message: str, priority: str = "normal", **kwargs
    ) -> bool:
        """
        Send alert notification via webhook

        Args:
            alert_type: Type of alert
            message: Alert message
            priority: Priority level (low, normal, high, critical)
            **kwargs: Additional parameters

        Returns:
            True if successful
        """

        def _send():
            payload = {
                "event": "alert",
                "alert_type": alert_type,
                "message": message,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
            }

            # Add any additional data
            if kwargs:
                payload["data"] = kwargs

            self._send_webhook(payload)
            logger.info(f"Webhook alert sent: {alert_type} ({priority})")
            return True

        return self._retry_with_backoff(_send)

    def send_trade_notification(self, trade_data: Dict[str, Any]) -> bool:
        """
        Send trade notification via webhook

        Args:
            trade_data: Trade information

        Returns:
            True if successful
        """

        def _send():
            payload = {
                "event": "trade",
                "trade_data": trade_data,
                "timestamp": datetime.now().isoformat(),
            }

            self._send_webhook(payload)
            logger.info(f"Webhook trade notification sent: {trade_data.get('symbol')}")
            return True

        return self._retry_with_backoff(_send)
