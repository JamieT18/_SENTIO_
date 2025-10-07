"""
API utility functions for response formatting and common operations
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps
from fastapi import HTTPException

from ..core.logger import get_logger
from ..core.constants import (
    STATUS_SUCCESS,
    STATUS_WARNING,
    STATUS_ERROR,
    TREND_UP,
    TREND_DOWN,
)

logger = get_logger(__name__)


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime to ISO format string

    Args:
        dt: datetime object, defaults to now()

    Returns:
        ISO formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def create_success_response(
    message: str, data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized success response

    Args:
        message: Success message
        data: Optional additional data

    Returns:
        Standardized response dictionary
    """
    response = {
        "status": STATUS_SUCCESS,
        "message": message,
        "timestamp": format_timestamp(),
    }
    if data:
        response.update(data)
    return response


def create_error_response(
    message: str, details: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response

    Args:
        message: Error message
        details: Optional error details

    Returns:
        Standardized error response dictionary
    """
    response = {
        "status": STATUS_ERROR,
        "message": message,
        "timestamp": format_timestamp(),
    }
    if details:
        response["details"] = details
    return response


def create_warning_response(
    message: str, data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized warning response

    Args:
        message: Warning message
        data: Optional additional data

    Returns:
        Standardized warning response dictionary
    """
    response = {
        "status": STATUS_WARNING,
        "message": message,
        "timestamp": format_timestamp(),
    }
    if data:
        response.update(data)
    return response


def get_trend_direction(value: float) -> str:
    """
    Determine trend direction based on value

    Args:
        value: Numeric value to evaluate

    Returns:
        'up' or 'down' trend indicator
    """
    return TREND_UP if value > 0 else TREND_DOWN


def api_error_handler(func):
    """
    Decorator for standardized API error handling

    Args:
        func: Async function to wrap

    Returns:
        Wrapped function with error handling
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTPExceptions as-is
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return wrapper


def format_performance_card(
    card_id: str,
    title: str,
    value: str,
    change: Optional[float] = None,
    change_label: Optional[str] = None,
    subtitle: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create standardized performance card

    Args:
        card_id: Unique card identifier
        title: Card title
        value: Main value to display
        change: Optional numeric change value
        change_label: Optional formatted change label
        subtitle: Optional subtitle text

    Returns:
        Performance card dictionary
    """
    card = {"id": card_id, "title": title, "value": value}

    if change is not None:
        card["change"] = change
        card["trend"] = get_trend_direction(change)

    if change_label:
        card["change_label"] = change_label

    if subtitle:
        card["subtitle"] = subtitle

    return card


def format_journal_entry(trade: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format trade data into journal entry

    Args:
        trade: Trade dictionary from history

    Returns:
        Formatted journal entry
    """
    timestamp = trade.get("timestamp", datetime.now())
    if isinstance(timestamp, datetime):
        timestamp_str = format_timestamp(timestamp)
    else:
        timestamp_str = str(timestamp)

    return {
        "symbol": trade.get("symbol", "N/A"),
        "action": trade.get("direction", "N/A"),
        "quantity": trade.get("size", 0),
        "entry_price": trade.get("entry_price", 0),
        "exit_price": trade.get("exit_price", 0),
        "pnl": trade.get("pnl", 0),
        "timestamp": timestamp_str,
        "notes": trade.get("notes", ""),
    }


def parse_symbol_list(symbols: Optional[str], default: List[str]) -> List[str]:
    """
    Parse comma-separated symbol string into list

    Args:
        symbols: Comma-separated symbol string or None
        default: Default symbol list if None

    Returns:
        List of symbol strings
    """
    if symbols:
        return [s.strip() for s in symbols.split(",")]
    return default
