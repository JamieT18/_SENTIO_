"""
Edge case tests for Sentio data manager
"""
import pytest
from sentio.data.market_data import MarketDataManager

def test_market_data_manager_init():
    manager = MarketDataManager()
    assert manager is not None
