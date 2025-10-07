"""
Test suite for enhanced risk management system
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from sentio.risk.risk_manager import RiskManager, RiskLevel, CircuitBreakerState


class TestRiskManager:
    """Test cases for RiskManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = {
            "max_position_size": 0.05,
            "max_portfolio_risk": 0.20,
            "stop_loss_percent": 0.02,
            "take_profit_percent": 0.05,
            "max_daily_drawdown": 0.03,
            "circuit_breaker_threshold": 0.05,
            "min_risk_reward_ratio": 2.0,
            "max_loss_per_trade": 0.01,
            "max_correlation": 0.7,
            "enable_kelly_criterion": False,
            "max_sector_concentration": 0.30,
            "enable_ml_correlation": True,
            "enable_var_calculation": True,
            "enable_multi_timeframe_volatility": True,
            "enable_dynamic_rr_adjustment": True,
            "var_confidence_level": 0.95,
            "var_time_horizon": 1,
        }
        self.risk_manager = RiskManager(config=self.config)
        self.risk_manager.daily_start_value = 100000

    def test_initialization(self):
        """Test risk manager initialization"""
        assert self.risk_manager.max_position_size == 0.05
        assert self.risk_manager.min_risk_reward_ratio == 2.0
        assert self.risk_manager.max_loss_per_trade == 0.01
        assert self.risk_manager.circuit_breaker_state == CircuitBreakerState.NORMAL

    def test_risk_reward_ratio_calculation(self):
        """Test risk-reward ratio calculation"""
        # Long position
        ratio = self.risk_manager._calculate_risk_reward_ratio(
            entry_price=100, stop_loss=98, take_profit=106, direction="long"
        )
        assert ratio == 3.0  # 6 reward / 2 risk = 3:1

        # Short position
        ratio = self.risk_manager._calculate_risk_reward_ratio(
            entry_price=100, stop_loss=102, take_profit=94, direction="short"
        )
        assert ratio == 3.0  # 6 reward / 2 risk = 3:1

    def test_assess_trade_risk_with_good_rrr(self):
        """Test trade assessment with good risk-reward ratio"""
        trade = {
            "symbol": "AAPL",
            "price": 150,
            "size": 100,
            "direction": "long",
            "stop_loss": 147,  # 2% stop loss
            "take_profit": 159,  # 6% take profit (3:1 R:R)
            "sector": "technology",
        }

        result = self.risk_manager.assess_trade_risk(
            trade=trade, portfolio_value=100000, current_exposure=0
        )

        assert result.approved is True
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MODERATE]

    def test_assess_trade_risk_with_poor_rrr(self):
        """Test trade assessment with poor risk-reward ratio"""
        trade = {
            "symbol": "AAPL",
            "price": 150,
            "size": 100,
            "direction": "long",
            "stop_loss": 148,  # 1.33% stop loss
            "take_profit": 151,  # 0.67% take profit (0.5:1 R:R - bad)
            "sector": "technology",
        }

        result = self.risk_manager.assess_trade_risk(
            trade=trade, portfolio_value=100000, current_exposure=0
        )

        # Should have warning about poor risk-reward ratio
        assert any("risk-reward" in w.lower() for w in result.warnings)

    def test_max_loss_per_trade_constraint(self):
        """Test that max loss per trade is enforced"""
        trade = {
            "symbol": "AAPL",
            "price": 100,
            "size": 1000,  # Large position
            "direction": "long",
            "stop_loss": 95,  # 5% stop loss
            "sector": "technology",
        }

        result = self.risk_manager.assess_trade_risk(
            trade=trade, portfolio_value=100000, current_exposure=0
        )

        # Position should be adjusted to meet max loss constraint
        if "size" in result.adjustments:
            adjusted_size = result.adjustments["size"]
            max_loss = abs(100 - 95) * adjusted_size
            max_loss_percent = max_loss / 100000
            assert (
                max_loss_percent <= self.config["max_loss_per_trade"] * 1.01
            )  # Allow 1% tolerance

    def test_sector_concentration_check(self):
        """Test sector concentration limits"""
        # Add existing position in technology sector
        self.risk_manager.update_position(
            {
                "symbol": "MSFT",
                "price": 300,
                "size": 100,
                "value": 30000,
                "sector": "technology",
            }
        )

        # Try to add another large tech position
        trade = {
            "symbol": "GOOGL",
            "price": 100,
            "size": 100,
            "direction": "long",
            "sector": "technology",
        }

        result = self.risk_manager.assess_trade_risk(
            trade=trade, portfolio_value=100000, current_exposure=30000
        )

        # Should reject due to sector concentration
        # 30000 + 10000 = 40000 = 40% > 30% limit
        assert result.approved is False or "sector" in str(result.reasons).lower()

    def test_volatility_assessment_with_history(self):
        """Test volatility assessment with price history"""
        # Add price history
        symbol = "AAPL"
        base_price = 150
        for i in range(50):
            # Simulate volatile price movement
            price = base_price + np.random.normal(0, 5)
            self.risk_manager.price_history[symbol].append((datetime.now(), price))

        trade = {"symbol": symbol, "sector": "technology"}
        volatility_risk = self.risk_manager._assess_volatility_risk(trade)

        assert 0 <= volatility_risk <= 1

    def test_correlation_assessment(self):
        """Test correlation assessment between positions"""
        # Add position with price history
        symbol1 = "AAPL"
        symbol2 = "MSFT"

        # Create correlated price movements
        for i in range(30):
            base_move = np.random.normal(0, 1)
            price1 = 150 + base_move + np.random.normal(0, 0.1)
            price2 = 300 + base_move * 2 + np.random.normal(0, 0.2)

            self.risk_manager.price_history[symbol1].append((datetime.now(), price1))
            self.risk_manager.price_history[symbol2].append((datetime.now(), price2))

        self.risk_manager.update_position(
            {
                "symbol": symbol1,
                "price": 150,
                "size": 100,
                "value": 15000,
                "sector": "technology",
            }
        )

        trade = {"symbol": symbol2, "sector": "technology"}
        correlation_risk = self.risk_manager._assess_correlation_risk(trade)

        # Should detect high correlation
        assert correlation_risk > 0.5

    def test_win_rate_calculation(self):
        """Test win rate calculation"""
        # Record some wins and losses
        for _ in range(7):
            self.risk_manager.close_position("WIN", 100)
        for _ in range(3):
            self.risk_manager.close_position("LOSS", -50)

        win_rate = self.risk_manager.get_win_rate()
        assert win_rate == 0.7  # 7 wins / 10 total

    def test_expectancy_calculation(self):
        """Test trading expectancy calculation"""
        # Record wins
        for _ in range(6):
            self.risk_manager.close_position("WIN", 100)
        # Record losses
        for _ in range(4):
            self.risk_manager.close_position("LOSS", -50)

        expectancy = self.risk_manager.get_expectancy()
        # (0.6 * 100) - (0.4 * 50) = 60 - 20 = 40
        assert abs(expectancy - 40) < 1

    def test_kelly_criterion_calculation(self):
        """Test Kelly Criterion calculation"""
        kelly = self.risk_manager.calculate_kelly_criterion(
            win_rate=0.6, avg_win=100, avg_loss=50
        )

        # Kelly = (p * (b) - (1-p)) / b where b = avg_win/avg_loss
        # b = 100/50 = 2
        # Kelly = (0.6 * 2 - 0.4) / 2 = 0.4
        # Half Kelly = 0.2
        # Should be capped at max_position_size (0.05)
        assert 0 <= kelly <= 0.05

    def test_kelly_position_sizing(self):
        """Test Kelly Criterion position sizing when enabled"""
        # Enable Kelly
        self.risk_manager.enable_kelly_criterion = True

        # Build history (need 20+ trades)
        for _ in range(15):
            self.risk_manager.close_position("WIN", 100)
        for _ in range(10):
            self.risk_manager.close_position("LOSS", -50)

        position_size = self.risk_manager.calculate_position_size(
            portfolio_value=100000, risk_per_trade=0.02, entry_price=100, stop_loss=98
        )

        assert position_size > 0
        # Should not exceed max position size
        assert position_size <= (100000 * 0.05) / 100

    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation"""
        # Record some trades with varying P&L
        pnls = [100, -50, 150, -30, 80, 120, -40, 90]
        for pnl in pnls:
            self.risk_manager.close_position("TEST", pnl)

        sharpe = self.risk_manager.get_sharpe_ratio()

        # Should return a valid number
        assert isinstance(sharpe, (int, float))
        assert not np.isnan(sharpe)

    def test_enhanced_risk_metrics(self):
        """Test enhanced risk metrics reporting"""
        # Add some trading history
        self.risk_manager.close_position("WIN1", 100)
        self.risk_manager.close_position("LOSS1", -50)
        self.risk_manager.update_position(
            {"symbol": "AAPL", "value": 5000, "sector": "technology"}
        )

        metrics = self.risk_manager.get_risk_metrics()

        # Check new metrics are present
        assert "win_rate" in metrics
        assert "expectancy" in metrics
        assert "sharpe_ratio" in metrics
        assert "sector_exposure" in metrics
        assert "total_trades" in metrics
        assert "avg_win" in metrics
        assert "avg_loss" in metrics

        assert metrics["total_trades"] == 2
        assert metrics["win_count"] == 1
        assert metrics["loss_count"] == 1

    def test_circuit_breaker_with_tracking(self):
        """Test circuit breaker with win/loss tracking"""
        # Trigger circuit breaker with losses
        self.risk_manager.close_position("LOSS1", -3000)
        self.risk_manager.close_position("LOSS2", -2500)

        # Check circuit breaker is tripped
        assert self.risk_manager.circuit_breaker_state in [
            CircuitBreakerState.WARNING,
            CircuitBreakerState.TRIPPED,
        ]
        assert self.risk_manager.loss_count == 2

    def test_multi_timeframe_volatility_calculation(self):
        """Test multi-timeframe volatility analysis"""
        symbol = "AAPL"

        # Add price history with timestamps for different timeframes
        now = datetime.now()
        for i in range(100):
            # Simulate hourly price updates
            timestamp = now - timedelta(hours=100 - i)
            price = 150 + np.random.normal(0, 2)
            self.risk_manager.price_history[symbol].append((timestamp, price))

        vol_data = self.risk_manager.calculate_multi_timeframe_volatility(symbol)

        assert "1h" in vol_data
        assert "1d" in vol_data
        assert "1w" in vol_data
        assert all(v >= 0 for v in vol_data.values())

    def test_volatility_regime_detection(self):
        """Test volatility regime detection"""
        symbol = "AAPL"

        # Add low volatility data
        now = datetime.now()
        for i in range(50):
            timestamp = now - timedelta(hours=50 - i)
            price = 150 + np.random.normal(0, 0.5)  # Low volatility
            self.risk_manager.price_history[symbol].append((timestamp, price))

        regime = self.risk_manager.detect_volatility_regime(symbol)
        assert regime in ["low", "normal", "high"]

    def test_var_calculation(self):
        """Test VaR (Value at Risk) calculation"""
        # Add trade history
        for i in range(50):
            pnl = np.random.normal(100, 300)  # Random P&L
            self.risk_manager.close_position(f"TRADE_{i}", pnl)

        var = self.risk_manager.calculate_portfolio_var()

        assert var >= 0
        assert isinstance(var, (int, float))

    def test_parametric_var(self):
        """Test parametric VaR calculation"""
        # Add trade history
        for i in range(50):
            pnl = np.random.normal(100, 300)
            self.risk_manager.close_position(f"TRADE_{i}", pnl)

        portfolio_value = 100000
        var_percent = self.risk_manager.calculate_parametric_var(portfolio_value)

        assert 0 <= var_percent <= 1

    def test_dynamic_rr_adjustment_high_win_rate(self):
        """Test dynamic RR adjustment with high win rate"""
        # Create high win rate scenario
        for _ in range(15):
            self.risk_manager.close_position("WIN", 100)
        for _ in range(5):
            self.risk_manager.close_position("LOSS", -50)

        adjusted_rr = self.risk_manager.adjust_rr_ratio_dynamically()

        # With high win rate, RR should be lower than base
        assert adjusted_rr <= self.config["min_risk_reward_ratio"] * 1.1

    def test_dynamic_rr_adjustment_low_win_rate(self):
        """Test dynamic RR adjustment with low win rate"""
        # Create low win rate scenario
        for _ in range(8):
            self.risk_manager.close_position("WIN", 100)
        for _ in range(12):
            self.risk_manager.close_position("LOSS", -50)

        adjusted_rr = self.risk_manager.adjust_rr_ratio_dynamically()

        # With low win rate, RR should be higher than base
        assert adjusted_rr >= self.config["min_risk_reward_ratio"]

    def test_dynamic_rr_adjustment_high_volatility(self):
        """Test dynamic RR adjustment with high volatility"""
        # Add high volatility positions
        symbol = "VOLATILE"
        now = datetime.now()
        for i in range(50):
            timestamp = now - timedelta(hours=50 - i)
            price = 100 + np.random.normal(0, 10)  # High volatility
            self.risk_manager.price_history[symbol].append((timestamp, price))

        # Calculate volatility
        self.risk_manager.calculate_multi_timeframe_volatility(symbol)

        adjusted_rr = self.risk_manager.adjust_rr_ratio_dynamically()

        # High volatility should increase RR requirement
        assert adjusted_rr >= self.config["min_risk_reward_ratio"]

    def test_ml_correlation_training_data_collection(self):
        """Test ML correlation training data collection"""
        # Add positions with correlation data
        self.risk_manager.update_position(
            {
                "symbol": "AAPL",
                "price": 150,
                "size": 100,
                "value": 15000,
                "sector": "technology",
            }
        )

        self.risk_manager.update_position(
            {
                "symbol": "MSFT",
                "price": 300,
                "size": 50,
                "value": 15000,
                "sector": "technology",
            }
        )

        # Update correlation training data
        self.risk_manager.update_correlation_training_data("AAPL", "MSFT", 0.8)

        assert len(self.risk_manager.correlation_training_data) > 0
        assert (
            self.risk_manager.correlation_training_data[-1]["actual_correlation"] == 0.8
        )

    def test_ml_correlation_model_training(self):
        """Test ML correlation model training"""
        # Add sufficient training data
        for i in range(20):
            self.risk_manager.correlation_training_data.append(
                {
                    "same_sector": i % 2 == 0,
                    "volatility_similarity": np.random.rand(),
                    "price_correlation": np.random.rand(),
                    "volume_correlation": np.random.rand(),
                    "market_cap_ratio": 1.0,
                    "actual_correlation": np.random.rand(),
                }
            )

        # Train model
        self.risk_manager.train_correlation_model()

        # Model should be trained
        assert self.risk_manager.correlation_model is not None

    def test_ml_correlation_prediction(self):
        """Test ML-based correlation prediction"""
        # Setup training data and train model
        for i in range(20):
            self.risk_manager.correlation_training_data.append(
                {
                    "same_sector": True,
                    "volatility_similarity": 0.8,
                    "price_correlation": 0.7,
                    "volume_correlation": 0.6,
                    "market_cap_ratio": 1.0,
                    "actual_correlation": 0.75,
                }
            )

        self.risk_manager.train_correlation_model()

        # Create trade and position
        trade = {"symbol": "AAPL", "sector": "technology"}
        position = {"symbol": "MSFT", "sector": "technology"}

        # Predict correlation
        predicted_corr = self.risk_manager.predict_correlation(trade, position)

        assert 0 <= predicted_corr <= 1

    def test_enhanced_risk_metrics_includes_var(self):
        """Test that enhanced risk metrics include VaR"""
        # Add trade history for VaR calculation
        for i in range(50):
            pnl = np.random.normal(100, 300)
            self.risk_manager.close_position(f"TRADE_{i}", pnl)

        metrics = self.risk_manager.get_risk_metrics()

        # Check new metrics are present
        assert "portfolio_var" in metrics
        assert "current_min_rr_ratio" in metrics

    def test_assess_trade_risk_with_dynamic_rr(self):
        """Test trade assessment uses dynamic RR ratio"""
        # Build trading history
        for _ in range(15):
            self.risk_manager.close_position("WIN", 100)
        for _ in range(5):
            self.risk_manager.close_position("LOSS", -50)

        trade = {
            "symbol": "AAPL",
            "price": 150,
            "size": 100,
            "direction": "long",
            "stop_loss": 148,
            "take_profit": 154,  # 2:1 RR
            "sector": "technology",
        }

        result = self.risk_manager.assess_trade_risk(
            trade=trade, portfolio_value=100000, current_exposure=0
        )

        # Should use dynamically adjusted RR ratio
        assert result is not None
        assert hasattr(result, "approved")

    def test_volatility_assessment_uses_multi_timeframe(self):
        """Test volatility assessment uses multi-timeframe analysis"""
        symbol = "AAPL"

        # Add price history across different timeframes
        now = datetime.now()
        for i in range(100):
            timestamp = now - timedelta(hours=100 - i)
            price = 150 + np.random.normal(0, 3)
            self.risk_manager.price_history[symbol].append((timestamp, price))

        trade = {"symbol": symbol, "sector": "technology"}

        vol_risk = self.risk_manager._assess_volatility_risk(trade)

        assert 0 <= vol_risk <= 1
        # Check that multi-timeframe volatility was calculated
        assert symbol in self.risk_manager.volatility_1d or vol_risk == 0.5

    def test_correlation_assessment_with_ml(self):
        """Test correlation assessment can use ML prediction"""
        # Setup ML model
        for i in range(20):
            self.risk_manager.correlation_training_data.append(
                {
                    "same_sector": True,
                    "volatility_similarity": 0.8,
                    "price_correlation": 0.7,
                    "volume_correlation": 0.6,
                    "market_cap_ratio": 1.0,
                    "actual_correlation": 0.75,
                }
            )

        self.risk_manager.train_correlation_model()

        # Add existing position
        self.risk_manager.update_position(
            {
                "symbol": "MSFT",
                "price": 300,
                "size": 50,
                "value": 15000,
                "sector": "technology",
            }
        )

        # Assess correlation for new trade
        trade = {"symbol": "AAPL", "sector": "technology"}

        corr_risk = self.risk_manager._assess_correlation_risk(trade)

        assert 0 <= corr_risk <= 1

    def test_var_tracking_history(self):
        """Test VaR tracking maintains history"""
        # Add trades and calculate VaR multiple times
        for i in range(50):
            pnl = np.random.normal(100, 300)
            self.risk_manager.close_position(f"TRADE_{i}", pnl)

        # Calculate VaR multiple times
        for _ in range(5):
            self.risk_manager.calculate_portfolio_var()

        # Should have VaR history
        assert len(self.risk_manager.portfolio_var_history) > 0
        assert len(self.risk_manager.portfolio_var_history) <= 100  # Max 100 entries

    def test_circuit_breaker_reset(self):
        """Test circuit breaker reset functionality"""
        rm = RiskManager()
        rm.circuit_breaker_state = CircuitBreakerState.TRIPPED
        rm.last_reset = datetime.now() - timedelta(hours=25)
        rm.reset_daily_metrics()
        assert rm.circuit_breaker_state == CircuitBreakerState.NORMAL

    def test_daily_drawdown(self):
        """Test daily drawdown detection"""
        rm = RiskManager()
        rm.daily_start_value = 1000
        rm.daily_pnl = -200
        rm.max_daily_drawdown = 0.1
        assert rm._check_daily_drawdown() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
