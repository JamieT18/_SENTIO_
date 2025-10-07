# Sentio Python SDK

Official Python SDK for the Sentio Trading API.

## Installation

```bash
# Install from source
cd sdk/python
pip install -e .

# Or copy the file to your project
cp sdk/python/sentio_sdk.py your_project/
```

## Quick Start

```python
from sentio_sdk import SentioClient

# Initialize client
client = SentioClient(base_url="http://localhost:8000")

# Login
response = client.login("username", "password")
print(f"Token: {response['access_token']}")

# Get trade signals
signals = client.get_trade_signals(["AAPL", "GOOGL", "MSFT"])
for signal in signals['signals']:
    print(f"{signal['symbol']}: {signal['signal']} (confidence: {signal['confidence']})")

# Analyze a symbol
analysis = client.analyze_symbol("AAPL")
print(f"Signal: {analysis['signal']}, Confidence: {analysis['confidence']}")

# Get earnings summary
earnings = client.get_earnings("user_123")
print(f"Portfolio Value: ${earnings['portfolio_value']:,.2f}")
print(f"Total Return: {earnings['total_return_pct']:.2f}%")
```

## Features

- ✅ **Complete API Coverage**: All 23 API endpoints supported
- ✅ **Type Hints**: Full type annotations for better IDE support
- ✅ **Error Handling**: Comprehensive error handling with custom exceptions
- ✅ **Auto Retry**: Automatic retry logic for failed requests
- ✅ **Authentication**: Built-in JWT token management
- ✅ **Logging**: Integrated logging support
- ✅ **Session Management**: Persistent HTTP sessions for better performance

## Usage Examples

### Authentication

```python
from sentio_sdk import SentioClient, SentioAPIError

client = SentioClient(base_url="http://localhost:8000")

try:
    # Login
    response = client.login("username", "password")
    print(f"Logged in! Token expires in {response['expires_in']} seconds")
    
    # Or initialize with existing token
    client2 = SentioClient(
        base_url="http://localhost:8000",
        token="your_jwt_token_here"
    )
except SentioAPIError as e:
    print(f"Login failed: {e}")
    print(f"Status code: {e.status_code}")
```

### Trading Operations

```python
# Analyze a symbol
analysis = client.analyze_symbol("AAPL")
if analysis['signal'] == 'buy' and analysis['confidence'] > 0.7:
    # Execute trade
    trade = client.execute_trade(
        symbol="AAPL",
        action="buy",
        quantity=100,
        price=150.00  # Optional limit price
    )
    print(f"Trade executed: {trade}")

# Get positions
positions = client.get_positions()
print(f"Open positions: {positions['positions']}")

# Get performance
performance = client.get_performance()
print(f"Win rate: {performance['win_rate']:.2%}")
```

### Dashboard Data

```python
# Load all dashboard data at once
dashboard = client.load_dashboard_data(
    user_id="user_123",
    symbols=["AAPL", "GOOGL", "MSFT"]
)

print("Performance Cards:", dashboard['performance_cards'])
print("Trade Signals:", dashboard['trade_signals'])
print("Earnings:", dashboard['earnings'])
print("AI Summary:", dashboard['ai_summary'])
```

### Market Intelligence

```python
# Get insider trades
insider_trades = client.get_insider_trades("AAPL", limit=20)
print(f"Recent insider trades: {insider_trades['trades']}")

# Get top insider symbols
top_symbols = client.get_top_insider_symbols(limit=10)
print(f"Top insider-traded symbols: {top_symbols['symbols']}")

# Get fundamental analysis
fundamentals = client.get_fundamental_analysis("AAPL")
print(f"Overall Score: {fundamentals['overall_score']}")
print(f"Recommendation: {fundamentals['recommendation']}")
```

### Subscription Management

