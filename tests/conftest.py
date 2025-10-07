"""
Pytest fixtures for Sentio 2.0 tests
Shared test data and utilities
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any


@pytest.fixture
def sample_ohlcv_data() -> pd.DataFrame:
    """
    Generate sample OHLCV data for testing strategies

    Returns:
        DataFrame with OHLCV columns and 100 rows
    """
    dates = pd.date_range(end=datetime.now(), periods=100, freq="5min")

    # Generate realistic price data with trend
    base_price = 100.0
    returns = np.random.randn(100) * 0.02  # 2% volatility
    prices = base_price * np.exp(np.cumsum(returns))

    data = pd.DataFrame(
        {
            "timestamp": dates,
            "open": prices * (1 + np.random.randn(100) * 0.001),
            "high": prices * (1 + np.abs(np.random.randn(100)) * 0.005),
            "low": prices * (1 - np.abs(np.random.randn(100)) * 0.005),
            "close": prices,
            "volume": np.random.randint(100000, 1000000, 100),
        }
    )

    # Ensure high is highest and low is lowest
    data["high"] = data[["open", "high", "close"]].max(axis=1)
    data["low"] = data[["open", "low", "close"]].min(axis=1)

    return data


@pytest.fixture
def trending_up_data() -> pd.DataFrame:
    """
    Generate OHLCV data with clear upward trend

    Returns:
        DataFrame with upward trending prices
    """
    dates = pd.date_range(end=datetime.now(), periods=100, freq="5min")

    # Generate upward trend
    base_price = 100.0
    trend = np.linspace(0, 0.2, 100)  # 20% gain over period
    noise = np.random.randn(100) * 0.01  # 1% noise
    prices = base_price * np.exp(trend + noise)

    data = pd.DataFrame(
        {
            "timestamp": dates,
            "open": prices * (1 - 0.002),
            "high": prices * (1 + 0.005),
            "low": prices * (1 - 0.005),
            "close": prices,
            "volume": np.random.randint(500000, 1500000, 100),
        }
    )

    return data


@pytest.fixture
def trending_down_data() -> pd.DataFrame:
    """
    Generate OHLCV data with clear downward trend

    Returns:
        DataFrame with downward trending prices
    """
    dates = pd.date_range(end=datetime.now(), periods=100, freq="5min")

    # Generate downward trend
    base_price = 100.0
    trend = np.linspace(0, -0.2, 100)  # 20% loss over period
    noise = np.random.randn(100) * 0.01  # 1% noise
    prices = base_price * np.exp(trend + noise)

    data = pd.DataFrame(
        {
            "timestamp": dates,
            "open": prices * (1 + 0.002),
            "high": prices * (1 + 0.005),
            "low": prices * (1 - 0.005),
            "close": prices,
            "volume": np.random.randint(300000, 800000, 100),
        }
    )

    return data


@pytest.fixture
def sideways_data() -> pd.DataFrame:
    """
    Generate OHLCV data with sideways/ranging market

    Returns:
        DataFrame with ranging prices
    """
    dates = pd.date_range(end=datetime.now(), periods=100, freq="5min")

    # Generate sideways movement
    base_price = 100.0
    noise = np.random.randn(100) * 0.015  # Oscillating around mean
    prices = base_price + base_price * noise

    data = pd.DataFrame(
        {
            "timestamp": dates,
            "open": prices * (1 + np.random.randn(100) * 0.002),
            "high": prices * (1 + np.abs(np.random.randn(100)) * 0.005),
            "low": prices * (1 - np.abs(np.random.randn(100)) * 0.005),
            "close": prices,
            "volume": np.random.randint(400000, 1000000, 100),
        }
    )

    return data


@pytest.fixture
def portfolio_config() -> Dict[str, Any]:
    """
    Standard portfolio configuration for testing

    Returns:
        Dictionary with portfolio parameters
    """
    return {
        "initial_capital": 100000.0,
        "current_value": 105000.0,
        "cash_available": 50000.0,
        "positions_value": 55000.0,
        "daily_pnl": 1500.0,
        "total_return": 0.05,
    }


@pytest.fixture
def risk_config() -> Dict[str, Any]:
    """
    Standard risk management configuration for testing

    Returns:
        Dictionary with risk parameters
    """
    return {
        "max_position_size": 0.05,
        "max_portfolio_risk": 0.20,
        "stop_loss_percent": 0.02,
        "take_profit_percent": 0.05,
        "max_daily_drawdown": 0.03,
        "circuit_breaker_threshold": 0.05,
    }


@pytest.fixture
def sample_trade() -> Dict[str, Any]:
    """
    Sample trade for testing

    Returns:
        Dictionary with trade details
    """
    return {
        "symbol": "AAPL",
        "direction": "long",
        "size": 100,
        "price": 150.0,
        "timestamp": datetime.now(),
        "strategy": "momentum",
    }


@pytest.fixture
def mock_api_token() -> str:
    """
    Mock authentication token for API testing

    Returns:
        Fake JWT token string
    """
    return "mock_jwt_token_for_testing_12345"


@pytest.fixture
def subscription_tiers() -> Dict[str, Dict[str, Any]]:
    """
    Subscription tier configurations for testing

    Returns:
        Dictionary with tier details
    """
    return {
        "free": {
            "price": 0.0,
            "features": {
                "day_trading": False,
                "long_term_investing": True,
                "max_strategies": 2,
                "profit_sharing_rate": 0.0,
            },
        },
        "professional": {
            "price": 99.0,
            "features": {
                "day_trading": True,
                "long_term_investing": True,
                "max_strategies": 5,
                "profit_sharing_rate": 0.15,
            },
        },
        "enterprise": {
            "price": 499.0,
            "features": {
                "day_trading": True,
                "long_term_investing": True,
                "max_strategies": -1,  # unlimited
                "profit_sharing_rate": 0.25,
            },
        },
    }
