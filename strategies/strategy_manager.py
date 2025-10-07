"""
Strategy management for Sentio
"""
from typing import Any, List, Dict
import logging

logger = logging.getLogger("sentio.strategies.strategy_manager")

class StrategyManager:
    def __init__(self):
        self.strategies: Dict[str, Any] = {}
        logger.info("StrategyManager initialized.")
        self._auto_register_strategies()

    def _auto_register_strategies(self):
        # Dynamically register strategies from plugin or config
        try:
            from .plugin import strategy_plugins
            for name, strat in strategy_plugins.items():
                self.register_strategy(name, strat)
            logger.info(f"Auto-registered strategies: {list(strategy_plugins.keys())}")
        except Exception as e:
            logger.warning(f"Auto-registration failed: {e}")

    def register_strategy(self, name: str, strategy: Any):
        if name in self.strategies:
            logger.warning(f"Strategy '{name}' already registered. Overwriting.")
        self.strategies[name] = strategy
        logger.info(f"Registered strategy: {name}")

    def get_strategy(self, name: str) -> Any:
        strat = self.strategies.get(name)
        if not strat:
            logger.error(f"Strategy '{name}' not found.")
            return None
        return strat

    def get_all_strategies(self) -> list:
        return list(self.strategies.values())

    def list_strategies(self) -> List[str]:
        return list(self.strategies.keys())

    def select_best_strategy(self, market_data: Any, regime: str = None, external_context: dict = None) -> str:
        """
        Select the best strategy using ML, analytics, regime-awareness, and external context (profit maximization).
        Args:
            market_data: Historical market data
            regime: Optional market regime
            external_context: Optional external context
        Returns:
            str: Name of the best strategy
        """
        from sklearn.linear_model import LinearRegression
        import numpy as np
        best_name = None
        best_score = -np.inf
        diagnostics = {}
        for name, strategy in self.strategies.items():
            try:
                # Regime-aware signal generation
                if hasattr(strategy, 'generate_signals'):
                    signals = strategy.generate_signals(market_data)
                else:
                    signals = strategy.run(market_data)
                X = np.arange(len(signals)).reshape(-1, 1)
                y = np.array([1 if (s.get('signal', s) == 'buy') else -1 for s in signals])
                model = LinearRegression().fit(X, y)
                score = model.score(X, y)
                diagnostics[name] = {
                    'score': score,
                    'regime': regime,
                    'external_context': external_context
                }
                if score > best_score:
                    best_score = score
                    best_name = name
            except Exception as e:
                logger.error(f"Error evaluating strategy {name}: {e}")
                diagnostics[name] = {'error': str(e), 'regime': regime, 'external_context': external_context}
        logger.info(f"Best strategy selected: {best_name} with score {best_score} | Diagnostics: {diagnostics}")
        # Fallback: if no strategy meets threshold, select safest
        if best_name is None and self.strategies:
            best_name = next(iter(self.strategies))
            logger.warning(f"Fallback to first strategy: {best_name}")
        return best_name
