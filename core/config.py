"""
Core configuration management for Sentio
Manages system-wide settings, API keys, and operational parameters
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings
from enum import Enum
import json
from pathlib import Path
import os
from sentio.core.logger import SentioLogger


class TradingMode(str, Enum):
    """Trading mode enumeration"""

    DAY_TRADING = "day_trading"
    LONG_TERM = "long_term"
    HYBRID = "hybrid"


class SubscriptionTier(str, Enum):
    """Subscription tier levels"""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class RiskLevel(str, Enum):
    """Risk tolerance levels"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class MarketDataConfig(BaseSettings):
    """Market data provider configuration"""

    provider: str = "alpaca"
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: str = "https://paper-api.alpaca.markets"
    websocket_url: str = "wss://stream.data.alpaca.markets"

    model_config = ConfigDict(env_prefix="MARKET_DATA_")


class DatabaseConfig(BaseSettings):
    """Database configuration with optimized pooling"""

    url: str = "sqlite:///sentio.db"
    pool_size: int = 20  # Increased for better concurrency
    max_overflow: int = 40  # Increased overflow capacity
    pool_timeout: int = 30
    pool_recycle: int = 3600  # Recycle connections every hour
    pool_pre_ping: bool = True  # Verify connections before use
    echo: bool = False  # Disable SQL logging for performance

    model_config = ConfigDict(env_prefix="DATABASE_")


