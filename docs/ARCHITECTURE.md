# Sentio 2.0 Architecture Documentation

## System Overview

Sentio 2.0 is a production-ready, modular intelligent trading system that implements:
- Multi-strategy confidence-weighted voting
- Comprehensive risk management
- Advanced technical and fundamental analysis
- AI/machine learning capabilities
- Political and insider trade tracking
- Professional API and CLI interfaces
- Tiered subscription and billing system

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Sentio 2.0                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │     CLI      │  │   REST API   │  │  Web UI      │    │
│  │   Interface  │  │   (FastAPI)  │  │  (Future)    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│         ┌──────────────────▼─────────────────┐             │
│         │     Trading Engine (Core)          │             │
│         │  - Strategy Orchestration          │             │
│         │  - Execution Management            │             │
│         │  - Position Tracking               │             │
│         └──────────────────┬─────────────────┘             │
│                            │                                │
│    ┌───────────────────────┼───────────────────────┐       │
│    │                       │                       │       │
│    ▼                       ▼                       ▼       │
│ ┌─────────┐          ┌─────────┐           ┌─────────┐   │
│ │Strategy │          │  Risk   │           │  Data   │   │
│ │ Voting  │◄────────►│Manager  │◄─────────►│Provider │   │
│ │ Engine  │          │         │           │         │   │
│ └────┬────┘          └─────────┘           └─────────┘   │
│      │                                                     │
│      ▼                                                     │
│ ┌─────────────────────────────────┐                       │
│ │   Trading Strategies            │                       │
│ ├─────────────────────────────────┤                       │
│ │ • TJR (Three Jump Rule)         │                       │
│ │ • Momentum                      │                       │
│ │ • Mean Reversion                │                       │
│ │ • Breakout                      │                       │
│ │ • [Custom Strategies]           │                       │
│ └─────────────────────────────────┘                       │
│                                                             │
│ ┌─────────────────────────────────┐                       │
│ │   Analysis Engines              │                       │
│ ├─────────────────────────────────┤                       │
│ │ • Technical Analysis (15+ ind)  │                       │
│ │ • Fundamental Analysis          │                       │
│ │ • Sentiment Analysis            │                       │
│ └─────────────────────────────────┘                       │
│                                                             │
│ ┌─────────────────────────────────┐                       │
│ │   Intelligence Modules          │                       │
│ ├─────────────────────────────────┤                       │
│ │ • AI/RL Learning Engine         │                       │
│ │ • Insider Trade Tracker         │                       │
│ │ • Political Trade Monitor       │                       │
│ └─────────────────────────────────┘                       │
│                                                             │
│ ┌─────────────────────────────────┐                       │
│ │   Business Logic                │                       │
│ ├─────────────────────────────────┤                       │
│ │ • Subscription Management       │                       │
│ │ • Billing & Profit Sharing      │                       │
│ │ • User Authentication           │                       │
│ └─────────────────────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### Core (`sentio/core/`)
- **config.py**: Centralized configuration management with Pydantic models
- **logger.py**: Structured JSON logging with multiple handlers
- **cli.py**: Command-line interface with argparse

**Key Classes:**
- `SentioConfig`: Main configuration container
- `ConfigManager`: Singleton configuration manager
- `SentioLogger`: Logging system with file and console handlers

### Strategies (`sentio/strategies/`)
- **base.py**: Abstract base strategy class
- **tjr_strategy.py**: Three Jump Rule momentum strategy
- **momentum_strategy.py**: ROC/RSI/MACD momentum trading
- **mean_reversion_strategy.py**: Bollinger Bands reversion
- **breakout_strategy.py**: Range breakout with volume
- **voting_engine.py**: Confidence-weighted aggregation

**Key Classes:**
- `BaseStrategy`: Abstract strategy interface
- `TradingSignal`: Signal with confidence and metadata
- `StrategyVotingEngine`: Multi-strategy aggregator
- `VotingResult`: Aggregated decision output

### Risk Management (`sentio/risk/`)
- **risk_manager.py**: Multi-layered risk control system

**Key Classes:**
- `RiskManager`: Comprehensive risk assessment
- `RiskCheckResult`: Risk analysis output
- `CircuitBreakerState`: System safety states

