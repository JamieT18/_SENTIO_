# Dashboard and Subscription API Endpoints

## Overview
This document describes the new dashboard and subscription management endpoints added to the Sentio 2.0 API.

## Dashboard Endpoints

### 1. Trade Signals Summary
**GET** `/api/v1/dashboard/trade-signals`

Get aggregated trade signals for multiple symbols.

**Query Parameters:**
- `symbols` (optional): Comma-separated list of symbols (default: AAPL,GOOGL,MSFT,TSLA)

**Response:**
```json
{
  "signals": [
    {
      "symbol": "AAPL",
      "signal": "buy",
      "confidence": 0.85,
      "consensus_strength": 0.92,
      "timestamp": "2024-10-05T10:30:00"
    }
  ],
  "count": 4,
  "timestamp": "2024-10-05T10:30:00"
}
```

### 2. Earnings Summary
**GET** `/api/v1/dashboard/earnings?user_id={user_id}`

Get comprehensive earnings and performance summary for a user.

**Query Parameters:**
- `user_id` (required): User identifier

**Response:**
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

### 3. AI Trade Summary
**GET** `/api/v1/dashboard/ai-summary?symbol={symbol}`

Get AI-generated summary of trading recommendations.

**Query Parameters:**
- `symbol` (optional): Symbol to analyze. If omitted, returns general market summary

**Response (with symbol):**
```json
{
  "symbol": "AAPL",
  "recommendation": "buy",
  "confidence": 0.85,
  "reasoning": "Based on 4 strategy votes, the system recommends BUY with 85.0% confidence...",
  "key_factors": [
    "Strategy consensus: 92.0%",
    "Signal confidence: 85.0%",
    "Active strategies: 4"
  ],
  "timestamp": "2024-10-05T10:30:00"
}
```

### 4. Strength Signal
**GET** `/api/v1/dashboard/strength-signal?symbol={symbol}`

Get market strength indicators for a symbol.

**Query Parameters:**
- `symbol` (required): Trading symbol

**Response:**
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

### 5. Trade Journal - Get Entries
**GET** `/api/v1/dashboard/trade-journal?user_id={user_id}&limit={limit}`

Retrieve trade journal entries for a user.

**Query Parameters:**
- `user_id` (required): User identifier
- `limit` (optional): Maximum entries to return (default: 50)

**Response:**
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
    }
  ],
  "count": 25,
  "timestamp": "2024-10-05T10:30:00"
}
```

### 6. Trade Journal - Add Entry
**POST** `/api/v1/dashboard/trade-journal?user_id={user_id}`

Add a manual trade journal entry.

**Request Body:**
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

**Response:**
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

### 7. Performance Cards
**GET** `/api/v1/dashboard/performance-cards?user_id={user_id}`

Get performance metrics formatted as dashboard cards.

**Query Parameters:**
- `user_id` (required): User identifier

**Response:**
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

## Subscription Endpoints

### 1. Get Pricing Information
**GET** `/api/v1/subscription/pricing`

Get pricing details for all subscription tiers.

**Response:**
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
      "tier": "professional",
      "price": 199.99,
      "features": {
        "max_concurrent_trades": 10,
        "max_strategies": 8,
        "day_trading": true,
        "api_access": true,
        "profit_sharing_rate": 20.0
      }
    }
  ],
  "timestamp": "2024-10-05T10:30:00"
}
```

### 2. Get User Subscription
**GET** `/api/v1/subscription/{user_id}`

Get detailed subscription information for a user.

**Response:**
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

### 3. Calculate Profit Sharing
**POST** `/api/v1/subscription/profit-sharing/calculate`

Calculate profit-sharing amount for a trading profit.

**Request Body:**
```json
{
  "user_id": "user_123",
  "trading_profit": 1000.00
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "trading_profit": 1000.00,
  "sharing_amount": 200.00,
  "profit_sharing_balance": 200.00,
  "timestamp": "2024-10-05T10:30:00"
}
```

### 4. Get Profit Sharing Balance
**GET** `/api/v1/subscription/profit-sharing/{user_id}`

Get user's current profit-sharing balance and configuration.

**Response:**
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

## Data Export & Import Endpoints

### 1. Export Trade History
**GET** `/api/v1/export/trade-history?user_id={user_id}&format={format}`

Export trade history in CSV or JSON format.

**Query Parameters:**
- `user_id` (required): User identifier
- `format` (optional): Export format - `csv` or `json` (default: csv)
- `start_date` (optional): Filter start date (ISO format)
- `end_date` (optional): Filter end date (ISO format)

**Response:**
- Returns a downloadable file with trade history
- CSV format: `trade_history_{user_id}_{date}.csv`
- JSON format: `trade_history_{user_id}_{date}.json`

**CSV Response Structure:**
```csv
symbol,entry_price,exit_price,quantity,pnl,pnl_percent,entry_time,exit_time,reason
AAPL,150.00,155.00,10,50.00,3.33,2024-10-01T10:00:00,2024-10-01T15:00:00,take_profit
GOOGL,2800.00,2750.00,5,-250.00,-1.79,2024-10-02T09:30:00,2024-10-02T14:00:00,stop_loss
```

