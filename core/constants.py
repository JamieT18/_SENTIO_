from typing import List

"""
Core constants for Sentio 2.0
Centralized configuration values and thresholds
# Core constants for Sentio

# Strength Signal Thresholds
STRENGTH_STRONG_BULLISH: int = 70
STRENGTH_BULLISH: int = 50
STRENGTH_NEUTRAL: int = 30
STRENGTH_BEARISH: int = 10

# RSI Thresholds
RSI_OVERBOUGHT: int = 70
RSI_STRONG: int = 50
RSI_OVERSOLD: int = 30

# Strength Component Scores
MOMENTUM_HIGH_SCORE: int = 80
MOMENTUM_STRONG_SCORE: int = 60
MOMENTUM_MODERATE_SCORE: int = 40
MOMENTUM_LOW_SCORE: int = 20

# API Configuration
DEFAULT_SYMBOLS: List[str] = ["AAPL", "GOOGL", "MSFT", "TSLA"]
DEFAULT_TIMEFRAME: str = "5min"
DEFAULT_TRADE_JOURNAL_LIMIT: int = 50

# Performance Trends
TREND_UP: str = "up"
TREND_DOWN: str = "down"

# Signal Types
SIGNAL_TYPES: List[str] = [
    "strong_bullish",
    "bullish",
    "neutral",
    "bearish",
    "strong_bearish",
    "error"
]

# Status Values
STATUS_VALUES: List[str] = [
    "success",
    "warning",
    "error",
    "operational",
    "healthy",
    "active",
    "idle"
]

# Dashboard States
PORTFOLIO_STATUS_ACTIVE: str = "active"
PORTFOLIO_STATUS_IDLE: str = "idle"
MARKET_OVERVIEW_GENERAL: str = "general"