```python
# Get pricing
pricing = client.get_pricing()
for tier in pricing['tiers']:
    print(f"{tier['tier']}: ${tier['price']}/month")

# Get user subscription
subscription = client.get_subscription("user_123")
print(f"Current tier: {subscription['tier']}")
print(f"Features: {subscription['features']}")

# Calculate profit sharing
calc = client.calculate_profit_sharing("user_123", profit=1000.00)
print(f"Profit sharing fee: ${calc['sharing_fee']:.2f}")
print(f"User keeps: ${calc['user_keeps']:.2f}")
```

### Strategy Management

```python
# Get available strategies
strategies = client.get_strategies()
for strategy in strategies['strategies']:
    print(f"{strategy['name']}: {'Enabled' if strategy['enabled'] else 'Disabled'}")

# Toggle strategy
result = client.toggle_strategy("momentum", enabled=True)
print(f"Momentum strategy is now {'enabled' if result['enabled'] else 'disabled'}")
```

### Error Handling

```python
from sentio_sdk import SentioClient, SentioAPIError

client = SentioClient(base_url="http://localhost:8000")

try:
    signals = client.get_trade_signals()
except SentioAPIError as e:
    if e.status_code == 401:
        print("Authentication failed. Please login.")
    elif e.status_code == 404:
        print("Endpoint not found.")
    elif e.status_code >= 500:
        print("Server error. Please try again later.")
    else:
        print(f"Error: {e}")
    
    # Access error details
    if e.response:
        print(f"Error details: {e.response}")
```

### Custom Configuration

```python
import logging

# Configure logging
logger = logging.getLogger("sentio_sdk")
logger.setLevel(logging.DEBUG)

# Initialize with custom settings
client = SentioClient(
    base_url="https://api.sentio.example.com",
    timeout=60,  # 60 second timeout
    max_retries=5,  # Retry up to 5 times
    logger=logger
)
```

## API Reference

### SentioClient

Main client class for interacting with the Sentio API.

#### Methods

**Authentication**
- `login(username, password)` - Login and obtain JWT token
- `health_check()` - Check API health
- `get_status()` - Get system status

**Trading**
- `analyze_symbol(symbol)` - Analyze a stock symbol
- `execute_trade(symbol, action, quantity, price=None)` - Execute a trade
- `get_positions(user_id=None)` - Get open positions
- `get_performance(user_id=None)` - Get performance metrics

**Strategies**
- `get_strategies()` - Get available strategies
- `toggle_strategy(strategy_name, enabled)` - Enable/disable a strategy

**Market Intelligence**
- `get_insider_trades(symbol, limit=50)` - Get insider trades
- `get_top_insider_symbols(limit=10)` - Get top insider-traded symbols
- `get_fundamental_analysis(symbol)` - Get fundamental analysis

**Dashboard**
- `get_trade_signals(symbols=None)` - Get trade signals
- `get_earnings(user_id)` - Get earnings summary
- `get_ai_summary(symbol=None)` - Get AI insights
- `get_strength_signal(symbol=None)` - Get strength indicators
- `get_trade_journal(user_id, limit=50)` - Get trade journal
- `add_trade_journal_entry(...)` - Add journal entry
- `get_performance_cards(user_id)` - Get performance cards

**Subscription**
- `get_pricing()` - Get pricing information
- `get_subscription(user_id)` - Get subscription details
- `calculate_profit_sharing(user_id, profit)` - Calculate profit sharing
- `get_profit_sharing_balance(user_id)` - Get profit sharing balance

**Utilities**
- `load_dashboard_data(user_id, symbols=None)` - Load all dashboard data

### Exceptions

- `SentioAPIError` - Base exception for all API errors
  - `message` - Error message
  - `status_code` - HTTP status code (if available)
  - `response` - Full error response (if available)

### Enums

- `SubscriptionTier` - FREE, BASIC, PROFESSIONAL, ENTERPRISE
- `TradeSignal` - BUY, SELL, HOLD

## Requirements

- Python 3.7+
- requests library

```bash
pip install requests
```

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check the main [API Documentation](../../API.md)
2. Review the [examples](../../examples/)
3. Open an issue on GitHub

## Version

2.0.0
