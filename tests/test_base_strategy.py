"""
Tests for base strategy module
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from sentio.strategies.base import SignalType, StrategyType, TradingSignal, BaseStrategy


def test_signal_type_enum():
    """Test SignalType enum values"""
    assert SignalType.BUY.value == "buy"
    assert SignalType.SELL.value == "sell"
    assert SignalType.HOLD.value == "hold"
    assert SignalType.CLOSE_LONG.value == "close_long"
    assert SignalType.CLOSE_SHORT.value == "close_short"


def test_strategy_type_enum():
    """Test StrategyType enum values"""
    assert StrategyType.SCALPING.value == "scalping"
    assert StrategyType.DAY_TRADING.value == "day_trading"
    assert StrategyType.SWING.value == "swing"
    assert StrategyType.MOMENTUM.value == "momentum"
    assert StrategyType.MEAN_REVERSION.value == "mean_reversion"
    assert StrategyType.BREAKOUT.value == "breakout"
    assert StrategyType.TJR.value == "tjr"


def test_trading_signal_creation():
    """Test TradingSignal creation with valid data"""
    signal = TradingSignal(
        signal_type=SignalType.BUY,
        confidence=0.8,
        strategy_name="TestStrategy",
        symbol="AAPL",
        timestamp=datetime.now(),
        price=150.0,
    )
    assert signal.signal_type == SignalType.BUY
    assert signal.confidence == 0.8
    assert signal.strategy_name == "TestStrategy"
    assert signal.symbol == "AAPL"
    assert signal.price == 150.0


def test_trading_signal_confidence_validation():
    """Test TradingSignal validates confidence is between 0 and 1"""
    with pytest.raises(ValueError):
        TradingSignal(
            signal_type=SignalType.BUY,
            confidence=1.5,  # Invalid: > 1.0
            strategy_name="TestStrategy",
            symbol="AAPL",
            timestamp=datetime.now(),
            price=150.0,
        )

    with pytest.raises(ValueError):
        TradingSignal(
            signal_type=SignalType.BUY,
            confidence=-0.1,  # Invalid: < 0.0
            strategy_name="TestStrategy",
            symbol="AAPL",
            timestamp=datetime.now(),
            price=150.0,
        )


def test_trading_signal_low_confidence_becomes_hold():
    """Test that low confidence signals become HOLD"""
    signal = TradingSignal(
        signal_type=SignalType.BUY,
        confidence=0.3,  # Low confidence
        strategy_name="TestStrategy",
        symbol="AAPL",
        timestamp=datetime.now(),
        price=150.0,
    )
    # Low confidence signals should be converted to HOLD
    assert signal.signal_type == SignalType.HOLD


class ConcreteStrategy(BaseStrategy):
    """Concrete implementation of BaseStrategy for testing"""

    def __init__(self):
        super().__init__(
            name="TestStrategy",
            strategy_type=StrategyType.MOMENTUM,
            timeframe="5min",
            min_confidence=0.65,
            enabled=True,
        )

    def analyze(self, data: pd.DataFrame):
        """Simple analysis implementation"""
        return {
            "sma_20": (
                data["close"].rolling(20).mean().iloc[-1]
                if len(data) >= 20
                else data["close"].iloc[-1]
            ),
            "sma_50": (
                data["close"].rolling(50).mean().iloc[-1]
                if len(data) >= 50
                else data["close"].iloc[-1]
            ),
        }

    def get_signal(self, data: pd.DataFrame, analysis: dict):
        """Simple signal generation"""
        current_price = data["close"].iloc[-1]
        confidence = self.calculate_confidence(data, analysis)

        if analysis["sma_20"] > analysis["sma_50"]:
            signal_type = SignalType.BUY
        elif analysis["sma_20"] < analysis["sma_50"]:
            signal_type = SignalType.SELL
        else:
            signal_type = SignalType.HOLD

        return TradingSignal(
            signal_type=signal_type,
            confidence=confidence,
            strategy_name=self.name,
            symbol="TEST",
            timestamp=datetime.now(),
            price=current_price,
        )

    def calculate_confidence(self, data: pd.DataFrame, analysis: dict):
        """Simple confidence calculation"""
        return 0.75


def test_base_strategy_initialization():
    """Test BaseStrategy initialization"""
    strategy = ConcreteStrategy()
    assert strategy.name == "TestStrategy"
    assert strategy.strategy_type == StrategyType.MOMENTUM
    assert strategy.timeframe == "5min"
    assert strategy.min_confidence == 0.65
    assert strategy.enabled is True


def test_base_strategy_execute():
    """Test BaseStrategy execute method"""
    strategy = ConcreteStrategy()

    # Create sample data
    data = pd.DataFrame(
        {
            "open": np.random.uniform(100, 110, 100),
            "high": np.random.uniform(110, 120, 100),
            "low": np.random.uniform(90, 100, 100),
            "close": np.random.uniform(100, 110, 100),
            "volume": np.random.randint(1000000, 10000000, 100),
        }
    )

    signal = strategy.execute(data)
    assert isinstance(signal, TradingSignal)
    assert signal.strategy_name == "TestStrategy"


def test_base_strategy_disabled():
    """Test BaseStrategy when disabled returns HOLD signal"""
    strategy = ConcreteStrategy()
    strategy.enabled = False

    data = pd.DataFrame(
        {
            "open": [100, 101, 102],
            "high": [105, 106, 107],
            "low": [95, 96, 97],
            "close": [100, 101, 102],
            "volume": [1000000, 1100000, 1200000],
        }
    )

    signal = strategy.execute(data)
    assert signal.signal_type == SignalType.HOLD
    assert signal.confidence == 0.0


def test_base_strategy_performance_metrics():
    """Test BaseStrategy performance metrics"""
    strategy = ConcreteStrategy()

    # Add some mock trade results
    strategy.update_performance({"profit": 100.0})
    strategy.update_performance({"profit": -50.0})
    strategy.update_performance({"profit": 75.0})

    metrics = strategy.get_performance_metrics()
    assert metrics["total_trades"] == 3
    assert metrics["win_rate"] == 2 / 3  # 2 winning trades out of 3
    assert metrics["avg_return"] == pytest.approx(41.67, rel=1e-2)


def test_base_strategy_reset():
    """Test BaseStrategy reset method"""
    strategy = ConcreteStrategy()

    # Set some state
    data = pd.DataFrame(
        {"open": [100], "high": [105], "low": [95], "close": [100], "volume": [1000000]}
    )
    strategy.execute(data)
    strategy.update_performance({"profit": 100.0})

    # Reset
    strategy.reset()

    assert strategy.last_signal is None
    assert len(strategy.performance_history) == 0
