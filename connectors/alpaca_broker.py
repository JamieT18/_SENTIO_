"""
Alpaca broker connector implementation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from .base import BrokerConnector, APIError, ConnectionError, RateLimitError
from ..core.logger import get_logger

logger = get_logger(__name__)


class AlpacaBrokerConnector(BrokerConnector):
    """
    Alpaca broker connector

    Provides interface to Alpaca trading API for order execution and account management
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize Alpaca broker connector

        Args:
            name: Connector name
            config: Configuration dictionary with api_key, api_secret, base_url
        """
        super().__init__(name, config)

        self.api_key = config.get("api_key")
        self.api_secret = config.get("api_secret")
        self.base_url = config.get("base_url", "https://paper-api.alpaca.markets")

        if not self.api_key or not self.api_secret:
            raise ValueError("Alpaca API key and secret are required")

        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Content-Type": "application/json",
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def connect(self) -> bool:
        """
        Establish connection to Alpaca API

        Returns:
            True if connection successful
        """
        try:
            # Test connection by getting account
            response = self._retry_with_backoff(self._get_account_raw)
            self.status = self.status.CONNECTED
            logger.info(f"Connected to Alpaca broker: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            return False

    def disconnect(self) -> bool:
        """
        Close connection to Alpaca API

        Returns:
            True if disconnection successful
        """
        try:
            self.session.close()
            self.status = self.status.DISCONNECTED
            logger.info(f"Disconnected from Alpaca broker: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting from Alpaca: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Check connector health

        Returns:
            Health status dictionary
        """
        try:
            # Check clock endpoint (lightweight health check)
            response = self.session.get(f"{self.base_url}/v2/clock")

            if response.status_code == 200:
                return {
                    "healthy": True,
                    "message": "Alpaca API accessible",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "healthy": False,
                    "message": f"Alpaca API returned status {response.status_code}",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "healthy": False,
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def _get_account_raw(self) -> Dict[str, Any]:
        """Internal method to get account (used for connection test)"""
        response = self.session.get(f"{self.base_url}/v2/account")
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate errors

        Args:
            response: HTTP response

        Returns:
            Response JSON data

        Raises:
            APIError, RateLimitError, ConnectionError
        """
        if response.status_code == 200:
            return response.json()

        elif response.status_code == 429:
            # Rate limited
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                "Alpaca API rate limit exceeded", self.name, retry_after=retry_after
            )

        elif response.status_code in [500, 502, 503, 504]:
            # Server error
            raise ConnectionError(
                f"Alpaca server error: {response.status_code}",
                self.name,
                {"status_code": response.status_code},
            )

        else:
            # Other API error
            try:
                error_data = response.json()
                message = error_data.get("message", "Unknown error")
            except:
                message = response.text or "Unknown error"

            raise APIError(
                f"Alpaca API error: {message}",
                self.name,
                status_code=response.status_code,
                response=response.text,
            )

    def place_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        order_type: str = "market",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Place order with Alpaca

        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            order_type: Order type (market, limit, stop, stop_limit)
            **kwargs: Additional parameters (limit_price, stop_price, etc.)

        Returns:
            Order details
        """

        def _place():
            order_data = {
                "symbol": symbol,
                "qty": quantity,
                "side": side,
                "type": order_type,
                "time_in_force": kwargs.get("time_in_force", "day"),
            }

            # Add price parameters if provided
            if "limit_price" in kwargs:
                order_data["limit_price"] = kwargs["limit_price"]
            if "stop_price" in kwargs:
                order_data["stop_price"] = kwargs["stop_price"]

            response = self.session.post(f"{self.base_url}/v2/orders", json=order_data)

            return self._handle_response(response)

        result = self._retry_with_backoff(_place)
        logger.info(f"Placed {side} order for {quantity} {symbol}: {result.get('id')}")
        return result

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel order

        Args:
            order_id: Order identifier

        Returns:
            True if successful
        """

        def _cancel():
            response = self.session.delete(f"{self.base_url}/v2/orders/{order_id}")

            if response.status_code == 204:
                return True

            self._handle_response(response)
            return True

        result = self._retry_with_backoff(_cancel)
        logger.info(f"Cancelled order: {order_id}")
        return result

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status

        Args:
            order_id: Order identifier

        Returns:
            Order status details
        """

        def _get_status():
            response = self.session.get(f"{self.base_url}/v2/orders/{order_id}")
            return self._handle_response(response)

        return self._retry_with_backoff(_get_status)

    def get_account(self) -> Dict[str, Any]:
        """
        Get account information

        Returns:
            Account details
        """
        return self._retry_with_backoff(self._get_account_raw)

    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions

        Returns:
            List of position details
        """

        def _get_positions():
            response = self.session.get(f"{self.base_url}/v2/positions")
            return self._handle_response(response)

        return self._retry_with_backoff(_get_positions)

    def get_orders(
        self, status: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get orders

        Args:
            status: Filter by status (open, closed, all)
            limit: Maximum number of orders

        Returns:
            List of orders
        """

        def _get_orders():
            params = {"limit": limit}
            if status:
                params["status"] = status

            response = self.session.get(f"{self.base_url}/v2/orders", params=params)
            return self._handle_response(response)

        return self._retry_with_backoff(_get_orders)
