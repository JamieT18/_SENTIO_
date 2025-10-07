"""
Example: Custom strategy plugin for Sentio
"""
from sentio.strategies.plugin import strategy_plugins
from sentio.strategies.strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def generate_signals(self, market_data, external_context=None):
        # Simple custom logic with external context and diagnostics
        signals = ['buy' if x['close'] > x['open'] else 'sell' for x in market_data]
        diagnostics = {
            "external_context": external_context,
            "signal_count": len(signals)
        }
        return signals, diagnostics

strategy_plugins.register('my_custom_strategy', MyCustomStrategy, version="1.1", diagnostics={"example": True})
