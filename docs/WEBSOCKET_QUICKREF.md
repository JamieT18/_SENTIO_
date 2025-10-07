# WebSocket Quick Reference

## Endpoints

| Endpoint | Purpose | Required Data |
|----------|---------|---------------|
| `/ws/trade-signals` | Real-time trade signals | `symbols`, `user_id` |
| `/ws/earnings` | Real-time earnings updates | `user_id` |
| `/ws/notifications` | Real-time notifications | `user_id` |
| `/ws/admin` | Admin dashboard updates | `admin_token` |
| `/ws/market-data` | Real-time market data | `symbols` |

## Quick Start

### 1. Backend (Python)

```python
# Import the WebSocket manager
from sentio.data.dashboard_websocket_service import dashboard_ws_manager

# Broadcast trade signals
await dashboard_ws_manager.broadcast_trade_signals([
    {'symbol': 'AAPL', 'signal': 'buy', 'confidence': 0.85}
])

# Broadcast earnings
await dashboard_ws_manager.broadcast_earnings('user_001', {
    'portfolio_value': 100000,
    'daily_pnl': 250
})

# Send notification
await dashboard_ws_manager.broadcast_notification('user_001', {
    'type': 'success',
    'title': 'Trade Executed',
    'message': 'Your order has been filled'
})
```

### 2. Frontend (React)

```javascript
// Import hooks
import { useTradeSignalsWebSocket } from '../hooks/useWebSocket';

// Use in component
const { signals, loading, error, isConnected } = useTradeSignalsWebSocket(
    ['AAPL', 'GOOGL'], 
    'user_001'
);

// Display data
{signals.map(signal => (
    <div key={signal.symbol}>
        {signal.symbol}: {signal.signal}
    </div>
))}
```

### 3. Vanilla JavaScript

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/trade-signals');

ws.onopen = () => {
    ws.send(JSON.stringify({
        action: 'subscribe',
        symbols: ['AAPL', 'GOOGL'],
        user_id: 'user_001'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};
```

## Message Protocol

### Client → Server

```json
{
    "action": "subscribe",
    "symbols": ["AAPL", "GOOGL"],
    "user_id": "user_001"
}
```

### Server → Client

```json
{
    "type": "trade_signals",
    "data": [
        {
            "symbol": "AAPL",
            "signal": "buy",
            "confidence": 0.85,
            "timestamp": "2024-10-05T10:30:00"
        }
    ],
    "timestamp": "2024-10-05T10:30:00"
}
```

## Testing

### HTML Test Page
Open `examples/websocket_test.html` in a browser

### Python Demo
```bash
python examples/websocket_demo.py
```

### Manual Testing
```bash
# Install wscat
npm install -g wscat

# Connect to endpoint
wscat -c ws://localhost:8000/ws/trade-signals

# Send subscription
{"action": "subscribe", "symbols": ["AAPL"], "user_id": "test"}
```

## Features

✅ Multi-channel support
✅ User-specific subscriptions
✅ Automatic reconnection
✅ Heartbeat mechanism
✅ Fallback to REST API
✅ Live status indicators
✅ Symbol filtering
✅ Admin dashboard support

## Common Issues

**Connection refused**
- Ensure API server is running
- Check WebSocket URL

**No updates received**
- Verify subscription was successful
- Check backend is broadcasting
- Verify user_id is correct

**Frequent disconnections**
- Check network stability
- Verify heartbeat is working
- Check server logs

## Documentation

- Full guide: [WEBSOCKET_INTEGRATION.md](WEBSOCKET_INTEGRATION.md)
- API docs: [API.md](API.md)
- Examples: `examples/websocket_demo.py`, `examples/websocket_test.html`
