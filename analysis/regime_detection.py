"""
Automated Regime Detection for Sentio
Detects market regime (bull, bear, neutral) using technical and sentiment indicators.
Propagates regime context to analytics, strategies, and plugins.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any

class RegimeDetector:
    def __init__(self, lookback: int = 20):
        self.lookback = lookback

    def detect_regime(self, market_data: pd.DataFrame, sentiment_score: float = None) -> str:
        """
        Detects market regime using price trends and sentiment.
        Args:
            market_data: OHLCV DataFrame
            sentiment_score: Optional sentiment score (-1 to 1)
        Returns:
            regime: 'bull', 'bear', or 'neutral'
        """
        Automated Regime Detection for Sentio
        """
        avg_return = returns.mean()
        std_return = returns.std()
        # Simple regime logic
        if avg_return > 0.01 and (sentiment_score is None or sentiment_score > 0.2):
            return 'bull'
        elif avg_return < -0.01 and (sentiment_score is None or sentiment_score < -0.2):
            return 'bear'
        else:
            return 'neutral'

    def regime_context(self, market_data: pd.DataFrame, sentiment_score: float = None) -> Dict[str, Any]:
        regime = self.detect_regime(market_data, sentiment_score)
        return {
            'regime': regime,
            'avg_return': market_data['close'].pct_change().tail(self.lookback).mean(),
            'sentiment_score': sentiment_score
        }

# Example usage:
# detector = RegimeDetector()
# context = detector.regime_context(market_data, sentiment_score)
# Pass context['regime'] to analytics, strategies, plugins
