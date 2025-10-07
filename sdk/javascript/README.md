# Sentio JavaScript/TypeScript SDK

Official JavaScript/TypeScript SDK for the Sentio Trading API.

Works in both Browser and Node.js environments.

## Installation

```bash
# NPM
npm install sentio-sdk

# Yarn
yarn add sentio-sdk

# Or copy the TypeScript file to your project
cp sdk/javascript/sentio-sdk.ts your-project/src/
```

## Quick Start

### TypeScript

```typescript
import { SentioClient } from 'sentio-sdk';

// Initialize client
const client = new SentioClient({
  baseUrl: 'http://localhost:8000'
});

// Login
const response = await client.login('username', 'password');
console.log(`Token: ${response.access_token}`);

// Get trade signals
const signals = await client.getTradeSignals(['AAPL', 'GOOGL', 'MSFT']);
signals.signals.forEach(signal => {
  console.log(`${signal.symbol}: ${signal.signal} (confidence: ${signal.confidence})`);
});

// Analyze a symbol
const analysis = await client.analyzeSymbol('AAPL');
console.log(`Signal: ${analysis.signal}, Confidence: ${analysis.confidence}`);
```

### JavaScript (ES6+)

```javascript
const { SentioClient } = require('sentio-sdk');

const client = new SentioClient({
  baseUrl: 'http://localhost:8000'
});

async function main() {
  // Login
  await client.login('username', 'password');
  
  // Get earnings
  const earnings = await client.getEarnings('user_123');
  console.log(`Portfolio Value: $${earnings.portfolio_value.toLocaleString()}`);
  console.log(`Total Return: ${earnings.total_return_pct}%`);
}

main().catch(console.error);
```

## Features

- ✅ **Full TypeScript Support**: Complete type definitions
- ✅ **Complete API Coverage**: All 23 API endpoints
- ✅ **Error Handling**: Custom error class with status codes
- ✅ **Auto Retry**: Automatic retry logic for failed requests
- ✅ **Browser & Node.js**: Works in both environments
- ✅ **Modern Async/Await**: Promise-based API
- ✅ **Zero Dependencies**: Uses native fetch API

## Usage Examples

### Authentication

```typescript
import { SentioClient, SentioAPIError } from 'sentio-sdk';

const client = new SentioClient({ baseUrl: 'http://localhost:8000' });

try {
  // Login
  const response = await client.login('username', 'password');
  console.log(`Logged in! Token expires in ${response.expires_in} seconds`);
  
  // Or initialize with existing token
  const client2 = new SentioClient({
    baseUrl: 'http://localhost:8000',
    token: 'your_jwt_token_here'
  });
} catch (error) {
  if (error instanceof SentioAPIError) {
    console.error(`Login failed: ${error.message}`);
    console.error(`Status code: ${error.statusCode}`);
  }
}
```

### Trading Operations

```typescript
// Analyze a symbol
const analysis = await client.analyzeSymbol('AAPL');
if (analysis.signal === 'buy' && analysis.confidence > 0.7) {
  // Execute trade
  const trade = await client.executeTrade('AAPL', 'buy', 100, 150.00);
  console.log('Trade executed:', trade);
}

// Get positions
const { positions } = await client.getPositions();
console.log('Open positions:', positions);

// Get performance
const performance = await client.getPerformance();
console.log(`Win rate: ${(performance.win_rate * 100).toFixed(2)}%`);
```

### Dashboard Data (React Example)

```typescript
import { useEffect, useState } from 'react';
import { SentioClient } from 'sentio-sdk';

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const client = new SentioClient({
      baseUrl: 'http://localhost:8000',
      token: localStorage.getItem('authToken')
    });
    
    async function loadData() {
      try {
        const dashboardData = await client.loadDashboardData(
          'user_123',
          ['AAPL', 'GOOGL', 'MSFT']
        );
        setData(dashboardData);
      } catch (error) {
        console.error('Failed to load dashboard:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Dashboard</h1>
      {/* Render dashboard data */}
    </div>
  );
}
```

### Market Intelligence

```typescript
// Get insider trades
const insiderTrades = await client.getInsiderTrades('AAPL', 20);
console.log('Recent insider trades:', insiderTrades.trades);

// Get top insider symbols
const topSymbols = await client.getTopInsiderSymbols(10);
console.log('Top insider-traded symbols:', topSymbols.symbols);

// Get fundamental analysis
const fundamentals = await client.getFundamentalAnalysis('AAPL');
console.log(`Overall Score: ${fundamentals.overall_score}`);
console.log(`Recommendation: ${fundamentals.recommendation}`);
```

### Subscription Management

