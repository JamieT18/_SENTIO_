"""
Political and Insider Trade Tracking System
Monitors congressional trades and corporate insider transactions for alpha generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..core.logger import get_logger

logger = get_logger(__name__)


class TradeType(str, Enum):
    """Type of insider trade"""

    BUY = "buy"
    SELL = "sell"
    OPTION_EXERCISE = "option_exercise"
    GIFT = "gift"


class TraderType(str, Enum):
    """Type of trader"""

    SENATOR = "senator"
    REPRESENTATIVE = "representative"
    CORPORATE_INSIDER = "corporate_insider"
    EXECUTIVE = "executive"


@dataclass
class InsiderTrade:
    """
    Individual insider trade record
    """

    symbol: str
    trader_name: str
    trader_type: TraderType
    trade_type: TradeType
    amount: float
    shares: Optional[int]
    trade_date: datetime
    disclosure_date: datetime
    disclosure_delay_days: int
    price: Optional[float]
    committee: Optional[str]  # For politicians
    position: Optional[str]  # For corporate insiders
    metadata: Dict[str, Any]


class InsiderTracker:
    def actor_network_centrality(self, trades: List[InsiderTrade]) -> dict:
        """
        Compute network centrality of traders based on shared symbols.
        """
        from collections import defaultdict
        graph = defaultdict(set)
        for t in trades:
            graph[t.trader_name].add(t.symbol)
        degrees = {k: len(v) for k, v in graph.items()}
        central_trader = max(degrees, key=degrees.get) if degrees else None
        return {'central_trader': central_trader, 'degrees': degrees}

    def forecast_trade_activity(self, trades: List[InsiderTrade], horizon: int = 7) -> dict:
        """
        Forecast future trade activity using simple trend extrapolation.
        """
        import numpy as np
        amounts = np.array([t.amount for t in trades])
        if len(amounts) < 2:
            return {'forecast': [float(a) for a in amounts]}
        trend = (amounts[-1] - amounts[0]) / max(len(amounts)-1, 1)
        forecast = [float(amounts[-1] + trend * i) for i in range(1, horizon+1)]
        return {'forecast': forecast, 'trend': trend}

    def propagate_trade_sentiment(self, trades: List[InsiderTrade]) -> dict:
        """
        Propagate sentiment through trader network.
        """
        from collections import defaultdict
        sentiment_map = defaultdict(float)
        for t in trades:
            sentiment = 1.0 if t.trade_type == TradeType.BUY else -1.0
            sentiment_map[t.trader_name] += sentiment
        return dict(sentiment_map)

    def overall_anomaly_score(self, trades: List[InsiderTrade]) -> float:
        """
        Score overall anomaly level in insider trades.
        """
        import numpy as np
        amounts = np.array([t.amount for t in trades])
        if len(amounts) == 0:
            return 0.0
        score = float(np.sum(amounts > (np.mean(amounts) + 2 * np.std(amounts))) / len(amounts))
        return score
    def correlate_trades_with_events(self, trades: List[InsiderTrade], events: List[dict]) -> dict:
        """
        Correlate insider trades with political events for predictive signals.
        """
        import numpy as np
        event_dates = [e.get('date') for e in events]
        trade_dates = [t.trade_date for t in trades]
        # Simple correlation: count trades within 3 days of events
        correlated = sum(1 for td in trade_dates for ed in event_dates if abs((td-ed).days) <= 3)
        score = correlated / (len(trades) + 1e-8)
        return {'correlated_trades': correlated, 'correlation_score': score}

    def predict_trade_impact(self, trades: List[InsiderTrade]) -> dict:
        """
        Predict market impact of tracked trades using ML (stub).
        """
        # In production, use price data and ML models
        import numpy as np
        impact = np.mean([t.amount for t in trades]) if trades else 0.0
        return {'predicted_impact': impact, 'trade_count': len(trades)}

    def detect_anomalous_trading(self, trades: List[InsiderTrade]) -> list:
        """
        Detect anomalous trading patterns (outliers, unusual clusters).
        """
        import numpy as np
        amounts = np.array([t.amount for t in trades])
        threshold = np.mean(amounts) + 2 * np.std(amounts)
        anomalies = [t for t in trades if t.amount > threshold]
        return [{'trader': t.trader_name, 'symbol': t.symbol, 'amount': t.amount} for t in anomalies]

    def influence_score(self, trader_name: str) -> float:
        """
        Score trader's influence based on trade size, frequency, and clustering.
        """
        trades = [t for t in self.tracked_trades if t.trader_name == trader_name]
        if not trades:
            return 0.0
        import numpy as np
        size_score = np.mean([t.amount for t in trades])
        freq_score = len(trades)
        cluster_score = sum(1 for t in trades if t.amount > 1e6)
        influence = size_score * 0.5 + freq_score * 0.3 + cluster_score * 0.2
        return float(influence)
    """
    Tracks and analyzes insider and political trades

    Features:
    - Congressional trade monitoring
    - Corporate insider transaction tracking
    - Disclosure delay analysis
    - Clustering of coordinated trades
    - Alpha attribution from following trades
    - Sentiment scoring based on trade patterns
    """

    def __init__(self):
        """Initialize insider tracker"""
        self.tracked_trades: List[InsiderTrade] = []
        self.alpha_attribution: Dict[str, Dict[str, Any]] = {}
        self.watchlist: Dict[str, List[str]] = {}  # Symbol -> [traders]

        logger.info("Insider tracker initialized")

    def track_congressional_trade(self, trade_data: Dict[str, Any]) -> InsiderTrade:
        """
        Track a congressional trade

        Args:
            trade_data: Trade information from disclosure

        Returns:
            Processed insider trade record
        """
        trade = InsiderTrade(
            symbol=trade_data["symbol"],
            trader_name=trade_data["name"],
            trader_type=(
                TraderType.SENATOR
                if trade_data.get("chamber") == "senate"
                else TraderType.REPRESENTATIVE
            ),
            trade_type=TradeType(trade_data["type"].lower()),
            amount=trade_data["amount"],
            shares=trade_data.get("shares"),
            trade_date=trade_data["trade_date"],
            disclosure_date=trade_data["disclosure_date"],
            disclosure_delay_days=(
                trade_data["disclosure_date"] - trade_data["trade_date"]
            ).days,
            price=trade_data.get("price"),
            committee=trade_data.get("committee"),
            position=None,
            metadata={
                "chamber": trade_data.get("chamber"),
                "party": trade_data.get("party"),
                "state": trade_data.get("state"),
            },
        )

        self.tracked_trades.append(trade)
        self._update_watchlist(trade)

        logger.info(
            f"Congressional trade tracked: {trade.trader_name} "
            f"{trade.trade_type.value} ${trade.amount:,.0f} of {trade.symbol}"
        )

        return trade

    def track_corporate_insider_trade(self, trade_data: Dict[str, Any]) -> InsiderTrade:
        """
        Track a corporate insider trade

        Args:
            trade_data: Trade information from SEC Form 4

        Returns:
            Processed insider trade record
        """
        trade = InsiderTrade(
            symbol=trade_data["symbol"],
            trader_name=trade_data["name"],
            trader_type=(
                TraderType.EXECUTIVE
                if trade_data.get("is_executive")
                else TraderType.CORPORATE_INSIDER
            ),
            trade_type=TradeType(trade_data["type"].lower()),
            amount=trade_data["amount"],
            shares=trade_data.get("shares"),
            trade_date=trade_data["trade_date"],
            disclosure_date=trade_data["disclosure_date"],
            disclosure_delay_days=(
                trade_data["disclosure_date"] - trade_data["trade_date"]
            ).days,
            price=trade_data.get("price"),
            committee=None,
            position=trade_data.get("position"),
            metadata={
                "title": trade_data.get("title"),
                "is_director": trade_data.get("is_director", False),
                "ownership_after": trade_data.get("ownership_after"),
            },
        )

        self.tracked_trades.append(trade)
        self._update_watchlist(trade)

        logger.info(
            f"Corporate insider trade tracked: {trade.trader_name} ({trade.position}) "
            f"{trade.trade_type.value} {trade.shares} shares of {trade.symbol}"
        )

        return trade

    def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze insider trading patterns for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Analysis with sentiment and signals
        """
        # Get trades for this symbol
        symbol_trades = [t for t in self.tracked_trades if t.symbol == symbol]

        if not symbol_trades:
            return {
                "symbol": symbol,
                "insider_sentiment": "neutral",
                "score": 0.0,
                "trades": [],
            }

        # Analyze recent trades (last 90 days)
        cutoff_date = datetime.now() - timedelta(days=90)
        recent_trades = [t for t in symbol_trades if t.trade_date >= cutoff_date]

        # Calculate sentiment
        buy_value = sum(
            t.amount for t in recent_trades if t.trade_type == TradeType.BUY
        )
        sell_value = sum(
            t.amount for t in recent_trades if t.trade_type == TradeType.SELL
        )

        net_value = buy_value - sell_value
        total_value = buy_value + sell_value

        if total_value == 0:
            sentiment_score = 0.0
            sentiment = "neutral"
        else:
            sentiment_score = net_value / total_value

            if sentiment_score > 0.3:
                sentiment = "bullish"
            elif sentiment_score < -0.3:
                sentiment = "bearish"
            else:
                sentiment = "neutral"

        # Identify notable traders
        notable_traders = self._identify_notable_traders(recent_trades)

        # Check for clusters (coordinated trading)
        clusters = self._detect_trade_clusters(recent_trades)

        return {
            "symbol": symbol,
            "insider_sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "buy_value": buy_value,
            "sell_value": sell_value,
            "net_value": net_value,
            "trade_count": len(recent_trades),
            "notable_traders": notable_traders,
            "clusters": clusters,
            "avg_disclosure_delay": sum(t.disclosure_delay_days for t in recent_trades)
            / len(recent_trades),
            "trades": [
                self._trade_to_dict(t) for t in recent_trades[:10]
            ],  # Last 10 trades
        }

    def get_top_traded_symbols(
        self, trader_type: Optional[TraderType] = None, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get most traded symbols by insiders

        Args:
            trader_type: Filter by trader type
            days: Look back period

        Returns:
            List of symbols with trading activity
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # Filter trades
        filtered_trades = [
            t
            for t in self.tracked_trades
            if t.trade_date >= cutoff_date
            and (trader_type is None or t.trader_type == trader_type)
        ]

        # Aggregate by symbol
        symbol_activity: Dict[str, Dict[str, Any]] = {}

        for trade in filtered_trades:
            if trade.symbol not in symbol_activity:
                symbol_activity[trade.symbol] = {
                    "symbol": trade.symbol,
                    "buy_count": 0,
                    "sell_count": 0,
                    "buy_value": 0.0,
                    "sell_value": 0.0,
                    "traders": set(),
                }

            activity = symbol_activity[trade.symbol]
            activity["traders"].add(trade.trader_name)

            if trade.trade_type == TradeType.BUY:
                activity["buy_count"] += 1
                activity["buy_value"] += trade.amount
            elif trade.trade_type == TradeType.SELL:
                activity["sell_count"] += 1
                activity["sell_value"] += trade.amount

        # Convert to list and sort
        result = []
        for symbol, activity in symbol_activity.items():
            activity["trader_count"] = len(activity["traders"])
            activity["total_value"] = activity["buy_value"] + activity["sell_value"]
            activity["net_value"] = activity["buy_value"] - activity["sell_value"]
            del activity["traders"]  # Remove set for JSON serialization
            result.append(activity)

        # Sort by total value
        result.sort(key=lambda x: x["total_value"], reverse=True)

        return result

    def calculate_alpha_attribution(
        self, symbol: str, follow_delay_days: int = 7
    ) -> Dict[str, Any]:
        """
        Calculate alpha from following insider trades

        Args:
            symbol: Stock symbol
            follow_delay_days: Days after disclosure to simulate entry

        Returns:
            Alpha attribution analysis
        """
        symbol_trades = [t for t in self.tracked_trades if t.symbol == symbol]

        # In production: fetch actual price data
        # For now: simulate returns

        total_alpha = 0.0
        trade_count = 0
        wins = 0

        for trade in symbol_trades:
            # Simulate following the trade after disclosure
            # In production: use actual price data
            simulated_return = 0.05 if trade.trade_type == TradeType.BUY else -0.05

            total_alpha += simulated_return
            trade_count += 1
            if simulated_return > 0:
                wins += 1

        if symbol not in self.alpha_attribution:
            self.alpha_attribution[symbol] = {
                "total_alpha": total_alpha,
                "trade_count": trade_count,
                "win_rate": wins / trade_count if trade_count > 0 else 0,
                "avg_alpha": total_alpha / trade_count if trade_count > 0 else 0,
            }

        return self.alpha_attribution[symbol]

    def _update_watchlist(self, trade: InsiderTrade):
        """Add symbol to watchlist based on trade"""
        if trade.symbol not in self.watchlist:
            self.watchlist[trade.symbol] = []

        if trade.trader_name not in self.watchlist[trade.symbol]:
            self.watchlist[trade.symbol].append(trade.trader_name)

    def _identify_notable_traders(
        self, trades: List[InsiderTrade]
    ) -> List[Dict[str, Any]]:
        """Identify notable traders (high success rate, large positions)"""
        trader_stats: Dict[str, Dict[str, Any]] = {}

        for trade in trades:
            if trade.trader_name not in trader_stats:
                trader_stats[trade.trader_name] = {
                    "name": trade.trader_name,
                    "type": trade.trader_type.value,
                    "trade_count": 0,
                    "total_value": 0.0,
                    "position": trade.position or trade.committee,
                }

            stats = trader_stats[trade.trader_name]
            stats["trade_count"] += 1
            stats["total_value"] += trade.amount

        # Sort by total value
        notable = sorted(
            trader_stats.values(), key=lambda x: x["total_value"], reverse=True
        )[:5]

        return notable

    def _detect_trade_clusters(
        self, trades: List[InsiderTrade], time_window_days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Detect clusters of trades (coordinated activity)

        Args:
            trades: List of trades
            time_window_days: Days within which trades are considered clustered

        Returns:
            List of detected clusters
        """
        if len(trades) < 2:
            return []

        # Sort by date
        sorted_trades = sorted(trades, key=lambda t: t.trade_date)

        clusters = []
        current_cluster = [sorted_trades[0]]

        for i in range(1, len(sorted_trades)):
            trade = sorted_trades[i]
            prev_trade = sorted_trades[i - 1]

            days_apart = (trade.trade_date - prev_trade.trade_date).days

            if days_apart <= time_window_days:
                current_cluster.append(trade)
            else:
                if len(current_cluster) >= 3:  # At least 3 trades
                    clusters.append(
                        {
                            "start_date": current_cluster[0].trade_date,
                            "end_date": current_cluster[-1].trade_date,
                            "trade_count": len(current_cluster),
                            "trader_count": len(
                                set(t.trader_name for t in current_cluster)
                            ),
                            "total_value": sum(t.amount for t in current_cluster),
                            "consensus": (
                                "buy"
                                if sum(
                                    1
                                    for t in current_cluster
                                    if t.trade_type == TradeType.BUY
                                )
                                > len(current_cluster) / 2
                                else "sell"
                            ),
                        }
                    )
                current_cluster = [trade]

        # Check last cluster
        if len(current_cluster) >= 3:
            clusters.append(
                {
                    "start_date": current_cluster[0].trade_date,
                    "end_date": current_cluster[-1].trade_date,
                    "trade_count": len(current_cluster),
                    "trader_count": len(set(t.trader_name for t in current_cluster)),
                    "total_value": sum(t.amount for t in current_cluster),
                    "consensus": (
                        "buy"
                        if sum(
                            1 for t in current_cluster if t.trade_type == TradeType.BUY
                        )
                        > len(current_cluster) / 2
                        else "sell"
                    ),
                }
            )

        return clusters

    def _trade_to_dict(self, trade: InsiderTrade) -> Dict[str, Any]:
        """Convert trade to dictionary"""
        return {
            "symbol": trade.symbol,
            "trader_name": trade.trader_name,
            "trader_type": trade.trader_type.value,
            "trade_type": trade.trade_type.value,
            "amount": trade.amount,
            "shares": trade.shares,
            "trade_date": trade.trade_date.isoformat(),
            "disclosure_date": trade.disclosure_date.isoformat(),
            "disclosure_delay_days": trade.disclosure_delay_days,
            "price": trade.price,
            "position": trade.position or trade.committee,
        }

    def get_watchlist(self) -> Dict[str, List[str]]:
        """Get current watchlist"""
        return self.watchlist.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get tracker statistics"""
        return {
            "total_trades": len(self.tracked_trades),
            "symbols_tracked": len(set(t.symbol for t in self.tracked_trades)),
            "unique_traders": len(set(t.trader_name for t in self.tracked_trades)),
            "congressional_trades": len(
                [
                    t
                    for t in self.tracked_trades
                    if t.trader_type in [TraderType.SENATOR, TraderType.REPRESENTATIVE]
                ]
            ),
            "corporate_trades": len(
                [
                    t
                    for t in self.tracked_trades
                    if t.trader_type
                    in [TraderType.CORPORATE_INSIDER, TraderType.EXECUTIVE]
                ]
            ),
            "avg_disclosure_delay": (
                sum(t.disclosure_delay_days for t in self.tracked_trades)
                / len(self.tracked_trades)
                if self.tracked_trades
                else 0
            ),
        }
