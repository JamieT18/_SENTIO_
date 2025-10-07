"""
Automated Portfolio Rebalancer for Sentio
Smart rebalancing based on risk, performance, and user goals
"""
from typing import Dict, Any, List
import numpy as np

class PortfolioRebalancer:
    def __init__(self, risk_tolerance: float = 0.05):
        self.risk_tolerance = risk_tolerance

    def rebalance(self, portfolio: Dict[str, float], target_alloc: Dict[str, float]) -> Dict[str, float]:
        """
        Rebalance portfolio to target allocation
        Args:
            portfolio: Current holdings {symbol: value}
            target_alloc: Target allocation {symbol: percent}
        Returns:
            Dict of trades to execute {symbol: trade_amount}
        """
        total_value = sum(portfolio.values())
        trades = {}
        for symbol, target_pct in target_alloc.items():
            current_value = portfolio.get(symbol, 0)
            target_value = total_value * target_pct
            trades[symbol] = target_value - current_value
        return trades

    def recommend_rebalance(self, portfolio: Dict[str, float], performance: Dict[str, Any]) -> Dict[str, float]:
        """
        Recommend rebalance based on risk and performance
        """
        # Example: overweight winners, underweight losers
        target_alloc = {symbol: 1/len(portfolio) for symbol in portfolio}
        for symbol, perf in performance.items():
            if perf['return'] > 0.05:
                target_alloc[symbol] += self.risk_tolerance
            elif perf['return'] < -0.05:
                target_alloc[symbol] -= self.risk_tolerance
        # Normalize
        total = sum(target_alloc.values())
        for symbol in target_alloc:
            target_alloc[symbol] /= total
        return self.rebalance(portfolio, target_alloc)
