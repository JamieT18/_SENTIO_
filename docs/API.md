# Sentio 2.0 API Documentation

> **Complete API Reference for Sentio 2.0 Trading System**

This document provides comprehensive documentation for all API endpoints in the Sentio 2.0 Trading System. The API is built with FastAPI and provides RESTful endpoints for trading operations, analysis, monitoring, and subscription management.

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [General Endpoints](#general-endpoints)
  - [Trading Operations](#trading-operations)
  - [Analysis & Intelligence](#analysis--intelligence)
  - [Dashboard Endpoints](#dashboard-endpoints)
  - [Subscription & Billing](#subscription--billing)
- [Request/Response Models](#requestresponse-models)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)
- [Integration Guide](#integration-guide)
- [Best Practices](#best-practices)

---

## Getting Started

### Base URL

```
http://localhost:8000
```

For production deployments, replace with your actual domain.

### API Version

Current version: `v1`

All endpoints are prefixed with `/api/v1/` except for root and health endpoints.

### Starting the API Server

```bash
# Method 1: Direct execution
python sentio/ui/api.py

# Method 2: Using uvicorn
uvicorn sentio.ui.api:app --reload --host 0.0.0.0 --port 8000

# Method 3: With custom configuration
uvicorn sentio.ui.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Authentication

Most endpoints require authentication via Bearer token in the Authorization header.

### Authentication Header

```http
Authorization: Bearer <your_jwt_token>
```

### Public Endpoints (No Authentication Required)

- `GET /` - Root endpoint
- `GET /api/v1/health` - Health check
- `GET /api/v1/subscription/pricing` - Pricing information

### Protected Endpoints

All other endpoints require a valid JWT token.

### Example Authentication

```bash
# Using curl
curl -H "Authorization: Bearer your_token_here" \
     http://localhost:8000/api/v1/status

# Using Python requests
import requests

headers = {"Authorization": "Bearer your_token_here"}
response = requests.get("http://localhost:8000/api/v1/status", headers=headers)
```

**Note**: In the current implementation, token verification is a placeholder. In production, implement proper JWT validation with user authentication and role-based access control.

---

## API Endpoints

### General Endpoints

#### 1. Root Endpoint

**GET** `/`

Get API service information and status.

**Authentication**: None required

**Response**:
```json
{
  "service": "Sentio 2.0 Trading API",
  "version": "2.0.0",
  "status": "operational"
}
```

**Example**:
```bash
curl http://localhost:8000/
```

---

#### 2. Health Check

**GET** `/api/v1/health`

Check API health status.

**Authentication**: None required

**Response**:
```json
{
  "status": "healthy"
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/health
```

---

#### 3. System Status

**GET** `/api/v1/status`

Get comprehensive system status including trading engine state.

**Authentication**: Required

**Response**:
```json
{
  "status": "operational",
  "mode": "day_trading",
  "active_strategies": 4,
  "open_positions": 3,
  "portfolio_value": 105000.50,
  "daily_pnl": 1250.75
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/status
```

---

### Trading Operations

#### 4. Analyze Symbol

**POST** `/api/v1/analyze`

Perform comprehensive multi-strategy analysis on a trading symbol.

**Authentication**: Required

**Request Body**:
```json
{
  "symbol": "AAPL",
  "timeframe": "5min"
}
```

**Parameters**:
- `symbol` (string, required): Trading symbol (e.g., "AAPL", "GOOGL")
- `timeframe` (string, optional): Data timeframe, default "5min"

**Response**:
```json
{
  "symbol": "AAPL",
  "timestamp": "2024-10-05T10:30:00",
  "voting_result": {
    "final_signal": "buy",
    "confidence": 0.85,
    "consensus_strength": 0.92,
    "votes": [
      {
        "strategy": "TJR",
        "signal": "buy",
        "confidence": 0.88
      },
      {
        "strategy": "Momentum",
        "signal": "buy",
        "confidence": 0.82
      }
    ]
  },
  "technical_analysis": {
    "rsi": 65.5,
    "macd": {
      "value": 1.2,
      "signal": 0.8,
      "histogram": 0.4
    },
    "trend": "bullish"
  },
  "insider_activity": {
    "recent_trades": 5,
    "net_sentiment": "positive"
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL", "timeframe": "5min"}'
```

```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
data = {"symbol": "AAPL", "timeframe": "5min"}

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    headers=headers,
    json=data
)
print(response.json())
```

---

#### 5. Execute Trade

**POST** `/api/v1/trade`

Execute a trade based on manual input or strategy recommendation.

**Authentication**: Required

**Request Body**:
```json
{
  "symbol": "AAPL",
  "action": "buy",
  "quantity": 100
}
```

**Parameters**:
- `symbol` (string, required): Trading symbol
- `action` (string, required): Trade action - "buy", "sell", or "close"
- `quantity` (number, optional): Number of shares/contracts

**Response** (Success):
```json
{
  "status": "success",
  "message": "Trade executed for AAPL",
  "voting_result": {
    "final_signal": "buy",
    "confidence": 0.85
  }
}
```

**Response** (Warning - Action conflicts with recommendation):
```json
{
  "status": "warning",
  "message": "Manual action conflicts with strategy recommendation: sell",
  "recommendation": {
    "final_signal": "sell",
    "confidence": 0.75
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/trade \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL", "action": "buy", "quantity": 100}'
```

---

#### 6. Get Open Positions

**GET** `/api/v1/positions`

Retrieve all currently open trading positions.

**Authentication**: Required

**Response**:
```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "entry_price": 150.50,
      "current_price": 152.00,
      "pnl": 150.00,
      "pnl_pct": 1.0,
      "timestamp": "2024-10-05T09:00:00"
    },
    {
      "symbol": "GOOGL",
      "quantity": 50,
      "entry_price": 140.00,
      "current_price": 141.50,
      "pnl": 75.00,
      "pnl_pct": 1.07,
      "timestamp": "2024-10-05T09:30:00"
    }
  ],
  "count": 2
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/positions
```

---

#### 7. Get Performance Metrics

**GET** `/api/v1/performance`

Get comprehensive trading performance metrics.

**Authentication**: Required

**Response**:
```json
{
  "portfolio_value": 105000.50,
  "total_return": 5000.50,
  "total_return_pct": 5.0,
  "daily_pnl": 250.50,
  "total_trades": 150,
  "wins": 100,
  "losses": 50,
  "win_rate": 0.67,
  "open_positions": 3,
  "sharpe_ratio": 1.85,
  "max_drawdown": 0.025,
  "average_win": 75.50,
  "average_loss": 35.25
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/performance
```

---

### Strategy Management

#### 8. Get Strategies

**GET** `/api/v1/strategies`

Get information about all available trading strategies and their performance.

**Authentication**: Required

**Response**:
```json
[
  {
    "name": "TJR",
    "type": "momentum",
    "enabled": true,
    "timeframe": "5min",
    "min_confidence": 0.70,
    "performance": {
      "total_trades": 45,
      "win_rate": 0.72,
      "avg_return": 0.015
    }
  },
  {
    "name": "Momentum",
    "type": "momentum",
    "enabled": true,
    "timeframe": "5min",
    "min_confidence": 0.65,
    "performance": {
      "total_trades": 38,
      "win_rate": 0.68,
      "avg_return": 0.012
    }
  },
  {
    "name": "MeanReversion",
    "type": "mean_reversion",
    "enabled": true,
    "timeframe": "15min",
    "min_confidence": 0.65,
    "performance": {
      "total_trades": 52,
      "win_rate": 0.65,
      "avg_return": 0.010
    }
  },
  {
    "name": "Breakout",
    "type": "breakout",
    "enabled": false,
    "timeframe": "5min",
    "min_confidence": 0.70,
    "performance": {
      "total_trades": 20,
      "win_rate": 0.70,
      "avg_return": 0.018
    }
  }
]
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/strategies
```

---

#### 9. Toggle Strategy

**POST** `/api/v1/strategies/{strategy_name}/toggle`

Enable or disable a specific trading strategy.

**Authentication**: Required

**Path Parameters**:
- `strategy_name` (string, required): Name of the strategy (e.g., "TJR", "Momentum")

**Response**:
```json
{
  "strategy": "TJR",
  "enabled": false
}
```

**Example**:
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/strategies/TJR/toggle
```

---

### Analysis & Intelligence

#### 10. Get Insider Trades for Symbol

**GET** `/api/v1/insider-trades/{symbol}`

Get insider trading activity analysis for a specific symbol.

**Authentication**: Required

**Path Parameters**:
- `symbol` (string, required): Trading symbol

**Response**:
```json
{
  "symbol": "AAPL",
  "recent_trades": [
    {
      "insider_name": "Timothy Cook",
      "title": "CEO",
      "transaction_type": "Purchase",
      "shares": 50000,
      "price": 150.00,
      "value": 7500000,
      "date": "2024-10-01"
    }
  ],
  "summary": {
    "total_buys": 3,
    "total_sells": 1,
    "net_sentiment": "positive",
    "total_value": 15000000
  },
  "analysis": {
    "insider_confidence": "high",
    "trend": "bullish"
  }
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/insider-trades/AAPL
```

---

#### 11. Get Top Traded Symbols by Insiders

**GET** `/api/v1/insider-trades/top`

Get the most traded symbols by insiders over a specified period.

**Authentication**: Required

**Query Parameters**:
- `days` (integer, optional): Number of days to look back (default: 30)

**Response**:
```json
[
  {
    "symbol": "AAPL",
    "total_transactions": 15,
    "net_buying": 8,
    "total_value": 50000000,
    "sentiment": "positive"
  },
  {
    "symbol": "MSFT",
    "total_transactions": 12,
    "net_buying": 7,
    "total_value": 35000000,
    "sentiment": "positive"
  }
]
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/insider-trades/top?days=30"
```

---

#### 12. Get Fundamental Analysis

**GET** `/api/v1/fundamental/{symbol}`

Get fundamental analysis for long-term investment evaluation.

**Authentication**: Required

**Path Parameters**:
- `symbol` (string, required): Trading symbol

**Response**:
```json
{
  "symbol": "AAPL",
  "overall_score": 85.5,
  "recommendation": "strong_buy",
  "target_price": 175.00,
  "scores": {
    "value": 78.0,
    "growth": 92.0,
    "profitability": 88.0,
    "financial_health": 85.0,
    "moat": 90.0,
    "management": 87.0,
    "esg": 82.0
  },
  "timestamp": "2024-10-05T10:30:00"
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/fundamental/AAPL
```

---

### Dashboard Endpoints

#### 13. Trade Signals Summary

**GET** `/api/v1/dashboard/trade-signals`

Get aggregated trade signals for multiple symbols for dashboard display.

**Authentication**: Required

**Query Parameters**:
- `symbols` (string, optional): Comma-separated list of symbols (default: "AAPL,GOOGL,MSFT,TSLA")

**Response**:
```json
{
  "signals": [
    {
      "symbol": "AAPL",
      "signal": "buy",
      "confidence": 0.85,
      "consensus_strength": 0.92,
      "timestamp": "2024-10-05T10:30:00"
    },
    {
      "symbol": "GOOGL",
      "signal": "hold",
      "confidence": 0.55,
      "consensus_strength": 0.60,
      "timestamp": "2024-10-05T10:30:00"
    },
    {
      "symbol": "MSFT",
      "signal": "buy",
      "confidence": 0.78,
      "consensus_strength": 0.85,
      "timestamp": "2024-10-05T10:30:00"
    },
    {
      "symbol": "TSLA",
      "signal": "sell",
      "confidence": 0.72,
      "consensus_strength": 0.80,
      "timestamp": "2024-10-05T10:30:00"
    }
  ],
  "count": 4,
  "timestamp": "2024-10-05T10:30:00"
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/dashboard/trade-signals?symbols=AAPL,GOOGL,MSFT"
```

---

#### 14. Earnings Summary

**GET** `/api/v1/dashboard/earnings`

Get comprehensive earnings and performance summary for a user's dashboard.

**Authentication**: Required

**Query Parameters**:
- `user_id` (string, required): User identifier

**Response**:
```json
{
  "user_id": "user_123",
  "portfolio_value": 105000.00,
  "total_return": 5000.00,
  "total_return_pct": 5.0,
  "daily_pnl": 250.50,
  "total_trades": 45,
  "win_rate": 0.67,
  "profit_sharing": {
    "total_shared": 1000.00,
    "rate": 0.20,
    "enabled": true
  },
  "timestamp": "2024-10-05T10:30:00"
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/dashboard/earnings?user_id=user_123"
```

---

#### 15. AI Trade Summary

**GET** `/api/v1/dashboard/ai-summary`

Get AI-generated summary of trading recommendations.

**Authentication**: Required

**Query Parameters**:
- `symbol` (string, optional): Symbol to analyze. If omitted, returns general market summary

**Response (with symbol)**:
```json
{
  "symbol": "AAPL",
  "recommendation": "buy",
  "confidence": 0.85,
  "reasoning": "Based on 4 strategy votes, the system recommends BUY with 85.0% confidence. Consensus strength: 92.0%.",
  "key_factors": [
    "Strategy consensus: 92.0%",
    "Signal confidence: 85.0%",
    "Active strategies: 4"
  ],
  "timestamp": "2024-10-05T10:30:00"
}
```

**Response (without symbol - general summary)**:
```json
{
  "market_overview": "general",
  "portfolio_status": "active",
  "summary": "Portfolio is up $250.50 today. 3 positions open. Win rate: 67.0%.",
  "key_metrics": {
    "daily_pnl": 250.50,
    "open_positions": 3,
    "win_rate": 0.67,
    "total_return_pct": 5.0
  },
  "timestamp": "2024-10-05T10:30:00"
}
```

**Example**:
```bash
# Get symbol-specific summary
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/dashboard/ai-summary?symbol=AAPL"

# Get general market summary
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/dashboard/ai-summary"
```

---

#### 16. Strength Signal

**GET** `/api/v1/dashboard/strength-signal`

Get market strength indicators for a symbol.

**Authentication**: Required

**Query Parameters**:
- `symbol` (string, required): Trading symbol

**Response**:
```json
{
  "symbol": "AAPL",
  "strength_score": 75.5,
  "signal": "bullish",
  "components": {
    "trend_strength": 80,
    "momentum": 75,
    "volume": 70,
    "volatility": 77
  },
  "timestamp": "2024-10-05T10:30:00"
}
```

**Strength Signals**:
- `strong_bullish`: strength_score >= 70
- `bullish`: strength_score >= 50
- `neutral`: strength_score >= 30
- `bearish`: strength_score >= 10
- `strong_bearish`: strength_score < 10

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/dashboard/strength-signal?symbol=AAPL"
```

---

#### 17. Get Trade Journal Entries

**GET** `/api/v1/dashboard/trade-journal`

Retrieve trade journal entries for a user.

**Authentication**: Required

**Query Parameters**:
- `user_id` (string, required): User identifier
- `limit` (integer, optional): Maximum entries to return (default: 50)

**Response**:
```json
{
  "user_id": "user_123",
  "entries": [
    {
      "symbol": "AAPL",
      "action": "long",
      "quantity": 10,
      "entry_price": 150.00,
      "exit_price": 155.00,
      "pnl": 50.00,
      "timestamp": "2024-10-05T10:30:00",
      "notes": "Strong momentum signal"
    },
    {
      "symbol": "GOOGL",
      "action": "short",
      "quantity": 5,
      "entry_price": 140.00,
      "exit_price": 138.00,
      "pnl": 10.00,
      "timestamp": "2024-10-04T14:20:00",
      "notes": "Breakout strategy"
    }
  ],
  "count": 25,
  "timestamp": "2024-10-05T10:30:00"
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/dashboard/trade-journal?user_id=user_123&limit=20"
```

---

#### 18. Add Trade Journal Entry

**POST** `/api/v1/dashboard/trade-journal`

Add a manual trade journal entry.

**Authentication**: Required

**Query Parameters**:
- `user_id` (string, required): User identifier

**Request Body**:
```json
{
  "symbol": "AAPL",
  "action": "buy",
  "quantity": 10,
  "price": 150.00,
  "notes": "Entry on breakout",
  "tags": ["breakout", "momentum"]
}
```

**Response**:
```json
{
  "status": "success",
  "entry": {
    "user_id": "user_123",
    "symbol": "AAPL",
    "action": "buy",
    "quantity": 10,
    "price": 150.00,
    "notes": "Entry on breakout",
    "tags": ["breakout", "momentum"],
    "timestamp": "2024-10-05T10:30:00"
  }
}
```

**Example**:
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/dashboard/trade-journal?user_id=user_123" \
     -d '{
       "symbol": "AAPL",
       "action": "buy",
       "quantity": 10,
       "price": 150.00,
       "notes": "Entry on breakout",
       "tags": ["breakout", "momentum"]
     }'
```

---

#### 19. Performance Cards

**GET** `/api/v1/dashboard/performance-cards`

Get performance metrics formatted as dashboard cards.

**Authentication**: Required

**Query Parameters**:
- `user_id` (string, required): User identifier

**Response**:
```json
{
  "user_id": "user_123",
  "cards": [
    {
      "id": "portfolio_value",
      "title": "Portfolio Value",
      "value": "$105,000.00",
      "change": 5.0,
      "change_label": "+5.00%",
      "trend": "up"
    },
    {
      "id": "daily_pnl",
      "title": "Daily P&L",
      "value": "$250.50",
      "change": 250.50,
      "change_label": "+$250.50",
      "trend": "up"
    },
    {
      "id": "win_rate",
      "title": "Win Rate",
      "value": "67.0%",
      "subtitle": "30W / 15L"
    },
    {
      "id": "total_trades",
      "title": "Total Trades",
      "value": "45",
      "subtitle": "3 open"
    },
    {
      "id": "subscription",
      "title": "Subscription Tier",
      "value": "Professional",
      "subtitle": "Active"
    }
  ],
  "timestamp": "2024-10-05T10:30:00"
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/dashboard/performance-cards?user_id=user_123"
```

---

### Subscription & Billing

#### 20. Get Pricing Information

**GET** `/api/v1/subscription/pricing`

Get pricing details for all subscription tiers.

**Authentication**: None required (public endpoint)

**Response**:
```json
{
  "tiers": [
    {
      "tier": "free",
      "price": 0.00,
      "features": {
        "max_concurrent_trades": 1,
        "max_strategies": 2,
        "day_trading": false,
        "api_access": false,
        "profit_sharing_rate": 0.0
      }
    },
    {
      "tier": "basic",
      "price": 49.99,
      "features": {
        "max_concurrent_trades": 3,
        "max_strategies": 4,
        "day_trading": false,
        "api_access": true,
        "profit_sharing_rate": 0.0
      }
    },
    {
      "tier": "professional",
      "price": 199.99,
      "features": {
        "max_concurrent_trades": 10,
        "max_strategies": 8,
        "day_trading": true,
        "api_access": true,
        "profit_sharing_rate": 20.0
      }
    },
    {
      "tier": "enterprise",
      "price": 999.99,
      "features": {
        "max_concurrent_trades": -1,
        "max_strategies": -1,
        "day_trading": true,
        "api_access": true,
        "profit_sharing_rate": 15.0
      }
    }
  ],
  "timestamp": "2024-10-05T10:30:00"
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/subscription/pricing
```

---

#### 21. Get User Subscription

**GET** `/api/v1/subscription/{user_id}`

Get detailed subscription information for a user.

**Authentication**: Required

**Path Parameters**:
- `user_id` (string, required): User identifier

**Response**:
```json
{
  "user_id": "user_123",
  "tier": "professional",
  "status": "active",
  "start_date": "2024-01-01T00:00:00",
  "profit_sharing": {
    "balance": 150.00,
    "total_shared": 1500.00,
    "rate": 0.20
  },
  "features": {
    "max_concurrent_trades": 10,
    "max_strategies": 8,
    "day_trading": true,
    "api_access": true,
    "advanced_analytics": true
  }
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/subscription/user_123
```

---

#### 22. Calculate Profit Sharing

**POST** `/api/v1/subscription/profit-sharing/calculate`

Calculate profit-sharing amount for a trading profit.

**Authentication**: Required

**Request Body**:
```json
{
  "user_id": "user_123",
  "trading_profit": 1000.00
}
```

**Response**:
```json
{
  "user_id": "user_123",
  "trading_profit": 1000.00,
  "sharing_amount": 200.00,
  "profit_sharing_balance": 200.00,
  "timestamp": "2024-10-05T10:30:00"
}
```

**Profit Sharing Rates by Tier**:
- FREE: 0% (disabled)
- BASIC: 0% (disabled)
- PROFESSIONAL: 20%
- ENTERPRISE: 15%

**Example**:
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/subscription/profit-sharing/calculate \
     -d '{"user_id": "user_123", "trading_profit": 1000.00}'
```

---

#### 23. Get Profit Sharing Balance

**GET** `/api/v1/subscription/profit-sharing/{user_id}`

Get user's current profit-sharing balance and configuration.

**Authentication**: Required

**Path Parameters**:
- `user_id` (string, required): User identifier

**Response**:
```json
{
  "user_id": "user_123",
  "balance": 200.00,
  "total_shared": 2000.00,
  "rate": 0.20,
  "enabled": true,
  "timestamp": "2024-10-05T10:30:00"
}
```

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/subscription/profit-sharing/user_123
```

---

## Request/Response Models

### AnalysisRequest

```python
{
  "symbol": "string",      # Required: Trading symbol
  "timeframe": "string"    # Optional: Default "5min"
}
```

### TradeRequest

```python
{
  "symbol": "string",      # Required: Trading symbol
  "action": "string",      # Required: "buy", "sell", or "close"
  "quantity": float        # Optional: Number of shares
}
```

### TradeJournalEntry

```python
{
  "symbol": "string",      # Required: Trading symbol
  "action": "string",      # Required: Trade action
  "quantity": float,       # Required: Number of shares
  "price": float,          # Required: Trade price
  "notes": "string",       # Optional: Additional notes
  "tags": ["string"]       # Optional: Array of tags
}
```

### ProfitSharingRequest

```python
{
  "user_id": "string",     # Required: User identifier
  "trading_profit": float  # Required: Profit amount
}
```

### SystemStatus

```python
{
  "status": "string",           # System status
  "mode": "string",             # Trading mode
  "active_strategies": int,     # Number of active strategies
  "open_positions": int,        # Number of open positions
  "portfolio_value": float,     # Current portfolio value
  "daily_pnl": float           # Daily profit/loss
}
```

---

## Error Handling

### Standard Error Response

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource successfully created
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

### Common Error Scenarios

#### 401 Unauthorized

```bash
curl http://localhost:8000/api/v1/status
```

Response:
```json
{
  "detail": "Not authenticated"
}
```

#### 404 Not Found

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/subscription/nonexistent_user
```

Response:
```json
{
  "detail": "Subscription not found"
}
```

#### 500 Internal Server Error

```json
{
  "detail": "Analysis error for INVALID_SYMBOL: Symbol not found"
}
```

---

## Usage Examples

### Python Integration

#### Basic Setup

```python
import requests
from typing import Dict, Any

class SentioAPI:
    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        self.base_url = base_url
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def analyze_symbol(self, symbol: str, timeframe: str = "5min") -> Dict[str, Any]:
        """Analyze a trading symbol"""
        url = f"{self.base_url}/api/v1/analyze"
        data = {"symbol": symbol, "timeframe": timeframe}
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_positions(self) -> Dict[str, Any]:
        """Get open positions"""
        url = f"{self.base_url}/api/v1/positions"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def execute_trade(self, symbol: str, action: str, quantity: float = None) -> Dict[str, Any]:
        """Execute a trade"""
        url = f"{self.base_url}/api/v1/trade"
        data = {"symbol": symbol, "action": action}
        if quantity:
            data["quantity"] = quantity
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Usage
api = SentioAPI(token="your_token_here")

# Analyze a symbol
analysis = api.analyze_symbol("AAPL")
print(f"Signal: {analysis['voting_result']['final_signal']}")
print(f"Confidence: {analysis['voting_result']['confidence']}")

# Get positions
positions = api.get_positions()
print(f"Open positions: {positions['count']}")

# Execute trade
result = api.execute_trade("AAPL", "buy", quantity=100)
print(f"Trade status: {result['status']}")
```

#### Dashboard Integration

```python
def load_dashboard_data(api: SentioAPI, user_id: str):
    """Load all dashboard data"""
    
    # Get performance cards
    cards = api.get(f"/api/v1/dashboard/performance-cards?user_id={user_id}")
    
    # Get trade signals
    signals = api.get("/api/v1/dashboard/trade-signals?symbols=AAPL,GOOGL,MSFT")
    
    # Get earnings summary
    earnings = api.get(f"/api/v1/dashboard/earnings?user_id={user_id}")
    
    # Get AI summary
    ai_summary = api.get("/api/v1/dashboard/ai-summary")
    
    return {
        "cards": cards,
        "signals": signals,
        "earnings": earnings,
        "ai_summary": ai_summary
    }
```

### JavaScript/TypeScript Integration

```typescript
class SentioAPI {
  private baseUrl: string;
  private token: string;

  constructor(baseUrl: string = 'http://localhost:8000', token?: string) {
    this.baseUrl = baseUrl;
    this.token = token || '';
  }

  private async request(
    method: string,
    endpoint: string,
    data?: any
  ): Promise<any> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config: RequestInit = {
      method,
      headers,
    };

    if (data) {
      config.body = JSON.stringify(data);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  }

  async analyzeSymbol(symbol: string, timeframe: string = '5min') {
    return this.request('POST', '/api/v1/analyze', { symbol, timeframe });
  }

  async getTradeSignals(symbols?: string[]) {
    const params = symbols ? `?symbols=${symbols.join(',)}` : '';
    return this.request('GET', `/api/v1/dashboard/trade-signals${params}`);
  }

  async getPerformanceCards(userId: string) {
    return this.request('GET', `/api/v1/dashboard/performance-cards?user_id=${userId}`);
  }

  async executeTrade(symbol: string, action: string, quantity?: number) {
    return this.request('POST', '/api/v1/trade', { symbol, action, quantity });
  }
}

// Usage
const api = new SentioAPI('http://localhost:8000', 'your_token_here');

// Analyze symbol
const analysis = await api.analyzeSymbol('AAPL');
console.log('Signal:', analysis.voting_result.final_signal);

// Get trade signals
const signals = await api.getTradeSignals(['AAPL', 'GOOGL', 'MSFT']);
console.log('Signals:', signals.signals);
```

### cURL Examples

#### Complete Trading Workflow

```bash
# 1. Check system health
curl http://localhost:8000/api/v1/health

# 2. Get system status
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/status

# 3. Analyze a symbol
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/analyze \
     -d '{"symbol": "AAPL", "timeframe": "5min"}'

# 4. Check active strategies
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/strategies

# 5. Execute trade
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/trade \
     -d '{"symbol": "AAPL", "action": "buy", "quantity": 100}'

# 6. Check positions
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/positions

# 7. Get performance metrics
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/performance
```

---

## Integration Guide

### Frontend Dashboard Integration

1. **Authentication Flow**
   - Obtain JWT token from authentication service
   - Store token securely (e.g., in httpOnly cookies or secure storage)
   - Include token in all API requests

2. **Dashboard Load Sequence**
   ```
   1. GET /api/v1/dashboard/performance-cards
   2. GET /api/v1/dashboard/trade-signals
   3. GET /api/v1/dashboard/earnings
   4. GET /api/v1/dashboard/ai-summary
   ```

3. **Real-time Updates**
   - Poll endpoints at appropriate intervals (30-60 seconds)
   - Consider implementing WebSocket for real-time updates (future enhancement)

4. **Error Handling**
   - Implement retry logic for network failures
   - Handle 401 errors by refreshing authentication
   - Display user-friendly error messages

### Backend Service Integration

1. **Service-to-Service Communication**
   - Use service accounts with dedicated tokens
   - Implement proper timeout and retry policies
   - Log all API interactions for debugging

2. **Batch Operations**
   - For multiple symbol analysis, use the trade-signals endpoint
   - Implement rate limiting to avoid overwhelming the API

3. **Data Persistence**
   - Store critical data (positions, trades) in your database
   - Use API responses to update cached data
   - Implement proper error recovery mechanisms

---

## Best Practices

### 1. Authentication

- **Never** expose your JWT tokens in client-side code or version control
- Implement token refresh mechanisms for long-running sessions
- Use environment variables for sensitive configuration
- Rotate tokens regularly in production

### 2. Rate Limiting

- Implement client-side rate limiting to avoid overwhelming the API
- Cache responses where appropriate (30-60 seconds for market data)
- Use batch endpoints (like trade-signals) instead of multiple individual requests

### 3. Error Handling

```python
import time
from requests.exceptions import RequestException

def api_call_with_retry(func, max_retries=3, backoff=2):
    """Retry API calls with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff ** attempt
            print(f"Request failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
```

### 4. Performance Optimization

- Use connection pooling for multiple requests
- Implement caching for frequently accessed, slowly changing data
- Compress request/response bodies for large payloads
- Use async/await for concurrent API calls

### 5. Security

- Always use HTTPS in production
- Validate and sanitize all input data
- Implement proper CORS policies
- Use rate limiting to prevent abuse
- Monitor for suspicious activity

### 6. Testing

```python
import pytest
from unittest.mock import Mock, patch

def test_analyze_symbol():
    """Test symbol analysis endpoint"""
    api = SentioAPI(token="test_token")
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            'symbol': 'AAPL',
            'voting_result': {
                'final_signal': 'buy',
                'confidence': 0.85
            }
        }
        
        result = api.analyze_symbol('AAPL')
        
        assert result['symbol'] == 'AAPL'
        assert result['voting_result']['final_signal'] == 'buy'
        assert result['voting_result']['confidence'] == 0.85
```

### 7. Monitoring

- Log all API requests and responses
- Monitor response times and error rates
- Set up alerts for critical failures
- Track API usage patterns

---

## Profit Sharing System

### How It Works

1. **Tier-Based Rates**
   - FREE: 0% (disabled)
   - BASIC: 0% (disabled)
   - PROFESSIONAL: 20%
   - ENTERPRISE: 15%

2. **Calculation Flow**
   ```
   User executes profitable trade
   → System calculates profit-sharing fee based on tier
   → Fee added to user's profit_sharing_balance
   → Balance charged during monthly billing
   → Only positive profits incur fees (losses don't)
   ```

3. **Example Calculation**
   ```python
   # Professional tier user makes $1,000 profit
   profit = 1000.00
   rate = 0.20  # 20%
   sharing_amount = profit * rate  # $200.00
   
   # User keeps: $800.00
   # Platform fee: $200.00
   ```

---

## WebSocket Support ✅ IMPLEMENTED

The platform now supports real-time updates via WebSocket connections. See [WEBSOCKET_INTEGRATION.md](WEBSOCKET_INTEGRATION.md) for detailed documentation.

### WebSocket Endpoints

#### 1. Trade Signals WebSocket
**WS** `ws://localhost:8000/ws/trade-signals`

Real-time trade signals streaming.

**Client sends:**
```json
{
  "action": "subscribe",
  "symbols": ["AAPL", "GOOGL", "MSFT"],
  "user_id": "user_001"
}
```

**Server sends:**
```json
{
  "type": "trade_signals",
  "data": [
    {
      "symbol": "AAPL",
      "signal": "buy",
      "confidence": 0.85,
      "consensus_strength": 0.92,
      "timestamp": "2024-10-05T10:30:00"
    }
  ],
  "timestamp": "2024-10-05T10:30:00"
}
```

#### 2. Earnings WebSocket
**WS** `ws://localhost:8000/ws/earnings`

Real-time earnings and portfolio updates.

**Client sends:**
```json
{
  "action": "subscribe",
  "user_id": "user_001"
}
```

**Server sends:**
```json
{
  "type": "earnings",
  "data": {
    "portfolio_value": 100000.00,
    "total_return": 5000.00,
    "daily_pnl": 250.00,
    "win_rate": 0.65
  },
  "timestamp": "2024-10-05T10:30:00"
}
```

#### 3. Notifications WebSocket
**WS** `ws://localhost:8000/ws/notifications`

Real-time notifications and alerts.

**Client sends:**
```json
{
  "action": "subscribe",
  "user_id": "user_001"
}
```

**Server sends:**
```json
{
  "type": "notification",
  "data": {
    "type": "success",
    "title": "Trade Executed",
    "message": "Your AAPL buy order has been executed"
  },
  "timestamp": "2024-10-05T10:30:00"
}
```

#### 4. Admin Dashboard WebSocket
**WS** `ws://localhost:8000/ws/admin`

Real-time admin dashboard updates (requires admin token).

**Client sends:**
```json
{
  "action": "subscribe",
  "admin_token": "admin-token"
}
```

**Server sends:**
```json
{
  "type": "admin_users",
  "data": {
    "total_users": 150,
    "active_subscriptions": 120
  },
  "timestamp": "2024-10-05T10:30:00"
}
```

#### 5. Market Data WebSocket
**WS** `ws://localhost:8000/ws/market-data`

Real-time market data streaming (existing endpoint).

**Features:**
- Automatic reconnection with exponential backoff
- Heartbeat ping/pong mechanism
- Multi-channel support
- Graceful fallback to REST API
- User-specific subscriptions
- Symbol filtering

**Example JavaScript client:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/trade-signals');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['AAPL', 'GOOGL', 'MSFT'],
    user_id: 'user_001'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

---

## API Changelog

### Version 2.1.0 (Current)
- ✅ **WebSocket support for real-time updates**
  - Trade signals streaming
  - Earnings updates
  - Notifications
  - Admin dashboard updates
  - Market data streaming
- Enhanced dashboard with live indicators
- Automatic fallback to REST API
- React hooks for easy WebSocket integration

### Version 2.0.0
- Initial release with 23 endpoints
- Multi-strategy trading analysis
- Dashboard and subscription management
- Profit-sharing calculation
- Insider trading analysis
- Fundamental analysis

### Upcoming Features
- JWT authentication for WebSockets
- Advanced analytics endpoints
- Historical data export
- Custom strategy configuration
- Portfolio optimization recommendations

---

## Support and Resources

### Documentation
- **Full API Docs**: This file (API.md)
- **Developer Quickstart**: [DEVELOPER_QUICKSTART.md](DEVELOPER_QUICKSTART.md) - ⭐ Get started in 5 minutes
- **Dashboard API**: [DASHBOARD_API.md](DASHBOARD_API.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Examples**: [examples/README.md](examples/README.md)

### Official SDKs
- **Python SDK**: [sdk/python/README.md](sdk/python/README.md) - Full-featured Python client
- **JavaScript/TypeScript SDK**: [sdk/javascript/README.md](sdk/javascript/README.md) - Browser & Node.js compatible
- **SDK Overview**: [sdk/README.md](sdk/README.md) - Compare and choose your SDK

### Developer Tools
- **CLI Tool**: [tools/README.md](tools/README.md) - Command-line interface for testing
- **Postman Collection**: `postman_collection.json` - Pre-built collection with all endpoints
- **OpenAPI Spec**: Generate with `python tools/generate_openapi.py`

### Interactive Testing
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman**: Import `postman_collection.json` for complete endpoint testing

### Example Code
- **Python Examples**: [examples/dashboard_api_demo.py](examples/dashboard_api_demo.py)
- **Profit Sharing**: [examples/profit_sharing_demo.py](examples/profit_sharing_demo.py)
- **WebSocket Demo**: [examples/websocket_demo.py](examples/websocket_demo.py)
- **SDK Examples**: See SDK README files for usage examples

### Getting Help
1. Start with [DEVELOPER_QUICKSTART.md](DEVELOPER_QUICKSTART.md)
2. Check the comprehensive documentation above
3. Review SDK examples in [sdk/](sdk/)
4. Try the CLI tool: `./tools/sentio-cli.py --help`
5. Use interactive API docs at `/docs`
6. Open an issue on GitHub

---

## Production Deployment Checklist

- [ ] Implement proper JWT authentication
- [ ] Set up HTTPS/TLS
- [ ] Configure CORS for your domain
- [ ] Implement rate limiting
- [ ] Set up database persistence
- [ ] Configure logging and monitoring
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Implement data backups
- [ ] Configure load balancing
- [ ] Set up CI/CD pipeline
- [ ] Security audit
- [ ] Performance testing
- [ ] Documentation review

---

**Last Updated**: 2024-10-05  
**API Version**: 2.0.0  
**Contact**: [GitHub Issues](https://github.com/JamieT18/Sentio-2.0/issues)
