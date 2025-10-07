# Sentio Strategy Plugin System

## Overview
Sentio supports custom strategy plugins for extensibility. Register your own trading strategies and use them in backtesting or live trading.

## Usage Example
```python
from sentio.strategies.plugin import strategy_plugins
from sentio.strategies.strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def generate_signals(self, market_data):
        # Custom logic
        return ['buy' if x['close'] > x['open'] else 'sell' for x in market_data]

strategy_plugins.register('my_custom_strategy', MyCustomStrategy)
```

## Listing Plugins
```python
print(strategy_plugins.list_plugins())
```
