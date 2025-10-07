"""
Unit tests for Sentio strategies module
"""
import unittest
from sentio.strategies import BaseStrategy, StrategyManager, optimize_strategy_params

class DummyStrategy(BaseStrategy):
    def generate_signals(self, market_data):
        # Simple logic for testing
        return ['buy' if x > 0 else 'sell' for x in market_data]

class TestStrategyOptimizer(unittest.TestCase):
    def test_optimize_strategy_params(self):
        strategy = DummyStrategy()
        market_data = [1, -1, 2, -2]
        param_grid = [
            {'threshold': 0},
            {'threshold': 1}
        ]
        best_params = optimize_strategy_params(strategy, market_data, param_grid)
        self.assertIn('threshold', best_params)

class TestStrategyManager(unittest.TestCase):
    def test_register_and_get_strategy(self):
        manager = StrategyManager()
        strategy = DummyStrategy()
        manager.register_strategy('dummy', strategy)
        self.assertIs(manager.get_strategy('dummy'), strategy)

    def test_list_strategies(self):
        manager = StrategyManager()
        manager.register_strategy('dummy', DummyStrategy())
        self.assertIn('dummy', manager.list_strategies())

    def test_select_best_strategy_stub(self):
        manager = StrategyManager()
        manager.register_strategy('dummy', DummyStrategy())
        self.assertEqual(manager.select_best_strategy([1, 2, 3]), 'dummy')

class TestBaseStrategy(unittest.TestCase):
    def test_set_params(self):
        strategy = BaseStrategy()
        strategy.set_params(a=1, b=2)
        self.assertEqual(strategy.params['a'], 1)
        self.assertEqual(strategy.params['b'], 2)

    def test_generate_signals_stub(self):
        strategy = BaseStrategy()
        signals = strategy.generate_signals([1, 2, 3])
        self.assertEqual(signals, [])

if __name__ == "__main__":
    unittest.main()
