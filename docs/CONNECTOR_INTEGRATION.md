# External Service Integration Guide

## Overview

Sentio 2.0 provides a modular connector architecture for integrating with external services including:
- **Broker APIs** (order execution, account management)
- **Data Providers** (market data, quotes, historical data)
- **Notification Services** (email, webhooks, alerts)

## Architecture

### Base Components

#### BaseConnector
All connectors inherit from `BaseConnector` which provides:
- **Connection management** - connect/disconnect lifecycle
- **Error handling** - retry logic with exponential backoff
- **Circuit breaker** - automatic failure protection
- **Health monitoring** - status tracking and diagnostics

#### Specialized Base Classes
- `BrokerConnector` - For order execution and account management
- `DataProviderConnector` - For market data retrieval
- `NotificationConnector` - For sending alerts and notifications

### Error Handling

The connector framework includes comprehensive error handling:

```python
from sentio.connectors import (
    ConnectorError,      # Base exception
    ConnectionError,     # Connection failures
    APIError,           # API-level errors
    RateLimitError      # Rate limiting
)
```

**Features:**
- Automatic retry with exponential backoff
- Circuit breaker pattern (opens after N failures, auto-resets)
- Configurable retry policies
- Detailed error tracking

### Health Monitoring

The `HealthMonitor` class provides centralized health checking:

```python
from sentio.connectors import HealthMonitor

# Create monitor
monitor = HealthMonitor(check_interval=60)

# Register connectors
monitor.register_connector('alpaca', alpaca_broker)

# Check health
health = monitor.check_health('alpaca')
summary = monitor.get_summary()
unhealthy = monitor.get_unhealthy_connectors()
```

## Available Connectors

### 1. Alpaca Broker Connector

**Purpose:** Execute trades and manage accounts via Alpaca API

**Configuration:**
```python
from sentio.connectors import ConnectorFactory

config = {
    'api_key': 'your_alpaca_key',
    'api_secret': 'your_alpaca_secret',
    'base_url': 'https://paper-api.alpaca.markets',  # Paper trading
    'max_retries': 3,
    'retry_delay': 1.0,
    'retry_backoff': 2.0
}

broker = ConnectorFactory.create_broker('alpaca', config)
```

**Features:**
- Place market/limit/stop orders
- Cancel orders
- Get order status
- Retrieve account information
- List positions
- Automatic retry on failures
- Rate limit handling

**Example Usage:**
```python
# Connect
broker.connect()

# Place order
order = broker.place_order(
    symbol='AAPL',
    quantity=100,
    side='buy',
    order_type='market'
)

# Check status
status = broker.get_order_status(order['id'])

# Get account
account = broker.get_account()
print(f"Buying power: ${account['buying_power']}")

# Get positions
positions = broker.get_positions()

# Health check
health = broker.health_check()
```

### 2. Polygon Data Provider Connector

**Purpose:** Fetch market data from Polygon.io API

**Configuration:**
```python
config = {
    'api_key': 'your_polygon_key',
    'base_url': 'https://api.polygon.io',
    'max_retries': 3,
    'retry_delay': 1.0
}

data_provider = ConnectorFactory.create_data_provider('polygon', config)
```

**Features:**
- Real-time quotes
- Historical bars (multiple timeframes)
- Batch quote fetching
- Automatic retry on failures

**Example Usage:**
```python
# Connect
data_provider.connect()

# Get quote
quote = data_provider.get_quote('AAPL')
print(f"Price: ${quote['price']}, Change: {quote['change_pct']:.2f}%")

# Get historical bars
bars = data_provider.get_bars(
    symbol='AAPL',
    timeframe='5min',
    limit=100
)

# Get multiple quotes
quotes = data_provider.get_multiple_quotes(['AAPL', 'GOOGL', 'MSFT'])
```

### 3. Email Notification Connector

**Purpose:** Send email notifications and alerts

**Configuration:**
```python
config = {
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your_email@gmail.com',
    'password': 'your_app_password',
    'from_address': 'sentio@trading.com',
    'use_tls': True,
    'max_retries': 3
}

email_notifier = ConnectorFactory.create_notification('email', config)
```

**Features:**
- Send HTML or plain text emails
- CC/BCC support
- Priority-based alerts
- Automatic retry on SMTP failures

**Example Usage:**
```python
# Connect
email_notifier.connect()

# Send notification
email_notifier.send_notification(
    recipient='trader@example.com',
    subject='Trade Executed',
    message='Your buy order for AAPL has been filled.',
    html=True
)

# Send alert
email_notifier.send_alert(
    alert_type='Risk Alert',
    message='Portfolio drawdown exceeds 5%',
    priority='high',
    recipient='trader@example.com'
)
```

### 4. Webhook Notification Connector

