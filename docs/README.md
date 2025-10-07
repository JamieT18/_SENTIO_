# Sentio: Intelligent Trading System

> **Advanced AI-Powered Multi-Strategy Trading Platform**

![CI/CD](https://github.com/JamieT18/Sentio-2.0/actions/workflows/ci-cd.yml/badge.svg)
![Tests](https://github.com/JamieT18/Sentio-2.0/actions/workflows/tests.yml/badge.svg)
![Code Quality](https://github.com/JamieT18/Sentio-2.0/actions/workflows/code-quality.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Sentio is a production-ready, modular intelligent trading system that combines multiple strategies with confidence-weighted voting, comprehensive risk management, and advanced technical analysis.

## 🚀 Key Features


### Engagement, Community & Social Features
- Suggestions & Feedback: Users can submit suggestions to improve Sentio
- Community Chat & Q&A: Real-time group chat, community Q&A, and social feed
- Friends & Groups: Add friends, join groups, group chat, and group profit sharing
- Leaderboard & Rival System: Compete with others, track rankings, and challenge rivals
- Achievements & Challenges: Unlock achievements, complete daily/weekly challenges, claim rewards
- Referral Program: Invite friends, earn rewards, and track referrals
- Profile Customization: Avatars, bios, badges, notification preferences

### Real-Time Analytics & Monitoring
- Live Analytics Dashboard: Real-time charts, alerts, and performance cards
- WebSocket Integration: Live trade signals, earnings, notifications, admin analytics
- Health & Integrity Checks: System diagnostics, compliance dashboard, trade health scanning
- Performance Profiling: Metrics for latency, resource usage, and strategy performance

### Billing & Monetization Upgrades
- Multi-Method Payments: Pay with crypto, cards, PayPal, Stripe
- Profit-Sharing Calculator: Track and calculate profit sharing for premium/enterprise users
- Referral & Rewards: Earn rewards for inviting users and participating in community events
- Enterprise Licensing: Advanced plans for organizations

### Security & Compliance
- Advanced Authentication: JWT for REST and WebSocket, RBAC, session management
- Compliance Dashboard: Track regulatory status, audit logs, and system integrity
- Enhanced Risk Controls: Circuit breakers, anomaly detection, adaptive sizing, sector exposure

### Developer & API Enhancements
- Expanded API Endpoints: New endpoints for engagement, billing, analytics, health, and more
- Automated Testing & CI/CD: Pytest suite, coverage reporting, GitHub Actions workflow
- SDKs & CLI Tools: Python/JS SDKs, CLI for health, analysis, signals, dashboard, and more

### UI/UX Improvements
- Modern Dashboard: Tabs for portfolio, analytics, community, profile, billing, offers, arbitrage, profit signals, strategy analytics, real-time analytics, live charts, live alerts, core upgrades
- Responsive Design: Mobile, tablet, desktop support
- Performance Cards & Visualizations: Portfolio value, P&L, win rate, trade count, strength signals
- Trade Journal & AI Insights: Journal interface, explainable AI, recommendations

### Advanced Analytics
- Custom Date Ranges & Comparative Analytics: User-defined ranges, benchmark comparisons
- PDF Export & Mobile App Integration: Export reports, mobile analytics views
- AI-Powered Insights: Machine learning trend predictions, clustering, meta-learning

### Other Upgrades
- Code Quality & Reliability: PEP-8, import organization, error handling, maintainability
- Performance Optimizations: GZip, caching, concurrent processing, database pooling, batch ops
- Clustering algorithms

### Safety & Risk Controls
- Multi-layered risk management
- Circuit breakers for extreme losses
- Anomaly detection
- Trade health scanning
- Compliance checks
- Adaptive position sizing

### Profitability Optimizers
- Dynamic profit targeting
- Partial exit strategies
- Profit attribution tracking
- Strategy stacking and rotation
- Trade rehearsal simulation

### Long-Term Investment Engine
- Fundamental analysis scoring
- Economic moat detection
- Money flow tracking
- CAGR simulation
- ESG filtering
- Megatrend overlay

### Political & Insider Trading Tracker
- Real-time congressional trade monitoring
- Insider trade overlays
- Disclosure delay tracking
- Alpha attribution

### Dashboards & UI
- Admin and user panels
- **🔴 NEW: Real-time WebSocket updates**
  - Live trade signals streaming
  - Real-time earnings and P&L updates
  - Instant notifications
  - Admin dashboard live analytics
- Profit-sharing logic
- Strength signal visualizations
- Trade journal interface
- Performance cards

### External Service Integration
- **🔴 NEW: Modular Connector Architecture**
  - Broker connectors (Alpaca, extendable)
  - Data provider connectors (Polygon.io, extendable)
  - Notification services (Email, Webhooks)
  - Circuit breaker pattern for resilience
  - Automatic retry with exponential backoff
  - Health monitoring and diagnostics
  - Factory pattern for easy extensibility

### Billing & Monetization
- Stripe integration
- Tiered subscription plans
- Profit-sharing calculator
- Enterprise licensing

### Security & Authentication
- JWT token-based authentication
- Role-based access control (RBAC)
- Bcrypt password hashing
- User management system
- Protected API endpoints
- Session management

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/JamieT18/Sentio-2.0.git
cd Sentio-2.0

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Optional: Install dashboard dependencies
cd dashboard
npm install
npm run build
cd ..

# Optional: Install SDKs
cd sdk/python && pip install -e .
cd ../javascript && npm install
cd ../..
```

## 🏗️ Architecture

```
sentio/
├── core/               # Core system configuration and logging
├── data/               # Market data integration
├── strategies/         # Trading strategies and voting engine
├── analysis/           # Technical and fundamental analysis
├── execution/          # Trade execution engine
├── risk/              # Risk management system
├── ai/                # AI and machine learning modules
├── longtermInvestment/ # Long-term investment engine
├── political/         # Political/insider trade tracking
├── auth/              # Authentication and security
├── ui/                # User interface and dashboards
├── billing/           # Billing and monetization
├── utils/             # Utility functions
└── tests/             # Test suite

# Additional modules:
├── social/             # Friends, groups, chat, leaderboard, referrals
├── notifications/      # Alerts, notifications, engagement
├── compliance/         # Compliance dashboard, audit logs
├── monitoring/         # Health checks, diagnostics, metrics
├── plugins/            # Extensible plugin system
```

## 🎯 Quick Start

### Basic Configuration

Create a `.env` file with your API keys:

```env
# Market Data
MARKET_DATA_API_KEY=your_alpaca_key
MARKET_DATA_API_SECRET=your_alpaca_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost/sentio

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Stripe
STRIPE_API_KEY=your_stripe_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# Security
SECRET_KEY=your_secret_key_here

# WebSocket
WEBSOCKET_SECRET=your_websocket_secret

# Community/Notifications
NOTIFICATION_API_KEY=your_notification_key

# Compliance
COMPLIANCE_API_KEY=your_compliance_key
```

### Running Strategies

```python
from sentio.strategies.tjr_strategy import TJRStrategy
from sentio.strategies.momentum_strategy import MomentumStrategy
from sentio.strategies.voting_engine import StrategyVotingEngine
from sentio.risk.risk_manager import RiskManager
import pandas as pd

# Initialize strategies
tjr = TJRStrategy(name="TJR", min_confidence=0.70)
momentum = MomentumStrategy(name="Momentum", min_confidence=0.65)

# Initialize voting engine
voting_engine = StrategyVotingEngine(
    min_confidence=0.65,
    min_strategies=2,
    consensus_threshold=0.6
)

# Initialize risk manager
risk_manager = RiskManager()

# Get market data (example)
# data = get_market_data("AAPL", timeframe="5min")

# Execute strategies
# tjr_signal = tjr.execute(data)
# momentum_signal = momentum.execute(data)

# Vote on signals
# result = voting_engine.vote([tjr_signal, momentum_signal])

# Assess risk
# risk_check = risk_manager.assess_trade_risk(
#     trade={'symbol': 'AAPL', 'size': 100, 'price': 150},
#     portfolio_value=100000,
#     current_exposure=20000
# )

# if result.final_signal != SignalType.HOLD and risk_check.approved:
#     # Execute trade
#     pass
```

### Authentication & Security

Sentio includes comprehensive security features:

```python
# Example: Using the authentication system
import requests

# 1. Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)
token = response.json()["access_token"]

# 2. Make authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Get trading signals
signals = requests.get(
    "http://localhost:8000/api/v1/dashboard/trade-signals?symbols=AAPL,GOOGL",
    headers=headers
)

# Get user profile
profile = requests.get(
    "http://localhost:8000/api/v1/auth/me",
    headers=headers
)
```

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change the default admin password immediately after installation!

For detailed security documentation, see [SECURITY_AUTHENTICATION.md](SECURITY_AUTHENTICATION.md).

### Technical Analysis

```python
from sentio.analysis.technical_analysis import TechnicalAnalysisEngine

# Initialize analysis engine
ta_engine = TechnicalAnalysisEngine()

# Perform comprehensive analysis
# analysis = ta_engine.analyze_comprehensive(data, symbol="AAPL")

# Access specific indicators
# print(f"RSI: {analysis['oscillators']['rsi']['value']}")
# print(f"Trend: {analysis['trend']['direction']}")
# print(f"Support: {analysis['support_resistance']['nearest_support']}")
```

### Running the API Server

Start the FastAPI server to access the REST API:

```bash
# Start the API server
python sentio/ui/api.py

# Or use uvicorn directly
uvicorn sentio.ui.api:app --host 0.0.0.0 --port 8000 --reload

# Start the React dashboard (optional)
cd dashboard
npm start
cd ..
```

The API will be available at:
- API Base: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Testing WebSocket Real-Time Updates

Test the WebSocket functionality using the included test page:

```bash
# 1. Start the API server
python sentio/ui/api.py

# 2. Open the WebSocket test page in your browser
# File: examples/websocket_test.html

# 3. Or use the Python demo
python examples/websocket_demo.py

# 4. Test with JavaScript SDK
node examples/analytics_integration_examples.js
```

WebSocket endpoints:
- `ws://localhost:8000/ws/trade-signals` - Real-time trade signals
- `ws://localhost:8000/ws/earnings` - Real-time earnings updates
- `ws://localhost:8000/ws/notifications` - Real-time notifications
- `ws://localhost:8000/ws/admin` - Admin dashboard updates

- `ws://localhost:8000/ws/community` - Community chat and Q&A
- `ws://localhost:8000/ws/alerts` - Real-time alerts and engagement

See [WEBSOCKET_INTEGRATION.md](WEBSOCKET_INTEGRATION.md) for detailed documentation.

## 🧪 Testing

Sentio includes a comprehensive test suite covering unit tests, integration tests, and API tests.

### Automated CI/CD
All code changes are automatically tested and validated via GitHub Actions. See `.github/workflows/ci.yml` for details.

### Quick Start

```bash
# Quick code quality validation (no dependencies required)
python validate_code.py

# Run all tests
pytest

# Run with coverage
pytest --cov=sentio --cov-report=html --cov-report=term

# Run specific test module
pytest sentio/tests/test_config.py
```

📖 **See [TESTING.md](TESTING.md) for comprehensive testing guide**

### Test Coverage

The project includes comprehensive unit tests for:
- Configuration management (`test_config.py`)
- Base strategy functionality (`test_base_strategy.py`)
- Logger module (`test_logger.py`)

- Billing & Monetization (`test_billing_integration.py`)
- Risk Management (`test_risk_manager.py`)
- Integrity & Health (`test_integrity.py`)
- Engagement & Social (`test_engagement.py`)

### Code Quality

All code is validated for:
- ✅ Zero syntax errors
- ✅ Pydantic v2 compatibility
- ✅ No wildcard imports
- ✅ No mutable default arguments

- ✅ Import organization, error handling, maintainability

## 📊 Strategy Overview

### TJR (Three Jump Rule) Strategy
Identifies three consecutive price movements with increasing volume, indicating strong momentum continuation.

### Momentum Strategy
Trades in the direction of strong momentum confirmed by ROC, RSI, MACD, and volume surge.

### Additional Strategies (In Development)
- Scalping Strategy
- Swing Trading Strategy
- Trend-Following Strategy
- Mean Reversion Strategy
- Breakout Strategy

- Arbitrage Strategy
- Profit Signals Strategy
- AI-Driven Meta Strategy

## 🛡️ Risk Management

The system includes comprehensive risk controls:

- **Position Sizing**: Maximum 5% of portfolio per position (configurable)
- **Stop-Loss**: Automatic 2% stop-loss on all positions
- **Drawdown Limits**: Daily 3% drawdown limit
- **Circuit Breakers**: System halts trading at 5% portfolio loss
- **Trade Health Scanning**: Continuous monitoring of open positions
- **Anomaly Detection**: Identifies unusual market conditions

## 🔧 Configuration

Configuration is managed through `sentio/core/config.py`. Key parameters:

```python
{
    "trading_mode": "hybrid",  # day_trading, long_term, hybrid
    "risk_level": "moderate",  # conservative, moderate, aggressive
    "max_position_size": 0.05,
    "min_confidence": 0.65,
    "circuit_breaker_threshold": 0.05
}
```

## 📈 Performance Metrics

The system tracks comprehensive performance metrics:
- Win rate
- Average return
- Sharpe ratio
- Maximum drawdown
- Total return
- Strategy-specific metrics

### 🚀 Performance Optimizations

Sentio includes comprehensive performance optimizations for production use:

- **Response Compression**: GZip middleware reduces bandwidth by 70%
- **Intelligent Caching**: Multi-tier caching with configurable TTL (75-85% hit rate)
- **Concurrent Processing**: Parallel symbol analysis with ThreadPoolExecutor
- **Database Pooling**: Optimized connection pooling (20 pool size, 40 overflow)
- **Batch Operations**: Efficient multi-symbol data fetching
- **React Optimization**: Component memoization with React.memo, useMemo, useCallback
- **Client-Side Caching**: Request deduplication and caching

**Performance Impact:**
- API response times: 60-80% faster (800ms → 150-300ms)
- Dashboard load: 50-60% faster (3-4s → 1-2s)
- Bandwidth usage: 70% reduction
- API call reduction: 85% with caching

📖 See [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) and [PERFORMANCE_SUMMARY.md](PERFORMANCE_SUMMARY.md) for detailed documentation.

## 🛠️ Developer Tools & SDK

Sentio provides comprehensive developer tools and SDKs for easy integration:

### Official SDKs

#### Python SDK
Full-featured Python client with type hints and comprehensive error handling:

```python
from sentio_sdk import SentioClient

# Initialize and login
client = SentioClient(base_url="http://localhost:8000")
client.login("admin", "admin123")

# Get trade signals
signals = client.get_trade_signals(["AAPL", "GOOGL", "MSFT"])
for signal in signals['signals']:
    print(f"{signal['symbol']}: {signal['signal']} ({signal['confidence']:.1%})")

# Load dashboard data
dashboard = client.load_dashboard_data("user_123", ["AAPL", "GOOGL"])
```

**Installation:** `cd sdk/python && pip install -e .`

# See [sdk/python/README.md](sdk/python/README.md) for full usage and advanced examples.

#### JavaScript/TypeScript SDK
Modern SDK for Browser and Node.js with full TypeScript support:

```typescript
import { SentioClient } from 'sentio-sdk';

const client = new SentioClient({ baseUrl: 'http://localhost:8000' });
await client.login('admin', 'admin123');

const signals = await client.getTradeSignals(['AAPL', 'GOOGL', 'MSFT']);
console.log(signals);
```

**Installation:** `npm install sentio-sdk` or copy `sdk/javascript/sentio-sdk.ts`

# See [sdk/javascript/README.md](sdk/javascript/README.md) for full usage and advanced examples.

### Developer CLI Tool

Command-line interface for testing and development:

```bash
# Check API health
./tools/sentio-cli.py health

# Login
./tools/sentio-cli.py login -u admin -p admin123

# Analyze a symbol
./tools/sentio-cli.py analyze AAPL --token YOUR_TOKEN

# Get trade signals
./tools/sentio-cli.py signals --symbols AAPL,GOOGL,MSFT --token YOUR_TOKEN

# Load dashboard
./tools/sentio-cli.py dashboard --user-id user_123 --token YOUR_TOKEN

# See [tools/README.md](tools/README.md) for all CLI commands and options.
```

### Postman Collection

Pre-built Postman collection with all 23 API endpoints:

```bash
# Generate collection
python tools/generate_postman.py

# Import postman_collection.json into Postman
```

### OpenAPI Specification

Generate OpenAPI 3.0 spec for use with code generators and documentation tools:

```bash
# Generate OpenAPI spec
python tools/generate_openapi.py

# Use with OpenAPI Generator
openapi-generator-cli generate -i openapi.json -g python -o generated/python
```

### Quick Start

See **[DEVELOPER_QUICKSTART.md](DEVELOPER_QUICKSTART.md)** for a complete getting started guide.

**Developer Resources:**
- **[sdk/README.md](sdk/README.md)** - SDK documentation and usage examples
- **[sdk/python/README.md](sdk/python/README.md)** - Python SDK guide
- **[sdk/javascript/README.md](sdk/javascript/README.md)** - JavaScript/TypeScript SDK guide
- **[tools/README.md](tools/README.md)** - Developer tools documentation
- **[CONNECTOR_INTEGRATION.md](CONNECTOR_INTEGRATION.md)** - External service connector integration guide
- **[examples/connector_integration_demo.py](examples/connector_integration_demo.py)** - Connector usage examples

- **[ANALYTICS_FEATURES.md](ANALYTICS_FEATURES.md)** - Analytics features and reporting
- **[ANALYTICS_IMPLEMENTATION_SUMMARY.md](ANALYTICS_IMPLEMENTATION_SUMMARY.md)** - Analytics implementation details
- **[ANALYTICS_USER_GUIDE.md](ANALYTICS_USER_GUIDE.md)** - Analytics user guide

## 📚 Documentation

Comprehensive documentation is available:

- **[API.md](API.md)** - Complete API reference with 23 endpoints documented
- **[DEVELOPER_QUICKSTART.md](DEVELOPER_QUICKSTART.md)** - ⭐ Quick start guide for developers
- **[CONNECTOR_INTEGRATION.md](CONNECTOR_INTEGRATION.md)** - 🔴 NEW: External service integration guide
- **[DASHBOARD_API.md](DASHBOARD_API.md)** - Dashboard-specific API documentation
- **[WEBSOCKET_INTEGRATION.md](WEBSOCKET_INTEGRATION.md)** - Real-time WebSocket integration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[TESTING.md](TESTING.md)** - Complete guide to testing the system
- **[CI_CD_DOCUMENTATION.md](CI_CD_DOCUMENTATION.md)** - CI/CD pipeline documentation
- **[CODE_QUALITY_IMPROVEMENTS.md](CODE_QUALITY_IMPROVEMENTS.md)** - Summary of code quality enhancements
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment instructions

## 🧪 Testing & Code Quality

Sentio has comprehensive automated testing and code quality validation:

### Automated Testing
- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: End-to-end tests for API, database, and workflows
- **Coverage Reporting**: Track code coverage with detailed reports
- **Multi-version Testing**: Tested on Python 3.9, 3.10, and 3.11

- **Integrity Tests**: Validate module imports and basic calls

### Code Quality Tools
- **Flake8**: PEP 8 style checking and linting
- **Pylint**: Advanced code analysis and quality metrics
- **MyPy**: Static type checking for type safety
- **Black**: Code formatting (optional)

- **validate_code.py**: Custom code validation script
# Run code quality checks
 python tools/validate_code.py
 flake8 sentio/
 pylint sentio/
 mypy sentio/ --config-file config/mypy.ini
3. ✅ Code coverage analysis
4. ✅ Package build verification

- 5. ✅ Automated deployment (optional)

### Running Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest sentio/tests/ -v

# Run with coverage
pytest sentio/tests/ --cov=sentio --cov-report=term-missing

# Run specific test categories
pytest sentio/tests/ -m "unit" -v
pytest sentio/tests/ -m "integration" -v

# Run code quality checks
python validate_code.py
flake8 sentio/
pylint sentio/
mypy sentio/ --config-file mypy.ini
```

See **[TESTING.md](TESTING.md)** for detailed testing guide and **[CI_CD_DOCUMENTATION.md](CI_CD_DOCUMENTATION.md)** for CI/CD pipeline details.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass and code quality checks succeed
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves substantial risk of loss. Past performance does not guarantee future results. Use at your own risk.

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: [Your contact information]

- Community chat: Join via dashboard for real-time support
- Suggestions: Submit via dashboard or GitHub issues

## 🗺️ Roadmap

See the [Project Board](https://github.com/JamieT18/Sentio-2.0/projects) for upcoming features and improvements.

- Upcoming: Mobile app, advanced analytics, social trading, strategy marketplace, neural network strategies, more brokers/data providers, paper trading competitions, enhanced compliance, and more.

---

**Built with ❤️ for intelligent trading**