"""
Arbitrage Trading Strategy
Detects price discrepancies across markets/instruments for risk-free profit.
"""
import pandas as pd
from .base import BaseStrategy, StrategyType, TradingSignal, SignalType
from datetime import datetime
class ArbitrageStrategy(BaseStrategy):
    def __init__(self, name="Arbitrage", min_confidence=0.7, enabled=True, venues=None):
        super().__init__(name=name, strategy_type=StrategyType.CUSTOM, min_confidence=min_confidence, enabled=enabled)
        self.venues = venues or ["ExchangeA", "ExchangeB"]
        self.latency_threshold = 0.5  # seconds
        self.risk_limit = 0.02  # 2% of capital

    def analyze(self, data: pd.DataFrame) -> dict:
        # Multi-venue support: check all pairs for arbitrage
        if len(data) < 10:
            return {"arbitrage_opportunity": False, "reason": "Insufficient data"}
        results = []
        for venue1 in self.venues:
            for venue2 in self.venues:
                if venue1 == venue2:
                    continue
                price1 = data.get(f"price_{venue1}", None)
                price2 = data.get(f"price_{venue2}", None)
                if price1 is None or price2 is None:
                    continue
                price_diff = price1 - price2
                mean_diff = price_diff.mean()
                std_diff = price_diff.std()
                last_diff = price_diff.iloc[-1]
                threshold = std_diff * 2
                latency = data.get(f"latency_{venue1}_{venue2}", pd.Series([0.3]*len(data))).iloc[-1]
                if abs(last_diff - mean_diff) > threshold and latency < self.latency_threshold:
                    signal_type = SignalType.BUY if last_diff < mean_diff else SignalType.SELL
                    confidence = min(1.0, abs(last_diff - mean_diff) / threshold)
                    risk = min(self.risk_limit, abs(last_diff - mean_diff) / mean_diff)
                    results.append({
                        "venue_pair": (venue1, venue2),
                        "arbitrage_opportunity": True,
                        "signal": signal_type.value,
                        "confidence": confidence,
                        "risk": risk,
                        "latency": latency,
                        "reason": f"Price diff {last_diff:.2f} deviates from mean {mean_diff:.2f} | Latency: {latency:.2f}s"
                    })
        if results:
            # Return best opportunity
            best = max(results, key=lambda x: x["confidence"])
            return best
        return {"arbitrage_opportunity": False, "reason": "No significant price discrepancy or latency too high"}
