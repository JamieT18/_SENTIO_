"""
Real-time and alternative data feeds for Sentio 2.0
"""
import requests
import numpy as np
from typing import List, Dict, Any

class DataFeed:
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}

    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        # Example: Finnhub API (can be extended)
        key = self.api_keys.get('finnhub', '')
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={key}"
        resp = requests.get(url)
        return resp.json() if resp.status_code == 200 else {}

    def get_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        # Placeholder for social sentiment API
        return {'symbol': symbol, 'sentiment_score': np.random.uniform(-1, 1)}

    def get_macro_indicators(self) -> Dict[str, Any]:
        # Placeholder for macro indicators
        return {'gdp_growth': 2.5, 'inflation': 3.1, 'interest_rate': 1.75}

    def get_news_events(self, symbol: str) -> List[Dict[str, Any]]:
        # Placeholder for news API
        return [{'symbol': symbol, 'headline': 'Market moves', 'impact': np.random.choice(['positive', 'negative', 'neutral'])}]

class EventDetector:
    def detect_anomalies(self, data: np.ndarray, threshold: float = 3.0) -> List[int]:
        # Simple z-score anomaly detection
        mean = np.mean(data)
        std = np.std(data)
        z_scores = np.abs((data - mean) / std)
        return [i for i, z in enumerate(z_scores) if z > threshold]

    def detect_events(self, news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Detect impactful news events
        return [event for event in news if event['impact'] != 'neutral']
