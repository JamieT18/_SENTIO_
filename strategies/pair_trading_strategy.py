"""
Pair Trading / Statistical Arbitrage Strategy
Trades correlated pairs for mean reversion opportunities.
"""
import pandas as pd
from .base import BaseStrategy, StrategyType, TradingSignal, SignalType
from datetime import datetime
class PairTradingStrategy(BaseStrategy):
    def __init__(self, name="PairTrading", min_confidence=0.7, lookback=20, enabled=True):
        super().__init__(name=name, strategy_type=StrategyType.CUSTOM, min_confidence=min_confidence, enabled=enabled)
        self.lookback = lookback
    def analyze(self, data: pd.DataFrame, external_data: dict = None) -> dict:
        # Regime adaptation, external data support, diagnostics
        if len(data) < self.lookback:
            return {"pair_signal": False, "reason": "Insufficient data"}
        spread = data['price1'] - data['price2']
        mean = spread.rolling(self.lookback).mean().iloc[-1]
        std = spread.rolling(self.lookback).std().iloc[-1]
        last_spread = spread.iloc[-1]
        z_score = (last_spread - mean) / std if std > 0 else 0
        # Regime adaptation: adjust z-score threshold
        regime = external_data.get("macro_trend") if external_data else None
        z_threshold = 2.0
        if regime == "bull":
            z_threshold *= 0.9
        elif regime == "bear":
            z_threshold *= 1.1
        if abs(z_score) > z_threshold:
            signal_type = SignalType.BUY if z_score < 0 else SignalType.SELL
            confidence = min(1.0, abs(z_score) / 3)
            diagnostics = {"regime": regime, "z_threshold": z_threshold, "external_data": external_data}
            return {"pair_signal": True, "signal": signal_type.value, "confidence": confidence, "reason": f"Spread z-score {z_score:.2f}", "diagnostics": diagnostics}
        return {"pair_signal": False, "reason": "No significant spread deviation", "diagnostics": {"regime": regime, "z_threshold": z_threshold, "external_data": external_data}}
