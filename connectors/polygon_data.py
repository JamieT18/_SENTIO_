"""
Polygon.io data provider connector implementation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from .base import DataProviderConnector, APIError, ConnectionError, RateLimitError
from ..core.logger import get_logger

logger = get_logger(__name__)


class PolygonDataConnector(DataProviderConnector):
    """
    Polygon.io data provider connector

    Provides interface to Polygon.io market data API
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize Polygon data connector

        Args:
            name: Connector name
            config: Configuration dictionary with api_key
        """
        super().__init__(name, config)

        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.polygon.io")

        if not self.api_key:
            raise ValueError("Polygon API key is required")

        self.session = requests.Session()

    def connect(self) -> bool:
        """
        Establish connection to Polygon API

        Returns:
            True if connection successful
        """
        try:
            # Test connection with a simple quote request
            response = self._retry_with_backoff(
                self._make_request,
                f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/AAPL",
            )
            self.status = self.status.CONNECTED
            logger.info(f"Connected to Polygon data provider: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Polygon: {e}")
            return False

    def disconnect(self) -> bool:
        """
        Close connection to Polygon API

        Returns:
            True if disconnection successful
        """
        try:
            self.session.close()
            self.status = self.status.DISCONNECTED
            logger.info(f"Disconnected from Polygon data provider: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting from Polygon: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Check connector health

        Returns:
            Health status dictionary
        """
        try:
            # Simple status check
            response = self.session.get(
                f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/AAPL",
                params={"apiKey": self.api_key},
            )

            if response.status_code == 200:
                return {
                    "healthy": True,
                    "message": "Polygon API accessible",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "healthy": False,
                    "message": f"Polygon API returned status {response.status_code}",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "healthy": False,
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def _make_request(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make API request to Polygon

        Args:
            url: Request URL
            params: Query parameters

        Returns:
            Response data

        Raises:
            APIError, RateLimitError, ConnectionError
        """
        if params is None:
            params = {}

        params["apiKey"] = self.api_key

        response = self.session.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Check for API-level errors
            if data.get("status") == "ERROR":
                raise APIError(
                    f"Polygon API error: {data.get('error', 'Unknown error')}",
                    self.name,
                    status_code=response.status_code,
                    response=data,
                )

            return data

        elif response.status_code == 429:
            # Rate limited
            raise RateLimitError(
                "Polygon API rate limit exceeded", self.name, retry_after=60
            )

        elif response.status_code in [500, 502, 503, 504]:
            # Server error
            raise ConnectionError(
                f"Polygon server error: {response.status_code}",
                self.name,
                {"status_code": response.status_code},
            )

        else:
            # Other API error
            try:
                error_data = response.json()
                message = error_data.get("error", "Unknown error")
            except:
                message = response.text or "Unknown error"

            raise APIError(
                f"Polygon API error: {message}",
                self.name,
                status_code=response.status_code,
                response=response.text,
            )

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote

        Args:
            symbol: Trading symbol

        Returns:
            Quote data
        """

        def _get_quote():
            url = (
                f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
            )
            data = self._make_request(url)

            # Extract ticker data
            ticker = data.get("ticker", {})

            # Format quote
            quote = {
                "symbol": symbol,
                "price": ticker.get("lastTrade", {}).get("p", 0),
                "bid": ticker.get("lastQuote", {}).get("p", 0),
                "ask": ticker.get("lastQuote", {}).get("P", 0),
                "high": ticker.get("day", {}).get("h", 0),
                "low": ticker.get("day", {}).get("l", 0),
                "volume": ticker.get("day", {}).get("v", 0),
                "prev_close": ticker.get("prevDay", {}).get("c", 0),
                "timestamp": datetime.now().isoformat(),
            }

            # Calculate change
            if quote["prev_close"] > 0:
                quote["change"] = quote["price"] - quote["prev_close"]
                quote["change_pct"] = (quote["change"] / quote["prev_close"]) * 100
            else:
                quote["change"] = 0
                quote["change_pct"] = 0

            return quote

        return self._retry_with_backoff(_get_quote)

    def get_bars(
        self, symbol: str, timeframe: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get historical bars

        Args:
            symbol: Trading symbol
            timeframe: Bar timeframe (1min, 5min, 1hour, 1day)
            limit: Number of bars

        Returns:
            List of OHLCV bars
        """

        def _get_bars():
            # Map timeframe to Polygon format
            timeframe_map = {
                "1min": ("1", "minute"),
                "5min": ("5", "minute"),
                "15min": ("15", "minute"),
                "1hour": ("1", "hour"),
                "1day": ("1", "day"),
            }

            multiplier, timespan = timeframe_map.get(timeframe, ("5", "minute"))

            # Get current time for date range
            from datetime import datetime, timedelta

            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            url = (
                f"{self.base_url}/v2/aggs/ticker/{symbol}/range/"
                f"{multiplier}/{timespan}/{start_date}/{end_date}"
            )

            data = self._make_request(url, {"limit": limit})

            # Convert to standardized format
            bars = []
            for bar in data.get("results", [])[-limit:]:
                bars.append(
                    {
                        "timestamp": datetime.fromtimestamp(
                            bar["t"] / 1000
                        ).isoformat(),
                        "open": bar["o"],
                        "high": bar["h"],
                        "low": bar["l"],
                        "close": bar["c"],
                        "volume": bar["v"],
                    }
                )

            return bars

        return self._retry_with_backoff(_get_bars)

    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get quotes for multiple symbols

        Args:
            symbols: List of trading symbols

        Returns:
            Dictionary mapping symbols to quotes
        """
        quotes = {}

        # Polygon doesn't have a batch endpoint, so we fetch individually
        # In production, this could be optimized with concurrent requests
        for symbol in symbols:
            try:
                quotes[symbol] = self.get_quote(symbol)
            except Exception as e:
                logger.warning(f"Failed to get quote for {symbol}: {e}")
                quotes[symbol] = None

        return quotes
