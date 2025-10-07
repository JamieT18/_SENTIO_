"""
Validation utilities for Sentio 2.0
"""
import re
from typing import Dict

def validate_email(email: str) -> bool:
    """
    Validate email format.
    Args:
        email: Email string
    Returns:
        bool: True if valid, False otherwise
    Raises:
        ValueError: If email is empty
    """
    if not email:
        raise ValueError("email must not be empty")
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def validate_portfolio(portfolio: Dict[str, float]) -> bool:
    """
    Validate portfolio data structure.
    Args:
        portfolio: Portfolio dict
    Returns:
        bool: True if valid, False otherwise
    Raises:
        ValueError: If portfolio is empty
    """
    if not portfolio:
        raise ValueError("portfolio must not be empty")
    return isinstance(portfolio, dict) and all(isinstance(v, (int, float)) for v in portfolio.values())

def validate_symbol(symbol: str) -> bool:
    """
    Validate trading symbol format (uppercase, alphanumeric)
    """
    return symbol.isalnum() and symbol.isupper()

def validate_trade_params_dict(params: Dict) -> bool:
    """
    Validate trade params dict structure
    """
    required = ['symbol', 'quantity', 'price']
    return all(k in params for k in required) and validate_symbol(params['symbol'])

def validate_batch_data(batch: list) -> bool:
    """
    Validate batch data for processing
    """
    return isinstance(batch, list) and all(isinstance(item, dict) for item in batch)
