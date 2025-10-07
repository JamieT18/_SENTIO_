"""
Mean Reversion Trading Strategy
Identifies overbought/oversold conditions and trades the reversion to mean
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime

from .base import BaseStrategy, StrategyType, TradingSignal, SignalType


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy

    Trades based on the principle that prices tend to revert to their mean.
    Uses:
    - Bollinger Bands for deviation measurement
    - RSI for overbought/oversold conditions
    - Z-score for statistical significance
    """

    def __init__(
        self,
        name: str = "MeanReversion",
        timeframe: str = "15min",
        min_confidence: float = 0.65,
        bb_period: int = 20,
        bb_std: float = 2.0,
        rsi_period: int = 14,
        z_threshold: float = 2.0,
        enabled: bool = True,
    ):
        super().__init__(
            name=name,
            strategy_type=StrategyType.MEAN_REVERSION,
            timeframe=timeframe,
            min_confidence=min_confidence,
            enabled=enabled,
        )
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.z_threshold = z_threshold

    def analyze(self, data: pd.DataFrame, external_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze for mean reversion opportunities with regime adaptation and external data support"""
        if len(data) < 50:
            return {"reversion_signal": False, "reason": "Insufficient data"}

        data = data.copy()

        # Bollinger Bands
        ma = data["close"].rolling(window=self.bb_period).mean()
        std = data["close"].rolling(window=self.bb_period).std()
        upper_band = ma + (std * self.bb_std)
        lower_band = ma - (std * self.bb_std)

        # Z-score
        z_score = (data["close"] - ma) / std

        # RSI
        rsi = self._calculate_rsi(data["close"], self.rsi_period)

        # Regime adaptation: adjust z_threshold based on macro regime
        regime = external_data.get("macro_trend") if external_data else None
        z_threshold = self.z_threshold
        if regime == "bull":
            z_threshold *= 0.9
        elif regime == "bear":
            z_threshold *= 1.1

        # Current values
        current_price = data["close"].iloc[-1]
        current_ma = ma.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_z = z_score.iloc[-1]
        current_rsi = rsi.iloc[-1]

        # Detect oversold (buy signal)
        oversold = (
            current_price < current_lower
            and current_rsi < 30
            and current_z < -z_threshold
        )

        # Detect overbought (sell signal)
        overbought = (
            current_price > current_upper
            and current_rsi > 70
            and current_z > z_threshold
        )

        # Calculate distance from mean
        distance_from_mean = abs(current_price - current_ma) / current_ma

        diagnostics = {
            "regime": regime,
            "z_threshold": z_threshold,
            "external_data": external_data,
        }

        return {
            "reversion_signal": oversold or overbought,
            "oversold": oversold,
            "overbought": overbought,
            "current_price": float(current_price),
            "mean": float(current_ma),
            "upper_band": float(current_upper),
            "lower_band": float(current_lower),
            "z_score": float(current_z),
            "rsi": float(current_rsi),
            "distance_from_mean": float(distance_from_mean),
            "diagnostics": diagnostics,
        }

    def get_signal(self, data: pd.DataFrame, analysis: Dict[str, Any]) -> TradingSignal:
        """Generate mean reversion signal"""
        if not analysis["reversion_signal"]:
            return self._create_hold_signal(data)

        confidence = self.calculate_confidence(data, analysis)

        if analysis["oversold"] and confidence >= self.min_confidence:
            signal_type = SignalType.BUY
            reasoning = f"Oversold condition detected (RSI: {analysis['rsi']:.1f}, Z-score: {analysis['z_score']:.2f})"
        elif analysis["overbought"] and confidence >= self.min_confidence:
            signal_type = SignalType.SELL
            reasoning = f"Overbought condition detected (RSI: {analysis['rsi']:.1f}, Z-score: {analysis['z_score']:.2f})"
        else:
            return self._create_hold_signal(data)

        current_price = analysis["current_price"]
        mean = analysis["mean"]

        # Target is the mean, stop is extended band
        if signal_type == SignalType.BUY:
            stop_loss = analysis["lower_band"] * 0.99
            take_profit = mean
        else:
            stop_loss = analysis["upper_band"] * 1.01
            take_profit = mean

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
        """Calculate confidence based on deviation strength"""
        if not analysis["reversion_signal"]:
            return 0.0

        # Base confidence
        confidence = 0.5

        # Z-score strength (higher deviation = higher confidence)
        z_strength = min(abs(analysis["z_score"]) / (self.z_threshold * 2), 0.2)
        confidence += z_strength

        # RSI extremity
        if analysis["oversold"]:
            rsi_strength = (30 - analysis["rsi"]) / 30 * 0.15
        else:  # overbought
            rsi_strength = (analysis["rsi"] - 70) / 30 * 0.15
        confidence += rsi_strength

        # Distance from mean bonus
        distance_bonus = min(analysis["distance_from_mean"] * 5, 0.15)
        confidence += distance_bonus

        return min(confidence, 1.0)

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
