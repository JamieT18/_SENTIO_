"""
Sentiment-Driven Strategy
Trades based on news/social sentiment.
"""
import pandas as pd
import numpy as np
from .base import BaseStrategy, StrategyType, TradingSignal, SignalType
from datetime import datetime
class SentimentStrategy(BaseStrategy):
    def __init__(self, name="Sentiment", min_confidence=0.7, enabled=True):
        super().__init__(name=name, strategy_type=StrategyType.CUSTOM, min_confidence=min_confidence, enabled=enabled)
    def analyze(self, data: pd.DataFrame, external_data: dict = None) -> dict:
        # Regime adaptation, external data support, diagnostics
        if 'sentiment_score' not in data:
            return {"sentiment_signal": False, "reason": "No sentiment data"}
        score = data['sentiment_score'].iloc[-1]
        regime = external_data.get("macro_trend") if external_data else None
        threshold = 0.5
        if regime == "bull":
            threshold *= 0.9
        elif regime == "bear":
            threshold *= 1.1
        diagnostics = {"regime": regime, "threshold": threshold, "external_data": external_data}
        if score > threshold:
            return {"sentiment_signal": True, "signal": SignalType.BUY.value, "confidence": min(1.0, score), "reason": "Positive sentiment", "diagnostics": diagnostics}
        elif score < -threshold:
            return {"sentiment_signal": True, "signal": SignalType.SELL.value, "confidence": min(1.0, abs(score)), "reason": "Negative sentiment", "diagnostics": diagnostics}
        return {"sentiment_signal": False, "reason": "Neutral sentiment", "diagnostics": diagnostics}