```typescript
// Get pricing
const pricing = await client.getPricing();
pricing.tiers.forEach(tier => {
  console.log(`${tier.tier}: $${tier.price}/month`);
});

// Get user subscription
const subscription = await client.getSubscription('user_123');
console.log(`Current tier: ${subscription.tier}`);
console.log('Features:', subscription.features);

// Calculate profit sharing
const calc = await client.calculateProfitSharing('user_123', 1000.00);
console.log(`Profit sharing fee: $${calc.sharing_fee.toFixed(2)}`);
console.log(`User keeps: $${calc.user_keeps.toFixed(2)}`);
```

### Error Handling

```typescript
import { SentioAPIError } from 'sentio-sdk';

try {
  const signals = await client.getTradeSignals();
} catch (error) {
  if (error instanceof SentioAPIError) {
    switch (error.statusCode) {
      case 401:
        console.error('Authentication failed. Please login.');
        break;
      case 404:
        console.error('Endpoint not found.');
        break;
      case 500:
        console.error('Server error. Please try again later.');
        break;
      default:
        console.error(`Error: ${error.message}`);
    }
    
    // Access error details
    if (error.response) {
      console.error('Error details:', error.response);
    }
  } else {
    console.error('Unexpected error:', error);
  }
}
```

### Advanced Configuration

```typescript
const client = new SentioClient({
  baseUrl: 'https://api.sentio.example.com',
  timeout: 60000,  // 60 second timeout
  maxRetries: 5,   // Retry up to 5 times
  token: 'your-jwt-token'  // Pre-configured token
});
```

## API Reference

### SentioClient

Main client class for interacting with the Sentio API.

#### Constructor Options

```typescript
interface SentioConfig {
  baseUrl?: string;      // API base URL (default: 'http://localhost:8000')
  token?: string;        // JWT authentication token
  timeout?: number;      // Request timeout in ms (default: 30000)
  maxRetries?: number;   // Max retry attempts (default: 3)
}
```

#### Methods

**Authentication**
- `login(username, password)` - Login and obtain JWT token
- `healthCheck()` - Check API health
- `getStatus()` - Get system status

**Trading**
- `analyzeSymbol(symbol)` - Analyze a stock symbol
- `executeTrade(symbol, action, quantity, price?)` - Execute a trade
- `getPositions(userId?)` - Get open positions
- `getPerformance(userId?)` - Get performance metrics

**Strategies**
- `getStrategies()` - Get available strategies
- `toggleStrategy(strategyName, enabled)` - Enable/disable a strategy

**Market Intelligence**
- `getInsiderTrades(symbol, limit?)` - Get insider trades
- `getTopInsiderSymbols(limit?)` - Get top insider-traded symbols
- `getFundamentalAnalysis(symbol)` - Get fundamental analysis

**Dashboard**
- `getTradeSignals(symbols?)` - Get trade signals
- `getEarnings(userId)` - Get earnings summary
- `getAISummary(symbol?)` - Get AI insights
- `getStrengthSignal(symbol?)` - Get strength indicators
- `getTradeJournal(userId, limit?)` - Get trade journal
- `addTradeJournalEntry(entry)` - Add journal entry
- `getPerformanceCards(userId)` - Get performance cards

**Subscription**
- `getPricing()` - Get pricing information
- `getSubscription(userId)` - Get subscription details
- `calculateProfitSharing(userId, profit)` - Calculate profit sharing
- `getProfitSharingBalance(userId)` - Get profit sharing balance

**Utilities**
- `loadDashboardData(userId, symbols?)` - Load all dashboard data

### Error Class

```typescript
class SentioAPIError extends Error {
  statusCode?: number;   // HTTP status code
  response?: any;        // Full error response
}
```

### Type Definitions

```typescript
interface TradeSignal {
  symbol: string;
  signal: 'buy' | 'sell' | 'hold';
  confidence: number;
  consensus_strength: number;
  timestamp: string;
}

interface Position {
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  unrealized_pnl: number;
}

interface SubscriptionTier {
  tier: 'free' | 'basic' | 'professional' | 'enterprise';
  price: number;
  features: Record<string, any>;
}
```

## Browser Compatibility

The SDK uses the native `fetch` API. For older browsers, include a polyfill:

```html
<script src="https://cdn.jsdelivr.net/npm/whatwg-fetch@3.6.2/dist/fetch.umd.js"></script>
```

Or install via npm:

```bash
npm install whatwg-fetch
```

## Node.js Compatibility

For Node.js < 18, you'll need to install `node-fetch`:

```bash
npm install node-fetch@2
```

Then use it as a polyfill:

```javascript
global.fetch = require('node-fetch');
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
