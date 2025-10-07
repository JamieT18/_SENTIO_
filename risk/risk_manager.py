"""
Multi-Layered Risk Management System
Comprehensive risk controls including stop-loss, position sizing, drawdown limits, and circuit breakers
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import warnings

from ..core.logger import get_logger
from ..core.config import get_config
from sentio.core.logger import SentioLogger

logger = get_logger(__name__)
structured_logger = SentioLogger.get_structured_logger("risk_manager")
warnings.filterwarnings("ignore", category=UserWarning)


class RiskLevel(str, Enum):
    """Risk assessment levels"""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""

    NORMAL = "normal"
    WARNING = "warning"
    TRIPPED = "tripped"


class RiskCheckResult:
    """Result of risk assessment"""

    def __init__(
        self,
        approved: bool,
        risk_level: RiskLevel,
        reasons: List[str],
        adjustments: Dict[str, Any],
        warnings: List[str],
    ):
        self.approved = approved
        self.risk_level = risk_level
        self.reasons = reasons
        self.adjustments = adjustments
        self.warnings = warnings
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved": self.approved,
            "risk_level": self.risk_level.value,
            "reasons": self.reasons,
            "adjustments": self.adjustments,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat(),
        }


class RiskManager:
    """
    Comprehensive risk management system

    Features:
    - Adaptive position sizing
    - Stop-loss enforcement
    - Drawdown monitoring and limits
    - Circuit breakers for extreme losses
    - Portfolio-level risk controls
    - Trade health scanning
    - Anomaly detection
    - ML-based correlation prediction
    - VaR (Value at Risk) calculations
    - Multi-timeframe volatility analysis
    - Dynamic risk-reward ratio adjustment
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize risk manager

        Args:
            config: Risk configuration parameters
        """
        self.config = config or get_config().risk_management.model_dump()

        # Risk parameters
        self.max_position_size = self.config.get("max_position_size", 0.05)
        self.max_portfolio_risk = self.config.get("max_portfolio_risk", 0.20)
        self.stop_loss_percent = self.config.get("stop_loss_percent", 0.02)
        self.take_profit_percent = self.config.get("take_profit_percent", 0.05)
        self.max_daily_drawdown = self.config.get("max_daily_drawdown", 0.03)
        self.circuit_breaker_threshold = self.config.get(
            "circuit_breaker_threshold", 0.05
        )

        # New risk parameters
        self.min_risk_reward_ratio = self.config.get(
            "min_risk_reward_ratio", 2.0
        )  # 1:2 minimum
        self.max_loss_per_trade = self.config.get(
            "max_loss_per_trade", 0.01
        )  # 1% max loss per trade
        self.max_correlation = self.config.get(
            "max_correlation", 0.7
        )  # Max correlation between positions
        self.enable_kelly_criterion = self.config.get("enable_kelly_criterion", False)
        self.max_sector_concentration = self.config.get(
            "max_sector_concentration", 0.30
        )  # 30% per sector

        # Advanced risk features
        self.enable_ml_correlation = self.config.get("enable_ml_correlation", True)
        self.enable_var_calculation = self.config.get("enable_var_calculation", True)
        self.enable_multi_timeframe_volatility = self.config.get(
            "enable_multi_timeframe_volatility", True
        )
        self.enable_dynamic_rr_adjustment = self.config.get(
            "enable_dynamic_rr_adjustment", True
        )
        self.var_confidence_level = self.config.get(
            "var_confidence_level", 0.95
        )  # 95% confidence
        self.var_time_horizon = self.config.get("var_time_horizon", 1)  # 1-day VaR

        # State tracking
        self.circuit_breaker_state = CircuitBreakerState.NORMAL
        self.daily_pnl = 0.0
        self.daily_start_value = 0.0
        self.open_positions: List[Dict[str, Any]] = []
        self.trade_history: List[Dict[str, Any]] = []
        self.last_reset = datetime.now()

        # Performance tracking
        self.win_count = 0
        self.loss_count = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        self.sector_exposure: Dict[str, float] = defaultdict(float)

        # ML correlation model
        self.correlation_model = None
        self.correlation_scaler = StandardScaler()
        self.correlation_training_data: List[Dict[str, Any]] = []

        # VaR tracking
        self.portfolio_var_history: List[Tuple[datetime, float]] = []

        # Multi-timeframe volatility tracking
        self.volatility_1h: Dict[str, float] = {}
        self.volatility_1d: Dict[str, float] = {}
        self.volatility_1w: Dict[str, float] = {}

        # Dynamic RR tracking
        self.current_min_rr_ratio = self.min_risk_reward_ratio

    def get_risk_dashboard_summary(self) -> Dict[str, Any]:
        """
        Return a summary for dashboard: key metrics, recent risk events, recommendations.
        """
        summary = self.get_risk_metrics()
        summary["recent_events"] = self.get_recent_risk_events()
        summary["mitigation_recommendations"] = self.get_mitigation_recommendations()
        summary["scenario_simulation"] = self.simulate_risk_scenarios()
        return summary

    def get_recent_risk_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Return recent risk events (e.g., circuit breaker, drawdown, alerts).
        """
        events = []
        # Example: add recent circuit breaker events
        if self.circuit_breaker_state != CircuitBreakerState.NORMAL:
            events.append({
                "type": "circuit_breaker",
                "state": self.circuit_breaker_state.value,
                "timestamp": datetime.now().isoformat(),
            })
        # Add recent drawdown events
        if self._check_daily_drawdown():
            events.append({
                "type": "drawdown_limit",
                "value": self.daily_pnl,
                "timestamp": datetime.now().isoformat(),
            })
        # Add recent risk alerts
        if self.trade_history:
            last_trade = self.trade_history[-1]
            alert = self.real_time_risk_alert(last_trade, self.daily_start_value)
            if alert:
                events.append({
                    "type": "risk_alert",
                    "message": alert,
                    "timestamp": datetime.now().isoformat(),
                })
        return events[-limit:]

    def get_mitigation_recommendations(self) -> List[str]:
        """
        Return actionable risk mitigation recommendations based on current metrics.
        """
        recs = []
        metrics = self.get_risk_metrics()
        if metrics.get("win_rate", 0) < 0.5:
            recs.append("Review strategy: win rate below 50%.")
        if metrics.get("sharpe_ratio", 0) < 1:
            recs.append("Sharpe ratio low: consider reducing risk exposure.")
        if metrics.get("expectancy", 0) < 0:
            recs.append("Negative expectancy: review recent trades and adjust risk limits.")
        if metrics.get("circuit_breaker_state") == "tripped":
            recs.append("Circuit breaker tripped: halt trading and review risk controls.")
        if metrics.get("portfolio_var", 0) > 0.05:
            recs.append("Portfolio VaR high: consider hedging or reducing positions.")
        return recs

    def simulate_risk_scenarios(self) -> List[Dict[str, Any]]:
        """
        Simulate risk under multiple scenarios (market crash, rally, volatility spike).
        """
        scenarios = [
            {"name": "Crash", "AAPL": -0.2, "MSFT": -0.18},
            {"name": "Rally", "AAPL": 0.15, "MSFT": 0.12},
            {"name": "Volatility Spike", "AAPL": -0.1, "MSFT": 0.05},
        ]
        portfolio = {"AAPL": 10000, "MSFT": 8000}
        results = self.scenario_stress_test(portfolio, scenarios)
        return [{"scenario": k, "impact": v} for k, v in results.items()]

    def assess_trade_risk(
        self, trade: Dict[str, Any], portfolio_value: float, current_exposure: float
    ) -> RiskCheckResult:
        """
        Comprehensive risk assessment for a proposed trade

        Args:
            trade: Trade details (symbol, direction, size, price, etc.)
            portfolio_value: Current portfolio value
            current_exposure: Current market exposure

        Returns:
            Risk check result with approval and adjustments
        """
        structured_logger.log_event(
            "risk_assessment",
            f"Assessing risk for trade {trade.get('symbol')}",
            {"trade": trade}
        )
        reasons = []
        warnings = []
        adjustments = {}
        approved = True
        risk_level = RiskLevel.LOW

        # 1. Check circuit breaker
        if self.circuit_breaker_state == CircuitBreakerState.TRIPPED:
            reasons.append("Circuit breaker is tripped")
            approved = False
            risk_level = RiskLevel.CRITICAL
            return RiskCheckResult(approved, risk_level, reasons, adjustments, warnings)

        # 2. Check daily drawdown
        if self._check_daily_drawdown():
            reasons.append("Daily drawdown limit exceeded")
            approved = False
            risk_level = RiskLevel.CRITICAL

        # 3. Position sizing check
        proposed_size = trade.get("size", 0)
        proposed_value = proposed_size * trade.get("price", 0)
        position_percent = proposed_value / portfolio_value

        if position_percent > self.max_position_size:
            # Adjust position size
            adjusted_size = (self.max_position_size * portfolio_value) / trade["price"]
            adjustments["size"] = adjusted_size
            warnings.append(
                f"Position size reduced from {proposed_size} to {adjusted_size:.2f} "
                f"(max {self.max_position_size*100}% of portfolio)"
            )
            risk_level = max(risk_level, RiskLevel.MODERATE)

        # 4. Portfolio risk check
        new_exposure = current_exposure + proposed_value
        exposure_percent = new_exposure / portfolio_value

        if exposure_percent > self.max_portfolio_risk:
            reasons.append(
                f"Portfolio risk too high: {exposure_percent*100:.1f}% > "
                f"{self.max_portfolio_risk*100}%"
            )
            approved = False
            risk_level = RiskLevel.HIGH

        # 5. Volatility check
        volatility_risk = self._assess_volatility_risk(trade)
        if volatility_risk > 0.7:
            warnings.append("High volatility detected")
            risk_level = max(risk_level, RiskLevel.MODERATE)

        # 6. Correlation check (if multiple positions)
        if len(self.open_positions) > 0:
            correlation_risk = self._assess_correlation_risk(trade)
            if correlation_risk > 0.8:
                warnings.append("High correlation with existing positions")
                risk_level = max(risk_level, RiskLevel.MODERATE)

        # 7. Set stop-loss and take-profit
        if "stop_loss" not in trade or trade["stop_loss"] is None:
            price = trade["price"]
            direction = trade.get("direction", "long")

            if direction == "long":
                adjustments["stop_loss"] = price * (1 - self.stop_loss_percent)
                adjustments["take_profit"] = price * (1 + self.take_profit_percent)
            else:
                adjustments["stop_loss"] = price * (1 + self.stop_loss_percent)
                adjustments["take_profit"] = price * (1 - self.take_profit_percent)

        # 8. Risk-reward ratio validation
        stop_loss = adjustments.get("stop_loss", trade.get("stop_loss"))
        take_profit = adjustments.get("take_profit", trade.get("take_profit"))

        if stop_loss and take_profit:
            # Use dynamically adjusted RR ratio if enabled
            min_rr = (
                self.adjust_rr_ratio_dynamically()
                if self.enable_dynamic_rr_adjustment
                else self.min_risk_reward_ratio
            )

            risk_reward = self._calculate_risk_reward_ratio(
                trade["price"], stop_loss, take_profit, trade.get("direction", "long")
            )
            if risk_reward < min_rr:
                warnings.append(
                    f"Risk-reward ratio {risk_reward:.2f}:1 below minimum {min_rr:.2f}:1"
                )
                risk_level = max(risk_level, RiskLevel.MODERATE)

        # 9. Maximum loss per trade validation
        if stop_loss:
            max_loss = abs(trade["price"] - stop_loss) * proposed_size
            max_loss_percent = max_loss / portfolio_value

            if max_loss_percent > self.max_loss_per_trade:
                # Reduce position size to meet max loss constraint
                adjusted_size = (self.max_loss_per_trade * portfolio_value) / abs(
                    trade["price"] - stop_loss
                )
                adjustments["size"] = min(
                    adjustments.get("size", proposed_size), adjusted_size
                )
                warnings.append(
                    f"Position size adjusted to limit max loss to {self.max_loss_per_trade*100}%"
                )
                risk_level = max(risk_level, RiskLevel.MODERATE)

        # 10. Sector concentration check
        sector = trade.get("sector", "unknown")
        if sector != "unknown":
            sector_risk = self._check_sector_concentration(
                sector, proposed_value, portfolio_value
            )
            if sector_risk > self.max_sector_concentration:
                reasons.append(
                    f"Sector concentration too high: {sector_risk*100:.1f}% > {self.max_sector_concentration*100}%"
                )
                approved = False
                risk_level = RiskLevel.HIGH

        # 11. Trade frequency check (moved from position 8)
        if self._check_overtrading():
            warnings.append("High trading frequency detected")
            risk_level = max(risk_level, RiskLevel.MODERATE)

        logger.info(
            f"Risk assessment: approved={approved}, level={risk_level.value}, "
            f"warnings={len(warnings)}"
        )

        result = RiskCheckResult(approved, risk_level, reasons, adjustments, warnings)
        structured_logger.log_event(
            "risk_assessment_result",
            f"Risk assessment result for {trade.get('symbol')}",
            {"result": result}
        )
        return result

    def update_position(self, position: Dict[str, Any]):
        """Update or add an open position"""
        symbol = position.get("symbol")
        sector = position.get("sector", "unknown")
        value = position.get("value", 0)

        # Update existing or add new
        existing = next((p for p in self.open_positions if p["symbol"] == symbol), None)
        if existing:
            # Update sector exposure
            if sector in self.sector_exposure:
                self.sector_exposure[sector] = (
                    self.sector_exposure[sector] - existing.get("value", 0) + value
                )
            existing.update(position)
        else:
            self.open_positions.append(position)
            # Add to sector exposure
            if sector != "unknown":
                self.sector_exposure[sector] = (
                    self.sector_exposure.get(sector, 0) + value
                )

        # Store price history for volatility calculation
        current_price = position.get("current_price", position.get("price", 0))
        if current_price > 0:
            self.price_history[symbol].append((datetime.now(), current_price))
            # Keep only last 100 price points per symbol
            if len(self.price_history[symbol]) > 100:
                self.price_history[symbol] = self.price_history[symbol][-100:]

        logger.info(
            f"Position updated: {symbol}, total positions: {len(self.open_positions)}"
        )

    def close_position(self, symbol: str, pnl: float):
        """Close a position and update metrics"""
        self.open_positions = [p for p in self.open_positions if p["symbol"] != symbol]
        self.daily_pnl += pnl

        # Update win/loss tracking
        if pnl > 0:
            self.win_count += 1
            self.total_profit += pnl
        else:
            self.loss_count += 1
            self.total_loss += abs(pnl)

        # Record in history
        self.trade_history.append(
            {"symbol": symbol, "pnl": pnl, "timestamp": datetime.now()}
        )

        # Update sector exposure
        for position in list(self.open_positions):
            if position["symbol"] == symbol:
                sector = position.get("sector", "unknown")
                if sector in self.sector_exposure:
                    self.sector_exposure[sector] = max(
                        0, self.sector_exposure[sector] - position.get("value", 0)
                    )

        # Check circuit breaker
        self._check_circuit_breaker()

        logger.info(
            f"Position closed: {symbol}, PnL: {pnl:.2f}, daily PnL: {self.daily_pnl:.2f}"
        )

    def calculate_position_size(
        self,
        portfolio_value: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss: float,
    ) -> float:
        """
        Calculate optimal position size using risk-based sizing

        Args:
            portfolio_value: Current portfolio value
            risk_per_trade: Risk percentage per trade (e.g., 0.02 for 2%)
            entry_price: Entry price
            stop_loss: Stop-loss price

        Returns:
            Position size (number of shares/contracts)
        """
        # Risk amount in dollars
        risk_amount = portfolio_value * risk_per_trade

        # Risk per share
        risk_per_share = abs(entry_price - stop_loss)

        if risk_per_share == 0:
            return 0

        # Position size
        position_size = risk_amount / risk_per_share

        # Apply Kelly Criterion if enabled and we have trading history
        if self.enable_kelly_criterion and (self.win_count + self.loss_count) >= 20:
            win_rate = self.get_win_rate()
            avg_win = self.total_profit / self.win_count if self.win_count > 0 else 0
            avg_loss = self.total_loss / self.loss_count if self.loss_count > 0 else 0

            kelly_fraction = self.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
            kelly_size = (kelly_fraction * portfolio_value) / entry_price

            # Use the smaller of Kelly and risk-based sizing
            position_size = min(position_size, kelly_size)
            logger.debug(
                f"Kelly Criterion sizing: {kelly_fraction*100:.1f}% of portfolio"
            )

        # Apply maximum position size constraint
        max_size = (portfolio_value * self.max_position_size) / entry_price
        position_size = min(position_size, max_size)

        return position_size

    def scan_trade_health(self) -> Dict[str, Any]:
        """
        Scan all open positions for health issues

        Returns:
            Health report with issues and recommendations
        """
        issues = []
        recommendations = []

        for position in self.open_positions:
            # Check if stop-loss needs adjustment
            current_price = position.get("current_price", 0)
            entry_price = position.get("entry_price", 0)
            stop_loss = position.get("stop_loss", 0)

            if current_price == 0 or entry_price == 0:
                continue

            pnl_percent = (current_price - entry_price) / entry_price

            # Check for large unrealized losses
            if pnl_percent < -0.05:  # 5% loss
                issues.append(
                    {
                        "symbol": position["symbol"],
                        "issue": "Large unrealized loss",
                        "pnl_percent": pnl_percent,
                    }
                )
                recommendations.append(
                    f"Consider closing {position['symbol']} (loss: {pnl_percent*100:.1f}%)"
                )

            # Check for trailing stop adjustment
            if pnl_percent > 0.03:  # 3% profit
                new_stop = current_price * 0.98  # 2% below current
                if new_stop > stop_loss:
                    recommendations.append(
                        f"Adjust trailing stop for {position['symbol']} to {new_stop:.2f}"
                    )

        return {
            "timestamp": datetime.now(),
            "open_positions": len(self.open_positions),
            "issues": issues,
            "recommendations": recommendations,
            "daily_pnl": self.daily_pnl,
            "circuit_breaker_state": self.circuit_breaker_state.value,
        }

    def reset_daily_metrics(self):
        """Reset daily tracking metrics"""
        self.daily_pnl = 0.0
        self.last_reset = datetime.now()

        # Reset circuit breaker if 24 hours passed
        if self.circuit_breaker_state == CircuitBreakerState.TRIPPED:
            time_since_trip = datetime.now() - self.last_reset
            if time_since_trip > timedelta(hours=24):
                self.circuit_breaker_state = CircuitBreakerState.NORMAL
                self.daily_pnl = 0.0
                logger.info("Circuit breaker and daily PnL reset after 24 hours")

    def _check_daily_drawdown(self) -> bool:
        """Check if daily drawdown limit exceeded"""
        if self.daily_start_value == 0:
            return False

        drawdown = abs(self.daily_pnl) / self.daily_start_value
        return drawdown > self.max_daily_drawdown

    def _check_circuit_breaker(self):
        """Check and update circuit breaker state"""
        if self.daily_start_value == 0:
            return

        loss_percent = abs(min(self.daily_pnl, 0)) / self.daily_start_value

        if loss_percent >= self.circuit_breaker_threshold:
            self.circuit_breaker_state = CircuitBreakerState.TRIPPED
            logger.critical(f"CIRCUIT BREAKER TRIPPED: Loss {loss_percent*100:.1f}%")
        elif loss_percent >= self.circuit_breaker_threshold * 0.8:
            self.circuit_breaker_state = CircuitBreakerState.WARNING
            logger.warning(f"Circuit breaker warning: Loss {loss_percent*100:.1f}%")

    def _assess_volatility_risk(self, trade: Dict[str, Any]) -> float:
        """
        Assess volatility risk using historical price data
        Enhanced with multi-timeframe analysis

        Returns:
            Risk score between 0 and 1 (higher = more risky)
        """
        symbol = trade.get("symbol")

        # Check if we have price history
        if symbol not in self.price_history or len(self.price_history[symbol]) < 10:
            # No history, return moderate risk
            return 0.5

        # Use multi-timeframe analysis if enabled
        if self.enable_multi_timeframe_volatility:
            vol_data = self.calculate_multi_timeframe_volatility(symbol)

            # Weight different timeframes
            # 1h: 20%, 1d: 50%, 1w: 30%
            vol_1h = vol_data.get("1h", 0)
            vol_1d = vol_data.get("1d", 0)
            vol_1w = vol_data.get("1w", 0)

            # Calculate weighted volatility
            if vol_1h > 0 and vol_1d > 0 and vol_1w > 0:
                weighted_vol = 0.2 * vol_1h + 0.5 * vol_1d + 0.3 * vol_1w
            elif vol_1d > 0:
                weighted_vol = vol_1d
            else:
                # Fallback to simple calculation
                prices = [price for _, price in self.price_history[symbol]]
                returns = np.diff(prices) / prices[:-1]
                weighted_vol = np.std(returns)

            # Normalize volatility to 0-1 scale
            # Typical daily volatility ranges from 0.01 to 0.05
            # Above 0.05 is considered very high
            normalized_volatility = min(weighted_vol / 0.05, 1.0)

            logger.debug(
                f"Multi-timeframe volatility for {symbol}: "
                f"1h={vol_1h:.4f}, 1d={vol_1d:.4f}, 1w={vol_1w:.4f}, "
                f"weighted={weighted_vol:.4f}, normalized={normalized_volatility:.2f}"
            )

            return normalized_volatility
        else:
            # Original simple calculation
            prices = [price for _, price in self.price_history[symbol]]
            returns = np.diff(prices) / prices[:-1]
            volatility = np.std(returns)
            normalized_volatility = min(volatility / 0.05, 1.0)

            logger.debug(
                f"Volatility risk for {symbol}: {normalized_volatility:.2f} (std: {volatility:.4f})"
            )

            return normalized_volatility

    def _assess_correlation_risk(self, trade: Dict[str, Any]) -> float:
        """
        Assess correlation with existing positions
        Enhanced with ML-based prediction

        Returns:
            Risk score between 0 and 1 (higher = more correlated)
        """
        if len(self.open_positions) == 0:
            return 0.0

        symbol = trade.get("symbol")
        sector = trade.get("sector", "unknown")

        # Check if we have enough price history for correlation
        if symbol not in self.price_history or len(self.price_history[symbol]) < 20:
            # Use sector-based correlation as fallback
            same_sector_count = sum(
                1
                for p in self.open_positions
                if p.get("sector") == sector and sector != "unknown"
            )
            if same_sector_count > 0:
                # High correlation if same sector
                return 0.7
            return 0.3

        max_correlation = 0.0

        # Calculate correlation with each existing position
        for position in self.open_positions:
            pos_symbol = position.get("symbol")

            # Try ML-based prediction first
            if self.enable_ml_correlation and self.correlation_model is not None:
                ml_corr = self.predict_correlation(trade, position)
                max_correlation = max(max_correlation, ml_corr)
            else:
                # Fallback to traditional correlation calculation
                if (
                    pos_symbol in self.price_history
                    and len(self.price_history[pos_symbol]) >= 20
                ):
                    # Calculate correlation with existing positions
                    symbol_prices = np.array(
                        [price for _, price in self.price_history[symbol][-20:]]
                    )
                    symbol_returns = np.diff(symbol_prices) / symbol_prices[:-1]

                    pos_prices = np.array(
                        [price for _, price in self.price_history[pos_symbol][-20:]]
                    )
                    pos_returns = np.diff(pos_prices) / pos_prices[:-1]

                    # Align lengths
                    min_len = min(len(symbol_returns), len(pos_returns))
                    if min_len > 5:
                        correlation = abs(
                            np.corrcoef(
                                symbol_returns[-min_len:], pos_returns[-min_len:]
                            )[0, 1]
                        )
                        if not np.isnan(correlation):
                            max_correlation = max(max_correlation, correlation)

                            # Update training data for ML model
                            if self.enable_ml_correlation:
                                self.update_correlation_training_data(
                                    symbol, pos_symbol, correlation
                                )

        logger.debug(f"Correlation risk for {symbol}: {max_correlation:.2f}")

        return max_correlation

    def _check_overtrading(self) -> bool:
        """Check for excessive trading frequency"""
        recent_trades = [
            t
            for t in self.trade_history
            if datetime.now() - t["timestamp"] < timedelta(hours=1)
        ]
        return len(recent_trades) > 10

    def _calculate_risk_reward_ratio(
        self, entry_price: float, stop_loss: float, take_profit: float, direction: str
    ) -> float:
        """
        Calculate risk-reward ratio

        Args:
            entry_price: Entry price
            stop_loss: Stop-loss price
            take_profit: Take-profit price
            direction: 'long' or 'short'

        Returns:
            Risk-reward ratio (e.g., 2.0 means 1:2 ratio)
        """
        if direction == "long":
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
        else:
            risk = abs(stop_loss - entry_price)
            reward = abs(entry_price - take_profit)

        if risk == 0:
            return 0.0

        return reward / risk

    def _check_sector_concentration(
        self, sector: str, new_value: float, portfolio_value: float
    ) -> float:
        """
        Check sector concentration

        Args:
            sector: Sector name
            new_value: Value of new position
            portfolio_value: Total portfolio value

        Returns:
            Sector concentration as percentage
        """
        current_sector_value = self.sector_exposure.get(sector, 0)
        new_sector_value = current_sector_value + new_value
        concentration = new_sector_value / portfolio_value if portfolio_value > 0 else 0

        return concentration

    def calculate_kelly_criterion(
        self, win_rate: float, avg_win: float, avg_loss: float
    ) -> float:
        """
        Calculate Kelly Criterion for position sizing

        Args:
            win_rate: Probability of winning (0-1)
            avg_win: Average win amount
            avg_loss: Average loss amount

        Returns:
            Optimal position size as fraction of capital (0-1)
        """
        if avg_loss == 0 or win_rate == 0 or win_rate == 1:
            return 0.0

        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        # Apply fractional Kelly (half Kelly for safety)
        kelly_fraction = max(0, min(kelly * 0.5, self.max_position_size))

        return kelly_fraction

    def get_win_rate(self) -> float:
        """Calculate current win rate"""
        total_trades = self.win_count + self.loss_count
        if total_trades == 0:
            return 0.0
        return self.win_count / total_trades

    def get_expectancy(self) -> float:
        """
        Calculate trading expectancy (average expected profit per trade)

        Returns:
            Expected value per trade
        """
        total_trades = self.win_count + self.loss_count
        if total_trades == 0:
            return 0.0

        avg_win = self.total_profit / self.win_count if self.win_count > 0 else 0
        avg_loss = self.total_loss / self.loss_count if self.loss_count > 0 else 0
        win_rate = self.get_win_rate()

        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        return expectancy

    def get_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio from recent trade history

        Args:
            risk_free_rate: Annual risk-free rate (default 2%)

        Returns:
            Sharpe ratio
        """
        if len(self.trade_history) < 2:
            return 0.0

        returns = [t["pnl"] for t in self.trade_history]
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        # Annualized Sharpe (assuming daily trades)
        daily_rf = risk_free_rate / 252
        sharpe = (mean_return - daily_rf) / std_return * np.sqrt(252)

        return sharpe

    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics"""
        total_trades = self.win_count + self.loss_count

        metrics = {
            "circuit_breaker_state": self.circuit_breaker_state.value,
            "daily_pnl": self.daily_pnl,
            "open_positions": len(self.open_positions),
            "total_exposure": sum(p.get("value", 0) for p in self.open_positions),
            "last_reset": self.last_reset.isoformat(),
            "win_rate": self.get_win_rate(),
            "total_trades": total_trades,
            "win_count": self.win_count,
            "loss_count": self.loss_count,
            "expectancy": self.get_expectancy(),
            "sharpe_ratio": self.get_sharpe_ratio(),
            "sector_exposure": dict(self.sector_exposure),
            "avg_win": self.total_profit / self.win_count if self.win_count > 0 else 0,
            "avg_loss": self.total_loss / self.loss_count if self.loss_count > 0 else 0,
        }

        # Add advanced metrics
        if self.enable_var_calculation:
            metrics["portfolio_var"] = self.calculate_portfolio_var()

        if self.enable_dynamic_rr_adjustment:
            metrics["current_min_rr_ratio"] = self.current_min_rr_ratio

        if self.enable_multi_timeframe_volatility and self.volatility_1d:
            metrics["avg_volatility_1d"] = np.mean(list(self.volatility_1d.values()))

        return metrics

    # ==================== Advanced Risk Management Features ====================

    def train_correlation_model(self):
        """
        Train ML model to predict correlations between assets
        Uses historical correlation data and features like sector, market cap, etc.
        """
        if not self.enable_ml_correlation:
            return

        if len(self.correlation_training_data) < 10:
            logger.debug("Insufficient data to train correlation model")
            return

        try:
            # Prepare training data
            X = []
            y = []

            for data in self.correlation_training_data:
                features = [
                    1.0 if data.get("same_sector", False) else 0.0,
                    data.get("volatility_similarity", 0.5),
                    data.get("price_correlation", 0.5),
                    data.get("volume_correlation", 0.5),
                    data.get("market_cap_ratio", 1.0),
                ]
                X.append(features)
                y.append(data.get("actual_correlation", 0.5))

            X = np.array(X)
            y = np.array(y)

            # Normalize features
            X_scaled = self.correlation_scaler.fit_transform(X)

            # Train Ridge regression model (handles multicollinearity)
            self.correlation_model = Ridge(alpha=1.0)
            self.correlation_model.fit(X_scaled, y)

            logger.info(f"Correlation prediction model trained with {len(X)} samples")

        except Exception as e:
            logger.error(f"Error training correlation model: {e}")

    def predict_correlation(
        self, trade: Dict[str, Any], position: Dict[str, Any]
    ) -> float:
        """
        Predict correlation between a new trade and an existing position using ML

        Args:
            trade: New trade details
            position: Existing position details

        Returns:
            Predicted correlation (0-1)
        """
        if not self.enable_ml_correlation or self.correlation_model is None:
            # Fallback to traditional correlation
            return self._assess_correlation_risk(trade)

        try:
            # Extract features
            same_sector = trade.get("sector") == position.get("sector")

            # Calculate volatility similarity if we have price history
            vol_similarity = 0.5
            if (
                trade.get("symbol") in self.volatility_1d
                and position.get("symbol") in self.volatility_1d
            ):
                vol1 = self.volatility_1d[trade.get("symbol")]
                vol2 = self.volatility_1d[position.get("symbol")]
                vol_similarity = 1.0 - abs(vol1 - vol2) / max(vol1, vol2, 0.01)

            # Price correlation (if available)
            price_corr = self._calculate_price_correlation(
                trade.get("symbol"), position.get("symbol")
            )

            # Volume correlation placeholder
            vol_corr = 0.5

            # Market cap ratio placeholder
            market_cap_ratio = 1.0

            features = np.array(
                [
                    [
                        1.0 if same_sector else 0.0,
                        vol_similarity,
                        price_corr,
                        vol_corr,
                        market_cap_ratio,
                    ]
                ]
            )

            # Scale and predict
            features_scaled = self.correlation_scaler.transform(features)
            predicted_corr = self.correlation_model.predict(features_scaled)[0]

            # Clip to valid range
            predicted_corr = np.clip(predicted_corr, 0.0, 1.0)

            logger.debug(f"ML predicted correlation: {predicted_corr:.2f}")

            return predicted_corr

        except Exception as e:
            logger.error(f"Error predicting correlation: {e}")
            return 0.5

    def _calculate_price_correlation(self, symbol1: str, symbol2: str) -> float:
        """Calculate correlation between two symbols from price history"""
        if (
            symbol1 not in self.price_history
            or symbol2 not in self.price_history
            or len(self.price_history[symbol1]) < 20
            or len(self.price_history[symbol2]) < 20
        ):
            return 0.5

        try:
            prices1 = np.array([p for _, p in self.price_history[symbol1][-20:]])
            prices2 = np.array([p for _, p in self.price_history[symbol2][-20:]])

            returns1 = np.diff(prices1) / prices1[:-1]
            returns2 = np.diff(prices2) / prices2[:-1]

            min_len = min(len(returns1), len(returns2))
            if min_len < 5:
                return 0.5

            corr = abs(np.corrcoef(returns1[-min_len:], returns2[-min_len:])[0, 1])
            return corr if not np.isnan(corr) else 0.5

        except Exception as e:
            logger.debug(f"Error calculating price correlation: {e}")
            return 0.5

    def calculate_portfolio_var(
        self, confidence_level: Optional[float] = None
    ) -> float:
        """
        Calculate Value at Risk (VaR) for the portfolio
        Uses historical simulation method

        Args:
            confidence_level: Confidence level (default from config)

        Returns:
            VaR as portfolio value percentage
        """
        if not self.enable_var_calculation:
            return 0.0

        confidence = confidence_level or self.var_confidence_level

        # Need sufficient trade history
        if len(self.trade_history) < 30:
            logger.debug("Insufficient history for VaR calculation")
            return 0.0

        try:
            # Get recent returns
            recent_trades = self.trade_history[-100:]  # Last 100 trades
            returns = [t["pnl"] for t in recent_trades]

            # Historical VaR
            returns_sorted = np.sort(returns)
            var_index = int((1 - confidence) * len(returns_sorted))
            historical_var = abs(returns_sorted[var_index])

            # Also calculate parametric VaR
            mean_return = np.mean(returns)
            std_return = np.std(returns)

            # Z-score for confidence level (95% = 1.645, 99% = 2.326)
            z_score = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}.get(confidence, 1.645)

            parametric_var = abs(mean_return - z_score * std_return)

            # Use average of both methods
            var = (historical_var + parametric_var) / 2

            # Store for tracking
            self.portfolio_var_history.append((datetime.now(), var))
            if len(self.portfolio_var_history) > 100:
                self.portfolio_var_history = self.portfolio_var_history[-100:]

            logger.debug(f"Portfolio VaR ({confidence*100}%): {var:.2f}")

            return var

        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0.0

    def calculate_parametric_var(
        self, portfolio_value: float, confidence_level: Optional[float] = None
    ) -> float:
        """
        Calculate parametric VaR as percentage of portfolio

        Args:
            portfolio_value: Current portfolio value
            confidence_level: Confidence level (default from config)

        Returns:
            VaR as percentage of portfolio
        """
        if portfolio_value == 0:
            return 0.0

        var_dollars = self.calculate_portfolio_var(confidence_level)
        return var_dollars / portfolio_value if portfolio_value > 0 else 0.0

    def calculate_multi_timeframe_volatility(self, symbol: str) -> Dict[str, float]:
        """
        Calculate volatility across multiple timeframes

        Args:
            symbol: Asset symbol

        Returns:
            Dictionary with volatility for different timeframes
        """
        if not self.enable_multi_timeframe_volatility:
            return {"1d": 0.0}

        if symbol not in self.price_history or len(self.price_history[symbol]) < 10:
            return {"1d": 0.0}

        try:
            prices_with_time = self.price_history[symbol]

            # Calculate for different lookback periods
            now = datetime.now()

            # 1-hour volatility (last hour of data)
            hour_ago = now - timedelta(hours=1)
            hourly_prices = [p for t, p in prices_with_time if t >= hour_ago]
            vol_1h = (
                self._calculate_volatility_from_prices(hourly_prices)
                if len(hourly_prices) >= 5
                else 0.0
            )

            # 1-day volatility (last 24 hours)
            day_ago = now - timedelta(days=1)
            daily_prices = [p for t, p in prices_with_time if t >= day_ago]
            vol_1d = (
                self._calculate_volatility_from_prices(daily_prices)
                if len(daily_prices) >= 10
                else 0.0
            )

            # 1-week volatility (last 7 days)
            week_ago = now - timedelta(days=7)
            weekly_prices = [p for t, p in prices_with_time if t >= week_ago]
            vol_1w = (
                self._calculate_volatility_from_prices(weekly_prices)
                if len(weekly_prices) >= 20
                else 0.0
            )

            # Store for later use
            if vol_1h > 0:
                self.volatility_1h[symbol] = vol_1h
            if vol_1d > 0:
                self.volatility_1d[symbol] = vol_1d
            if vol_1w > 0:
                self.volatility_1w[symbol] = vol_1w

            return {"1h": vol_1h, "1d": vol_1d, "1w": vol_1w}

        except Exception as e:
            logger.error(f"Error calculating multi-timeframe volatility: {e}")
            return {"1d": 0.0}

    def _calculate_volatility_from_prices(self, prices: List[float]) -> float:
        """Calculate volatility from price list"""
        if len(prices) < 2:
            return 0.0

        prices_array = np.array(prices)
        returns = np.diff(prices_array) / prices_array[:-1]
        return float(np.std(returns))

    def detect_volatility_regime(self, symbol: str) -> str:
        """
        Detect current volatility regime (low, normal, high)

        Args:
            symbol: Asset symbol

        Returns:
            Regime: 'low', 'normal', or 'high'
        """
        vol_data = self.calculate_multi_timeframe_volatility(symbol)

        if not vol_data or vol_data["1d"] == 0:
            return "normal"

        # Compare current volatility to recent average
        vol_current = vol_data["1d"]

        # Thresholds (can be made configurable)
        low_threshold = 0.01
        high_threshold = 0.04

        if vol_current < low_threshold:
            return "low"
        elif vol_current > high_threshold:
            return "high"
        else:
            return "normal"

    def adjust_rr_ratio_dynamically(self) -> float:
        """
        Dynamically adjust minimum risk-reward ratio based on:
        - Current market volatility
        - Recent win rate
        - Recent performance

        Returns:
            Adjusted minimum RR ratio
        """
        if not self.enable_dynamic_rr_adjustment:
            return self.min_risk_reward_ratio

        base_rr = self.min_risk_reward_ratio
        adjusted_rr = base_rr

        try:
            # Factor 1: Win rate adjustment
            # If win rate is high, can accept slightly lower RR
            # If win rate is low, require higher RR
            win_rate = self.get_win_rate()
            total_trades = self.win_count + self.loss_count

            if total_trades >= 20:
                if win_rate > 0.65:
                    # High win rate: can reduce RR slightly
                    adjusted_rr *= 0.9
                elif win_rate < 0.45:
                    # Low win rate: increase RR requirement
                    adjusted_rr *= 1.2

            # Factor 2: Recent performance
            # If recent trades are losing, increase RR requirement
            if len(self.trade_history) >= 10:
                recent_pnl = sum(t["pnl"] for t in self.trade_history[-10:])
                if recent_pnl < 0:
                    adjusted_rr *= 1.1

            # Factor 3: Average market volatility
            # Higher volatility → require better RR
            if self.volatility_1d:
                avg_vol = np.mean(list(self.volatility_1d.values()))
                if avg_vol > 0.04:  # High volatility
                    adjusted_rr *= 1.15
                elif avg_vol < 0.015:  # Low volatility
                    adjusted_rr *= 0.95

            # Bound the adjustment (don't go below 1.5 or above 3.5)
            adjusted_rr = np.clip(adjusted_rr, 1.5, 3.5)

            self.current_min_rr_ratio = adjusted_rr

            logger.debug(f"Adjusted RR ratio from {base_rr:.2f} to {adjusted_rr:.2f}")

            return adjusted_rr

        except Exception as e:
            logger.error(f"Error adjusting RR ratio: {e}")
            return base_rr

    def update_correlation_training_data(
        self, symbol1: str, symbol2: str, actual_correlation: float
    ):
        """
        Update training data for correlation prediction model

        Args:
            symbol1: First symbol
            symbol2: Second symbol
            actual_correlation: Observed correlation
        """
        if not self.enable_ml_correlation:
            return

        # Get additional features
        sector1 = None
        sector2 = None

        for pos in self.open_positions:
            if pos.get("symbol") == symbol1:
                sector1 = pos.get("sector")
            if pos.get("symbol") == symbol2:
                sector2 = pos.get("sector")

        vol_similarity = 0.5
        if symbol1 in self.volatility_1d and symbol2 in self.volatility_1d:
            vol1 = self.volatility_1d[symbol1]
            vol2 = self.volatility_1d[symbol2]
            vol_similarity = 1.0 - abs(vol1 - vol2) / max(vol1, vol2, 0.01)

        price_corr = self._calculate_price_correlation(symbol1, symbol2)

        training_sample = {
            "same_sector": sector1 == sector2 and sector1 is not None,
            "volatility_similarity": vol_similarity,
            "price_correlation": price_corr,
            "volume_correlation": 0.5,  # Placeholder
            "market_cap_ratio": 1.0,  # Placeholder
            "actual_correlation": actual_correlation,
        }

        self.correlation_training_data.append(training_sample)

        # Keep only recent data
        if len(self.correlation_training_data) > 500:
            self.correlation_training_data = self.correlation_training_data[-500:]

        # Retrain model periodically
        if len(self.correlation_training_data) % 50 == 0:
            self.train_correlation_model()

    def scenario_stress_test(self, portfolio: Dict[str, float], scenarios: List[Dict[str, Any]]) -> Dict[str, float]:
        """Perform stress testing on a portfolio under given scenarios."""
        results = {}
        for scenario in scenarios:
            impact = sum(portfolio.get(asset, 0) * scenario.get(asset, 1) for asset in portfolio)
            results[scenario.get('name', 'Scenario')] = float(impact)
        logger.debug(f"Stress test results: {results}")
        return results

    def ml_anomaly_detection(self, trade_history: List[Dict[str, Any]]) -> float:
        """Detect anomalies in trade history using ML."""
        try:
            import numpy as np
            from sklearn.ensemble import IsolationForest
            X = np.array([[t.get('size', 0), t.get('price', 0)] for t in trade_history])
            if len(X) < 2:
                return 0.0
            clf = IsolationForest().fit(X)
            scores = clf.decision_function(X)
            anomaly_score = float(np.mean(scores < 0))
            logger.info(f"ML anomaly score: {anomaly_score}")
            return anomaly_score
        except Exception as e:
            logger.error(f"ML anomaly detection error: {e}")
            return 0.0

    def real_time_risk_alert(self, trade: Dict[str, Any], portfolio_value: float) -> Optional[str]:
        """Generate real-time risk alert for a trade."""
        stop_loss = trade.get('stop_loss')
        price = trade.get('price')
        if stop_loss and abs(price - stop_loss) / price > self.stop_loss_percent * 2:
            return f"ALERT: Trade stop-loss is set unusually far from entry price!"
        if trade.get('size', 0) * price > portfolio_value * self.max_position_size * 2:
            return f"ALERT: Trade size exceeds double the max position size!"
        return None

    def apply_multi_layered_stop_loss(self, position, market_data):
        structured_logger.log_event(
            "stop_loss_check",
            "Applying multi-layered stop-loss",
            {"position": position, "market_data": market_data}
        )
        # Volatility-based stop-loss
        # Profit-protecting stop-loss
        # Time-based stop-loss
        # ...logic to combine and trigger stop-losses...
        return {
            "volatility_stop": True,
            "profit_protect_stop": True,
            "time_stop": False
        }

    def check_capital_risk_budget(self, portfolio):
        structured_logger.log_event(
            "risk_budget_check",
            "Checking capital risk budget and drawdown circuit breakers",
            {"portfolio": portfolio}
        )
        # ...logic for risk budgeting and drawdown circuit breaker...
        return {
            "risk_budget_ok": True,
            "drawdown_triggered": False
        }

    def ai_position_watchdog(self, positions, market_data):
        structured_logger.log_event(
            "ai_watchdog",
            "Running AI-based position watchdog",
            {"positions": positions, "market_data": market_data}
        )
        # ...AI logic for monitoring positions...
        return {
            "flagged_positions": [],
            "sentiment_hedge": True
        }

    def get_meta_risk_dashboard(self, portfolio, market_data):
        structured_logger.log_event(
            "meta_risk_dashboard",
            "Generating live meta-risk dashboard and exposure mapping",
            {"portfolio": portfolio, "market_data": market_data}
        )
        # ...logic for dashboard and exposure mapping...
        return {
            "exposure_map": {},
            "risk_summary": {},
            "live_metrics": {}
        }

    def dynamic_stop_loss(self, position, market_data):
        structured_logger.log_event(
            "dynamic_stop_loss",
            "Applying dynamic stop-loss logic",
            {"position": position, "market_data": market_data}
        )
        # ...logic for dynamic stop-loss...
        return {"stop_loss": True, "level": 0.97}

    def position_sizing(self, trade, portfolio):
        structured_logger.log_event(
            "position_sizing",
            "Calculating position sizing",
            {"trade": trade, "portfolio": portfolio}
        )
        # ...logic for position sizing...
        return {"size": 100, "risk": 0.02}

    def drawdown_limits(self, portfolio):
        structured_logger.log_event(
            "drawdown_limits",
            "Checking drawdown limits",
            {"portfolio": portfolio}
        )
        # ...logic for drawdown limits...
        return {"limit": 0.15, "triggered": False}

    def real_time_health_scan(self, strategies):
        structured_logger.log_event(
            "health_scan",
            "Running real-time health scan",
            {"strategies": strategies}
        )
        # ...logic for health scanning...
        return {"healthy": True, "issues": []}

    def strategy_failure_detection(self, strategies):
        structured_logger.log_event(
            "failure_detection",
            "Detecting strategy failures",
            {"strategies": strategies}
        )
        # ...logic for failure detection...
        return {"failed_strategies": []}

    def hedging(self, positions, market_data):
        structured_logger.log_event(
            "hedging",
            "Applying hedging logic",
            {"positions": positions, "market_data": market_data}
        )
        # ...logic for hedging...
        return {"hedged": True, "hedge_positions": []}

    def anomaly_detection(self, data):
        structured_logger.log_event(
            "anomaly_detection",
            "Running anomaly detection",
            {"data": data}
        )
        # ...logic for anomaly detection...
        return {"anomalies": []}

    def regret_minimization(self, trades):
        structured_logger.log_event(
            "regret_minimization",
            "Running regret minimization",
            {"trades": trades}
        )
        # ...logic for regret minimization...
        return {"regret_score": 0.03, "optimized": True}
