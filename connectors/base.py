"""
Base connector classes and error types for external service integration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import time
from ..core.logger import get_logger

logger = get_logger(__name__)


class ConnectorStatus(str, Enum):
    """Connector status enumeration"""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    CONNECTING = "connecting"
    RATE_LIMITED = "rate_limited"


class ConnectorError(Exception):
    """Base exception for connector errors"""

    def __init__(
        self,
        message: str,
        connector_name: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.connector_name = connector_name
        self.details = details or {}
        self.timestamp = datetime.now()


class ConnectionError(ConnectorError):
    """Exception raised when connection fails"""

    pass


class APIError(ConnectorError):
    """Exception raised when API call fails"""

    def __init__(
        self,
        message: str,
        connector_name: str,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, connector_name, details)
        self.status_code = status_code
        self.response = response


class RateLimitError(ConnectorError):
    """Exception raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str,
        connector_name: str,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, connector_name, details)
        self.retry_after = retry_after


class BaseConnector(ABC):
    """
    Base class for all external service connectors

    Features:
    - Connection management
    - Error handling with retry logic
    - Health monitoring
    - Circuit breaker pattern
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize connector

        Args:
            name: Connector name
            config: Configuration dictionary
        """
        self.name = name
        self.config = config
        self.status = ConnectorStatus.DISCONNECTED
        self.last_error: Optional[ConnectorError] = None
        self.error_count = 0
        self.last_success_time: Optional[datetime] = None
        self.last_error_time: Optional[datetime] = None

        # Circuit breaker settings
        self.max_errors = config.get("max_errors", 5)
        self.error_reset_time = config.get("error_reset_time", 300)  # 5 minutes
        self.circuit_open = False
        self.circuit_open_time: Optional[datetime] = None

        # Retry settings
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        self.retry_backoff = config.get("retry_backoff", 2.0)

        logger.info(f"Connector initialized: {self.name}")

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to external service

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Close connection to external service

        Returns:
            True if disconnection successful
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Check connector health

        Returns:
            Health status dictionary
        """
        pass

    def _check_circuit_breaker(self) -> bool:
        """
        Check if circuit breaker is open

        Returns:
            True if circuit is closed (ok to proceed)
        """
        if not self.circuit_open:
            return True

        # Check if enough time has passed to reset circuit
        if self.circuit_open_time:
            elapsed = (datetime.now() - self.circuit_open_time).total_seconds()
            if elapsed >= self.error_reset_time:
                logger.info(f"Circuit breaker reset for {self.name}")
                self.circuit_open = False
                self.error_count = 0
                return True

        logger.warning(f"Circuit breaker open for {self.name}")
        return False

    def _record_success(self):
        """Record successful operation"""
        self.last_success_time = datetime.now()
        self.status = ConnectorStatus.CONNECTED

        # Reset error count after successful operation
        if self.error_count > 0:
            self.error_count = max(0, self.error_count - 1)

    def _record_error(self, error: ConnectorError):
        """
        Record error and update circuit breaker state

        Args:
            error: Error that occurred
        """
        self.last_error = error
        self.last_error_time = datetime.now()
        self.error_count += 1
        self.status = ConnectorStatus.ERROR

        logger.error(
            f"Connector error in {self.name}: {error} "
            f"(error count: {self.error_count}/{self.max_errors})"
        )

        # Open circuit breaker if max errors exceeded
        if self.error_count >= self.max_errors:
            self.circuit_open = True
            self.circuit_open_time = datetime.now()
            logger.error(f"Circuit breaker opened for {self.name}")

    def _retry_with_backoff(self, operation, *args, **kwargs) -> Any:
        """
        Execute operation with retry logic and exponential backoff

        Args:
            operation: Function to execute
            *args: Arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            Operation result

        Raises:
            ConnectorError: If all retries fail
        """
        if not self._check_circuit_breaker():
            raise ConnectionError(
                "Circuit breaker is open", self.name, {"error_count": self.error_count}
            )

        last_exception = None
        delay = self.retry_delay

        for attempt in range(self.max_retries):
            try:
                result = operation(*args, **kwargs)
                self._record_success()
                return result

            except RateLimitError as e:
                # Handle rate limiting specially
                self.status = ConnectorStatus.RATE_LIMITED
                retry_after = e.retry_after or delay
                logger.warning(
                    f"Rate limited in {self.name}, waiting {retry_after}s "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                time.sleep(retry_after)
                last_exception = e

            except (ConnectionError, APIError) as e:
                self._record_error(e)
                last_exception = e

                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"Retry {attempt + 1}/{self.max_retries} for {self.name} "
                        f"after {delay}s delay"
                    )
                    time.sleep(delay)
                    delay *= self.retry_backoff

            except Exception as e:
                # Unexpected error - wrap and record
                error = ConnectorError(str(e), self.name)
                self._record_error(error)
                raise error

        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise ConnectorError(
                f"Operation failed after {self.max_retries} retries", self.name
            )

    def get_status(self) -> Dict[str, Any]:
        """
        Get connector status information

        Returns:
            Status dictionary
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "error_count": self.error_count,
            "circuit_open": self.circuit_open,
            "last_success": (
                self.last_success_time.isoformat() if self.last_success_time else None
            ),
            "last_error": (
                self.last_error_time.isoformat() if self.last_error_time else None
            ),
            "last_error_message": str(self.last_error) if self.last_error else None,
        }


class BrokerConnector(BaseConnector):
    """
    Base class for broker connectors

    Provides interface for order execution and account management
    """

    @abstractmethod
    def place_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        order_type: str = "market",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Place order with broker

        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            order_type: Order type (market, limit, etc.)
            **kwargs: Additional order parameters

        Returns:
            Order details
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel order

        Args:
            order_id: Order identifier

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status

        Args:
            order_id: Order identifier

        Returns:
            Order status details
        """
        pass

    @abstractmethod
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information

        Returns:
            Account details
        """
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions

        Returns:
            List of position details
        """
        pass


class DataProviderConnector(BaseConnector):
    """
    Base class for market data provider connectors

    Provides interface for market data retrieval
    """

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote

        Args:
            symbol: Trading symbol

        Returns:
            Quote data
        """
        pass

    @abstractmethod
    def get_bars(
        self, symbol: str, timeframe: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get historical bars

        Args:
            symbol: Trading symbol
            timeframe: Bar timeframe
            limit: Number of bars

        Returns:
            List of OHLCV bars
        """
        pass

    @abstractmethod
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get quotes for multiple symbols

        Args:
            symbols: List of trading symbols

        Returns:
            Dictionary mapping symbols to quotes
        """
        pass


class NotificationConnector(BaseConnector):
    """
    Base class for notification service connectors

    Provides interface for sending notifications
    """

    @abstractmethod
    def send_notification(
        self, recipient: str, subject: str, message: str, **kwargs
    ) -> bool:
        """
        Send notification

        Args:
            recipient: Notification recipient
            subject: Notification subject
            message: Notification message
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def send_alert(
        self, alert_type: str, message: str, priority: str = "normal", **kwargs
    ) -> bool:
        """
        Send alert notification

        Args:
            alert_type: Type of alert
            message: Alert message
            priority: Priority level
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        pass
