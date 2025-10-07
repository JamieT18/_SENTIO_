"""
Macro/Regime Detection Strategy
Adapts signals based on macroeconomic regime.
"""
import pandas as pd
import numpy as np
from .base import BaseStrategy, StrategyType, TradingSignal, SignalType
from datetime import datetime
class MacroRegimeStrategy(BaseStrategy):
    def __init__(self, name="MacroRegime", min_confidence=0.7, enabled=True):
        super().__init__(name=name, strategy_type=StrategyType.CUSTOM, min_confidence=min_confidence, enabled=enabled)
    def analyze(self, data: pd.DataFrame, external_data: dict = None) -> dict:
        # Multi-factor scoring, adaptive confidence, external data integration
        required = ['gdp_growth', 'inflation', 'interest_rate']
        if not all(col in data for col in required):
            return {"macro_signal": False, "reason": "Missing macro data"}
        gdp = data['gdp_growth'].iloc[-1]
        inflation = data['inflation'].iloc[-1]
        rate = data['interest_rate'].iloc[-1]
        # Multi-factor scoring
        score = 0.0
        if gdp > 2.5:
            score += 0.4
        if inflation < 3:
            score += 0.3
        if rate < 2:
            score += 0.3
        if gdp < 1.5:
            score -= 0.3
        if inflation > 4:
            score -= 0.3
        if rate > 3:
            score -= 0.2
        # External data integration (e.g., global risk sentiment)
        ext_score = 0.0
        if external_data and "risk_sentiment" in external_data:
            ext_score = external_data["risk_sentiment"] * 0.2
            score += ext_score
        # Adaptive confidence
        confidence = min(1.0, abs(score))
        if score > 0.5:
            return {"macro_signal": True, "signal": SignalType.BUY.value, "confidence": confidence, "reason": "Growth regime", "diagnostics": {"score": score, "external": external_data}}
        elif score < -0.5:
            return {"macro_signal": True, "signal": SignalType.SELL.value, "confidence": confidence, "reason": "Stagflation regime", "diagnostics": {"score": score, "external": external_data}}
        return {"macro_signal": False, "reason": "Neutral regime", "diagnostics": {"score": score, "external": external_data}}
