# Sentio Developer Tools

This directory contains developer tools for working with the Sentio Trading API.

## Available Tools

### 1. Sentio CLI (`sentio-cli.py`)

Command-line interface for testing and interacting with the Sentio API.

**Usage:**

```bash
# Make executable (first time only)
chmod +x tools/sentio-cli.py

# Check API health
./tools/sentio-cli.py health

# Login and get token
./tools/sentio-cli.py login -u admin -p admin123

# Analyze a symbol
./tools/sentio-cli.py analyze AAPL --token YOUR_TOKEN

# Get trade signals
./tools/sentio-cli.py signals --symbols AAPL,GOOGL,MSFT --token YOUR_TOKEN

# Get pricing tiers
./tools/sentio-cli.py pricing

# Load full dashboard
./tools/sentio-cli.py dashboard --user-id user_123 --token YOUR_TOKEN

# Get insider trades
./tools/sentio-cli.py insider AAPL --limit 10 --token YOUR_TOKEN

# Get fundamental analysis
./tools/sentio-cli.py fundamental AAPL --token YOUR_TOKEN
```

**Available Commands:**

- `health` - Check API health
- `status` - Get system status
- `login` - Login and get JWT token
- `analyze` - Analyze a stock symbol
- `signals` - Get trade signals
- `insider` - Get insider trades
- `top-insider` - Get top insider symbols
- `fundamental` - Get fundamental analysis
- `pricing` - Get subscription pricing
- `dashboard` - Load dashboard data
- `earnings` - Get earnings summary
- `performance` - Get performance metrics
- `strategies` - List available strategies
- `toggle` - Toggle strategy on/off

**Options:**

