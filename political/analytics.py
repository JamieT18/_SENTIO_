def network_analysis(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze network of political actors and event connections.
    """
    from collections import defaultdict
    import numpy as np
    actor_graph = defaultdict(set)
    for event in events:
        actors = event.get('actors', [])
        for a in actors:
            for b in actors:
                if a != b:
                    actor_graph[a].add(b)
    degrees = {a: len(b) for a, b in actor_graph.items()}
    central_actor = max(degrees, key=degrees.get) if degrees else None
    return {'actor_graph': {k: list(v) for k, v in actor_graph.items()}, 'central_actor': central_actor, 'degrees': degrees}

def forecast_events(events: List[Dict[str, Any]], horizon: int = 7) -> Dict[str, Any]:
    """
    Forecast future event impact using simple time series extrapolation.
    """
    import numpy as np
    impacts = np.array([e.get('impact', 0.0) for e in events])
    if len(impacts) < 2:
        return {'forecast': [float(i) for i in impacts]}
    trend = (impacts[-1] - impacts[0]) / max(len(impacts)-1, 1)
    forecast = [float(impacts[-1] + trend * i) for i in range(1, horizon+1)]
    return {'forecast': forecast, 'trend': trend}

def propagate_sentiment(events: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Propagate sentiment through event network.
    """
    from collections import defaultdict
    sentiment_map = defaultdict(float)
    for event in events:
        actors = event.get('actors', [])
        sentiment = event.get('sentiment', 0.0)
        for a in actors:
            sentiment_map[a] += sentiment
    return dict(sentiment_map)

def insider_anomaly_score(trades: List[Dict[str, Any]]) -> float:
    """
    Score overall anomaly level in insider trades.
    """
    import numpy as np
    amounts = np.array([t.get('amount', 0.0) for t in trades])
    if len(amounts) == 0:
        return 0.0
    score = float(np.sum(amounts > (np.mean(amounts) + 2 * np.std(amounts))) / len(amounts))
    return score
"""
Political and insider trading analytics for Sentio 2.0
"""
from typing import List, Dict, Any


import numpy as np
from collections import Counter

def analyze_political_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Advanced analysis: impact scoring, sentiment, regime detection, risk quantification.
    """
    if not events:
        raise ValueError("events must not be empty")
    type_counts = Counter(event.get('type', 'unknown') for event in events)
    impact_scores = [event.get('impact', 0.0) for event in events]
    avg_impact = float(np.mean(impact_scores)) if impact_scores else 0.0
    sentiment_scores = [event.get('sentiment', 0.0) for event in events]
    avg_sentiment = float(np.mean(sentiment_scores)) if sentiment_scores else 0.0
    # Regime detection: classify periods as stable/volatile
    volatility = np.std(impact_scores) if impact_scores else 0.0
    regime = 'volatile' if volatility > 0.5 else 'stable'
    # Risk quantification: sum of negative impacts
    risk_score = float(np.sum([s for s in impact_scores if s < 0]))
    return {
        'type_counts': dict(type_counts),
        'avg_impact': avg_impact,
        'avg_sentiment': avg_sentiment,
        'regime': regime,
        'risk_score': risk_score,
        'event_count': len(events)
    }


def analyze_insider_trades(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Advanced analysis: trade clustering, sentiment, alpha signals, risk flags.
    """
    if not trades:
        raise ValueError("trades must not be empty")
    symbol_counts = Counter(trade.get('symbol', 'unknown') for trade in trades)
    buy_count = sum(1 for t in trades if t.get('type', '').lower() == 'buy')
    sell_count = sum(1 for t in trades if t.get('type', '').lower() == 'sell')
    net_activity = buy_count - sell_count
    sentiment = 'bullish' if net_activity > 5 else 'bearish' if net_activity < -5 else 'neutral'
    # Alpha signal: high buy/sell ratio
    alpha_signal = buy_count / (sell_count + 1e-8)
    # Risk flag: large trades or clusters
    large_trades = [t for t in trades if t.get('amount', 0) > 1e6]
    cluster_flag = len(large_trades) > 3
    return {
        'symbol_counts': dict(symbol_counts),
        'buy_count': buy_count,
        'sell_count': sell_count,
        'sentiment': sentiment,
        'alpha_signal': alpha_signal,
        'risk_flag': cluster_flag,
        'large_trades': large_trades,
        'trade_count': len(trades)
    }
