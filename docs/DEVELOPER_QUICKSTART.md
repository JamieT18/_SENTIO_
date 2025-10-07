# Sentio 2.0 Developer Quickstart

Get started with the Sentio 2.0 Trading API in 5 minutes.

## Prerequisites

- Python 3.7+ (for backend/Python SDK)
- Node.js 14+ (for JavaScript SDK)
- Git
- Text editor or IDE

## Step 1: Clone the Repository

```bash
git clone https://github.com/JamieT18/Sentio-2.0.git
cd Sentio-2.0
```

## Step 2: Start the API Server

### Option A: Python Script

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python sentio/ui/api.py
```

### Option B: Uvicorn

```bash
# Install dependencies
pip install -r requirements.txt

# Start with uvicorn
uvicorn sentio.ui.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## Step 3: Verify the API

### Using Browser

Open http://localhost:8000/docs to access the interactive Swagger UI.

### Using CLI

```bash
# Check health
curl http://localhost:8000/api/v1/health

# Get pricing (no auth required)
curl http://localhost:8000/api/v1/subscription/pricing
```

### Using Sentio CLI

```bash
chmod +x tools/sentio-cli.py
./tools/sentio-cli.py health
```

## Step 4: Choose Your SDK

### Python SDK

```bash
# Navigate to SDK directory
cd sdk/python

# Install
pip install -e .

# Test
python -c "from sentio_sdk import SentioClient; print('SDK ready!')"
```

**Quick Example:**

```python
from sentio_sdk import SentioClient

# Initialize
client = SentioClient(base_url="http://localhost:8000")

# Login
client.login("admin", "admin123")

# Get signals
signals = client.get_trade_signals(["AAPL", "GOOGL"])
print(signals)
```

### JavaScript/TypeScript SDK

```bash
# Copy SDK to your project
cp sdk/javascript/sentio-sdk.ts your-project/src/

# Or install as package (when published)
# npm install sentio-sdk
```

**Quick Example:**

```typescript
import { SentioClient } from './sentio-sdk';

// Initialize
const client = new SentioClient({ baseUrl: 'http://localhost:8000' });

// Login
await client.login('admin', 'admin123');

// Get signals
const signals = await client.getTradeSignals(['AAPL', 'GOOGL']);
console.log(signals);
```

## Step 5: Test with Postman

### Generate Collection

```bash
python tools/generate_postman.py
```

### Import to Postman

1. Open Postman
2. Click "Import"
3. Select `config/postman_collection.json`
4. Update environment variable `base_url` if needed
5. Run "Login" request to get auth token
6. Test other endpoints

## Common Use Cases

### 1. Get Trade Signals

**Python:**

```python
from sentio_sdk import SentioClient

client = SentioClient()
client.login("admin", "admin123")

signals = client.get_trade_signals(["AAPL", "GOOGL", "MSFT", "TSLA"])
for signal in signals['signals']:
    print(f"{signal['symbol']}: {signal['signal']} ({signal['confidence']:.1%})")
```

**JavaScript:**

```typescript
const signals = await client.getTradeSignals(['AAPL', 'GOOGL', 'MSFT', 'TSLA']);
signals.signals.forEach(signal => {
    console.log(`${signal.symbol}: ${signal.signal} (${(signal.confidence * 100).toFixed(1)}%)`);
});
```

**CLI:**

```bash
./tools/sentio-cli.py signals --symbols AAPL,GOOGL,MSFT --token YOUR_TOKEN
```

**cURL:**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/dashboard/trade-signals?symbols=AAPL,GOOGL,MSFT"
```

### 2. Analyze a Symbol

**Python:**

```python
analysis = client.analyze_symbol("AAPL")
print(f"Signal: {analysis['signal']}")
print(f"Confidence: {analysis['confidence']:.1%}")
```

**JavaScript:**

```typescript
const analysis = await client.analyzeSymbol('AAPL');
console.log(`Signal: ${analysis.signal}`);
console.log(`Confidence: ${(analysis.confidence * 100).toFixed(1)}%`);
```

**CLI:**

```bash
./tools/sentio-cli.py analyze AAPL --token YOUR_TOKEN
```

### 3. Load Dashboard Data

**Python:**

```python
dashboard = client.load_dashboard_data(
    user_id="user_123",
    symbols=["AAPL", "GOOGL", "MSFT"]
)

print("Performance:", dashboard['performance_cards'])
print("Signals:", dashboard['trade_signals'])
print("Earnings:", dashboard['earnings'])
```

**JavaScript:**

```typescript
const dashboard = await client.loadDashboardData('user_123', ['AAPL', 'GOOGL', 'MSFT']);

