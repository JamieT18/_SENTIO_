"""
Breakout Trading Strategy
Identifies and trades price breakouts above resistance or below support
"""

import pandas as pd
from typing import Dict, Any
from datetime import datetime

from .base import BaseStrategy, StrategyType, TradingSignal, SignalType


class BreakoutStrategy(BaseStrategy):
    """
    Breakout Strategy

    Identifies price breakouts from consolidation ranges or key levels.
    Confirms with:
    - Volume surge
    - Momentum indicators
    - Range duration
    - Volatility expansion
    """

    def __init__(
        self,
        name: str = "Breakout",
        timeframe: str = "15min",
        min_confidence: float = 0.65,
        lookback_period: int = 20,
        volume_multiplier: float = 1.5,
        breakout_threshold: float = 0.01,  # 1% beyond high/low
        enabled: bool = True,
    ):
        super().__init__(
            name=name,
            strategy_type=StrategyType.BREAKOUT,
            timeframe=timeframe,
            min_confidence=min_confidence,
            enabled=enabled,
        )
        self.lookback_period = lookback_period
        self.volume_multiplier = volume_multiplier
        self.breakout_threshold = breakout_threshold

    def analyze(self, data: pd.DataFrame, external_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze for breakout patterns with regime adaptation and external data support"""
        if len(data) < self.lookback_period + 10:
            return {"breakout_detected": False, "reason": "Insufficient data"}

        data = data.copy()

        # Find consolidation range
        lookback_data = data.tail(self.lookback_period)
        range_high = lookback_data["high"].max()
        range_low = lookback_data["low"].min()
        range_size = range_high - range_low

        # Current price and volume
        current_price = data["close"].iloc[-1]
        current_volume = data["volume"].iloc[-1]
        avg_volume = data["volume"].rolling(window=20).mean().iloc[-1]

        # Calculate volatility (ATR)
        atr = self._calculate_atr(data, period=14)
        current_atr = atr.iloc[-1]
        avg_atr = atr.rolling(window=20).mean().iloc[-1]

        # Regime adaptation: boost breakout threshold in high volatility
        regime = external_data.get("macro_trend") if external_data else None
        breakout_threshold = self.breakout_threshold
        if regime == "bull":
            breakout_threshold *= 0.9
        elif regime == "bear":
            breakout_threshold *= 1.1

        # Detect bullish breakout
        bullish_breakout = (
            current_price > range_high * (1 + breakout_threshold)
            and current_volume > avg_volume * self.volume_multiplier
        )

        # Detect bearish breakout
        bearish_breakout = (
            current_price < range_low * (1 - breakout_threshold)
            and current_volume > avg_volume * self.volume_multiplier
        )

        # Check if consolidation was tight (higher quality breakout)
        consolidation_tightness = range_size / ((range_high + range_low) / 2)
        is_tight_range = consolidation_tightness < 0.05  # 5% range

        # Volatility expansion (confirms genuine breakout)
        volatility_expansion = current_atr > avg_atr * 1.2

        # Real-time diagnostics
        diagnostics = {
            "regime": regime,
            "breakout_threshold": breakout_threshold,
            "volatility": current_atr,
            "external_data": external_data,
        }

        return {
            "breakout_detected": bullish_breakout or bearish_breakout,
            "bullish_breakout": bullish_breakout,
            "bearish_breakout": bearish_breakout,
            "current_price": float(current_price),
            "range_high": float(range_high),
            "range_low": float(range_low),
            "range_size": float(range_size),
            "consolidation_tightness": float(consolidation_tightness),
            "is_tight_range": is_tight_range,
            "volume_ratio": float(current_volume / avg_volume),
            "volatility_expansion": volatility_expansion,
            "atr": float(current_atr),
            "diagnostics": diagnostics,
        }

    def get_signal(self, data: pd.DataFrame, analysis: Dict[str, Any]) -> TradingSignal:
        """Generate breakout signal"""
        if not analysis["breakout_detected"]:
            return self._create_hold_signal(data)

        confidence = self.calculate_confidence(data, analysis)

        if analysis["bullish_breakout"] and confidence >= self.min_confidence:
            signal_type = SignalType.BUY
            reasoning = (
                f"Bullish breakout above {analysis['range_high']:.2f} with volume surge"
            )
        elif analysis["bearish_breakout"] and confidence >= self.min_confidence:
            signal_type = SignalType.SELL
            reasoning = (
                f"Bearish breakout below {analysis['range_low']:.2f} with volume surge"
            )
        else:
            return self._create_hold_signal(data)

        current_price = analysis["current_price"]

        # Set stops and targets based on range size
        range_size = analysis["range_size"]

        if signal_type == SignalType.BUY:
            # Stop below the breakout level
            stop_loss = analysis["range_high"] * 0.99
            # Target is range size projected upward
            take_profit = current_price + range_size
        else:
            # Stop above the breakout level
            stop_loss = analysis["range_low"] * 1.01
            # Target is range size projected downward
            take_profit = current_price - range_size

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
        """Calculate confidence based on breakout quality"""
        if not analysis["breakout_detected"]:
            return 0.0

        confidence = 0.5

        # Volume confirmation (up to 0.2)
        volume_score = min((analysis["volume_ratio"] - 1) / 2, 0.2)
        confidence += volume_score

        # Tight range bonus (0.15)
        if analysis["is_tight_range"]:
            confidence += 0.15

        # Volatility expansion bonus (0.1)
        if analysis["volatility_expansion"]:
            confidence += 0.1

        # Breakout strength (distance from range, up to 0.1)
        if analysis["bullish_breakout"]:
            breakout_strength = (
                analysis["current_price"] - analysis["range_high"]
            ) / analysis["range_high"]
        else:
            breakout_strength = (
                analysis["range_low"] - analysis["current_price"]
            ) / analysis["range_low"]

        strength_score = min(breakout_strength * 10, 0.1)
        confidence += strength_score

        return min(confidence, 1.0)

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = data["high"]
        low = data["low"]
        close = data["close"]

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr
