"""
Sentio 2.0 Python SDK

Official Python SDK for the Sentio 2.0 Trading API.
Provides easy-to-use client for all API endpoints with type hints and comprehensive error handling.
"""
import requests
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import logging


class SentioAPIError(Exception):
    """Base exception for Sentio API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class SubscriptionTier(str, Enum):
    """Subscription tier options"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TradeSignal(str, Enum):
    """Trade signal types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class SentioClient:
    """
    Sentio 2.0 API Client
    
    Provides access to all Sentio Trading API endpoints with automatic
    authentication, error handling, and retry logic.
    
    Example:
        >>> client = SentioClient(base_url="http://localhost:8000")
        >>> client.login("username", "password")
        >>> signals = client.get_trade_signals(["AAPL", "GOOGL"])
        >>> print(signals)
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Sentio API client
        
        Args:
            base_url: Base URL for the API (default: http://localhost:8000)
            token: Optional JWT token for authentication
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
            logger: Optional logger instance
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            require_auth: Whether authentication is required
            
        Returns:
            Response data as dictionary
            
        Raises:
            SentioAPIError: If request fails
        """
        if require_auth and not self.token:
            raise SentioAPIError("Authentication required. Please login first.")
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise SentioAPIError(
                        "Authentication failed. Token may be expired.",
                        status_code=401,
                        response=response.json() if response.text else None
                    )
                elif response.status_code == 404:
                    raise SentioAPIError(
                        f"Endpoint not found: {endpoint}",
                        status_code=404,
                        response=response.json() if response.text else None
                    )
                elif response.status_code >= 500:
                    if attempt < self.max_retries - 1:
                        self.logger.warning(f"Server error, retrying... (attempt {attempt + 1}/{self.max_retries})")
                        continue
                    raise SentioAPIError(
                        f"Server error: {response.status_code}",
                        status_code=response.status_code,
                        response=response.json() if response.text else None
                    )
                else:
                    error_data = response.json() if response.text else {}
                    raise SentioAPIError(
                        error_data.get("detail", f"Request failed with status {response.status_code}"),
                        status_code=response.status_code,
                        response=error_data
                    )
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Request failed, retrying... (attempt {attempt + 1}/{self.max_retries})")
                    continue
                raise SentioAPIError(f"Request failed: {str(e)}")
        
        raise SentioAPIError("Max retries exceeded")
    
    # Authentication Methods
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and obtain JWT token
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Token response with access_token and expires_in
        """
        response = self._request(
            "POST",
            "/api/v1/auth/login",
            data={"username": username, "password": password},
            require_auth=False
        )
        self.token = response.get("access_token")
        return response
    
    # General Endpoints
    
    def health_check(self) -> Dict[str, Any]:
        """Get API health status"""
        return self._request("GET", "/api/v1/health", require_auth=False)
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status and metrics"""
        return self._request("GET", "/api/v1/status")
    
    # Trading Operations
    
    def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze a stock symbol
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            
        Returns:
            Analysis results with signal and confidence
        """
        return self._request("POST", "/api/v1/analyze", data={"symbol": symbol})
    
    def execute_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute a trade
        
        Args:
            symbol: Stock symbol
            action: Trade action ("buy" or "sell")
            quantity: Number of shares
            price: Optional limit price
            
        Returns:
            Trade execution result
        """
        data = {
            "symbol": symbol,
            "action": action,
            "quantity": quantity
        }
        if price is not None:
            data["price"] = price
        return self._request("POST", "/api/v1/trade", data=data)
    
    def get_positions(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get open positions
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            List of open positions
        """
        params = {"user_id": user_id} if user_id else None
        return self._request("GET", "/api/v1/positions", params=params)
    
    def get_performance(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            Performance metrics and statistics
        """
        params = {"user_id": user_id} if user_id else None
        return self._request("GET", "/api/v1/performance", params=params)
    
    # Strategy Management
    
    def get_strategies(self) -> Dict[str, Any]:
        """Get list of available trading strategies"""
        return self._request("GET", "/api/v1/strategies")
    
    def toggle_strategy(self, strategy_name: str, enabled: bool) -> Dict[str, Any]:
        """
        Enable or disable a trading strategy
        
        Args:
            strategy_name: Name of the strategy
            enabled: True to enable, False to disable
            
        Returns:
            Updated strategy status
        """
        return self._request(
            "POST",
            f"/api/v1/strategies/{strategy_name}/toggle",
            data={"enabled": enabled}
        )
    
    # Analysis & Intelligence
    
    def get_insider_trades(self, symbol: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get insider trades for a symbol
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of trades to return (default: 50)
            
        Returns:
            List of insider trades
        """
        params = {"limit": limit}
        return self._request("GET", f"/api/v1/insider-trades/{symbol}", params=params)
    
    def get_top_insider_symbols(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get top symbols traded by insiders
        
        Args:
            limit: Number of symbols to return (default: 10)
            
        Returns:
            List of top insider-traded symbols
        """
        params = {"limit": limit}
        return self._request("GET", "/api/v1/insider-trades/top", params=params)
    
    def get_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get fundamental analysis for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Fundamental analysis scores and recommendation
        """
        return self._request("GET", f"/api/v1/fundamental/{symbol}")
    
    # Dashboard Endpoints
    
    def get_trade_signals(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get trade signals for multiple symbols
        
        Args:
            symbols: List of stock symbols (default: ["AAPL", "GOOGL", "MSFT", "TSLA"])
            
        Returns:
            Trade signals for each symbol
        """
        params = None
        if symbols:
            params = {"symbols": ",".join(symbols)}
        return self._request("GET", "/api/v1/dashboard/trade-signals", params=params)
    
    def get_earnings(self, user_id: str) -> Dict[str, Any]:
        """
        Get earnings summary for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Comprehensive earnings and performance data
        """
        return self._request("GET", "/api/v1/dashboard/earnings", params={"user_id": user_id})
    
    def get_ai_summary(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get AI-generated trade summary
        
        Args:
            symbol: Optional stock symbol for focused analysis
            
        Returns:
            AI-generated insights and recommendations
        """
        params = {"symbol": symbol} if symbol else None
        return self._request("GET", "/api/v1/dashboard/ai-summary", params=params)
    
    def get_strength_signal(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get market strength signal
        
        Args:
            symbol: Optional stock symbol
            
        Returns:
            Market strength indicators
        """
        params = {"symbol": symbol} if symbol else None
        return self._request("GET", "/api/v1/dashboard/strength-signal", params=params)
    
    def get_trade_journal(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get trade journal entries
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries (default: 50)
            
        Returns:
            List of trade journal entries
        """
        params = {"user_id": user_id, "limit": limit}
        return self._request("GET", "/api/v1/dashboard/trade-journal", params=params)
    
    def add_trade_journal_entry(
        self,
        user_id: str,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a manual trade journal entry
        
        Args:
            user_id: User identifier
            symbol: Stock symbol
            action: Trade action ("buy" or "sell")
            quantity: Number of shares
            price: Trade price
            notes: Optional notes about the trade
            
        Returns:
            Created journal entry
        """
        data = {
            "user_id": user_id,
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price
        }
        if notes:
            data["notes"] = notes
        return self._request("POST", "/api/v1/dashboard/trade-journal", data=data)
    
    def get_performance_cards(self, user_id: str) -> Dict[str, Any]:
        """
        Get performance metrics as dashboard cards
        
        Args:
            user_id: User identifier
            
        Returns:
            Performance metrics formatted as dashboard cards
        """
        return self._request(
            "GET",
            "/api/v1/dashboard/performance-cards",
            params={"user_id": user_id}
        )
    
    # Subscription & Billing
    
    def get_pricing(self) -> Dict[str, Any]:
        """
        Get subscription pricing information
        
        Returns:
            Available subscription tiers and pricing
        """
        return self._request("GET", "/api/v1/subscription/pricing", require_auth=False)
    
    def get_subscription(self, user_id: str) -> Dict[str, Any]:
        """
        Get user subscription details
        
        Args:
            user_id: User identifier
            
        Returns:
            Subscription details and features
        """
        return self._request("GET", f"/api/v1/subscription/{user_id}")
    
    def calculate_profit_sharing(self, user_id: str, profit: float) -> Dict[str, Any]:
        """
        Calculate profit sharing fee
        
        Args:
            user_id: User identifier
            profit: Trading profit amount
            
        Returns:
            Profit sharing calculation
        """
        data = {"user_id": user_id, "profit": profit}
        return self._request("POST", "/api/v1/subscription/profit-sharing/calculate", data=data)
    
    def get_profit_sharing_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Get profit sharing balance
        
        Args:
            user_id: User identifier
            
        Returns:
            Profit sharing balance and history
        """
        return self._request("GET", f"/api/v1/subscription/profit-sharing/{user_id}")
    
    # Utility Methods
    
    def load_dashboard_data(self, user_id: str, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Load all dashboard data in a single call
        
        Args:
            user_id: User identifier
            symbols: Optional list of symbols for trade signals
            
        Returns:
            Dictionary with all dashboard data
        """
        return {
            "performance_cards": self.get_performance_cards(user_id),
            "trade_signals": self.get_trade_signals(symbols),
            "earnings": self.get_earnings(user_id),
            "ai_summary": self.get_ai_summary(),
            "strength_signal": self.get_strength_signal()
        }
    
    def get_portfolio_summary(self) -> Dict:
        url = f"{self.base_url}/api/v1/portfolio/summary"
        resp = requests.get(url, headers=self._headers())
        return resp.json() if resp.status_code == 200 else {}

    def post_custom_metric(self, metric: Dict[str, Any]) -> Dict:
        url = f"{self.base_url}/api/v1/metrics/custom"
        resp = requests.post(url, json=metric, headers=self._headers())
        return resp.json() if resp.status_code == 200 else {}
