# Sentio SDK

Official SDKs and developer tools for the Sentio Trading API.

## Available SDKs

### Python SDK

Full-featured Python client for the Sentio API with type hints and comprehensive error handling.

**Location:** `sdk/python/`

**Features:**
- ✅ Complete API coverage (23 endpoints)
- ✅ Type hints for better IDE support
- ✅ Automatic retry logic
- ✅ Built-in error handling
- ✅ JWT token management

**Quick Start:**

```python
from sentio_sdk import SentioClient

client = SentioClient(base_url="http://localhost:8000")
client.login("username", "password")

# Get trade signals
signals = client.get_trade_signals(["AAPL", "GOOGL"])
for signal in signals['signals']:
    print(f"{signal['symbol']}: {signal['signal']}")

# Analyze a symbol
analysis = client.analyze_symbol("AAPL")
print(f"Signal: {analysis['signal']}, Confidence: {analysis['confidence']}")
```

**Documentation:** [Python SDK README](python/README.md)

### JavaScript/TypeScript SDK

Modern JavaScript/TypeScript client that works in both Browser and Node.js environments.

**Location:** `sdk/javascript/`

**Features:**
- ✅ Full TypeScript support
- ✅ Browser and Node.js compatible
- ✅ Promise-based async/await API
- ✅ Zero dependencies (uses native fetch)
- ✅ Automatic retry logic

**Quick Start:**

```typescript
import { SentioClient } from 'sentio-sdk';

const client = new SentioClient({ baseUrl: 'http://localhost:8000' });
await client.login('username', 'password');

// Get trade signals
const signals = await client.getTradeSignals(['AAPL', 'GOOGL']);
console.log(signals);

// Load dashboard data
const dashboard = await client.loadDashboardData('user_123', ['AAPL', 'MSFT']);
console.log(dashboard);
```

**Documentation:** [JavaScript SDK README](javascript/README.md)

## Installation

### Python

```bash
# Install from source
cd sdk/python
pip install -e .

# Or install dependencies and use directly
pip install requests
python -c "from sentio_sdk import SentioClient; print('SDK ready!')"
```

### JavaScript/TypeScript

```bash
# NPM
npm install sentio-sdk

# Yarn
yarn add sentio-sdk

# Or copy the TypeScript file
cp sdk/javascript/sentio-sdk.ts your-project/src/
```

## Usage Examples

### Complete Trading Workflow (Python)

```python
from sentio_sdk import SentioClient, SentioAPIError

# Initialize client
client = SentioClient(base_url="http://localhost:8000")

try:
    # Login
    response = client.login("admin", "admin123")
    print(f"Logged in! Token expires in {response['expires_in']} seconds")
    
    # Get trade signals
    signals = client.get_trade_signals(["AAPL", "GOOGL", "MSFT"])
    
    # Analyze and trade based on signals
    for signal in signals['signals']:
        if signal['signal'] == 'buy' and signal['confidence'] > 0.8:
            # Execute trade
            trade = client.execute_trade(
                symbol=signal['symbol'],
                action='buy',
                quantity=100,
                price=None  # Market order
            )
            print(f"Bought {signal['symbol']}: {trade}")
    
    # Get performance
    performance = client.get_performance()
    print(f"Win rate: {performance['win_rate']:.2%}")
    
except SentioAPIError as e:
    print(f"Error: {e}")
    if e.status_code == 401:
        print("Authentication failed. Check credentials.")
```

### Dashboard Integration (TypeScript)

```typescript
import { SentioClient, SentioAPIError } from 'sentio-sdk';

async function loadDashboard(userId: string) {
    const client = new SentioClient({
        baseUrl: 'http://localhost:8000',
        token: localStorage.getItem('authToken') || undefined
    });
    
    try {
        // If no token, login first
        if (!client.token) {
            await client.login('username', 'password');
        }
        
        // Load all dashboard data
        const data = await client.loadDashboardData(userId, ['AAPL', 'GOOGL']);
        
        return {
            cards: data.performanceCards,
            signals: data.tradeSignals,
            earnings: data.earnings,
            ai: data.aiSummary
        };
        
    } catch (error) {
        if (error instanceof SentioAPIError) {
            console.error(`API Error: ${error.message}`);
            if (error.statusCode === 401) {
                // Redirect to login
                window.location.href = '/login';
            }
        }
        throw error;
    }
}
```

### Market Intelligence (Python)