**Features:**
- Adaptive position sizing
- Stop-loss/take-profit enforcement
- Circuit breakers (5% threshold)
- Daily drawdown monitoring (3% limit)
- Trade health scanning
- Portfolio exposure limits (20% max)

### Analysis (`sentio/analysis/`)
- **technical_analysis.py**: Technical indicator engine

**Key Classes:**
- `TechnicalAnalysisEngine`: 15+ indicators
- `SupportResistance`: S/R level detection
- `TrendAnalysis`: Trend direction and strength

**Indicators:**
- RSI, Stochastic, CCI (Oscillators)
- MACD, ADX, Moving Averages (Trend)
- Bollinger Bands, ATR
- Volume analysis, OBV
- Support/Resistance detection
- Confluence scoring

### Execution (`sentio/execution/`)
- **trading_engine.py**: Main trading orchestrator

**Key Classes:**
- `TradingEngine`: Multi-strategy coordinator
- `TradingMode`: Paper/Live/Backtest modes
- `OrderType`: Market/Limit/Stop orders

**Features:**
- Strategy orchestration
- Position management
- Order execution
- Performance tracking
- Risk integration

### Data (`sentio/data/`)
- **market_data.py**: Market data provider abstraction

**Key Classes:**
- `MarketDataProvider`: Abstract data interface
- `AlpacaDataProvider`: Alpaca API integration
- `MarketDataManager`: Caching and validation

**Features:**
- Multiple provider support
- Data caching (5min TTL)
- Quality validation
- Real-time quotes
- Historical OHLCV

### AI (`sentio/ai/`)
- **reinforcement_learning.py**: RL trading agent

**Key Classes:**
- `RLAgent`: Q-learning agent
- `TradingEnvironment`: Simulation environment
- `ReplayBuffer`: Experience replay (10K capacity)
- `AdaptiveLearningEngine`: Continuous learning

**Features:**
- Q-learning with epsilon-greedy
- Experience replay
- Adaptive learning from trades
- Action recommendation

### Long-Term Investment (`sentio/longtermInvestment/`)
- **fundamental_analysis.py**: Company fundamentals

**Key Classes:**
- `FundamentalAnalysisEngine`: Scoring system
- `FundamentalScore`: Multi-factor score
- `MoatType`: Economic moat types

**Features:**
- Value metrics (P/E, P/B, PEG)
- Growth analysis (CAGR)
- Profitability (ROE, ROA)
- Financial health (debt ratios)
- Moat detection (7 types)
- ESG scoring
- Target price estimation

### Political/Insider (`sentio/political/`)
- **insider_tracker.py**: Trade monitoring

**Key Classes:**
- `InsiderTracker`: Trade tracking system
- `InsiderTrade`: Individual trade record
- `TraderType`: Senator/Representative/Executive

**Features:**
- Congressional trade tracking
- Corporate insider monitoring
- Disclosure delay analysis
- Trade clustering detection
- Sentiment scoring
- Alpha attribution

### UI (`sentio/ui/`)
- **api.py**: FastAPI REST interface

**Endpoints:**
- `POST /api/v1/analyze`: Symbol analysis
- `POST /api/v1/trade`: Execute trade
- `GET /api/v1/positions`: Open positions
- `GET /api/v1/performance`: Metrics
- `GET /api/v1/strategies`: Strategy info
- `GET /api/v1/insider-trades/{symbol}`: Insider activity
- `GET /api/v1/fundamental/{symbol}`: Fundamental score

### Billing (`sentio/billing/`)
- **subscription_manager.py**: Subscription system

**Key Classes:**
- `SubscriptionManager`: Tier management
- `TierFeatures`: Feature definitions
- `Subscription`: User subscription

**Tiers:**
- Free: $0/mo, 1 trade, 2 strategies
- Basic: $49.99/mo, 3 trades, 4 strategies
- Professional: $199.99/mo, 10 trades, 8 strategies, 20% profit-sharing
- Enterprise: $999.99/mo, 50 trades, 20 strategies, 15% profit-sharing

### Utils (`sentio/utils/`)
- **helpers.py**: Utility functions

**Functions:**
- Currency/percentage formatting
- Return calculations
- Sharpe ratio, max drawdown
- Win rate, profit factor
- Market hours checking
- Data validation

## Data Flow

### 1. Analysis Pipeline
```
Market Data → Technical Analysis → Strategy Execution → Signal Generation
     ↓              ↓                      ↓                    ↓
  Caching    Indicators (15+)      Confidence Score    TradingSignal
```