console.log('Performance:', dashboard.performanceCards);
console.log('Signals:', dashboard.tradeSignals);
console.log('Earnings:', dashboard.earnings);
```

**CLI:**

```bash
./tools/sentio-cli.py dashboard --user-id user_123 --symbols AAPL,GOOGL,MSFT --token YOUR_TOKEN
```

### 4. Get Insider Trades

**Python:**

```python
trades = client.get_insider_trades("AAPL", limit=10)
print(f"Insider trades for AAPL: {trades}")
```

**JavaScript:**

```typescript
const trades = await client.getInsiderTrades('AAPL', 10);
console.log('Insider trades for AAPL:', trades);
```

**CLI:**

```bash
./tools/sentio-cli.py insider AAPL --limit 10 --token YOUR_TOKEN
```

## Authentication

### Default Credentials

The system comes with default admin credentials:

- **Username:** `admin`
- **Password:** `admin123`

**⚠️ Change these in production!**

### Getting a Token

**Python:**

```python
response = client.login("admin", "admin123")
token = response['access_token']
print(f"Token: {token}")
```

**JavaScript:**

```typescript
const response = await client.login('admin', 'admin123');
const token = response.access_token;
console.log(`Token: ${token}`);
```

**CLI:**

```bash
./tools/sentio-cli.py login -u admin -p admin123
```

**cURL:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Using a Token

**Python:**

```python
# Option 1: Login (automatic)
client.login("admin", "admin123")

# Option 2: Set token directly
client = SentioClient(token="your_jwt_token")
```

**JavaScript:**

```typescript
// Option 1: Login (automatic)
await client.login('admin', 'admin123');

// Option 2: Set token in constructor
const client = new SentioClient({ 
    baseUrl: 'http://localhost:8000',
    token: 'your_jwt_token' 
});
```

**CLI:**

```bash
./tools/sentio-cli.py signals --token YOUR_JWT_TOKEN
```

**cURL:**

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v1/dashboard/trade-signals
```

## Next Steps

### 1. Explore the Documentation

- **API Reference:** [API.md](API.md) - Complete API documentation
- **Dashboard API:** [DASHBOARD_API.md](DASHBOARD_API.md) - Dashboard endpoints
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- **SDK Documentation:** [sdk/README.md](sdk/README.md) - SDK guides

### 2. Try the Examples

```bash
# Python examples
python examples/dashboard_api_demo.py
python examples/profit_sharing_demo.py
python examples/auth_demo.py

# WebSocket example
python examples/websocket_demo.py
```

### 3. Use Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 4. Build Your Application

Use the SDKs to build your own trading application:

```python
# Example: Trading bot
from sentio_sdk import SentioClient

class TradingBot:
    def __init__(self):
        self.client = SentioClient()
        self.client.login("admin", "admin123")
    
    def run(self):
        # Get signals
        signals = self.client.get_trade_signals()
        
        # Process signals
        for signal in signals['signals']:
            if signal['signal'] == 'buy' and signal['confidence'] > 0.8:
                print(f"Strong buy signal for {signal['symbol']}")
                # Add your trading logic here

bot = TradingBot()
bot.run()
```

### 5. Customize and Extend

- Add new strategies
- Integrate with your data sources
- Build custom dashboards
- Implement automated trading

## Troubleshooting

### API Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn sentio.ui.api:app --port 8001
```

### Import Errors

```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.7+
```

### Authentication Errors

```bash
# Check if API is running
curl http://localhost:8000/api/v1/health

# Verify credentials
./tools/sentio-cli.py login -u admin -p admin123
```

### CORS Errors (Browser)

The API is configured to allow all origins for development. For production, update CORS settings in `sentio/ui/api.py`.

## Getting Help

1. **Documentation:** Check [API.md](API.md) for comprehensive API docs
2. **Examples:** Review code in [examples/](examples/) directory
3. **Tools:** Use [tools/](tools/) for testing and development
4. **Interactive Docs:** Try http://localhost:8000/docs
5. **GitHub Issues:** Open an issue for bugs or questions

## Resources

- **Main Documentation:** [API.md](API.md)
- **Python SDK:** [sdk/python/README.md](sdk/python/README.md)
- **JavaScript SDK:** [sdk/javascript/README.md](sdk/javascript/README.md)
- **Developer Tools:** [tools/README.md](tools/README.md)
- **Examples:** [examples/README.md](examples/README.md)

---

**Happy coding! 🚀**
