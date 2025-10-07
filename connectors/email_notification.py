"""
Email notification connector implementation
"""

from typing import Dict, Any
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .base import NotificationConnector, ConnectionError, APIError
from ..core.logger import get_logger

logger = get_logger(__name__)


class EmailNotificationConnector(NotificationConnector):
    """
    Email notification connector

    Provides email notification capabilities via SMTP
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize email notification connector

        Args:
            name: Connector name
            config: Configuration with smtp_host, smtp_port, username, password, from_address
        """
        super().__init__(name, config)

        self.smtp_host = config.get("smtp_host", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_address = config.get("from_address", self.username)
        self.use_tls = config.get("use_tls", True)

        if not self.username or not self.password:
            raise ValueError("Email username and password are required")

        self.smtp_connection = None

    def connect(self) -> bool:
        """
        Establish connection to SMTP server

        Returns:
            True if connection successful
        """
        try:
            self.smtp_connection = smtplib.SMTP(self.smtp_host, self.smtp_port)

            if self.use_tls:
                self.smtp_connection.starttls()

            self.smtp_connection.login(self.username, self.password)

            self.status = self.status.CONNECTED
            logger.info(f"Connected to email service: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to email service: {e}")
            raise ConnectionError(
                f"Failed to connect to SMTP server: {str(e)}", self.name
            )

    def disconnect(self) -> bool:
        """
        Close connection to SMTP server

        Returns:
            True if disconnection successful
        """
        try:
            if self.smtp_connection:
                self.smtp_connection.quit()
                self.smtp_connection = None

            self.status = self.status.DISCONNECTED
            logger.info(f"Disconnected from email service: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting from email service: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Check connector health

        Returns:
            Health status dictionary
        """
        try:
            # Try to establish connection
            if not self.smtp_connection:
                self.connect()

            # Send NOOP command to check connection
            status = self.smtp_connection.noop()

            if status[0] == 250:
                return {
                    "healthy": True,
                    "message": "Email service accessible",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "healthy": False,
                    "message": f"SMTP server returned: {status}",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "healthy": False,
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def send_notification(
        self, recipient: str, subject: str, message: str, **kwargs
    ) -> bool:
        """
        Send email notification

        Args:
            recipient: Email address of recipient
            subject: Email subject
            message: Email message body
            **kwargs: Additional parameters (html, cc, bcc, etc.)

        Returns:
            True if successful
        """

        def _send():
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_address
            msg["To"] = recipient
            msg["Subject"] = subject

            # Add CC and BCC if provided
            if "cc" in kwargs:
                msg["Cc"] = kwargs["cc"]
            if "bcc" in kwargs:
                msg["Bcc"] = kwargs["bcc"]

            # Add message body
            if kwargs.get("html"):
                # HTML email
                msg.attach(MIMEText(message, "html"))
            else:
                # Plain text email
                msg.attach(MIMEText(message, "plain"))

            # Ensure connection
            if not self.smtp_connection:
                self.connect()

            # Send email
            self.smtp_connection.send_message(msg)

            logger.info(f"Email sent to {recipient}: {subject}")
            return True

        return self._retry_with_backoff(_send)

    def send_alert(
        self, alert_type: str, message: str, priority: str = "normal", **kwargs
    ) -> bool:
        """
        Send alert notification

        Args:
            alert_type: Type of alert
            message: Alert message
            priority: Priority level (low, normal, high, critical)
            **kwargs: Additional parameters (recipient, etc.)

        Returns:
            True if successful
        """
        recipient = kwargs.get("recipient")
        if not recipient:
            logger.warning("No recipient specified for alert")
            return False

        # Format subject based on priority
        priority_prefix = {
            "low": "[INFO]",
            "normal": "[ALERT]",
            "high": "[WARNING]",
            "critical": "[CRITICAL]",
        }

        subject = f"{priority_prefix.get(priority, '[ALERT]')} {alert_type}"

        # Add timestamp to message
        formatted_message = f"{message}\n\nTimestamp: {datetime.now().isoformat()}"

        return self.send_notification(recipient, subject, formatted_message, **kwargs)
