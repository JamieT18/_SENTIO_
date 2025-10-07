# Analysis module for Sentio
# Analysis module for Sentio

from .patterns import detect_candlestick_patterns, detect_chart_patterns
from .plugin import analysis_plugins
from .regime_detection import RegimeDetector


def real_time_market_analysis(exchanges, news, social_media, regime=None, external_context=None, diagnostics=None):
    detector = RegimeDetector()
    market_data = exchanges.get('market_data') if isinstance(exchanges, dict) and 'market_data' in exchanges else None
    sentiment_score = news.get('sentiment_score') if isinstance(news, dict) and 'sentiment_score' in news else None
    detected_context = detector.regime_context(market_data, sentiment_score) if market_data is not None else {}
    return {
        "exchange_data": exchanges,
        "news_data": news,
        "social_data": social_media,
        "regime": regime or detected_context.get('regime'),
        "external_context": external_context,
        "diagnostics": diagnostics,
        "regime_detection": detected_context,
    }


def ml_predictive_modeling(market_data, features, regime=None, external_context=None, diagnostics=None):
    detector = RegimeDetector()
    detected_context = detector.regime_context(market_data) if market_data is not None else {}
    prediction = 1.05
    confidence = 0.87
    regime_val = regime or detected_context.get('regime')
    if regime_val == "bull":
        confidence += 0.02
    elif regime_val == "bear":
        confidence -= 0.02
    if diagnostics and diagnostics.get("error_rate", 0) > 0.1:
        confidence -= 0.02
    if external_context and external_context.get("macro") == "positive":
        confidence += 0.01
    return {
        "prediction": prediction,
        "confidence": confidence,
        "regime": regime_val,
        "external_context": external_context,
        "diagnostics": diagnostics,
        "regime_detection": detected_context,
    }


def sentiment_narrative_to_price_analysis(sentiment_data, narrative_data, price_data, regime=None, external_context=None, diagnostics=None):
    detector = RegimeDetector()
    detected_context = detector.regime_context(price_data, sentiment_data.get('score') if isinstance(sentiment_data, dict) and 'score' in sentiment_data else None) if price_data is not None else {}
    sentiment_score = 0.72
    narrative_impact = "bullish"
    price_effect = 0.03
    regime_val = regime or detected_context.get('regime')
    if regime_val == "bear":
        price_effect -= 0.01
    if diagnostics and diagnostics.get("error_rate", 0) > 0.1:
        price_effect -= 0.01
    if external_context and external_context.get("macro") == "negative":
        price_effect -= 0.01
    return {
        "sentiment_score": sentiment_score,
        "narrative_impact": narrative_impact,
        "price_effect": price_effect,
        "regime": regime_val,
        "external_context": external_context,
        "diagnostics": diagnostics,
        "regime_detection": detected_context,
    }