```python
from sentio_sdk import SentioClient

client = SentioClient()
client.login("admin", "admin123")

# Get insider trades
insider_trades = client.get_insider_trades("AAPL", limit=20)
print(f"Recent insider trades for AAPL:")
for trade in insider_trades['trades'][:5]:
    print(f"  {trade}")

# Get top insider-traded symbols
top_symbols = client.get_top_insider_symbols(limit=10)
print(f"\nTop 10 insider-traded symbols:")
for symbol in top_symbols['symbols']:
    print(f"  {symbol['symbol']}: {symbol['trade_count']} trades")

# Get fundamental analysis
fundamentals = client.get_fundamental_analysis("AAPL")
print(f"\nApple Fundamental Analysis:")
print(f"  Overall Score: {fundamentals['overall_score']}")
print(f"  Recommendation: {fundamentals['recommendation']}")
print(f"  Target Price: ${fundamentals['target_price']:.2f}")
```

## API Coverage

Both SDKs provide complete coverage of all Sentio API endpoints:

### Authentication
- ✅ Login (JWT token)
- ✅ Token management

### General
- ✅ Health check
- ✅ System status

### Trading Operations
- ✅ Analyze symbol
- ✅ Execute trade
- ✅ Get positions
- ✅ Get performance

### Strategy Management
- ✅ List strategies
- ✅ Toggle strategy

### Market Intelligence
- ✅ Insider trades
- ✅ Top insider symbols
- ✅ Fundamental analysis

### Dashboard
- ✅ Trade signals
- ✅ Earnings summary
- ✅ AI summary
- ✅ Strength signal
- ✅ Trade journal (get/add)
- ✅ Performance cards

### Subscription & Billing
- ✅ Get pricing
- ✅ Get subscription
- ✅ Calculate profit sharing
- ✅ Get profit sharing balance

## Error Handling

Both SDKs provide comprehensive error handling:

### Python

```python
from sentio_sdk import SentioAPIError

try:
    result = client.get_trade_signals()
except SentioAPIError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status_code}")
    print(f"Response: {e.response}")
```

### JavaScript/TypeScript

```typescript
import { SentioAPIError } from 'sentio-sdk';

try {
    const result = await client.getTradeSignals();
} catch (error) {
    if (error instanceof SentioAPIError) {
        console.log(`Error: ${error.message}`);
        console.log(`Status: ${error.statusCode}`);
        console.log(`Response:`, error.response);
    }
}
```

## Configuration

### Python

```python
client = SentioClient(
    base_url="https://api.sentio.example.com",  # API URL
    token="your_jwt_token",                      # Pre-configured token
    timeout=60,                                  # Request timeout (seconds)
    max_retries=5                                # Retry attempts
)
```

### JavaScript/TypeScript

```typescript
const client = new SentioClient({
    baseUrl: 'https://api.sentio.example.com',  // API URL
    token: 'your_jwt_token',                     // Pre-configured token
    timeout: 60000,                              // Request timeout (ms)
    maxRetries: 5                                // Retry attempts
});
```

## Testing

### Python

```python
import unittest
from sentio_sdk import SentioClient

class TestSentioSDK(unittest.TestCase):
    def setUp(self):
        self.client = SentioClient(base_url="http://localhost:8000")
        self.client.login("test_user", "test_pass")
    
    def test_get_signals(self):
        result = self.client.get_trade_signals()
        self.assertIn('signals', result)
        self.assertIsInstance(result['signals'], list)

if __name__ == '__main__':
    unittest.main()
```

### JavaScript/TypeScript

```typescript
import { SentioClient } from 'sentio-sdk';

describe('SentioClient', () => {
    let client: SentioClient;
    
    beforeEach(async () => {
        client = new SentioClient({ baseUrl: 'http://localhost:8000' });
        await client.login('test_user', 'test_pass');
    });
    
    test('should get trade signals', async () => {
        const result = await client.getTradeSignals();
        expect(result).toHaveProperty('signals');
        expect(Array.isArray(result.signals)).toBe(true);
    });
});
```

## Requirements

### Python SDK
- Python 3.7+
- requests library

### JavaScript/TypeScript SDK
- Node.js 14+ (for Node.js usage)
- Modern browser with fetch API
- TypeScript 4.0+ (for TypeScript usage)

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check the [API Documentation](../API.md)
2. Review SDK-specific READMEs
3. Try the [examples](../examples/)
4. Use the [developer tools](../tools/)
5. Open an issue on GitHub

## Contributing

Contributions are welcome! Please:
1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

## Version

2.0.0