**Purpose:** Send notifications to webhook endpoints (Slack, Discord, custom services)

**Configuration:**
```python
config = {
    'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    'auth_token': 'optional_bearer_token',
    'headers': {
        'Custom-Header': 'value'
    },
    'max_retries': 3
}

webhook_notifier = ConnectorFactory.create_notification('webhook', config)
```

**Features:**
- Send JSON payloads to webhooks
- Custom headers and authentication
- Trade notifications
- Alert notifications
- Automatic retry on failures

**Example Usage:**
```python
# Connect
webhook_notifier.connect()

# Send notification
webhook_notifier.send_notification(
    recipient='#trading-alerts',
    subject='Trade Alert',
    message='AAPL buy signal detected'
)

# Send alert
webhook_notifier.send_alert(
    alert_type='trade_execution',
    message='Bought 100 shares of AAPL @ $150.00',
    priority='normal'
)

# Send trade notification
webhook_notifier.send_trade_notification({
    'symbol': 'AAPL',
    'side': 'buy',
    'quantity': 100,
    'price': 150.00,
    'timestamp': '2024-01-01T10:30:00'
})
```

## Connector Factory

The `ConnectorFactory` manages connector registration and creation:

```python
from sentio.connectors import ConnectorFactory

# List available connectors
brokers = ConnectorFactory.list_registered_brokers()
data_providers = ConnectorFactory.list_registered_data_providers()
notifications = ConnectorFactory.list_registered_notifications()

# Create instances
broker = ConnectorFactory.create_broker('alpaca', config, instance_id='main_broker')
data = ConnectorFactory.create_data_provider('polygon', config)

# Retrieve instances
broker = ConnectorFactory.get_instance('main_broker')

# List all instances
instances = ConnectorFactory.list_instances()
```

## Advanced Features

### Circuit Breaker

Connectors automatically implement circuit breaker pattern:

```python
# Configure circuit breaker
config = {
    'api_key': 'key',
    'max_errors': 5,           # Open circuit after 5 errors
    'error_reset_time': 300    # Reset after 5 minutes
}

connector = ConnectorFactory.create_broker('alpaca', config)

# Circuit opens automatically after max_errors
# Prevents cascading failures
# Auto-resets after error_reset_time
```

### Retry Logic

Configurable retry with exponential backoff:

```python
config = {
    'api_key': 'key',
    'max_retries': 3,          # Retry up to 3 times
    'retry_delay': 1.0,        # Initial delay 1 second
    'retry_backoff': 2.0       # Double delay each retry
}

# Retries: 1s, 2s, 4s before giving up
```

### Health Monitoring

Monitor connector health continuously:

```python
from sentio.connectors import HealthMonitor

monitor = HealthMonitor(check_interval=60)

# Register connectors
monitor.register_connector('broker', broker)
monitor.register_connector('data', data_provider)

# Periodic checks
while True:
    # Check if due for health check
    if monitor.should_check('broker'):
        health = monitor.check_health('broker')
        if not health['healthy']:
            print(f"Warning: {health['message']}")
    
    # Get overall summary
    summary = monitor.get_summary()
    print(f"Healthy: {summary['healthy']}/{summary['total_connectors']}")
    
    time.sleep(60)
```

## Error Handling Best Practices

### Basic Error Handling

```python
from sentio.connectors import (
    ConnectorError,
    ConnectionError,
    APIError,
    RateLimitError
)

try:
    order = broker.place_order('AAPL', 100, 'buy')
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e}")
except ConnectorError as e:
    print(f"Connector error: {e}")
```

### Graceful Degradation

```python
def get_quote_with_fallback(symbol):
    """Get quote with fallback to secondary provider"""
    try:
        return primary_provider.get_quote(symbol)
    except ConnectorError:
        logger.warning("Primary provider failed, using fallback")
        return fallback_provider.get_quote(symbol)
```

### Status Monitoring

```python
def ensure_connected(connector):
    """Ensure connector is connected"""
    status = connector.get_status()
    
    if status['circuit_open']:
        raise Exception("Circuit breaker is open")
    
    if status['status'] != 'connected':
        connector.connect()
```

## Integration with Trading Engine

```python
from sentio.connectors import ConnectorFactory
from sentio.execution.trading_engine import TradingEngine

# Setup connectors
broker = ConnectorFactory.create_broker('alpaca', broker_config)
data_provider = ConnectorFactory.create_data_provider('polygon', data_config)
notifier = ConnectorFactory.create_notification('webhook', webhook_config)

# Connect services
broker.connect()
data_provider.connect()
notifier.connect()

# Initialize trading engine
engine = TradingEngine(
    strategies=strategies,
    broker=broker,
    data_provider=data_provider
)

# Execute trade with notifications
def execute_trade_with_alerts(signal):
    try:
        # Place order
        order = broker.place_order(
            symbol=signal['symbol'],
            quantity=signal['quantity'],
            side=signal['side']
        )
        
        # Send notification
        notifier.send_trade_notification({
            'symbol': signal['symbol'],
            'action': signal['side'],
            'quantity': signal['quantity'],
            'order_id': order['id']
        })
        
    except ConnectorError as e:
        # Send alert on failure
        notifier.send_alert(
            alert_type='order_failure',
            message=f"Failed to execute order: {e}",
            priority='high'
        )
```