class RedisConfig(BaseSettings):
    """Redis cache configuration optimized for performance"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    socket_keepalive: bool = True
    max_connections: int = 50  # Connection pool size
    decode_responses: bool = True

    model_config = ConfigDict(env_prefix="REDIS_")


class StrategyConfig(BaseModel):
    """Strategy execution configuration"""

    enabled_strategies: list = Field(
        default_factory=lambda: [
            "tjr",
            "scalping",
            "swing",
            "trend_following",
            "momentum",
            "breakout",
            "mean_reversion",
        ]
    )
    confidence_threshold: float = 0.65
    min_voting_strategies: int = 2
    max_concurrent_trades: int = 5
    enable_strategy_rotation: bool = True


class RiskManagementConfig(BaseModel):
    """Risk management parameters"""

    max_position_size: float = 0.05  # 5% of portfolio per position
    max_portfolio_risk: float = 0.20  # 20% maximum risk
    stop_loss_percent: float = 0.02  # 2% stop loss
    take_profit_percent: float = 0.05  # 5% take profit
    max_daily_drawdown: float = 0.03  # 3% daily drawdown limit
    circuit_breaker_threshold: float = (
        0.05  # 5% portfolio loss triggers circuit breaker
    )
    enable_adaptive_sizing: bool = True
    enable_anomaly_detection: bool = True

    # Enhanced risk parameters
    min_risk_reward_ratio: float = 2.0  # Minimum 1:2 risk-reward ratio
    max_loss_per_trade: float = 0.01  # Maximum 1% loss per trade
    max_correlation: float = 0.7  # Maximum correlation between positions
    enable_kelly_criterion: bool = False  # Enable Kelly Criterion position sizing
    max_sector_concentration: float = 0.30  # Maximum 30% exposure per sector

    # Advanced risk management features
    enable_ml_correlation: bool = True  # Enable ML-based correlation prediction
    enable_var_calculation: bool = True  # Enable VaR calculations
    enable_multi_timeframe_volatility: bool = (
        True  # Enable multi-timeframe volatility analysis
    )
    enable_dynamic_rr_adjustment: bool = (
        True  # Enable dynamic risk-reward ratio adjustment
    )
    var_confidence_level: float = 0.95  # VaR confidence level (95%)
    var_time_horizon: int = 1  # VaR time horizon in days


class AIConfig(BaseModel):
    """AI and machine learning configuration"""

    enable_reinforcement_learning: bool = True
    enable_multi_agent: bool = True
    enable_meta_learning: bool = True
    model_update_frequency: int = 24  # hours
    trade_memory_size: int = 10000
    clustering_algorithm: str = "kmeans"
    confidence_calibration: bool = True


class BillingConfig(BaseSettings):
    """Billing and monetization configuration"""

    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    enable_profit_sharing: bool = True
    profit_sharing_percentage: float = 0.20  # 20% profit sharing

    model_config = ConfigDict(env_prefix="STRIPE_")


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""

    enabled: bool = False
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000


class MonitoringConfig(BaseModel):
    """API monitoring configuration"""

    enabled: bool = False
    max_history: int = 1000


class CacheConfig(BaseModel):
    """Caching configuration for performance optimization"""

    enabled: bool = True
    default_ttl: int = 300  # 5 minutes default TTL
    market_data_ttl: int = 60  # 1 minute for market data
    quote_ttl: int = 30  # 30 seconds for quotes
    analysis_ttl: int = 300  # 5 minutes for analysis results
    strategy_ttl: int = 180  # 3 minutes for strategy signals
    max_cache_size: int = 1000  # Maximum number of cached items


class SentioConfig(BaseSettings):
    """Main Sentio system configuration"""

    # System settings
    trading_mode: TradingMode = TradingMode.HYBRID
    risk_level: RiskLevel = RiskLevel.MODERATE

    # Component configurations
    market_data: MarketDataConfig = Field(default_factory=MarketDataConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    strategy: StrategyConfig = Field(default_factory=StrategyConfig)
    risk_management: RiskManagementConfig = Field(default_factory=RiskManagementConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    billing: BillingConfig = Field(default_factory=BillingConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)

    # System parameters
    log_level: str = "INFO"
    enable_backtesting: bool = True
    enable_paper_trading: bool = True
    enable_live_trading: bool = False

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_base_url: str = "http://localhost:8000"

    # Security
    secret_key: str = "CHANGE_THIS_SECRET_KEY"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )


structured_logger = SentioLogger.get_structured_logger("config_manager")


class ConfigManager:
    """
    Dynamic configuration manager for Sentio
    """
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "sentio_config.json"
        self._config = None
        self.load_config()

    def load_config(self):
        structured_logger.log_event(
            "config_load",
            "Loading configuration",
            {"config_path": getattr(self, 'config_path', None)}
        )
        try:
            config = self._load_config_logic()
            structured_logger.log_event(
                "config_load_result",
                "Configuration loaded",
                {"config_keys": list(config.keys()) if hasattr(config, 'keys') else str(config)[:200]}
            )
            return config
        except Exception as e:
            structured_logger.log_event(
                "config_load_error",
                str(e),
                {"config_path": getattr(self, 'config_path', None), "exception": repr(e)},
                level="error"
            )
            raise

    def apply_env_overrides(self):
        for key in self._config:
            env_key = f"SENTIO_{key.upper()}"
            if env_key in os.environ:
                self._config[key] = os.environ[env_key]

    def reload(self):
        structured_logger.log_event(
            "config_reload",
            "Reloading configuration",
            {"config_path": getattr(self, 'config_path', None)}
        )
        try:
            config = self._reload_logic()
            structured_logger.log_event(
                "config_reload_result",
                "Configuration reloaded",
                {"config_keys": list(config.keys()) if hasattr(config, 'keys') else str(config)[:200]}
            )
            return config
        except Exception as e:
            structured_logger.log_event(
                "config_reload_error",
                str(e),
                {"config_path": getattr(self, 'config_path', None), "exception": repr(e)},
                level="error"
            )
            raise

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value):
        structured_logger.log_event(
            "config_update",
            f"Updating config key {key}",
            {"key": key, "value": value}
        )
        try:
            result = self._set_logic(key, value)
            structured_logger.log_event(
                "config_update_result",
                f"Config key {key} updated",
                {"result": result}
            )
            return result
        except Exception as e:
            structured_logger.log_event(
                "config_update_error",
                str(e),
                {"key": key, "value": value, "exception": repr(e)},
                level="error"
            )
            raise

    def validate(self):
        # Add validation logic for required keys and types
        required_keys = ["api_key", "db_uri", "log_level"]
        for key in required_keys:
            if key not in self._config:
                raise ValueError(f"Missing required config key: {key}")
        # Example: type checks
        if not isinstance(self._config.get("api_key"), str):
            raise TypeError("api_key must be a string")
        if not isinstance(self._config.get("db_uri"), str):
            raise TypeError("db_uri must be a string")
        if self._config.get("log_level") not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            raise ValueError("Invalid log_level")


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> SentioConfig:
    """Get global configuration instance"""
    return config_manager._config
