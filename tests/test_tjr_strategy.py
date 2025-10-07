"""
Unit tests for TJR Strategy
Tests the Three Jump Rule strategy implementation
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from sentio.strategies.tjr_strategy import TJRStrategy
from sentio.strategies.base import SignalType, TradingSignal


@pytest.mark.unit
@pytest.mark.strategy
class TestTJRStrategy:
    """Test TJR Strategy functionality"""

    @pytest.fixture
    def tjr_strategy(self):
        """Create a TJR strategy instance"""
        return TJRStrategy()

    def test_initialization(self, tjr_strategy):
        """Test TJR strategy initialization"""
        assert tjr_strategy.name == "TJR"
        assert tjr_strategy.timeframe == "5min"
        assert tjr_strategy.min_confidence == 0.70
        assert tjr_strategy.volume_threshold == 1.2
        assert tjr_strategy.enabled is True

    def test_analyze_with_valid_data(self, tjr_strategy, sample_ohlcv_data):
        """Test analysis with valid OHLCV data"""
        analysis = tjr_strategy.analyze(sample_ohlcv_data)

        assert "pattern_found" in analysis
        assert "bullish_pattern" in analysis
        assert "bearish_pattern" in analysis
        assert "current_price" in analysis
        assert "rsi" in analysis

    def test_analyze_with_insufficient_data(self, tjr_strategy):
        """Test analysis with insufficient data points"""
        # Create small dataset
        small_data = pd.DataFrame(
            {
                "open": [100, 101],
                "high": [102, 103],
                "low": [99, 100],
                "close": [101, 102],
                "volume": [1000, 1100],
            }
        )

        analysis = tjr_strategy.analyze(small_data)

        assert analysis["pattern_found"] is False
        assert "reason" in analysis

    def test_execute_with_trending_up_data(self, tjr_strategy, trending_up_data):
        """Test strategy execution with upward trending data"""
        signal = tjr_strategy.execute(trending_up_data)

        assert isinstance(signal, TradingSignal)
        assert signal.strategy_name == "TJR"
        assert signal.symbol is not None
        assert 0.0 <= signal.confidence <= 1.0

    def test_execute_with_trending_down_data(self, tjr_strategy, trending_down_data):
        """Test strategy execution with downward trending data"""
        signal = tjr_strategy.execute(trending_down_data)

        assert isinstance(signal, TradingSignal)
        assert signal.strategy_name == "TJR"

    def test_execute_with_sideways_data(self, tjr_strategy, sideways_data):
        """Test strategy execution with sideways market"""
        signal = tjr_strategy.execute(sideways_data)

        assert isinstance(signal, TradingSignal)
        # In sideways market, signal should likely be HOLD
        # or have low confidence
        if signal.signal_type != SignalType.HOLD:
            assert signal.confidence < 0.8

    def test_signal_confidence_bounds(self, tjr_strategy, sample_ohlcv_data):
        """Test that signal confidence is within valid bounds"""
        signal = tjr_strategy.execute(sample_ohlcv_data)

        assert 0.0 <= signal.confidence <= 1.0

    def test_disabled_strategy_returns_hold(self, tjr_strategy, sample_ohlcv_data):
        """Test that disabled strategy returns HOLD signal"""
        tjr_strategy.enabled = False
        signal = tjr_strategy.execute(sample_ohlcv_data)

        assert signal.signal_type == SignalType.HOLD
        assert signal.confidence == 0.0

    def test_custom_parameters(self):
        """Test TJR strategy with custom parameters"""
        strategy = TJRStrategy(
            name="CustomTJR",
            timeframe="15min",
            min_confidence=0.80,
            volume_threshold=1.5,
            price_jump_min=0.01,
        )

        assert strategy.name == "CustomTJR"
        assert strategy.timeframe == "15min"
        assert strategy.min_confidence == 0.80
        assert strategy.volume_threshold == 1.5
        assert strategy.price_jump_min == 0.01