- `--base-url` - API base URL (default: http://localhost:8000)
- `--token` - JWT authentication token

### 2. OpenAPI Generator (`generate_openapi.py`)

Generates OpenAPI 3.0 specification from the FastAPI application.

**Usage:**

```bash
python tools/generate_openapi.py
```

**Output:** `openapi.json` in the root directory

This file can be used with:
- Swagger UI
- ReDoc
- Postman (import OpenAPI spec)
- OpenAPI code generators
- API documentation tools

### 3. Postman Collection Generator (`generate_postman.py`)

Generates a Postman collection with all API endpoints.

**Usage:**

```bash
python tools/generate_postman.py
```

**Output:** `postman_collection.json` in the `config/` directory

**Import to Postman:**

1. Open Postman
2. Click "Import" button
3. Select `config/postman_collection.json`
4. Update the `base_url` variable if needed

**Features:**

- All 23 API endpoints organized by category
- Pre-configured authentication
- Sample request bodies
- Environment variables for base URL and token
- Auto-save token after login

## SDK Libraries

### Python SDK

Location: `sdk/python/`

**Installation:**

```bash
# Install from source
cd sdk/python
pip install -e .

# Or copy to your project
cp sdk/python/sentio_sdk.py your_project/
```

**Quick Start:**

```python
from sentio_sdk import SentioClient

client = SentioClient(base_url="http://localhost:8000")
client.login("username", "password")

signals = client.get_trade_signals(["AAPL", "GOOGL"])
print(signals)
```

See [sdk/python/README.md](../sdk/python/README.md) for full documentation.

### JavaScript/TypeScript SDK

Location: `sdk/javascript/`

**Installation:**

```bash
# NPM
npm install sentio-sdk

# Or copy to your project
cp sdk/javascript/sentio-sdk.ts your-project/src/
```

**Quick Start:**

```typescript
import { SentioClient } from 'sentio-sdk';

const client = new SentioClient({ baseUrl: 'http://localhost:8000' });
await client.login('username', 'password');

const signals = await client.getTradeSignals(['AAPL', 'GOOGL']);
console.log(signals);
```

See [sdk/javascript/README.md](../sdk/javascript/README.md) for full documentation.

## Testing Workflow

### 1. Start the API Server

```bash
python sentio/ui/api.py
# or
uvicorn sentio.ui.api:app --reload
```

### 2. Test with CLI

```bash
# Quick health check
./tools/sentio-cli.py health

# Login
./tools/sentio-cli.py login -u admin -p admin123

# Test endpoints
./tools/sentio-cli.py signals --token YOUR_TOKEN
```

### 3. Test with Postman

1. Import `config/postman_collection.json`
2. Update environment variables
3. Run "Login" request to get token
4. Test other endpoints

### 4. Test with SDK

```python
# Python
from sentio_sdk import SentioClient

client = SentioClient()
client.login("admin", "admin123")
result = client.get_trade_signals()
```

```typescript
// TypeScript
import { SentioClient } from 'sentio-sdk';

const client = new SentioClient();
await client.login('admin', 'admin123');
const result = await client.getTradeSignals();
```

## Code Generation

### Generate Client Code from OpenAPI

After generating `openapi.json`, you can use OpenAPI generators to create client code:

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate -i openapi.json -g python -o generated/python

# Generate JavaScript client
openapi-generator-cli generate -i openapi.json -g javascript -o generated/javascript

# Generate Java client
openapi-generator-cli generate -i openapi.json -g java -o generated/java

# Generate Go client
openapi-generator-cli generate -i openapi.json -g go -o generated/go
```

## Interactive API Documentation

The Sentio API includes built-in interactive documentation:

### Swagger UI

- URL: http://localhost:8000/docs
- Test endpoints directly in the browser
- View request/response schemas
- Try authentication

### ReDoc

- URL: http://localhost:8000/redoc
- Clean, readable documentation
- Search functionality
- Code samples

## Development Best Practices

### 1. Use Environment Variables

```bash
# .env file
SENTIO_API_URL=http://localhost:8000
SENTIO_API_TOKEN=your_token_here
```

```python
import os
from sentio_sdk import SentioClient

client = SentioClient(
    base_url=os.getenv('SENTIO_API_URL'),
    token=os.getenv('SENTIO_API_TOKEN')
)
```

### 2. Error Handling

Always wrap API calls in try-except blocks:

```python
from sentio_sdk import SentioClient, SentioAPIError

try:
    result = client.get_trade_signals()
except SentioAPIError as e:
    if e.status_code == 401:
        # Handle auth error
        pass
    else:
        # Handle other errors
        pass
```

### 3. Rate Limiting

Be aware of rate limits when making API calls:

- Monitor response headers for rate limit info
- Implement exponential backoff for retries
- Use batch endpoints when available

### 4. Testing

Write tests for your API integrations:

```python
import unittest
from sentio_sdk import SentioClient

class TestSentioAPI(unittest.TestCase):
    def setUp(self):
        self.client = SentioClient()
        self.client.login("test_user", "test_pass")
    
    def test_get_signals(self):
        result = self.client.get_trade_signals()
        self.assertIn('signals', result)
```

## Troubleshooting

### Common Issues

**1. Connection Refused**

- Ensure API server is running: `python sentio/ui/api.py`
- Check the base URL is correct
- Verify firewall settings

**2. Authentication Errors**

- Check token is valid and not expired
- Use the login endpoint to get a fresh token
- Verify Bearer token format: `Bearer YOUR_TOKEN`

**3. Import Errors (Python SDK)**

- Install dependencies: `pip install requests`
- Check Python path includes SDK directory
- Verify Python version >= 3.7

**4. CORS Errors (Browser)**

- API needs to allow your origin in CORS settings
- Check browser console for specific errors
- Use Postman for testing if CORS is an issue

## Contributing

When adding new tools:

1. Follow existing code style
2. Add comprehensive help text
3. Update this README
4. Test with the actual API
5. Add error handling

## Support

For issues or questions:

1. Check the [main documentation](../API.md)
2. Review [example code](../examples/)
3. Try the interactive docs at `/docs`
4. Open an issue on GitHub

## Version

2.0.0