## Creating Custom Connectors

### Custom Broker Connector

```python
from sentio.connectors.base import BrokerConnector

class CustomBrokerConnector(BrokerConnector):
    def __init__(self, name, config):
        super().__init__(name, config)
        self.api_key = config['api_key']
        # Setup your API client
    
    def connect(self):
        # Implement connection logic
        self.status = ConnectorStatus.CONNECTED
        return True
    
    def disconnect(self):
        # Implement disconnection logic
        return True
    
    def health_check(self):
        # Implement health check
        return {'healthy': True}
    
    def place_order(self, symbol, quantity, side, order_type='market', **kwargs):
        # Implement order placement with retry
        def _place():
            # Your API call here
            return {'id': 'order_123', 'status': 'filled'}
        
        return self._retry_with_backoff(_place)
    
    # Implement other required methods...

# Register custom connector
ConnectorFactory.register_broker('custom', CustomBrokerConnector)
```

### Custom Data Provider

```python
from sentio.connectors.base import DataProviderConnector

class CustomDataConnector(DataProviderConnector):
    def get_quote(self, symbol):
        def _get_quote():
            # Your implementation
            return {'symbol': symbol, 'price': 150.0}
        
        return self._retry_with_backoff(_get_quote)
    
    # Implement other required methods...

ConnectorFactory.register_data_provider('custom_data', CustomDataConnector)
```

## Configuration Examples

### Environment Variables

```bash
# Alpaca
ALPACA_API_KEY=your_key
ALPACA_API_SECRET=your_secret

# Polygon
POLYGON_API_KEY=your_key

# Email
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Webhook
WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Configuration File

```json
{
  "connectors": {
    "broker": {
      "type": "alpaca",
      "config": {
        "api_key": "${ALPACA_API_KEY}",
        "api_secret": "${ALPACA_API_SECRET}",
        "base_url": "https://paper-api.alpaca.markets",
        "max_retries": 3
      }
    },
    "data": {
      "type": "polygon",
      "config": {
        "api_key": "${POLYGON_API_KEY}",
        "max_retries": 3
      }
    },
    "notifications": [
      {
        "type": "email",
        "config": {
          "smtp_host": "smtp.gmail.com",
          "username": "${EMAIL_USERNAME}",
          "password": "${EMAIL_PASSWORD}"
        }
      },
      {
        "type": "webhook",
        "config": {
          "webhook_url": "${WEBHOOK_URL}"
        }
      }
    ]
  }
}
```

## Troubleshooting

### Connection Issues

```python
# Check connector status
status = connector.get_status()
print(f"Status: {status['status']}")
print(f"Error count: {status['error_count']}")
print(f"Circuit open: {status['circuit_open']}")
print(f"Last error: {status['last_error_message']}")

# Check health
health = connector.health_check()
print(f"Healthy: {health['healthy']}")
print(f"Message: {health['message']}")
```

### Rate Limiting

```python
# Connectors automatically handle rate limits
# Configure retry behavior:
config = {
    'max_retries': 5,
    'retry_delay': 2.0,
    'retry_backoff': 2.0
}

# Rate limit errors will be retried automatically
# with exponential backoff
```

### Circuit Breaker Issues

```python
# Check if circuit is open
if connector.circuit_open:
    # Wait for reset or manually reset
    connector.circuit_open = False
    connector.error_count = 0
```

## Performance Considerations

1. **Connection Pooling** - Reuse connector instances
2. **Batch Operations** - Use `get_multiple_quotes()` when possible
3. **Health Checks** - Don't check too frequently (60s recommended)
4. **Retry Configuration** - Balance between resilience and latency
5. **Circuit Breaker** - Prevents cascading failures

## Security Best Practices

1. **Never hardcode credentials** - Use environment variables
2. **Use secure protocols** - TLS/SSL for all connections
3. **Rotate API keys** - Regularly update credentials
4. **Monitor access** - Track connector usage and errors
5. **Least privilege** - Use read-only keys where possible

## Next Steps

- Implement additional broker connectors (Interactive Brokers, TD Ameritrade)
- Add more data providers (Alpha Vantage, IEX Cloud)
- Create notification connectors for Slack, Discord, Telegram
- Add metrics collection and reporting
- Implement connection pooling for improved performance
