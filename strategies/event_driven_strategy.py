"""
Event-Driven Strategy
Trades around earnings, splits, or major news events.
"""
import pandas as pd
from .base import BaseStrategy, StrategyType, TradingSignal, SignalType
from datetime import datetime
class EventDrivenStrategy(BaseStrategy):
    def __init__(self, name="EventDriven", min_confidence=0.7, enabled=True, external_news=None):
        super().__init__(name=name, strategy_type=StrategyType.CUSTOM, min_confidence=min_confidence, enabled=enabled)
        self.external_news = external_news or []

    def analyze(self, data: pd.DataFrame, external_data: dict = None) -> dict:
        # Multi-event support: scan for all recent impactful events
        if 'event_type' not in data or 'event_impact' not in data:
            return {"event_signal": False, "reason": "No event data"}
        events = []
        for idx in range(len(data)):
            impact = data['event_impact'].iloc[idx]
            event_type = data['event_type'].iloc[idx]
            if abs(impact) > 0.5:
                signal_type = SignalType.BUY if impact > 0 else SignalType.SELL
                confidence = min(1.0, abs(impact))
                events.append({
                    "event_signal": True,
                    "signal": signal_type.value,
                    "confidence": confidence,
                    "reason": f"{'Positive' if impact > 0 else 'Negative'} event: {event_type}",
                    "event_type": event_type,
                    "impact": impact
                })
        # Integrate external news sentiment
        news_sentiment = 0.0
        if external_data and "news_sentiment" in external_data:
            news_sentiment = external_data["news_sentiment"]
        if events:
            # Boost confidence if news sentiment aligns
            for e in events:
                if (e["signal"] == SignalType.BUY.value and news_sentiment > 0.2) or (e["signal"] == SignalType.SELL.value and news_sentiment < -0.2):
                    e["confidence"] = min(1.0, e["confidence"] + abs(news_sentiment) * 0.2)
            best = max(events, key=lambda x: x["confidence"])
            best["diagnostics"] = {"news_sentiment": news_sentiment, "external_news": self.external_news}
            return best
        return {"event_signal": False, "reason": "No impactful event or neutral news", "diagnostics": {"news_sentiment": news_sentiment, "external_news": self.external_news}}