**JSON Response Structure:**
```json
{
  "user_id": "user_123",
  "trades": [
    {
      "symbol": "AAPL",
      "entry_price": 150.00,
      "exit_price": 155.00,
      "quantity": 10,
      "pnl": 50.00,
      "pnl_percent": 3.33,
      "entry_time": "2024-10-01T10:00:00",
      "exit_time": "2024-10-01T15:00:00",
      "reason": "take_profit"
    }
  ],
  "count": 45,
  "export_date": "2024-10-05T10:30:00",
  "filters": {
    "start_date": null,
    "end_date": null
  }
}
```

### 2. Export Performance Report
**GET** `/api/v1/export/performance-report?user_id={user_id}&format={format}`

Export comprehensive performance report in CSV or JSON format.

**Query Parameters:**
- `user_id` (required): User identifier
- `format` (optional): Export format - `csv` or `json` (default: json)

**Response:**
- Returns a downloadable file with performance metrics
- CSV format: `performance_report_{user_id}_{date}.csv`
- JSON format: `performance_report_{user_id}_{date}.json`

**JSON Response Structure:**
```json
{
  "user_id": "user_123",
  "subscription_tier": "professional",
  "report_date": "2024-10-05T10:30:00",
  "portfolio": {
    "current_value": 105000.00,
    "initial_value": 100000.00,
    "total_return": 5000.00,
    "total_return_pct": 5.0,
    "daily_pnl": 250.50
  },
  "trading_statistics": {
    "total_trades": 45,
    "wins": 30,
    "losses": 15,
    "win_rate": 0.67,
    "avg_win": 200.00,
    "avg_loss": -100.00,
    "open_positions": 3
  },
  "profit_sharing": {
    "balance": 150.00,
    "total_shared": 1500.00,
    "rate": 0.20,
    "enabled": true
  }
}
```

### 3. Import Trade Journal
**POST** `/api/v1/import/trade-journal?user_id={user_id}`

Import trade journal entries for manual trade logging or migration.

**Request Body:**
```json
{
  "data": [
    {
      "symbol": "AAPL",
      "action": "buy",
      "quantity": 10,
      "price": 150.00,
      "notes": "Entry on breakout",
      "tags": ["breakout", "momentum"],
      "timestamp": "2024-10-01T10:00:00"
    },
    {
      "symbol": "GOOGL",
      "action": "sell",
      "quantity": 5,
      "price": 2800.00,
      "notes": "Taking profit",
      "tags": ["profit-taking"]
    }
  ],
  "format": "json",
  "overwrite": false
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "imported_count": 2,
  "total_entries": 2,
  "errors": [],
  "timestamp": "2024-10-05T10:30:00"
}
```

### 4. Import Trades
**POST** `/api/v1/import/trades?user_id={user_id}`

Import trade history for bulk data migration or analysis.

**Request Body:**
```json
{
  "data": [
    {
      "symbol": "AAPL",
      "entry_price": 150.00,
      "exit_price": 155.00,
      "quantity": 10,
      "entry_time": "2024-10-01T10:00:00",
      "exit_time": "2024-10-01T15:00:00",
      "reason": "take_profit"
    },
    {
      "symbol": "GOOGL",
      "entry_price": 2800.00,
      "exit_price": 2750.00,
      "quantity": 5,
      "entry_time": "2024-10-02T09:30:00",
      "exit_time": "2024-10-02T14:00:00",
      "reason": "stop_loss"
    }
  ],
  "format": "json",
  "overwrite": false
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "imported_count": 2,
  "total_entries": 2,
  "overwrite_mode": false,
  "errors": [],
  "timestamp": "2024-10-05T10:30:00"
}
```

**Import Features:**
- Validates required fields before import
- Calculates P&L automatically from entry/exit prices
- Updates portfolio value based on imported trades
- Returns detailed error information for failed entries
- Supports overwrite mode to replace existing data
- Supports both CSV and JSON input formats

## Profit Sharing Configuration

### Tier-Based Rates:
- **FREE**: 0% (disabled)
- **BASIC**: 0% (disabled)
- **PROFESSIONAL**: 20%
- **ENTERPRISE**: 15%

### How It Works:
1. User executes profitable trades
2. System calculates profit-sharing fee based on tier
3. Fee is added to user's profit_sharing_balance
4. Balance is charged during monthly billing
5. Only positive profits incur fees (losses don't)

## Authentication

All endpoints (except `/api/v1/health` and `/api/v1/subscription/pricing`) require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <your_token_here>
```

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message description"
}
```

Common status codes:
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

## Integration Notes

1. **Dashboard Integration**: Frontend can call these endpoints to populate dashboard widgets
2. **Real-time Updates**: Consider using WebSocket for real-time signal updates
3. **Caching**: Trade signals and performance data can be cached for 30-60 seconds
4. **Rate Limiting**: Implement rate limiting in production (not included in this version)
5. **Pagination**: Trade journal supports pagination via `limit` parameter
6. **Data Export**: Use export endpoints to download trade history and performance reports for offline analysis
7. **Data Import**: Use import endpoints to migrate data from other platforms or upload historical trades

## Next Steps

1. Add WebSocket support for real-time updates
2. Implement proper JWT authentication
3. Add database persistence for trade journal
4. Create admin endpoints for subscription management
5. Add analytics and reporting endpoints
6. Add CSV parsing for file uploads (currently accepts JSON in request body)
