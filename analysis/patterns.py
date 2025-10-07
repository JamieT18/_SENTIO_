"""
Pattern recognition and candlestick analysis for Sentio
"""
import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger("sentio.analysis.patterns")

def detect_candlestick_patterns(data: pd.DataFrame, regime: str = None, external_context: dict = None) -> List[Dict[str, Any]]:
    """
    Detect candlestick patterns in OHLCV data with regime/context-aware diagnostics
    Returns list of detected patterns with diagnostics
    """
    required_cols = {'open', 'high', 'low', 'close'}
    if data.empty or not required_cols.issubset(data.columns):
        raise ValueError("Data must contain open, high, low, close columns and not be empty")
    patterns = []
    # Example: simple bullish/bearish engulfing detection
    for i in range(1, len(data)):
        prev = data.iloc[i-1]
        curr = data.iloc[i]
        if curr['close'] > curr['open'] and prev['close'] < prev['open'] and curr['open'] < prev['close'] and curr['close'] > prev['open']:
            patterns.append({'type': 'bullish_engulfing', 'index': i, 'regime': regime, 'external_context': external_context})
        elif curr['close'] < curr['open'] and prev['close'] > prev['open'] and curr['open'] > prev['close'] and curr['close'] < prev['open']:
            patterns.append({'type': 'bearish_engulfing', 'index': i, 'regime': regime, 'external_context': external_context})
    # ML-based pattern detection (optional)
    try:
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        X = data[['open', 'high', 'low', 'close']].values
        y = np.random.randint(0, 2, size=len(data))  # Dummy labels for demonstration
        clf = RandomForestClassifier().fit(X, y)
        preds = clf.predict(X)
        for i, p in enumerate(preds):
            if p == 1:
                patterns.append({'index': i, 'pattern': 'ML_Bullish', 'regime': regime, 'external_context': external_context})
            else:
                patterns.append({'index': i, 'pattern': 'ML_Bearish', 'regime': regime, 'external_context': external_context})
        logger.debug(f"ML-detected candlestick patterns: {patterns}")
    except Exception as e:
    logger.error(f"Candlestick pattern ML error: {e}")
    return patterns
def detect_candlestick_patterns(data: pd.DataFrame, regime: str = None, external_context: dict = None) -> List[Dict[str, Any]]:
    """
    Detect candlestick patterns in OHLCV data with regime/context-aware diagnostics
    Returns list of detected patterns with diagnostics
    """
    patterns = []  # Initialize patterns list
    # Example: simple bullish/bearish engulfing detection
    for i in range(1, len(data)):
        prev = data.iloc[i-1]
        curr = data.iloc[i]
        if curr['close'] > curr['open'] and prev['close'] < prev['open'] and curr['open'] < prev['close'] and curr['close'] > prev['open']:
            patterns.append({'type': 'bullish_engulfing', 'index': i, 'regime': regime, 'external_context': external_context})
        elif curr['close'] < curr['open'] and prev['close'] > prev['open'] and curr['open'] > prev['close'] and curr['close'] < prev['open']:
            patterns.append({'type': 'bearish_engulfing', 'index': i, 'regime': regime, 'external_context': external_context})
    return patterns  # Return the detected patterns
        logger.error(f"Candlestick pattern ML error: {e}")
        return []

def detect_chart_patterns(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detect chart patterns (e.g., head and shoulders, triangles).
    Args:
        data: OHLCV DataFrame
    Returns:
        list: Detected patterns
    """
    try:
        from sklearn.cluster import KMeans
        import numpy as np
        X = data[['high', 'low']].values
        kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
        labels = kmeans.labels_
        patterns = []
        for i, label in enumerate(labels):
            patterns.append({'index': i, 'pattern': f'Cluster_{label}'})
        logger.info(f"ML-detected chart patterns: {patterns}")
        return patterns
    except Exception as e:
        logger.error(f"Chart pattern ML error: {e}")
        return []
