"""
Advanced scenario simulation utilities for Sentio
"""
"""
Advanced scenario simulation utilities for Sentio
"""
import numpy as np
from typing import Dict, Any, List

class MonteCarloSimulator:
    def simulate(self, portfolio: Dict[str, float], n_simulations: int = 1000, horizon: int = 252, regime: str = None, external_context: dict = None) -> np.ndarray:
        # Simulate portfolio returns using normal distribution, regime/context-aware
        mu = 0.08
        sigma = 0.15
        if regime == "bull":
            mu += 0.03
        elif regime == "bear":
            mu -= 0.04
            sigma += 0.05
        if external_context and "volatility" in external_context:
            sigma *= external_context["volatility"]
        returns = np.random.normal(mu, sigma, (n_simulations, horizon))
        return returns

class StressTester:
    def stress_test(self, portfolio: Dict[str, float], scenarios: Dict[str, Dict[str, float]], regime: str = None, external_context: dict = None) -> Dict[str, Any]:
        # Apply stress scenarios to portfolio, regime/context-aware
        results = {}
        for name, scenario in scenarios.items():
            stressed = {asset: value * scenario.get(asset, 1.0) for asset, value in portfolio.items()}
            # Regime/context diagnostics
            results[name] = {
                "stressed": stressed,
                "regime": regime,
                "external_context": external_context
            }
        return results

class WhatIfEngine:
    def what_if(self, portfolio: Dict[str, float], changes: Dict[str, float], regime: str = None, external_context: dict = None) -> Dict[str, Any]:
        # Apply hypothetical changes to portfolio, regime/context-aware
        result = {asset: value * changes.get(asset, 1.0) for asset, value in portfolio.items()}
        return {
            "result": result,
            "regime": regime,
            "external_context": external_context
        }
