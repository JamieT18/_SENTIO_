"""
Multi-Strategy Trading Execution Engine
Coordinates strategy execution, voting, risk management, and order execution
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import asyncio
import importlib
import time
import threading

from sentio.strategies.base import BaseStrategy, SignalType
from sentio.strategies.voting_engine import StrategyVotingEngine, VotingResult
from sentio.risk.risk_manager import RiskManager
from sentio.data.market_data import MarketDataManager
from sentio.core.logger import get_logger, SentioLogger
from sentio.core.config import get_config
from sentio.analysis.explainable_ai import ExplainableAI
from sentio.long_term_investment.portfolio import PortfolioOptimizer
from sentio.core.compliance import ComplianceChecker
from sentio.ui.accessibility import Accessibility

logger = get_logger(__name__)
structured_logger = SentioLogger.get_structured_logger("trading_engine")


class TradingMode(str, Enum):
    """Trading mode enumeration"""

    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"


class OrderType(str, Enum):
    """Order types"""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(str, Enum):
    """Order status"""

    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TradingEngine:
    """
    Multi-strategy trading execution engine

    Features:
    - Strategy orchestration
    - Confidence-weighted voting
    - Risk management integration
    - Order execution
    - Position tracking
    - Performance monitoring
    - Dual mode (day trading / long-term)
    """

    def __init__(
        self,
        strategies: List[BaseStrategy],
        mode: TradingMode = TradingMode.PAPER,
        portfolio_value: float = 100000.0,
        selected_strategies: Optional[List[str]] = None,  # User-selected strategies
        use_voting_engine: bool = True,  # If true, treat voting engine as a meta-strategy
    ):
        """
        Initialize trading engine

        Args:
            strategies: List of trading strategies
            mode: Trading mode (paper, live, backtest)
            portfolio_value: Initial portfolio value
        """
        self.strategies = {s.name: s for s in strategies}
        self.mode = mode
        self.portfolio_value = portfolio_value
        self.initial_value = portfolio_value

        # User-selected strategies (default: all)
        self.selected_strategies = selected_strategies or list(self.strategies.keys())
        self.use_voting_engine = use_voting_engine

        # Initialize components
        self.voting_engine = StrategyVotingEngine(
            min_confidence=0.65, min_strategies=2, consensus_threshold=0.6
        )
        self.risk_manager = RiskManager()
        self.data_manager = MarketDataManager()

        # State tracking
        self.open_positions: Dict[str, Dict[str, Any]] = {}
        self.pending_orders: List[Dict[str, Any]] = []
        self.trade_history: List[Dict[str, Any]] = []
        self.order_history: List[Dict[str, Any]] = []  # Track all orders
        self.daily_pnl = 0.0

        # Configuration
        self.config = get_config()
        self.max_concurrent_positions = self.config.strategy.max_concurrent_trades

        logger.info(
            f"Trading engine initialized: mode={mode.value}, "
            f"strategies={len(strategies)}, portfolio=${portfolio_value:,.2f}"
        )

    def run_analysis_cycle(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Run complete analysis cycle for multiple symbols.
        Args:
            symbols: List of symbols to analyze
        Returns:
            Dictionary of results by symbol
        """
        results = {}
        for symbol in symbols:
            try:
                result = self.analyze_symbol(symbol)
                results[symbol] = result
                # Execute if signal is actionable (if using voting engine)
                voting_result = result["voting_result"] if isinstance(result, dict) and "voting_result" in result else result
                if hasattr(voting_result, "final_signal") and voting_result.final_signal != SignalType.HOLD:
                    self.execute_signal(symbol, voting_result)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
                results[symbol] = {"error": str(e)}
        return results

    def analyze_symbol(self, symbol: str, use_voting: Optional[bool] = None, strategy_names: Optional[List[str]] = None) -> Any:
        """
        Analyze a single symbol with selected strategies or voting engine.
        Args:
            symbol: Trading symbol
            use_voting: If True, use voting engine; if False, use selected strategies directly
            strategy_names: List of strategy names to use (overrides selected_strategies)
        Returns:
            VotingResult if voting engine used, else dict of signals and stats
        """
        logger.info(f"Analyzing {symbol}")

        # Get market data
        data = self.data_manager.get_data(symbol, timeframe="5min")

        # Determine strategies to use
        strategies_to_use = strategy_names or self.selected_strategies

        # If user wants voting engine, aggregate signals and stats
        use_voting_engine = self.use_voting_engine if use_voting is None else use_voting
        if use_voting_engine:
            signals = []
            for strategy_name in strategies_to_use:
                strategy = self.strategies.get(strategy_name)
                if not strategy or not strategy.enabled:
                    continue
                try:
                    signal = strategy.execute(data)
                    signals.append(signal)
                    logger.debug(
                        f"{strategy_name}: {signal.signal_type.value} "
                        f"(confidence: {signal.confidence:.2f})"
                    )
                except Exception as e:
                    logger.error(f"Strategy {strategy_name} failed: {e}")

            # Get performance metrics for weighting
            performances = {
                name: self.strategies[name].get_performance_metrics()
                for name in strategies_to_use if name in self.strategies
            }

            # Vote on signals
            result = self.voting_engine.vote(signals, performances)

            # Treat voting engine as its own strategy for stats
            voting_stats = {
                "name": "VotingEngine",
                "enabled": True,
                "performance": self.get_voting_engine_stats(result)
            }
            return {
                "voting_result": result,
                "voting_stats": voting_stats,
                "strategy_stats": self.list_strategy_stats(strategies_to_use)
            }
        else:
            # Direct signals and stats for selected strategies
            signals = {}
            stats = {}
            for strategy_name in strategies_to_use:
                strategy = self.strategies.get(strategy_name)
                if not strategy or not strategy.enabled:
                    continue
                try:
                    signal = strategy.execute(data)
                    signals[strategy_name] = signal
                    stats[strategy_name] = strategy.get_performance_metrics()
                except Exception as e:
                    logger.error(f"Strategy {strategy_name} failed: {e}")
            return {
                "signals": signals,
                "strategy_stats": stats
            }
    def reload_strategies(self, strategies: List[BaseStrategy]) -> None:
        """
        Reload all strategies (hot-reload for live trading).
        Args:
            strategies: List of new strategy instances
        """
        self.strategies = {s.name: s for s in strategies}
        self.selected_strategies = list(self.strategies.keys())
        logger.info(f"Strategies reloaded: {self.selected_strategies}")
    def summarize_state(self) -> Dict[str, Any]:
        """
        Summarize engine state for UI/dashboard.
        Returns:
            Dict with key engine metrics and strategy status
        """
        return {
            "mode": self.mode.value,
            "portfolio_value": self.portfolio_value,
            "open_positions": len(self.open_positions),
            "active_strategies": self.selected_strategies,
            "use_voting_engine": self.use_voting_engine,
            "performance": self.get_performance_summary(),
            "strategy_stats": self.list_strategy_stats(),
        }
        """
        Analyze a single symbol with selected strategies or voting engine

        Args:
            symbol: Trading symbol
            use_voting: If True, use voting engine; if False, use selected strategies directly
            strategy_names: List of strategy names to use (overrides selected_strategies)

        Returns:
            VotingResult if voting engine used, else dict of signals and stats
        """
        logger.info(f"Analyzing {symbol}")

        # Get market data
        data = self.data_manager.get_data(symbol, timeframe="5min")

        # Determine strategies to use
        strategies_to_use = strategy_names or self.selected_strategies

        # If user wants voting engine, aggregate signals and stats
        use_voting_engine = self.use_voting_engine if use_voting is None else use_voting
        if use_voting_engine:
            signals = []
            for strategy_name in strategies_to_use:
                strategy = self.strategies.get(strategy_name)
                if not strategy or not strategy.enabled:
                    continue
                try:
                    signal = strategy.execute(data)
                    signals.append(signal)
                    logger.debug(
                        f"{strategy_name}: {signal.signal_type.value} "
                        f"(confidence: {signal.confidence:.2f})"
                    )
                except Exception as e:
                    logger.error(f"Strategy {strategy_name} failed: {e}")

            # Get performance metrics for weighting
            performances = {
                name: self.strategies[name].get_performance_metrics()
                for name in strategies_to_use if name in self.strategies
            }

            # Vote on signals
            result = self.voting_engine.vote(signals, performances)

            # Treat voting engine as its own strategy for stats
            voting_stats = {
                "name": "VotingEngine",
                "enabled": True,
                "performance": self.get_voting_engine_stats(result)
            }
            return {
                "voting_result": result,
                "voting_stats": voting_stats,
                "strategy_stats": self.list_strategy_stats(strategies_to_use)
            }
        else:
            # Direct signals and stats for selected strategies
            signals = {}
            stats = {}
            for strategy_name in strategies_to_use:
                strategy = self.strategies.get(strategy_name)
                if not strategy or not strategy.enabled:
                    continue
                try:
                    signal = strategy.execute(data)
                    signals[strategy_name] = signal
                    stats[strategy_name] = strategy.get_performance_metrics()
                except Exception as e:
                    logger.error(f"Strategy {strategy_name} failed: {e}")
            return {
                "signals": signals,
                "strategy_stats": stats
            }
    def set_selected_strategies(self, strategy_names: List[str], use_voting_engine: Optional[bool] = None) -> None:
        """
        Set which strategies (by name) are used for analysis/trading
        Args:
            strategy_names: List of strategy names
            use_voting_engine: If True, use voting engine; if False, use direct strategies
        """
        self.selected_strategies = strategy_names
        if use_voting_engine is not None:
            self.use_voting_engine = use_voting_engine

    def list_strategy_stats(self, strategy_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        List stats for each strategy (win rate, trades, avg return, etc.)
        Args:
            strategy_names: List of strategy names (default: all)
        Returns:
            Dict of stats for each strategy
        """
        names = strategy_names or list(self.strategies.keys())
        stats = {}
        for name in names:
            strat = self.strategies.get(name)
            if strat:
                stats[name] = strat.get_performance_metrics()
        return stats

    def get_voting_engine_stats(self, voting_result: VotingResult) -> Dict[str, Any]:
        """
        Get stats for the voting engine as a meta-strategy
        Args:
            voting_result: VotingResult object
        Returns:
            Dict of stats (confidence, consensus, uncertainty, etc.)
        """
        return {
            "confidence": voting_result.confidence,
            "consensus_strength": voting_result.consensus_strength,
            "uncertainty": getattr(voting_result, "uncertainty", None),
            "top_strategies": getattr(voting_result, "top_strategies", []),
            "participating_strategies": voting_result.participating_strategies,
            "vote_breakdown": voting_result.vote_breakdown,
        }

    def execute_signal(
        self, symbol: str, voting_result: VotingResult
    ) -> Dict[str, Any]:
        """
        Execute trading signal with risk management

        Args:
            symbol: Trading symbol
            voting_result: Aggregated voting result

        Returns:
            Order details including status and execution info
        """
        signal_type = voting_result.final_signal

        # Check if we already have a position
        if symbol in self.open_positions:
            logger.info(f"Position already exists for {symbol}")
            return {
                "status": OrderStatus.REJECTED,
                "symbol": symbol,
                "message": f"Position already exists for {symbol}",
                "timestamp": datetime.now(),
            }

        # Check max concurrent positions
        if len(self.open_positions) >= self.max_concurrent_positions:
            logger.info(
                f"Max concurrent positions reached ({self.max_concurrent_positions})"
            )
            return {
                "status": OrderStatus.REJECTED,
                "symbol": symbol,
                "message": f"Max concurrent positions reached ({self.max_concurrent_positions})",
                "timestamp": datetime.now(),
            }

        # Get current quote
        try:
            quote = self.data_manager.get_quote(symbol)
            current_price = quote["last"]
        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {e}")
            return {
                "status": OrderStatus.REJECTED,
                "symbol": symbol,
                "message": f"Failed to get market data: {str(e)}",
                "timestamp": datetime.now(),
            }

        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            portfolio_value=self.portfolio_value,
            risk_per_trade=0.02,  # 2% risk per trade
            entry_price=current_price,
            stop_loss=current_price * 0.98,  # 2% stop loss
        )

        # Prepare trade
        trade = {
            "symbol": symbol,
            "direction": "long" if signal_type == SignalType.BUY else "short",
            "size": position_size,
            "price": current_price,
            "signal_type": signal_type.value,
            "confidence": voting_result.confidence,
        }

        # Risk assessment
        current_exposure = sum(p["value"] for p in self.open_positions.values())
        risk_check = self.risk_manager.assess_trade_risk(
            trade=trade,
            portfolio_value=self.portfolio_value,
            current_exposure=current_exposure,
        )

        if not risk_check.approved:
            logger.warning(f"Trade rejected by risk manager: {risk_check.reasons}")
            return {
                "status": OrderStatus.REJECTED,
                "symbol": symbol,
                "message": f'Risk check failed: {", ".join(risk_check.reasons)}',
                "timestamp": datetime.now(),
                "risk_reasons": risk_check.reasons,
            }

        # Apply risk adjustments
        if risk_check.adjustments:
            trade.update(risk_check.adjustments)
            logger.info(f"Trade adjusted: {risk_check.adjustments}")

        # Execute order
        order = self.place_order(trade)

        if order["status"] == OrderStatus.FILLED:
            self.open_position(symbol, order, voting_result)

        logger.info(f"Order executed: {order}")

        return order

    def place_order(self, trade: dict) -> dict:
        """
        Place order (paper or live)

        Args:
            trade: Trade details

        Returns:
            Order result with status, order_id, and execution details
        """
        structured_logger.log_event(
            "order_placement",
            f"Placing order for {trade.get('symbol')}",
            {"trade": trade}
        )
        try:
            # Validate trade
            required_cost = trade["size"] * trade["price"]
            if required_cost > self.portfolio_value:
                error_order = {
                    "symbol": trade["symbol"],
                    "status": OrderStatus.REJECTED,
                    "message": f"Insufficient funds: ${required_cost:,.2f} required, ${self.portfolio_value:,.2f} available",
                    "timestamp": datetime.now(),
                    "order_id": None,
                }
                self.order_history.append(error_order)
                SentioLogger.log_error(
                    logger,
                    Exception(f"Insufficient funds for {trade['symbol']}"),
                    context={
                        "trade": trade,
                        "required_cost": required_cost,
                        "portfolio_value": self.portfolio_value,
                    },
                )
                return error_order

            if self.mode == TradingMode.PAPER:
                # Simulate order execution
                order = {
                    "symbol": trade["symbol"],
                    "side": "buy" if trade["direction"] == "long" else "sell",
                    "quantity": trade["size"],
                    "price": trade["price"],
                    "status": OrderStatus.FILLED,
                    "filled_price": trade["price"],
                    "filled_qty": trade["size"],
                    "timestamp": datetime.now(),
                    "order_id": f"paper_{datetime.now().timestamp()}",
                    "message": "Order filled (simulated)",
                }
                logger.info(f"Paper order filled: {order['order_id']}")
                SentioLogger.log_trade(
                    logger,
                    {
                        "order_id": order["order_id"],
                        "symbol": order["symbol"],
                        "side": order["side"],
                        "quantity": order["quantity"],
                        "price": order["filled_price"],
                        "status": order["status"],
                    },
                )

            elif self.mode == TradingMode.LIVE:
                # In production, place actual order via broker API
                # order = self.broker.place_order(...)
                order = {
                    "symbol": trade["symbol"],
                    "side": "buy" if trade["direction"] == "long" else "sell",
                    "quantity": trade["size"],
                    "price": trade["price"],
                    "status": OrderStatus.PENDING,
                    "message": "Live trading not yet implemented",
                    "timestamp": datetime.now(),
                    "order_id": f"live_{datetime.now().timestamp()}",
                }
                logger.warning(
                    f"Live trading order created but not executed: {order['order_id']}"
                )

            else:
                order = {
                    "symbol": trade["symbol"],
                    "status": OrderStatus.REJECTED,
                    "message": "Invalid trading mode",
                    "timestamp": datetime.now(),
                    "order_id": None,
                }
                logger.error(f"Invalid trading mode: {self.mode}")

            # Track order in history
            self.order_history.append(order.copy())

            structured_logger.log_event(
                "order_placed",
                f"Order placed for {trade.get('symbol')}",
                {"result": order}
            )

            return order
        except Exception as e:
            structured_logger.log_event(
                "order_error",
                str(e),
                {"trade": trade, "exception": repr(e)},
                level="error"
            )
            raise

    def open_position(
        self, symbol: str, order: Dict[str, Any], voting_result: VotingResult
    ):
        """
        Record opened position

        Args:
            symbol: Trading symbol
            order: Order details
            voting_result: Voting result that triggered the trade
        """
        position = {
            "symbol": symbol,
            "entry_price": order["filled_price"],
            "quantity": order["filled_qty"],
            "value": order["filled_price"] * order["filled_qty"],
            "direction": order["side"],
            "stop_loss": order.get("stop_loss"),
            "take_profit": order.get("take_profit"),
            "entry_time": datetime.now(),
            "voting_result": voting_result.to_dict(),
        }

        self.open_positions[symbol] = position
        self.risk_manager.update_position(position)

        logger.info(f"Position opened: {symbol} @ {position['entry_price']}")

    def close_position(self, symbol: str, reason: str = "manual"):
        """
        Close a position

        Args:
            symbol: Trading symbol
            reason: Reason for closing
        """
        if symbol not in self.open_positions:
            logger.warning(f"No open position for {symbol}")
            return

        position = self.open_positions[symbol]

        # Get current price
        quote = self.data_manager.get_quote(symbol)
        exit_price = quote["last"]

        # Calculate P&L
        if position["direction"] == "buy":
            pnl = (exit_price - position["entry_price"]) * position["quantity"]
        else:
            pnl = (position["entry_price"] - exit_price) * position["quantity"]

        pnl_percent = pnl / position["value"]

        # Record trade
        trade_record = {
            "symbol": symbol,
            "entry_price": position["entry_price"],
            "exit_price": exit_price,
            "quantity": position["quantity"],
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "entry_time": position["entry_time"],
            "exit_time": datetime.now(),
            "reason": reason,
        }

        self.trade_history.append(trade_record)
        self.daily_pnl += pnl
        self.portfolio_value += pnl

        # Update risk manager
        self.risk_manager.close_position(symbol, pnl)

        # Remove position
        del self.open_positions[symbol]

        logger.info(
            f"Position closed: {symbol} @ {exit_price}, "
            f"P&L: ${pnl:.2f} ({pnl_percent*100:.2f}%)"
        )

    def monitor_positions(self):
        """
        Monitor open positions for stop-loss/take-profit
        """
        for symbol in list(self.open_positions.keys()):
            position = self.open_positions[symbol]

            # Get current price
            quote = self.data_manager.get_quote(symbol)
            current_price = quote["last"]

            # Check stop-loss
            if position.get("stop_loss"):
                if (
                    position["direction"] == "buy"
                    and current_price <= position["stop_loss"]
                ):
                    logger.warning(f"Stop-loss triggered for {symbol}")
                    self.close_position(symbol, reason="stop_loss")
                    continue
                elif (
                    position["direction"] == "sell"
                    and current_price >= position["stop_loss"]
                ):
                    logger.warning(f"Stop-loss triggered for {symbol}")
                    self.close_position(symbol, reason="stop_loss")
                    continue

            # Check take-profit
            if position.get("take_profit"):
                if (
                    position["direction"] == "buy"
                    and current_price >= position["take_profit"]
                ):
                    logger.info(f"Take-profit triggered for {symbol}")
                    self.close_position(symbol, reason="take_profit")
                    continue
                elif (
                    position["direction"] == "sell"
                    and current_price <= position["take_profit"]
                ):
                    logger.info(f"Take-profit triggered for {symbol}")
                    self.close_position(symbol, reason="take_profit")
                    continue

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary

        Returns:
            Performance metrics
        """
        if not self.trade_history:
            return {
                "total_trades": 0,
                "portfolio_value": self.portfolio_value,
                "total_return": 0.0,
                "win_rate": 0.0,
            }

        wins = [t for t in self.trade_history if t["pnl"] > 0]
        losses = [t for t in self.trade_history if t["pnl"] < 0]

        total_return = self.portfolio_value - self.initial_value
        total_return_pct = (total_return / self.initial_value) * 100

        return {
            "total_trades": len(self.trade_history),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(self.trade_history),
            "portfolio_value": self.portfolio_value,
            "initial_value": self.initial_value,
            "total_return": total_return,
            "total_return_pct": total_return_pct,
            "daily_pnl": self.daily_pnl,
            "open_positions": len(self.open_positions),
            "avg_win": sum(t["pnl"] for t in wins) / len(wins) if wins else 0,
            "avg_loss": sum(t["pnl"] for t in losses) / len(losses) if losses else 0,
        }

    def get_health_report(self) -> Dict[str, Any]:
        """Get system health report"""
        return {
            "timestamp": datetime.now(),
            "mode": self.mode.value,
            "portfolio": self.get_performance_summary(),
            "risk": self.risk_manager.get_risk_metrics(),
            "positions": self.open_positions,
            "strategies": {
                name: {
                    "enabled": strategy.enabled,
                    "performance": strategy.get_performance_metrics(),
                }
                for name, strategy in self.strategies.items()
            },
        }

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific order

        Args:
            order_id: Unique order identifier

        Returns:
            Order details if found, None otherwise
        """
        for order in self.order_history:
            if order.get("order_id") == order_id:
                return order.copy()
        return None

    def get_all_orders(
        self, symbol: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get order history

        Args:
            symbol: Optional symbol filter
            limit: Maximum number of orders to return

        Returns:
            List of order records
        """
        orders = self.order_history
        if symbol:
            orders = [o for o in orders if o.get("symbol") == symbol]

        # Return most recent first
        return sorted(
            orders, key=lambda x: x.get("timestamp", datetime.min), reverse=True
        )[:limit]

    def monitor_order(self, order_id: str) -> Dict[str, Any]:
        """
        Monitor and update order status

        In paper trading mode, orders are filled immediately.
        In live trading mode, this would check with broker API for updates.

        Args:
            order_id: Order identifier to monitor

        Returns:
            Updated order status
        """
        order = self.get_order_status(order_id)

        if not order:
            return {"status": "error", "message": f"Order {order_id} not found"}

        # In paper mode, orders are already filled
        if self.mode == TradingMode.PAPER:
            return order

        # In live mode, check broker API for status
        if self.mode == TradingMode.LIVE:
            # In production: check with broker
            # status = self.broker.get_order_status(order_id)
            # Update order in history
            logger.info(
                f"Monitoring live order {order_id} - broker integration pending"
            )

        return order

    async def execute_order_async(self, order: dict) -> dict:
        """
        Asynchronously execute a single order (stub for real broker integration)
        """
        await asyncio.sleep(0.01)  # Simulate network latency
        order['status'] = 'filled'
        self.order_history.append(order)
        return order

    async def execute_batch_orders_async(self, orders: List[dict]) -> List[dict]:
        """
        Asynchronously execute a batch of orders
        """
        tasks = [self.execute_order_async(order) for order in orders]
        results = await asyncio.gather(*tasks)
        return results

    def run_risk_checks(self, order: dict) -> bool:
        """
        Run advanced risk checks before executing an order
        """
        structured_logger.log_event(
            "risk_check",
            f"Running risk checks for {order.get('symbol')}",
            {"order": order}
        )
        result = self._run_risk_checks_logic(order)
        structured_logger.log_event(
            "risk_check_result",
            f"Risk check result for {order.get('symbol')}",
            {"result": result}
        )
        return result

    def get_performance_metrics(self) -> dict:
        """
        Get real-time performance metrics
        """
        return {
            'daily_pnl': self.daily_pnl,
            'open_positions': len(self.open_positions),
            'trade_count': len(self.trade_history),
            'order_count': len(self.order_history)
        }

    def track_strategy_performance(self) -> dict:
        """
        Track performance metrics for each strategy
        """
        metrics = {}
        for name, strat in self.strategies.items():
            trades = [t for t in self.trade_history if t.get('strategy') == name]
            metrics[name] = {
                'trade_count': len(trades),
                'profit': sum(t.get('pnl', 0) for t in trades),
                'win_rate': sum(1 for t in trades if t.get('pnl', 0) > 0) / len(trades) if trades else 0.0
            }
        return metrics

    def load_strategy(self, module_path: str, class_name: str):
        """
        Dynamically load a strategy class
        """
        module = importlib.import_module(module_path)
        strategy_class = getattr(module, class_name)
        strat_instance = strategy_class()
        self.strategies[strat_instance.name] = strat_instance
        return strat_instance

    def unload_strategy(self, name: str):
        """
        Unload a strategy by name
        """
        if name in self.strategies:
            del self.strategies[name]

    def health_check(self) -> dict:
        """
        Monitor engine health (latency, error rate, active strategies)
        """
        latency = time.time()  # Placeholder for real latency measurement
        error_count = sum(1 for o in self.order_history if o.get('status') == 'rejected')
        return {
            'active_strategies': list(self.strategies.keys()),
            'error_count': error_count,
            'latency': latency
        }

    def update_strategy_live(self, name: str, new_params: dict):
        """
        Update strategy parameters live (if supported)
        """
        strat = self.strategies.get(name)
        if strat and hasattr(strat, 'update_params'):
            strat.update_params(new_params)
            return True
        return False

    def distributed_execute(self, orders: List[dict], worker_count: int = 2):
        """
        Stub for distributed order execution (multi-threaded)
        """
        def worker(order_batch):
            for order in order_batch:
                self.execute_order_async(order)
        batches = [orders[i::worker_count] for i in range(worker_count)]
        threads = [threading.Thread(target=worker, args=(batch,)) for batch in batches]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def register_event_hook(self, event: str, hook_fn):
        """
        Register a custom event hook (e.g., on_trade, on_signal)
        """
        if not hasattr(self, '_event_hooks'):
            self._event_hooks = {}
        self._event_hooks[event] = hook_fn

    def trigger_event(self, event: str, *args, **kwargs):
        """
        Trigger a registered event hook
        """
        if hasattr(self, '_event_hooks') and event in self._event_hooks:
            self._event_hooks[event](*args, **kwargs)

    def update_analytics(self, trade: dict):
        """
        Hook to update analytics (e.g., explainable AI, dashboard)
        """
        model = None  # Replace with actual model reference
        X = None      # Replace with actual feature vector
        if model and X is not None:
            explainer = ExplainableAI(model)
            explanation = explainer.shap_explain(X)
            self.trigger_event('on_analytics_update', explanation)

    def update_portfolio(self, trade: dict):
        """
        Hook to update portfolio optimizer after trade
        """
        optimizer = PortfolioOptimizer()
        optimizer.log_action('trade', trade)
        self.trigger_event('on_portfolio_update', trade)

    def check_compliance(self, trade: dict) -> bool:
        """
        Hook to check compliance before/after trade
        """
        # Example: pass actual compliance rules for robust checking
        rules = [
            {"type": "max_trade_size", "value": 100000},
            {"type": "restricted_asset", "assets": ["XYZ"]},
        ]
        checker = ComplianceChecker(rules)
        result = checker.check(trade)
        self.trigger_event('on_compliance_check', result)
        return not result

    def update_ui(self, event: str, data: dict):
        """
        Hook to update UI/dashboard (e.g., accessibility, widgets)
        """
        accessibility = Accessibility()
        label = accessibility.translate(event)
        self.trigger_event('on_ui_update', {'label': label, 'data': data})

    def dynamic_targeting(self, position, market_data):
        structured_logger.log_event(
            "dynamic_targeting",
            "Applying dynamic targeting",
            {"position": position, "market_data": market_data}
        )
        # ...logic for dynamic targeting...
        return {"target": 1.05, "adjusted": True}

    def trailing_profit(self, position, market_data):
        structured_logger.log_event(
            "trailing_profit",
            "Applying trailing profit logic",
            {"position": position, "market_data": market_data}
        )
        # ...logic for trailing profit...
        return {"trail": 0.03, "active": True}

    def partial_exit(self, position, exit_ratio):
        structured_logger.log_event(
            "partial_exit",
            "Executing partial exit",
            {"position": position, "exit_ratio": exit_ratio}
        )
        # ...logic for partial exit...
        return {"exited": exit_ratio, "remaining": 1-exit_ratio}

    def trade_cloning(self, trade, times):
        structured_logger.log_event(
            "trade_cloning",
            "Cloning trade",
            {"trade": trade, "times": times}
        )
        # ...logic for trade cloning...
        return {"clones": [trade]*times}

    def trade_stacking(self, trades):
        structured_logger.log_event(
            "trade_stacking",
            "Stacking trades",
            {"trades": trades}
        )
        # ...logic for stacking...
        return {"stacked": trades, "count": len(trades)}

    def trade_rotation(self, trades):
        structured_logger.log_event(
            "trade_rotation",
            "Rotating trades",
            {"trades": trades}
        )
        # ...logic for rotation...
        return {"rotated": trades[::-1]}

    def trade_attribution(self, trade, strategy):
        structured_logger.log_event(
            "trade_attribution",
            "Attributing trade to strategy",
            {"trade": trade, "strategy": strategy}
        )
        # ...logic for attribution...
        return {"attributed": True, "strategy": strategy}


class MultiStrategyTradingEngine:
    def __init__(self, subscription_tier):
        self.subscription_tier = subscription_tier
        self.day_trading_engine = TradingEngine()
        self.long_term_engine = TradingEngine()
        structured_logger.log_event(
            "multi_strategy_engine_init",
            "Initialized multi-strategy trading engine",
            {"subscription_tier": subscription_tier}
        )

    def run_dual_mode(self, market_data, portfolio):
        structured_logger.log_event(
            "dual_mode_run",
            "Running dual mode trading engine",
            {"market_data": str(market_data)[:200], "portfolio": str(portfolio)[:200]}
        )
        if self.subscription_tier == "premium":
            day_result = self.day_trading_engine.run_analysis_cycle(market_data)
            long_result = self.long_term_engine.run_analysis_cycle(market_data)
            return {"day_trading": day_result, "long_term": long_result}
        else:
            day_result = self.day_trading_engine.run_analysis_cycle(market_data)
            return {"day_trading": day_result, "long_term": None}

    def select_strategy(self, strategies, auto_optimize=False):
        structured_logger.log_event(
            "strategy_selection",
            "Selecting user-defined or auto-optimized strategy",
            {"strategies": strategies, "auto_optimize": auto_optimize}
        )
        if auto_optimize:
            # ...logic for auto-optimization...
            selected = strategies[0] if strategies else None
        else:
            # ...logic for user selection...
            selected = strategies[0] if strategies else None
        return {"selected_strategy": selected}
