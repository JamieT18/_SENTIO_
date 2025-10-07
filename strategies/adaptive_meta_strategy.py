"""
Adaptive Meta-Strategy
Dynamically weights strategies based on recent performance and market regime.
"""
import pandas as pd
from .base import BaseStrategy, StrategyType, TradingSignal, SignalType
from datetime import datetime
class AdaptiveMetaStrategy(BaseStrategy):
    def __init__(self, name="AdaptiveMeta", min_confidence=0.7, enabled=True):
        super().__init__(name=name, strategy_type=StrategyType.CUSTOM, min_confidence=min_confidence, enabled=enabled)
        self.performance_history = {}
    def analyze(self, data: pd.DataFrame, strategies: list = None, external_context: dict = None) -> dict:
        # Multi-objective optimization, regime adaptation, external context
        if not strategies:
            return {"meta_signal": False, "reason": "No strategies provided"}
        results = []
        for strat in strategies:
            signals = strat.analyze(data)
            win_rate = signals.get('confidence', 0.5)
            # Multi-objective: Sharpe, drawdown, ROI
            sharpe = signals.get('sharpe_ratio', 0.0)
            drawdown = signals.get('max_drawdown', 0.0)
            roi = signals.get('roi', 0.0)
            score = win_rate + sharpe * 0.2 - abs(drawdown) * 0.1 + roi * 0.2
            # Regime adaptation
            if external_context:
                regime = external_context.get('macro_trend')
                if regime == 'bull' and 'trend' in strat.name.lower():
                    score += 0.1
                elif regime == 'bear' and 'mean' in strat.name.lower():
                    score += 0.1
            results.append((strat, score))
        best = max(results, key=lambda x: x[1])
        self.performance_history[type(best[0]).__name__] = best[1]
        diagnostics = {"external_context": external_context, "scores": {type(s[0]).__name__: s[1] for s in results}}
        return {"meta_signal": True, "signal": best[0].__class__.__name__, "confidence": best[1], "reason": f"Selected {best[0].__class__.__name__} with score {best[1]:.2f}", "diagnostics": diagnostics}
