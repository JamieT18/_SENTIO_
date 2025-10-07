"""
Utility helper functions for Sentio Trading System
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import asyncio


def format_currency(amount: float, symbol: str = "$") -> str:
    """
    Format currency with thousands separators

    Args:
        amount: Amount to format
        symbol: Currency symbol

    Returns:
        Formatted string
    """
    return f"{symbol}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage value

    Args:
        value: Decimal value (e.g., 0.15 for 15%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_returns(
    entry_price: float, exit_price: float, quantity: float = 1.0
) -> Dict[str, float]:
    """
    Calculate trade returns

    Args:
        entry_price: Entry price
        exit_price: Exit price
        quantity: Number of shares/contracts

    Returns:
        Dictionary with return metrics
    """
    profit = (exit_price - entry_price) * quantity
    return_pct = (exit_price - entry_price) / entry_price

    return {
        "profit": profit,
        "return_pct": return_pct,
        "return_pct_formatted": format_percentage(return_pct),
    }


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio

    Args:
        returns: List of period returns
        risk_free_rate: Annual risk-free rate

    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return 0.0

    returns_array = np.array(returns)
    excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate

    if np.std(excess_returns) == 0:
        return 0.0

    sharpe = np.mean(excess_returns) / np.std(excess_returns)

    # Annualize
    return sharpe * np.sqrt(252)


def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """
    Calculate maximum drawdown

    Args:
        equity_curve: List of equity values over time

    Returns:
        Maximum drawdown as decimal (e.g., 0.15 for 15% drawdown)
    """
    if len(equity_curve) < 2:
        return 0.0

    equity_array = np.array(equity_curve)
    running_max = np.maximum.accumulate(equity_array)
    drawdown = (equity_array - running_max) / running_max

    return float(np.min(drawdown))


def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
    """
    Calculate win rate from trade history

    Args:
        trades: List of trade dictionaries with 'pnl' key

    Returns:
        Win rate as decimal (e.g., 0.65 for 65%)
    """
    if not trades:
        return 0.0

    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    return wins / len(trades)


def calculate_profit_factor(trades: List[Dict[str, Any]]) -> float:
    """
    Calculate profit factor (gross profit / gross loss)

    Args:
        trades: List of trade dictionaries with 'pnl' key

    Returns:
        Profit factor
    """
    if not trades:
        return 0.0

    gross_profit = sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0)
    gross_loss = abs(sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0))

    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def normalize_symbol(symbol: str) -> str:
    """
    Normalize stock symbol (uppercase, strip whitespace)

    Args:
        symbol: Stock symbol

    Returns:
        Normalized symbol
    """
    return symbol.strip().upper()


def is_market_open(dt: Optional[datetime] = None) -> bool:
    """
    Check if US stock market is open

    Args:
        dt: Datetime to check (defaults to now)

    Returns:
        True if market is open
    """
    if dt is None:
        dt = datetime.now()

    # Check if weekend
    if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Check market hours (9:30 AM - 4:00 PM EST)
    market_open = dt.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = dt.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= dt <= market_close


def get_trading_days(
    start_date: datetime, end_date: datetime, exclude_weekends: bool = True
) -> List[datetime]:
    """
    Get list of trading days between dates

    Args:
        start_date: Start date
        end_date: End date
        exclude_weekends: Whether to exclude weekends

    Returns:
        List of trading days
    """
    days = []
    current = start_date

    while current <= end_date:
        if not exclude_weekends or current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)

    return days


def resample_ohlcv(data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resample OHLCV data to different timeframe

    Args:
        data: OHLCV DataFrame with DatetimeIndex
        timeframe: Target timeframe (e.g., '1h', '1d')

    Returns:
        Resampled DataFrame
    """
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("DataFrame must have DatetimeIndex")

    resampled = data.resample(timeframe).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )

    return resampled.dropna()


def calculate_position_value(
    price: float, quantity: float, multiplier: float = 1.0
) -> float:
    """
    Calculate position value

    Args:
        price: Current price
        quantity: Number of shares/contracts
        multiplier: Contract multiplier (default 1.0 for stocks)

    Returns:
        Position value
    """
    return price * quantity * multiplier


def calculate_required_margin(
    price: float, quantity: float, margin_requirement: float = 0.25
) -> float:
    """
    Calculate required margin for a position

    Args:
        price: Current price
        quantity: Number of shares
        margin_requirement: Margin requirement (e.g., 0.25 for 25%)

    Returns:
        Required margin
    """
    position_value = calculate_position_value(price, quantity)
    return position_value * margin_requirement


def format_timestamp(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime as string

    Args:
        dt: Datetime object
        format: Format string

    Returns:
        Formatted string
    """
    return dt.strftime(format)


def parse_timeframe(timeframe: str) -> timedelta:
    """
    Parse timeframe string to timedelta

    Args:
        timeframe: Timeframe string (e.g., '5min', '1h', '1d')

    Returns:
        Timedelta object
    """
    if timeframe.endswith("min"):
        minutes = int(timeframe[:-3])
        return timedelta(minutes=minutes)
    elif timeframe.endswith("h"):
        hours = int(timeframe[:-1])
        return timedelta(hours=hours)
    elif timeframe.endswith("d"):
        days = int(timeframe[:-1])
        return timedelta(days=days)
    else:
        raise ValueError(f"Invalid timeframe format: {timeframe}")


def validate_trade_params(
    symbol: str, quantity: float, price: float
) -> tuple[bool, Optional[str]]:
    """
    Validate trade parameters

    Args:
        symbol: Trading symbol
        quantity: Number of shares
        price: Price per share

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not symbol or len(symbol.strip()) == 0:
        return False, "Symbol cannot be empty"

    if quantity <= 0:
        return False, "Quantity must be positive"

    if price <= 0:
        return False, "Price must be positive"

    return True, None


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails

    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def async_run(coro):
    """
    Run an async coroutine synchronously (for quick utility use)
    """
    return asyncio.get_event_loop().run_until_complete(coro)


def moving_average(data: List[float], window: int = 5) -> List[float]:
    """
    Calculate moving average for a list of floats
    """
    if len(data) < window:
        return []
    return np.convolve(data, np.ones(window)/window, mode='valid').tolist()


def zscore(data: List[float]) -> List[float]:
    """
    Calculate z-score for a list of floats
    """
    arr = np.array(data)
    mean = np.mean(arr)
    std = np.std(arr)
    return ((arr - mean) / std).tolist() if std > 0 else [0]*len(arr)


def df_to_dict(df: pd.DataFrame) -> dict:
    """
    Convert pandas DataFrame to dictionary
    """
    return df.to_dict(orient='records')