### 2. Decision Pipeline
```
Multiple Signals → Voting Engine → Risk Assessment → Order Execution
       ↓               ↓                  ↓                ↓
  4+ Strategies  Weighted Vote     Risk Checks      Position Track
```

### 3. Learning Pipeline
```
Trade Outcome → Trade Memory → Experience Replay → Model Update
      ↓              ↓               ↓                  ↓
    P&L        Replay Buffer    Batch Learning    Q-Table Update
```

## Configuration System

### Environment Variables
```bash
# Market Data
MARKET_DATA_API_KEY=your_key
MARKET_DATA_API_SECRET=your_secret

# Database
DATABASE_URL=postgresql://user:pass@host/db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Stripe
STRIPE_API_KEY=your_stripe_key

# Security
SECRET_KEY=your_secret_key
```

### Configuration Hierarchy
1. Environment variables (highest priority)
2. .env file
3. config.json file
4. Default values (lowest priority)

## Safety & Risk Controls

### Multi-Layered Protection
1. **Position Level**
   - Max 5% per position
   - 2% stop-loss
   - 5% take-profit

2. **Portfolio Level**
   - Max 20% total exposure
   - 3% daily drawdown limit
   - Position correlation checks

3. **System Level**
   - Circuit breaker at 5% loss
   - Trade frequency limits
   - Anomaly detection

4. **Validation**
   - Data quality checks
   - Parameter validation
   - Trade health scanning

## Performance Considerations

### Caching Strategy
- Market data: 5-minute TTL
- Analysis results: Symbol-specific cache
- Configuration: In-memory singleton

### Scalability
- Async-ready with FastAPI
- Stateless API design
- Database connection pooling
- Redis for distributed caching

### Monitoring
- Structured JSON logging
- Performance metrics tracking
- Trade history recording
- Error tracking

## Extension Points

### Adding New Strategies
1. Inherit from `BaseStrategy`
2. Implement `analyze()`, `get_signal()`, `calculate_confidence()`
3. Register in trading engine
4. Configure parameters

### Adding New Indicators
1. Add to `TechnicalAnalysisEngine`
2. Implement calculation method
3. Add to `analyze_comprehensive()`
4. Update confluence scoring

### Adding New Data Providers
1. Inherit from `MarketDataProvider`
2. Implement required methods
3. Register in `MarketDataManager`
4. Configure credentials

## Testing Strategy

### Unit Tests
- Strategy logic
- Risk calculations
- Indicator computations
- Configuration validation

### Integration Tests
- End-to-end analysis pipeline
- Order execution flow
- API endpoints
- Database operations

### Backtesting
- Historical data replay
- Performance validation
- Strategy comparison
- Risk metric verification

## Deployment Architecture

### Recommended Setup
```
┌─────────────┐
│   Nginx     │ (Reverse Proxy)
│   + SSL     │
└──────┬──────┘
       │
┌──────▼──────┐
│  FastAPI    │ (API Server)
│  + Uvicorn  │ (4 workers)
└──────┬──────┘
       │
┌──────▼──────┐
│  PostgreSQL │ (Persistence)
│  + Redis    │ (Cache)
└─────────────┘
```

### Scaling Considerations
- Horizontal: Multiple API instances
- Vertical: Worker processes
- Database: Read replicas
- Cache: Redis cluster

## Security

### Authentication
- JWT tokens
- API key rotation
- Rate limiting

### Data Protection
- Encrypted API keys
- Secure credential storage
- HTTPS enforcement

### Compliance
- Trade logging
- Audit trails
- Data retention policies

## Monitoring & Observability

### Metrics
- Request latency
- Trade execution times
- Strategy performance
- System resource usage

### Logging
- Structured JSON logs
- Multiple log levels
- Separate error logs
- Trade journal

### Alerts
- Circuit breaker trips
- High risk situations
- System errors
- Performance degradation

## Future Enhancements

### Planned Features
- Neural network strategies
- Multi-agent systems
- Real-time sentiment analysis
- Web dashboard UI
- Mobile app
- Advanced backtesting
- Paper trading competitions

### Integration Roadmap
- Additional brokers
- More data providers
- Social trading features
- Community marketplace
- Strategy backtesting marketplace

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Status**: Production Ready (Framework Complete)
