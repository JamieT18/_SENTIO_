"""
Tests for core configuration module
"""

import pytest
from sentio.core.config import (
    TradingMode,
    SubscriptionTier,
    RiskLevel,
    MarketDataConfig,
    DatabaseConfig,
    RedisConfig,
    StrategyConfig,
    RiskManagementConfig,
    AIConfig,
    BillingConfig,
    SentioConfig,
    ConfigManager,
    get_config,
)


def test_trading_mode_enum():
    """Test TradingMode enum values"""
    assert TradingMode.DAY_TRADING.value == "day_trading"
    assert TradingMode.LONG_TERM.value == "long_term"
    assert TradingMode.HYBRID.value == "hybrid"


def test_subscription_tier_enum():
    """Test SubscriptionTier enum values"""
    assert SubscriptionTier.FREE.value == "free"
    assert SubscriptionTier.BASIC.value == "basic"
    assert SubscriptionTier.PROFESSIONAL.value == "professional"
    assert SubscriptionTier.ENTERPRISE.value == "enterprise"


def test_risk_level_enum():
    """Test RiskLevel enum values"""
    assert RiskLevel.CONSERVATIVE.value == "conservative"
    assert RiskLevel.MODERATE.value == "moderate"
    assert RiskLevel.AGGRESSIVE.value == "aggressive"


def test_market_data_config_defaults():
    """Test MarketDataConfig default values"""
    config = MarketDataConfig()
    assert config.provider == "alpaca"
    assert config.api_key is None
    assert config.api_secret is None
    assert config.base_url == "https://paper-api.alpaca.markets"


def test_database_config_defaults():
    """Test DatabaseConfig default values"""
    config = DatabaseConfig()
    assert config.url == "sqlite:///sentio.db"
    assert config.pool_size == 10
    assert config.max_overflow == 20
    assert config.pool_timeout == 30


def test_redis_config_defaults():
    """Test RedisConfig default values"""
    config = RedisConfig()
    assert config.host == "localhost"
    assert config.port == 6379
    assert config.db == 0
    assert config.password is None


def test_strategy_config_defaults():
    """Test StrategyConfig default values"""
    config = StrategyConfig()
    assert config.confidence_threshold == 0.65
    assert config.min_voting_strategies == 2
    assert config.max_concurrent_trades == 5
    assert config.enable_strategy_rotation is True


def test_risk_management_config_defaults():
    """Test RiskManagementConfig default values"""
    config = RiskManagementConfig()
    assert config.max_position_size == 0.05
    assert config.max_portfolio_risk == 0.20
    assert config.stop_loss_percent == 0.02
    assert config.take_profit_percent == 0.05
    assert config.max_daily_drawdown == 0.03


def test_ai_config_defaults():
    """Test AIConfig default values"""
    config = AIConfig()
    assert config.enable_reinforcement_learning is True
    assert config.enable_multi_agent is True
    assert config.enable_meta_learning is True
    assert config.model_update_frequency == 24


def test_billing_config_defaults():
    """Test BillingConfig default values"""
    config = BillingConfig()
    assert config.enable_profit_sharing is True
    assert config.profit_sharing_percentage == 0.20


def test_sentio_config_defaults():
    """Test SentioConfig default values"""
    config = SentioConfig()
    assert config.trading_mode == TradingMode.HYBRID
    assert config.risk_level == RiskLevel.MODERATE
    assert config.log_level == "INFO"
    assert config.enable_backtesting is True
    assert config.enable_paper_trading is True
    assert config.enable_live_trading is False


def test_config_manager_singleton():
    """Test ConfigManager is a singleton"""
    manager1 = ConfigManager()
    manager2 = ConfigManager()
    assert manager1 is manager2


def test_get_config():
    """Test get_config returns SentioConfig instance"""
    config = get_config()
    assert isinstance(config, SentioConfig)


def test_sentio_config_model_dump():
    """Test SentioConfig can be dumped to dict"""
    config = SentioConfig()
    config_dict = config.model_dump()
    assert isinstance(config_dict, dict)
    assert "trading_mode" in config_dict
    assert "risk_level" in config_dict
    assert "market_data" in config_dict
