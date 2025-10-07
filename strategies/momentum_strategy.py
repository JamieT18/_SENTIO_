"""
Momentum Trading Strategy
Identifies strong trending moves with momentum confirmation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime

from .base import BaseStrategy, StrategyType, TradingSignal, SignalType


class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy

    Trades in the direction of strong momentum confirmed by:
    - Rate of Change (ROC)
    - RSI trending
    - MACD alignment
    - Volume surge
    """

    def __init__(
        self,
        name: str = "Momentum",
        timeframe: str = "15min",
        min_confidence: float = 0.65,
        roc_period: int = 12,
        momentum_threshold: float = 0.02,  # 2% ROC threshold
        enabled: bool = True,
    ):
        super().__init__(
            name=name,
            strategy_type=StrategyType.MOMENTUM,
            timeframe=timeframe,
            min_confidence=min_confidence,
            enabled=enabled,
        )
        self.roc_period = roc_period
        self.momentum_threshold = momentum_threshold

    def analyze(self, data: pd.DataFrame, external_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze momentum indicators with regime adaptation and external data support"""
        if len(data) < 50:
            return {"has_momentum": False, "reason": "Insufficient data"}

        data = data.copy()

        # Rate of Change
        data["roc"] = self._calculate_roc(data["close"], self.roc_period)

        # RSI
        data["rsi"] = self._calculate_rsi(data["close"], 14)

        # MACD
        macd, signal, histogram = self._calculate_macd(data["close"])
        data["macd"] = macd
        data["macd_signal"] = signal
        data["macd_histogram"] = histogram

        # Volume momentum
        data["volume_ma"] = data["volume"].rolling(20).mean()
        data["volume_ratio"] = data["volume"] / data["volume_ma"]

        # Regime adaptation: adjust momentum threshold
        regime = external_data.get("macro_trend") if external_data else None
        momentum_threshold = self.momentum_threshold
        if regime == "bull":
            momentum_threshold *= 0.9
        elif regime == "bear":
            momentum_threshold *= 1.1

        # Detect momentum signals
        current = data.iloc[-1]
        bullish_momentum = self._detect_bullish_momentum(data)
        bearish_momentum = self._detect_bearish_momentum(data)

        diagnostics = {
            "regime": regime,
            "momentum_threshold": momentum_threshold,
            "external_data": external_data,
        }

        return {
            "has_momentum": bullish_momentum or bearish_momentum,
            "bullish_momentum": bullish_momentum,
            "bearish_momentum": bearish_momentum,
            "roc": float(current["roc"]),
            "rsi": float(current["rsi"]),
            "macd": float(current["macd"]),
            "macd_signal": float(current["macd_signal"]),
            "macd_histogram": float(current["macd_histogram"]),
            "volume_ratio": float(current["volume_ratio"]),
            "current_price": float(current["close"]),
            "diagnostics": diagnostics,
        }

    def get_signal(self, data: pd.DataFrame, analysis: Dict[str, Any]) -> TradingSignal:
        """Generate momentum-based signal"""
        if not analysis["has_momentum"]:
            return self._create_hold_signal(data)

        confidence = self.calculate_confidence(data, analysis)

        if analysis["bullish_momentum"] and confidence >= self.min_confidence:
            signal_type = SignalType.BUY
            reasoning = "Strong bullish momentum detected"
        elif analysis["bearish_momentum"] and confidence >= self.min_confidence:
            signal_type = SignalType.SELL
            reasoning = "Strong bearish momentum detected"
        else:
            return self._create_hold_signal(data)

        current_price = analysis["current_price"]

        return TradingSignal(
            signal_type=signal_type,
            confidence=confidence,
            strategy_name=self.name,
            symbol=data.attrs.get("symbol", "UNKNOWN"),
            timestamp=datetime.now(),
            price=current_price,
            stop_loss=current_price * (0.97 if signal_type == SignalType.BUY else 1.03),
            take_profit=current_price
            * (1.06 if signal_type == SignalType.BUY else 0.94),
            reasoning=reasoning,
            metadata=analysis,
        )

    def calculate_confidence(
        self, data: pd.DataFrame, analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on momentum strength"""
        if not analysis["has_momentum"]:
            return 0.0

        confidence = 0.5  # Base confidence

        # ROC strength
        roc_strength = abs(analysis["roc"]) / self.momentum_threshold
        confidence += min(roc_strength * 0.15, 0.15)

        # RSI confirmation
        rsi = analysis["rsi"]
        if analysis["bullish_momentum"] and 40 < rsi < 70:
            confidence += 0.1
        elif analysis["bearish_momentum"] and 30 < rsi < 60:
            confidence += 0.1

        # MACD confirmation
        if analysis["macd_histogram"] > 0 and analysis["bullish_momentum"]:
            confidence += 0.1
        elif analysis["macd_histogram"] < 0 and analysis["bearish_momentum"]:
            confidence += 0.1

        # Volume confirmation
        if analysis["volume_ratio"] > 1.2:
            confidence += 0.1

        return min(confidence, 1.0)

    def _detect_bullish_momentum(self, data: pd.DataFrame) -> bool:
        """Detect bullish momentum"""
        current = data.iloc[-1]

        # ROC positive and above threshold
        roc_bullish = current["roc"] > self.momentum_threshold

        # RSI in bullish zone
        rsi_bullish = 50 < current["rsi"] < 80

        # MACD bullish crossover or above signal
        macd_bullish = current["macd"] > current["macd_signal"]

        # At least 2 out of 3 conditions
        return sum([roc_bullish, rsi_bullish, macd_bullish]) >= 2

    def _detect_bearish_momentum(self, data: pd.DataFrame) -> bool:
        """Detect bearish momentum"""
        current = data.iloc[-1]

        # ROC negative and below threshold
        roc_bearish = current["roc"] < -self.momentum_threshold

        # RSI in bearish zone
        rsi_bearish = 20 < current["rsi"] < 50

        # MACD bearish crossover or below signal
        macd_bearish = current["macd"] < current["macd_signal"]

        # At least 2 out of 3 conditions
        return sum([roc_bearish, rsi_bearish, macd_bearish]) >= 2

    def _calculate_roc(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Rate of Change"""
        return prices.pct_change(periods=period)

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(
        self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> tuple:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
