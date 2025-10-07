"""
Market Data Manager
Handles retrieval and caching of market data from various providers
"""

from typing import Dict, Any
import pandas as pd
from datetime import datetime
import yfinance as yf
from ..core.logger import get_logger
from ..core.config import get_config
import requests
import numpy as np
import finnhub
from sentio.core.logger import SentioLogger

logger = get_logger(__name__)
config = get_config()
structured_logger = SentioLogger.get_structured_logger("market_data")

FINNHUB_API_KEY = getattr(config, 'finnhub_api_key', None)
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY) if FINNHUB_API_KEY else None

class MarketDataManager:
    def get_alternative_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch alternative data (satellite, weather, ESG, blockchain, etc.)
        """
        # Mock implementation, replace with real API calls
        return {
            "symbol": symbol,
            "satellite_activity": np.random.uniform(0, 1),
            "weather_impact": np.random.uniform(-1, 1),
            "esg_score": np.random.uniform(0, 100),
            "blockchain_activity": np.random.randint(0, 10000),
            "timestamp": datetime.now().isoformat(),
        }

    def stream_market_data(self, symbol: str, callback, interval: int = 5):
        """
        Stream real-time market data using polling or websocket
        """
        import threading, time
        def poll():
            while True:
                data = self.get_quote(symbol)
                callback(data)
                time.sleep(interval)
        t = threading.Thread(target=poll, daemon=True)
        t.start()
        logger.info(f"Started streaming for {symbol}")

    def ml_anomaly_detection(self, data: np.ndarray) -> Dict[str, Any]:
        """
        ML-based anomaly detection for market data
        """
        from sklearn.ensemble import IsolationForest
        clf = IsolationForest()
        preds = clf.fit_predict(data.reshape(-1, 1))
        anomalies = np.where(preds == -1)[0].tolist()
        return {"anomalies": anomalies, "count": len(anomalies)}

    def enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature engineering, normalization, outlier handling
        """
        df = df.copy()
        # Normalize columns
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df:
                df[col + "_norm"] = (df[col] - df[col].mean()) / (df[col].std() + 1e-6)
        # Outlier handling
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df:
                q_low = df[col].quantile(0.01)
                q_high = df[col].quantile(0.99)
                df[col] = np.clip(df[col], q_low, q_high)
        return df

    def diagnostics_hook(self, info: Dict[str, Any]):
        """
        Diagnostics callback for monitoring and billing
        """
        logger.info(f"Diagnostics: {info}")

    def distributed_aggregate(self, data_list: list) -> pd.DataFrame:
        """
        Aggregate data from distributed sources for federated analytics
        """
        dfs = [pd.DataFrame(d) for d in data_list]
        result = pd.concat(dfs).groupby('timestamp').mean().reset_index()
        logger.info(f"Distributed aggregation complete: {len(result)} rows")
        return result
    """
    Manages market data retrieval and caching

    Features:
    - Multi-provider support (yfinance, Alpaca, Polygon, etc.)
    - Data caching with TTL
    - Real-time and historical data
    - Multiple timeframes
    """

    def __init__(self, use_real_data: bool = True):
        """Initialize market data manager

        Args:
            use_real_data: If True, fetch from real providers (yfinance). If False, use mock data.
        """
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        # Use configurable cache TTL
        self.cache_ttl: int = (
            config.cache.market_data_ttl if hasattr(config, "cache") else 60
        )
        self.quote_cache_ttl: int = (
            config.cache.quote_ttl if hasattr(config, "cache") else 30
        )
        self.use_real_data = use_real_data
        self.provider = (
            config.market_data.provider
            if hasattr(config, "market_data")
            else "yfinance"
        )
        logger.info(
            f"Market data manager initialized (use_real_data={use_real_data}, provider={self.provider}, cache_ttl={self.cache_ttl}s)"
        )

    def _is_cache_valid(self, cache_key: str, use_quote_ttl: bool = False) -> bool:
        """Check if cached data is still valid based on TTL

        Args:
            cache_key: Cache key to check
            use_quote_ttl: If True, use shorter quote TTL instead of regular cache TTL

        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self.cache_timestamps:
            return False

        age = (datetime.now() - self.cache_timestamps[cache_key]).total_seconds()
        ttl = self.quote_cache_ttl if use_quote_ttl else self.cache_ttl
        return age < ttl

    def _fetch_real_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Fetch real market data from yfinance

        Args:
            symbol: Trading symbol
            timeframe: Data timeframe (1min, 5min, 1hour, 1day)
            limit: Number of bars to retrieve

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)

            # Map timeframe to yfinance interval and period
            interval_map = {
                "1min": "1m",
                "2min": "2m",
                "5min": "5m",
                "15min": "15m",
                "30min": "30m",
                "1hour": "1h",
                "1day": "1d",
                "1week": "1wk",
                "1month": "1mo",
            }

            period_map = {
                "1min": "1d",
                "2min": "1d",
                "5min": "5d",
                "15min": "5d",
                "30min": "1mo",
                "1hour": "1mo",
                "1day": "1y",
                "1week": "2y",
                "1month": "5y",
            }

            interval = interval_map.get(timeframe, "5m")
            period = period_map.get(timeframe, "5d")

            # Fetch historical data
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No data returned from yfinance for {symbol}")
                return self._create_mock_data(symbol, limit)

            # Standardize column names to lowercase
            df.columns = df.columns.str.lower()

            # Ensure we have the required columns
            required_cols = ["open", "high", "low", "close", "volume"]
            if not all(col in df.columns for col in required_cols):
                logger.warning(
                    f"Missing required columns for {symbol}, using mock data"
                )
                return self._create_mock_data(symbol, limit)

            # Return last 'limit' rows
            result = df[required_cols].tail(limit)

            logger.info(
                f"Fetched {len(result)} bars for {symbol} ({timeframe}) from yfinance"
            )
            return result

        except Exception as e:
            logger.error(f"Error fetching real data for {symbol}: {e}")
            return self._create_mock_data(symbol, limit)

    def _create_mock_data(self, symbol: str, limit: int) -> pd.DataFrame:
        """Create mock market data for testing

        Args:
            symbol: Trading symbol
            limit: Number of bars to create

        Returns:
            DataFrame with mock OHLCV data
        """
        # Create mock DataFrame with basic structure
        data = pd.DataFrame(
            {
                "open": [100.0] * limit,
                "high": [101.0] * limit,
                "low": [99.0] * limit,
                "close": [100.5] * limit,
                "volume": [1000000] * limit,
            },
            index=pd.date_range(end=datetime.now(), periods=limit, freq="5min"),
        )

        return data

    def get_data(
        self, symbol: str, timeframe: str = "5min", limit: int = 100
    ) -> pd.DataFrame:
        """
        Get market data for a symbol

        Args:
            symbol: Trading symbol
            timeframe: Data timeframe (1min, 5min, 1hour, 1day)
            limit: Number of bars to retrieve

        Returns:
            DataFrame with OHLCV data
        """
        structured_logger.log_event(
            "data_fetch",
            f"Fetching data for {symbol}",
            {"symbol": symbol, "timeframe": timeframe, "limit": limit}
        )
        cache_key = f"{symbol}_{timeframe}_{limit}"

        # Check cache validity
        if cache_key in self.cache and self._is_cache_valid(cache_key):
            cached_data = self.cache[cache_key]
            if isinstance(cached_data, pd.DataFrame) and not cached_data.empty:
                logger.debug(f"Returning cached data for {symbol} ({timeframe})")
                return cached_data

        # Fetch data based on configuration
        if self.use_real_data:
            try:
                data = self._fetch_real_data(symbol, timeframe, limit)
                structured_logger.log_event(
                    "data_fetch_result",
                    f"Data fetched for {symbol}",
                    {"data_shape": getattr(data, 'shape', str(data)[:200])}
                )
            except Exception as e:
                structured_logger.log_event(
                    "data_fetch_error",
                    str(e),
                    {"symbol": symbol, "timeframe": timeframe, "limit": limit, "exception": repr(e)},
                    level="error"
                )
                data = self._create_mock_data(symbol, limit)
        else:
            logger.debug(f"Using mock data for {symbol} ({timeframe})")
            data = self._create_mock_data(symbol, limit)

        # Cache the data
        self.cache[cache_key] = data
        self.cache_timestamps[cache_key] = datetime.now()

        return data

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get current quote for a symbol with optimized caching

        Args:
            symbol: Trading symbol

        Returns:
            Quote data with price, bid, ask, volume
        """
        # Check cache first with shorter TTL for quotes
        cache_key = f"quote_{symbol}"
        if cache_key in self.cache and self._is_cache_valid(
            cache_key, use_quote_ttl=True
        ):
            logger.debug(f"Returning cached quote for {symbol}")
            return self.cache[cache_key]

        if self.use_real_data:
            try:
                ticker = yf.Ticker(symbol)

                # Get current price info
                info = ticker.info

                # Try to get real-time data from fast_info (yfinance v0.2.28+)
                try:
                    current_price = ticker.fast_info.last_price
                    prev_close = ticker.fast_info.previous_close
                except (AttributeError, KeyError, Exception):
                    current_price = info.get(
                        "currentPrice", info.get("regularMarketPrice", 100.0)
                    )
                    prev_close = info.get("previousClose", 100.0)

                # Get intraday data for bid/ask (if available)
                intraday = ticker.history(period="1d", interval="1m")

                if not intraday.empty:
                    latest = intraday.iloc[-1]
                    high = float(latest.get("High", current_price * 1.01))
                    low = float(latest.get("Low", current_price * 0.99))
                    volume = int(latest.get("Volume", 0))
                else:
                    high = current_price * 1.01
                    low = current_price * 0.99
                    volume = info.get("volume", 0)

                quote = {
                    "symbol": symbol,
                    "price": float(current_price),
                    "bid": float(current_price * 0.9998),  # Estimate bid
                    "ask": float(current_price * 1.0002),  # Estimate ask
                    "high": high,
                    "low": low,
                    "volume": volume,
                    "prev_close": float(prev_close),
                    "change": float(current_price - prev_close),
                    "change_pct": (
                        float((current_price - prev_close) / prev_close * 100)
                        if prev_close
                        else 0
                    ),
                    "timestamp": datetime.now().isoformat(),
                }

                # Cache the quote
                self.cache[cache_key] = quote
                self.cache_timestamps[cache_key] = datetime.now()

                logger.info(f"Fetched real quote for {symbol}: ${current_price:.2f}")
                return quote

            except Exception as e:
                logger.error(f"Error fetching real quote for {symbol}: {e}")
                # Fall back to mock data

        # Return mock quote data
        mock_quote = {
            "symbol": symbol,
            "price": 100.0,
            "bid": 99.98,
            "ask": 100.02,
            "high": 101.0,
            "low": 99.0,
            "volume": 1000000,
            "prev_close": 99.5,
            "change": 0.5,
            "change_pct": 0.5,
            "timestamp": datetime.now().isoformat(),
        }
        # Cache mock quote too for consistency
        self.cache[cache_key] = mock_quote
        self.cache_timestamps[cache_key] = datetime.now()
        return mock_quote

    def get_historical(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Get historical data for a symbol

        Args:
            symbol: Trading symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with historical OHLCV data
        """
        if self.use_real_data:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)

                if df.empty:
                    logger.warning(
                        f"No historical data for {symbol} from {start_date} to {end_date}"
                    )
                    return self._create_mock_data(symbol, 100)

                # Standardize column names
                df.columns = df.columns.str.lower()

                logger.info(f"Fetched {len(df)} historical bars for {symbol}")
                return df

            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol}: {e}")

        # Fallback to mock data
        logger.debug(
            f"Using mock historical data for {symbol}: {start_date} to {end_date}"
        )
        return self._create_mock_data(symbol, 100)

    def get_multiple_quotes(self, symbols: list) -> Dict[str, Dict[str, Any]]:
        """
        Get quotes for multiple symbols efficiently using batch fetching

        Args:
            symbols: List of trading symbols

        Returns:
            Dictionary mapping symbols to quote data
        """
        quotes = {}

        # Check cache first
        uncached_symbols = []
        for symbol in symbols:
            cache_key = f"quote_{symbol}"
            if cache_key in self.cache and self._is_cache_valid(
                cache_key, use_quote_ttl=True
            ):
                quotes[symbol] = self.cache[cache_key]
            else:
                uncached_symbols.append(symbol)

        # Batch fetch uncached symbols if using real data
        if uncached_symbols and self.use_real_data:
            try:
                # Use yfinance's batch download for efficiency
                import yfinance as yf

                tickers = yf.Tickers(" ".join(uncached_symbols))

                for symbol in uncached_symbols:
                    try:
                        ticker = tickers.tickers[symbol]
                        info = ticker.info

                        # Try to get real-time data
                        try:
                            current_price = ticker.fast_info.last_price
                            prev_close = ticker.fast_info.previous_close
                        except (AttributeError, KeyError, Exception):
                            current_price = info.get(
                                "currentPrice", info.get("regularMarketPrice", 100.0)
                            )
                            prev_close = info.get("previousClose", 100.0)

                        quote = {
                            "symbol": symbol,
                            "price": float(current_price),
                            "bid": float(current_price * 0.9998),
                            "ask": float(current_price * 1.0002),
                            "high": float(current_price * 1.01),
                            "low": float(current_price * 0.99),
                            "volume": info.get("volume", 0),
                            "prev_close": float(prev_close),
                            "change": float(current_price - prev_close),
                            "change_pct": (
                                float((current_price - prev_close) / prev_close * 100)
                                if prev_close
                                else 0
                            ),
                            "timestamp": datetime.now().isoformat(),
                        }

                        # Cache the quote
                        cache_key = f"quote_{symbol}"
                        self.cache[cache_key] = quote
                        self.cache_timestamps[cache_key] = datetime.now()
                        quotes[symbol] = quote

                    except Exception as e:
                        logger.warning(f"Error in batch quote for {symbol}: {e}")
                        # Fallback to individual fetch
                        quotes[symbol] = self.get_quote(symbol)

            except Exception as e:
                logger.error(f"Error in batch quote fetch: {e}")
                # Fallback to individual fetches
                for symbol in uncached_symbols:
                    quotes[symbol] = self.get_quote(symbol)
        else:
            # Use mock data or individual fetch for uncached symbols
            for symbol in uncached_symbols:
                quotes[symbol] = self.get_quote(symbol)

        return quotes

    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("Market data cache cleared")

    def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector performance data (mock or real)"""
        if finnhub_client:
            try:
                sectors = finnhub_client.sector()
                perf = {s['name']: s['performance'] for s in sectors}
                return {"sector_performance": perf, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Finnhub sector performance error: {e}")
        # In production, fetch from provider (e.g., Alpha Vantage, Finnhub)
        # Here, mock data for demonstration
        sectors = [
            "Technology", "Healthcare", "Finance", "Energy", "Consumer", "Utilities"
        ]
        perf = {s: np.random.uniform(-2, 2) for s in sectors}
        return {"sector_performance": perf, "timestamp": datetime.now().isoformat()}

    def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get news sentiment for a symbol (mock or real)"""
        if finnhub_client:
            try:
                news = finnhub_client.general_news(symbol)
                sentiment = np.mean([n.get('sentiment', 0) for n in news]) if news else 0.0
                headlines = [n['headline'] for n in news[:3]]
                return {"symbol": symbol, "sentiment": sentiment, "headlines": headlines, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Finnhub news sentiment error: {e}")
        # In production, fetch from news API (e.g., NewsAPI, Finnhub)
        # Here, mock data for demonstration
        sentiment = np.random.uniform(-1, 1)
        headlines = [
            f"{symbol} beats earnings expectations!",
            f"{symbol} faces regulatory scrutiny.",
            f"{symbol} launches new product line.",
        ]
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "headlines": headlines,
            "timestamp": datetime.now().isoformat(),
        }

    def get_macro_trends(self) -> Dict[str, Any]:
        """Get macroeconomic trend data (mock or real)"""
        if finnhub_client:
            try:
                macro = {
                    "gdp_growth": finnhub_client.economic_data('GDP'),
                    "inflation": finnhub_client.economic_data('CPI'),
                    "unemployment": finnhub_client.economic_data('UNRATE'),
                    "interest_rate": finnhub_client.economic_data('FEDFUNDS'),
                }
                return {"macro_trends": macro, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Finnhub macro trends error: {e}")
        # In production, fetch from macro data provider
        # Here, mock data for demonstration
        macro = {
            "gdp_growth": np.random.uniform(1, 4),
            "inflation": np.random.uniform(1, 5),
            "unemployment": np.random.uniform(3, 7),
            "interest_rate": np.random.uniform(0.5, 5),
        }
        return {"macro_trends": macro, "timestamp": datetime.now().isoformat()}

    def get_etf_flows(self) -> Dict[str, Any]:
        """Get ETF flows data (mock or real)"""
        if finnhub_client:
            try:
                etfs = ["SPY", "QQQ", "VTI", "ARKK", "XLF", "XLV"]
                flows = {etf: finnhub_client.etf_profile(etf).get('fundFlows', 0) for etf in etfs}
                return {"etf_flows": flows, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Finnhub ETF flows error: {e}")
        # In production, fetch from provider (e.g., Alpha Vantage, Finnhub)
        # Here, mock data for demonstration
        etfs = ["SPY", "QQQ", "VTI", "ARKK", "XLF", "XLV"]
        flows = {etf: np.random.uniform(-500, 500) for etf in etfs}
        return {"etf_flows": flows, "timestamp": datetime.now().isoformat()}

    def get_global_events(self) -> Dict[str, Any]:
        """Get global event impact analytics (mock or real)"""
        if finnhub_client:
            try:
                events = finnhub_client.economic_calendar()
                parsed = [{"event": e['event'], "impact": e.get('impact', 0)} for e in events[:4]]
                return {"global_events": parsed, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Finnhub global events error: {e}")
        # In production, fetch from provider (e.g., Alpha Vantage, Finnhub)
        # Here, mock data for demonstration
        events = [
            {"event": "Fed Rate Decision", "impact": np.random.uniform(-1, 1)},
            {"event": "OPEC Meeting", "impact": np.random.uniform(-1, 1)},
            {"event": "Elections", "impact": np.random.uniform(-1, 1)},
            {"event": "Geopolitical Tension", "impact": np.random.uniform(-1, 1)},
        ]
        return {"global_events": events, "timestamp": datetime.now().isoformat()}
