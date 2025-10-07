"""
Volatility/Options Strategy
Uses implied/realized volatility for signal generation.
"""
import pandas as pd
import numpy as np
from .base import BaseStrategy, StrategyType, TradingSignal, SignalType
from datetime import datetime
class VolatilityStrategy(BaseStrategy):
    def __init__(self, name="Volatility", min_confidence=0.7, lookback=20, enabled=True):
        super().__init__(name=name, strategy_type=StrategyType.CUSTOM, min_confidence=min_confidence, enabled=enabled)
        self.lookback = lookback
    def analyze(self, data: pd.DataFrame, external_data: dict = None) -> dict:
        # Regime adaptation, external data support, diagnostics
        if len(data) < self.lookback:
            return {"vol_signal": False, "reason": "Insufficient data"}
        realized_vol = data['close'].pct_change().rolling(self.lookback).std().iloc[-1]
        implied_vol = data['implied_vol'].iloc[-1] if 'implied_vol' in data else realized_vol
        regime = external_data.get("macro_trend") if external_data else None
        buy_mult = 1.2
        sell_mult = 0.8
        if regime == "bull":
            buy_mult *= 0.95
            sell_mult *= 1.05
        elif regime == "bear":
            buy_mult *= 1.05
            sell_mult *= 0.95
        diagnostics = {"regime": regime, "buy_mult": buy_mult, "sell_mult": sell_mult, "external_data": external_data}
        if implied_vol > realized_vol * buy_mult:
            return {"vol_signal": True, "signal": SignalType.BUY.value, "confidence": 0.8, "reason": "Implied vol > realized vol", "diagnostics": diagnostics}
        elif implied_vol < realized_vol * sell_mult:
            return {"vol_signal": True, "signal": SignalType.SELL.value, "confidence": 0.8, "reason": "Implied vol < realized vol", "diagnostics": diagnostics}
        return {"vol_signal": False, "reason": "No significant vol difference", "diagnostics": diagnostics}
