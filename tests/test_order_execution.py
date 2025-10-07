"""
Unit tests for order execution and tracking
Tests the automated trade execution functionality
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from sentio.execution.trading_engine import TradingEngine, TradingMode, OrderStatus
from sentio.strategies.base import SignalType
from sentio.strategies.voting_engine import VotingResult


@pytest.mark.unit
class TestOrderTracking:
    """Test order tracking and history functionality"""

    @pytest.fixture
    def mock_strategies(self):
        """Create mock strategies for testing"""
        strategy = Mock()
        strategy.name = "test_strategy"
        strategy.enabled = True
        return [strategy]

    @pytest.fixture
    def trading_engine(self, mock_strategies):
        """Create trading engine for testing"""
        return TradingEngine(
            strategies=mock_strategies, mode=TradingMode.PAPER, portfolio_value=100000.0
        )

    def test_order_history_initialized(self, trading_engine):
        """Test that order history is initialized as empty list"""
        assert hasattr(trading_engine, "order_history")
        assert isinstance(trading_engine.order_history, list)
        assert len(trading_engine.order_history) == 0

    def test_place_order_adds_to_history(self, trading_engine):
        """Test that placing an order adds it to history"""
        trade = {"symbol": "AAPL", "direction": "long", "size": 10, "price": 150.0}

        order = trading_engine.place_order(trade)

        assert len(trading_engine.order_history) == 1
        assert trading_engine.order_history[0]["order_id"] == order["order_id"]

    def test_get_order_status_existing_order(self, trading_engine):
        """Test retrieving status of existing order"""
        trade = {"symbol": "AAPL", "direction": "long", "size": 10, "price": 150.0}

        order = trading_engine.place_order(trade)
        order_id = order["order_id"]

        retrieved_order = trading_engine.get_order_status(order_id)

        assert retrieved_order is not None
        assert retrieved_order["order_id"] == order_id
        assert retrieved_order["symbol"] == "AAPL"

    def test_get_order_status_nonexistent_order(self, trading_engine):
        """Test retrieving status of non-existent order"""
        order = trading_engine.get_order_status("nonexistent_id")
        assert order is None

    def test_get_all_orders(self, trading_engine):
        """Test retrieving all orders"""
        # Place multiple orders
        for i in range(3):
            trade = {
                "symbol": f"TEST{i}",
                "direction": "long",
                "size": 10,
                "price": 100.0 + i,
            }
            trading_engine.place_order(trade)

        orders = trading_engine.get_all_orders()

        assert len(orders) == 3

    def test_get_all_orders_filtered_by_symbol(self, trading_engine):
        """Test retrieving orders filtered by symbol"""
        # Place orders for different symbols
        symbols = ["AAPL", "GOOGL", "AAPL"]
        for symbol in symbols:
            trade = {"symbol": symbol, "direction": "long", "size": 10, "price": 150.0}
            trading_engine.place_order(trade)

        aapl_orders = trading_engine.get_all_orders(symbol="AAPL")

        assert len(aapl_orders) == 2
        assert all(o["symbol"] == "AAPL" for o in aapl_orders)

    def test_get_all_orders_respects_limit(self, trading_engine):
        """Test that order retrieval respects limit parameter"""
        # Place 10 orders
        for i in range(10):
            trade = {
                "symbol": f"TEST{i}",
                "direction": "long",
                "size": 10,
                "price": 100.0,
            }
            trading_engine.place_order(trade)

        orders = trading_engine.get_all_orders(limit=5)

        assert len(orders) == 5


@pytest.mark.unit
class TestOrderExecution:
    """Test order execution functionality"""

    @pytest.fixture
    def mock_strategies(self):
        """Create mock strategies for testing"""
        strategy = Mock()
        strategy.name = "test_strategy"
        strategy.enabled = True
        return [strategy]

    @pytest.fixture
    def trading_engine(self, mock_strategies):
        """Create trading engine for testing"""
        return TradingEngine(
            strategies=mock_strategies, mode=TradingMode.PAPER, portfolio_value=100000.0
        )

    def test_paper_order_immediate_fill(self, trading_engine):
        """Test that paper trading orders are immediately filled"""
        trade = {"symbol": "AAPL", "direction": "long", "size": 10, "price": 150.0}

        order = trading_engine.place_order(trade)

        assert order["status"] == OrderStatus.FILLED
        assert order["filled_price"] == trade["price"]
        assert order["filled_qty"] == trade["size"]
        assert "order_id" in order
        assert order["order_id"].startswith("paper_")

    def test_order_includes_timestamp(self, trading_engine):
        """Test that orders include timestamp"""
        trade = {"symbol": "AAPL", "direction": "long", "size": 10, "price": 150.0}

        order = trading_engine.place_order(trade)

        assert "timestamp" in order
        assert isinstance(order["timestamp"], datetime)

    def test_insufficient_funds_rejection(self, trading_engine):
        """Test that orders are rejected when insufficient funds"""
        # Try to place order larger than portfolio
        trade = {
            "symbol": "AAPL",
            "direction": "long",
            "size": 1000,  # 1000 shares at $150 = $150k > $100k portfolio
            "price": 150.0,
        }

        order = trading_engine.place_order(trade)

        assert order["status"] == OrderStatus.REJECTED
        assert "Insufficient funds" in order["message"]
        assert order["order_id"] is None

    def test_order_rejection_added_to_history(self, trading_engine):
        """Test that rejected orders are added to history"""
        trade = {"symbol": "AAPL", "direction": "long", "size": 1000, "price": 150.0}

        order = trading_engine.place_order(trade)

        assert len(trading_engine.order_history) == 1
        assert trading_engine.order_history[0]["status"] == OrderStatus.REJECTED


@pytest.mark.unit
class TestExecuteSignal:
    """Test execute_signal with order tracking"""

    @pytest.fixture
    def mock_strategies(self):
        """Create mock strategies"""
        strategy = Mock()
        strategy.name = "test_strategy"
        strategy.enabled = True
        return [strategy]

    @pytest.fixture
    def trading_engine(self, mock_strategies):
        """Create trading engine"""
        return TradingEngine(
            strategies=mock_strategies, mode=TradingMode.PAPER, portfolio_value=100000.0
        )

    @pytest.fixture
    def mock_voting_result(self):
        """Create mock voting result"""
        result = Mock(spec=VotingResult)
        result.final_signal = SignalType.BUY
        result.confidence = 0.8
        result.consensus_strength = 0.7
        result.votes = []
        return result

    def test_execute_signal_returns_order(self, trading_engine, mock_voting_result):
        """Test that execute_signal returns order details"""
        with patch.object(trading_engine.data_manager, "get_quote") as mock_quote:
            mock_quote.return_value = {"last": 150.0}

            order = trading_engine.execute_signal("AAPL", mock_voting_result)

            assert order is not None
            assert "status" in order
            assert "order_id" in order or order["status"] == OrderStatus.REJECTED

    def test_execute_signal_existing_position_rejection(
        self, trading_engine, mock_voting_result
    ):
        """Test that execute_signal rejects when position already exists"""
        # Manually add a position
        trading_engine.open_positions["AAPL"] = {"symbol": "AAPL"}

        order = trading_engine.execute_signal("AAPL", mock_voting_result)

        assert order["status"] == OrderStatus.REJECTED
        assert "already exists" in order["message"]

    def test_execute_signal_max_positions_rejection(
        self, trading_engine, mock_voting_result
    ):
        """Test that execute_signal rejects when max positions reached"""
        # Fill up position slots
        max_positions = trading_engine.max_concurrent_positions
        for i in range(max_positions):
            trading_engine.open_positions[f"TEST{i}"] = {"symbol": f"TEST{i}"}

        order = trading_engine.execute_signal("AAPL", mock_voting_result)

        assert order["status"] == OrderStatus.REJECTED
        assert "Max concurrent positions" in order["message"]

    def test_execute_signal_market_data_error(self, trading_engine, mock_voting_result):
        """Test that execute_signal handles market data errors"""
        with patch.object(trading_engine.data_manager, "get_quote") as mock_quote:
            mock_quote.side_effect = Exception("Market data unavailable")

            order = trading_engine.execute_signal("AAPL", mock_voting_result)

            assert order["status"] == OrderStatus.REJECTED
            assert "Failed to get market data" in order["message"]


@pytest.mark.unit
class TestOrderMonitoring:
    """Test order monitoring functionality"""

    @pytest.fixture
    def mock_strategies(self):
        """Create mock strategies"""
        strategy = Mock()
        strategy.name = "test_strategy"
        strategy.enabled = True
        return [strategy]

    @pytest.fixture
    def trading_engine(self, mock_strategies):
        """Create trading engine"""
        return TradingEngine(
            strategies=mock_strategies, mode=TradingMode.PAPER, portfolio_value=100000.0
        )

    def test_monitor_order_returns_order_status(self, trading_engine):
        """Test that monitor_order returns order status"""
        trade = {"symbol": "AAPL", "direction": "long", "size": 10, "price": 150.0}

        order = trading_engine.place_order(trade)
        order_id = order["order_id"]

        status = trading_engine.monitor_order(order_id)

        assert status is not None
        assert "symbol" in status
        assert status["symbol"] == "AAPL"

    def test_monitor_order_nonexistent(self, trading_engine):
        """Test monitoring non-existent order"""
        status = trading_engine.monitor_order("nonexistent_id")

        assert "status" in status
        assert status["status"] == "error"
        assert "not found" in status["message"]
