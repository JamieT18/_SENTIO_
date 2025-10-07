"""
Three Jump Rule (TJR) Trading Strategy
Enhanced implementation with confidence weighting and multiple confirmation signals
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime

from .base import BaseStrategy, StrategyType, TradingSignal, SignalType


class TJRStrategy(BaseStrategy):
    """
    Three Jump Rule (TJR) Strategy

    Identifies three consecutive price movements in the same direction
    with increasing volume, indicating strong momentum continuation.

    Entry signals:
    - Three consecutive higher highs (bullish) or lower lows (bearish)
    - Each jump should have confirmation (volume, momentum)
    - Time-of-day filters applied
    - Confluence with other indicators
    """

    def __init__(
        self,
        name: str = "TJR",
        timeframe: str = "5min",
        min_confidence: float = 0.70,
        volume_threshold: float = 1.2,  # 20% above average
        price_jump_min: float = 0.005,  # Minimum 0.5% price move
        enabled: bool = True,
    ):
        super().__init__(
            name=name,
            strategy_type=StrategyType.TJR,
            timeframe=timeframe,
            min_confidence=min_confidence,
            enabled=enabled,
        )
        self.volume_threshold = volume_threshold
        self.price_jump_min = price_jump_min

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze data for TJR pattern

        Args:
            data: OHLCV DataFrame

        Returns:
            Analysis results with pattern detection
        """
        if len(data) < 10:
            return {"pattern_found": False, "reason": "Insufficient data"}

        # Calculate indicators
        data = data.copy()
        data["price_change"] = data["close"].pct_change()
        data["volume_ma"] = data["volume"].rolling(window=20).mean()
        data["volume_ratio"] = data["volume"] / data["volume_ma"]

        # RSI for momentum confirmation
        data["rsi"] = self._calculate_rsi(data["close"], period=14)

        # Detect three consecutive jumps
        bullish_pattern, bullish_confidence = self._detect_bullish_tjr(data)
        bearish_pattern, bearish_confidence = self._detect_bearish_tjr(data)

        # Time-of-day filter (avoid low liquidity periods)
        time_score = self._get_time_of_day_score()

        # Trend confirmation
        trend_alignment = self._check_trend_alignment(data)

        return {
            "pattern_found": bullish_pattern or bearish_pattern,
            "bullish_pattern": bullish_pattern,
            "bearish_pattern": bearish_pattern,
            "bullish_confidence": bullish_confidence,
            "bearish_confidence": bearish_confidence,
            "current_price": data["close"].iloc[-1],
            "current_volume_ratio": data["volume_ratio"].iloc[-1],
            "rsi": data["rsi"].iloc[-1],
            "time_score": time_score,
            "trend_alignment": trend_alignment,
            "recent_jumps": self._get_recent_jumps(data),
        }

    def get_signal(self, data: pd.DataFrame, analysis: Dict[str, Any]) -> TradingSignal:
        """
        Generate trading signal from TJR analysis

        Args:
            data: OHLCV DataFrame
            analysis: Analysis results

        Returns:
            Trading signal
        """
        if not analysis["pattern_found"]:
            return self._create_hold_signal(data)

        # Determine signal type
        if (
            analysis["bullish_pattern"]
            and analysis["bullish_confidence"] >= self.min_confidence
        ):
            signal_type = SignalType.BUY
            confidence = analysis["bullish_confidence"]
            reasoning = "Bullish TJR pattern detected with strong momentum"
        elif (
            analysis["bearish_pattern"]
            and analysis["bearish_confidence"] >= self.min_confidence
        ):
            signal_type = SignalType.SELL
            confidence = analysis["bearish_confidence"]
            reasoning = "Bearish TJR pattern detected with strong momentum"
        else:
            return self._create_hold_signal(data)

        current_price = analysis["current_price"]

        # Calculate stop-loss and take-profit
        if signal_type == SignalType.BUY:
            stop_loss = current_price * 0.98  # 2% stop-loss
            take_profit = current_price * 1.05  # 5% take-profit
        else:
            stop_loss = current_price * 1.02
            take_profit = current_price * 0.95

        return TradingSignal(
            signal_type=signal_type,
            confidence=confidence,
            strategy_name=self.name,
            symbol=data.attrs.get("symbol", "UNKNOWN"),
            timestamp=datetime.now(),
            price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reasoning=reasoning,
            metadata=analysis,
        )

    def calculate_confidence(
        self, data: pd.DataFrame, analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for TJR signal

        Args:
            data: OHLCV DataFrame
            analysis: Analysis results

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not analysis["pattern_found"]:
            return 0.0

        # Base confidence from pattern strength
        base_confidence = max(
            analysis["bullish_confidence"], analysis["bearish_confidence"]
        )

        # Volume confirmation bonus
        volume_score = (
            min(analysis["current_volume_ratio"] / self.volume_threshold, 1.0) * 0.1
        )

        # Time-of-day bonus
        time_bonus = analysis["time_score"] * 0.1

        # Trend alignment bonus
        trend_bonus = analysis["trend_alignment"] * 0.1

        # RSI confirmation
        rsi = analysis["rsi"]
        rsi_score = 0.0
        if analysis["bullish_pattern"] and 30 < rsi < 70:
            rsi_score = 0.05
        elif analysis["bearish_pattern"] and 30 < rsi < 70:
            rsi_score = 0.05

        total_confidence = min(
            base_confidence + volume_score + time_bonus + trend_bonus + rsi_score, 1.0
        )

        return total_confidence

    def _detect_bullish_tjr(self, data: pd.DataFrame) -> tuple:
        """Detect bullish three jump pattern"""
        if len(data) < 4:
            return False, 0.0

        recent = data.tail(4)

        # Check for three consecutive higher closes
        price_increases = (
            recent["close"].iloc[-1] > recent["close"].iloc[-2]
            and recent["close"].iloc[-2] > recent["close"].iloc[-3]
            and recent["close"].iloc[-3] > recent["close"].iloc[-4]
        )

        if not price_increases:
            return False, 0.0

        # Calculate jump sizes
        jumps = recent["close"].pct_change().tail(3)

        # Check minimum jump size
        if not all(jumps > self.price_jump_min):
            return False, 0.0

        # Check volume confirmation
        volume_increases = (
            recent["volume_ratio"].iloc[-1] >= 1.0
            and recent["volume_ratio"].iloc[-2] >= 1.0
            and recent["volume_ratio"].iloc[-3] >= 1.0
        )

        # Calculate confidence based on jump strength
        jump_strength = float(jumps.mean() / self.price_jump_min)
        volume_strength = float(recent["volume_ratio"].tail(3).mean())

        confidence = min((jump_strength * 0.5 + volume_strength * 0.3) / 0.8, 1.0)

        return volume_increases, confidence

    def _detect_bearish_tjr(self, data: pd.DataFrame) -> tuple:
        """Detect bearish three jump pattern"""
        if len(data) < 4:
            return False, 0.0

        recent = data.tail(4)

        # Check for three consecutive lower closes
        price_decreases = (
            recent["close"].iloc[-1] < recent["close"].iloc[-2]
            and recent["close"].iloc[-2] < recent["close"].iloc[-3]
            and recent["close"].iloc[-3] < recent["close"].iloc[-4]
        )

        if not price_decreases:
            return False, 0.0

        # Calculate jump sizes (negative)
        jumps = recent["close"].pct_change().tail(3)

        # Check minimum jump size (absolute value)
        if not all(abs(jumps) > self.price_jump_min):
            return False, 0.0

        # Check volume confirmation
        volume_increases = (
            recent["volume_ratio"].iloc[-1] >= 1.0
            and recent["volume_ratio"].iloc[-2] >= 1.0
            and recent["volume_ratio"].iloc[-3] >= 1.0
        )

        # Calculate confidence
        jump_strength = float(abs(jumps).mean() / self.price_jump_min)
        volume_strength = float(recent["volume_ratio"].tail(3).mean())

        confidence = min((jump_strength * 0.5 + volume_strength * 0.3) / 0.8, 1.0)

        return volume_increases, confidence

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _get_time_of_day_score(self) -> float:
        """
        Score based on time of day (higher during high liquidity periods)
        Market hours: 9:30 AM - 4:00 PM EST
        Best times: 9:30-11:30 AM and 2:00-4:00 PM
        """
        current_hour = datetime.now().hour

        # High liquidity periods
        if 9 <= current_hour < 12 or 14 <= current_hour < 16:
            return 1.0
        # Moderate liquidity
        elif 12 <= current_hour < 14:
            return 0.7
        # Low liquidity
        else:
            return 0.3

    def _check_trend_alignment(self, data: pd.DataFrame) -> float:
        """Check if pattern aligns with broader trend"""
        if len(data) < 50:
            return 0.5

        # Calculate moving averages
        ma_20 = data["close"].rolling(window=20).mean().iloc[-1]
        ma_50 = data["close"].rolling(window=50).mean().iloc[-1]
        current_price = data["close"].iloc[-1]

        # Score based on price position relative to MAs
        if current_price > ma_20 > ma_50:
            return 1.0  # Strong uptrend
        elif current_price < ma_20 < ma_50:
            return 1.0  # Strong downtrend
        elif current_price > ma_20:
            return 0.7  # Moderate uptrend
        elif current_price < ma_20:
            return 0.7  # Moderate downtrend
        else:
            return 0.5  # No clear trend

    def _get_recent_jumps(self, data: pd.DataFrame) -> list:
        """Get information about recent price jumps"""
        if len(data) < 4:
            return []

        recent = data.tail(4)
        jumps = []

        for i in range(1, 4):
            jump = {
                "index": i,
                "price_change": float(
                    recent["close"].iloc[-i] - recent["close"].iloc[-(i + 1)]
                ),
                "pct_change": float(recent["close"].pct_change().iloc[-i]),
                "volume_ratio": float(recent["volume_ratio"].iloc[-i]),
            }
            jumps.append(jump)

        return jumps
