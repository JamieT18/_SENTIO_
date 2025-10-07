# WebSocket Integration Documentation

## Overview

The Sentio 2.0 platform now supports real-time updates via WebSocket connections for:
- **Trade Signals**: Live trading recommendations and analysis
- **Earnings**: Real-time portfolio performance and P&L updates
- **Notifications**: Instant alerts and system messages
- **Admin Dashboard**: Live analytics, user updates, and revenue tracking

## Architecture

### Backend (Python/FastAPI)

The WebSocket system consists of:

1. **`dashboard_websocket_service.py`**: Core WebSocket manager that handles:
   - Multi-client connections
   - User-specific subscriptions
   - Broadcasting updates to relevant clients
   - Automatic reconnection handling

2. **WebSocket Endpoints** (`api.py`):
   - `/ws/trade-signals` - Real-time trade signals
   - `/ws/earnings` - Real-time earnings updates
   - `/ws/notifications` - Real-time notifications
   - `/ws/admin` - Real-time admin dashboard updates
   - `/ws/market-data` - Real-time market data (existing)

### Frontend (React)

The frontend integration includes:

1. **`websocket.js`**: WebSocket service manager with:
   - Connection management
   - Automatic reconnection with exponential backoff
   - Ping/pong heartbeat mechanism
   - Multi-channel support

2. **`useWebSocket.js`**: React hooks for easy integration:
   - `useTradeSignalsWebSocket(symbols, userId)`
   - `useEarningsWebSocket(userId)`
   - `useNotificationsWebSocket(userId)`
   - `useAdminWebSocket(adminToken)`

3. **Updated Components**:
   - `TradeSignals.js` - Now supports WebSocket with fallback to REST
   - `EarningsSummary.js` - Real-time earnings updates
   - `Notifications.js` - New component for real-time notifications
   - `AdminDashboardWithWebSocket.js` - Admin dashboard with live updates

## Usage

### Backend: Broadcasting Updates

#### Trade Signals

When trade signals are generated or updated:

```python
from sentio.data.dashboard_websocket_service import dashboard_ws_manager

# Broadcast trade signals to all subscribed clients
signals = [
    {
        'symbol': 'AAPL',
        'signal': 'buy',
        'confidence': 0.85,
        'timestamp': datetime.now().isoformat()
    }
]

await dashboard_ws_manager.broadcast_trade_signals(signals)
```

#### Earnings Updates

When earnings data changes:

```python
from sentio.data.dashboard_websocket_service import dashboard_ws_manager

# Broadcast earnings update to specific user
earnings_data = {
    'portfolio_value': 100000.00,
    'total_return': 5000.00,
    'daily_pnl': 250.00,
    'win_rate': 0.65
}

await dashboard_ws_manager.broadcast_earnings('user_001', earnings_data)
```

#### Notifications

Send notifications to users:

```python
from sentio.data.dashboard_websocket_service import dashboard_ws_manager

# Send notification to specific user
notification = {
    'type': 'success',
    'title': 'Trade Executed',
    'message': 'Your AAPL buy order has been executed',
    'timestamp': datetime.now().isoformat()
}

await dashboard_ws_manager.broadcast_notification('user_001', notification)
```

#### Admin Updates

Broadcast updates to admin dashboard:

```python
from sentio.data.dashboard_websocket_service import dashboard_ws_manager

# Broadcast admin update
update_data = {
    'total_users': 150,
    'active_subscriptions': 120,
    'monthly_revenue': 15000.00
}

await dashboard_ws_manager.broadcast_admin_update('users', update_data)
```

### Frontend: Using WebSocket

#### Trade Signals Component

```javascript
import React from 'react';
import { useTradeSignalsWebSocket } from '../hooks/useWebSocket';

const TradeSignals = ({ userId }) => {
  const symbols = ['AAPL', 'GOOGL', 'MSFT'];
  const { signals, loading, error, isConnected } = useTradeSignalsWebSocket(symbols, userId);

  return (
    <div>
      <h2>
        Trade Signals 
        {isConnected && <span>🟢 Live</span>}
      </h2>
      {signals.map(signal => (
        <div key={signal.symbol}>
          {signal.symbol}: {signal.signal} ({signal.confidence})
        </div>
      ))}
    </div>
  );
};
```

#### Earnings Component

```javascript
import React from 'react';
import { useEarningsWebSocket } from '../hooks/useWebSocket';

const Earnings = ({ userId }) => {
  const { earnings, loading, error, isConnected } = useEarningsWebSocket(userId);

  if (!earnings) return <div>Loading...</div>;

  return (
    <div>
      <h2>
        Earnings 
        {isConnected && <span>🟢 Live</span>}
      </h2>
      <p>Portfolio Value: ${earnings.portfolio_value}</p>
      <p>Daily P&L: ${earnings.daily_pnl}</p>
    </div>
  );
};
```

#### Notifications Component

```javascript
import React from 'react';
import { useNotificationsWebSocket } from '../hooks/useWebSocket';

const Notifications = ({ userId }) => {
  const { notifications, clearNotifications, isConnected } = useNotificationsWebSocket(userId);

  return (
    <div>
      <h2>
        Notifications 
        {isConnected && <span>🟢 Live</span>}
      </h2>
      {notifications.map(notif => (
        <div key={notif.id}>
          <strong>{notif.title}</strong>: {notif.message}
        </div>
      ))}
      <button onClick={clearNotifications}>Clear All</button>
    </div>
  );
};
```

## WebSocket Protocol

### Connection Flow

1. **Client Initiates Connection**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/trade-signals');
   ```

2. **Client Sends Initial Subscription**
   ```json
   {
     "action": "subscribe",
     "symbols": ["AAPL", "GOOGL"],
     "user_id": "user_001"
   }
   ```

3. **Server Sends Updates**
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

### Message Types

#### Client → Server

- **Subscribe**: `{"action": "subscribe", "symbols": ["AAPL"], "user_id": "user_001"}`
- **Unsubscribe**: `{"action": "unsubscribe", "symbols": ["AAPL"]}`
- **Ping**: `{"action": "ping"}` (heartbeat)

#### Server → Client

- **Trade Signals**: `{"type": "trade_signals", "data": [...], "timestamp": "..."}`
- **Earnings**: `{"type": "earnings", "data": {...}, "timestamp": "..."}`
- **Notification**: `{"type": "notification", "data": {...}, "timestamp": "..."}`
- **Admin Update**: `{"type": "admin_users", "data": {...}, "timestamp": "..."}`
- **Pong**: `{"type": "pong", "timestamp": "..."}` (heartbeat response)
- **Error**: `{"type": "error", "message": "...", "timestamp": "..."}`

## Configuration

### Environment Variables

```bash
# WebSocket URL (auto-derived from API URL if not set)
REACT_APP_WS_URL=ws://localhost:8000

# API URL
REACT_APP_API_URL=http://localhost:8000
```

### Component Props

Components support both WebSocket and REST API:

```javascript
// Enable WebSocket (default)
<TradeSignals symbols={symbols} userId={userId} useWebSocket={true} />

// Disable WebSocket (use REST polling)
<TradeSignals symbols={symbols} userId={userId} useWebSocket={false} />
```

## Reconnection Strategy

The WebSocket service implements automatic reconnection with exponential backoff:

1. **First reconnection**: Immediate
2. **Second reconnection**: 3 seconds delay
3. **Third reconnection**: 6 seconds delay
4. **Fourth reconnection**: 9 seconds delay
5. **Fifth reconnection**: 12 seconds delay
6. **After 5 attempts**: Stops trying and logs error

## Fallback Mechanism

All components support graceful degradation:

1. **WebSocket Available**: Real-time updates via WebSocket
2. **WebSocket Unavailable**: Automatic fallback to REST API polling (30-second intervals)
3. **User Control**: Can disable WebSocket via component props

## Security Considerations

1. **Authentication**: 
   - User endpoints require `user_id` verification
   - Admin endpoints require `admin_token` verification
   - Enhance with JWT tokens in production

2. **Rate Limiting**: WebSocket connections are monitored
3. **Connection Limits**: Maximum connections per user/channel
4. **Message Validation**: All messages are validated before processing

## Performance

- **Update Interval**: 5 seconds (configurable)
- **Heartbeat**: 30 seconds ping/pong
- **Max Reconnection Attempts**: 5
- **Message Queue**: Buffered for disconnected clients
- **Concurrent Connections**: Supports unlimited clients (resource-dependent)

## Testing

### Manual Testing

1. Start the backend server:
   ```bash
   cd /home/runner/work/Sentio-2.0/Sentio-2.0
   python -m sentio.ui.api
   ```

2. Open browser console and test WebSocket:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/trade-signals');
   
   ws.onopen = () => {
     console.log('Connected');
     ws.send(JSON.stringify({
       action: 'subscribe',
       symbols: ['AAPL', 'GOOGL'],
       user_id: 'test_user'
     }));
   };
   
   ws.onmessage = (event) => {
     console.log('Received:', JSON.parse(event.data));
   };
   ```

### Frontend Testing

1. Start the React app:
   ```bash
   cd dashboard
   npm start
   ```

2. Components will automatically connect and display live indicator (🟢) when connected

## Troubleshooting

### WebSocket Not Connecting

1. Check WebSocket URL configuration
2. Verify backend server is running
3. Check browser console for errors
4. Verify firewall/proxy settings

### No Updates Received

1. Check if subscribed to correct symbols/channels
2. Verify backend is broadcasting updates
3. Check network tab for WebSocket messages
4. Verify user_id is correct

### Frequent Disconnections

1. Check network stability
2. Adjust heartbeat interval
3. Check server logs for errors
4. Verify resource limits

## Future Enhancements

1. **JWT Authentication**: Replace simple tokens with JWT
2. **Message Compression**: gzip compression for large messages
3. **Message Filtering**: Server-side filtering of updates
4. **Presence System**: Track online users
5. **Private Channels**: User-specific private channels
6. **Message History**: Send last N messages on reconnect
7. **Load Balancing**: Support for multiple WebSocket servers

## API Reference

See full API documentation in:
- [API.md](../API.md) - General API documentation
- [DASHBOARD_API.md](../DASHBOARD_API.md) - Dashboard-specific API docs
- [ADMIN_DASHBOARD.md](../ADMIN_DASHBOARD.md) - Admin dashboard docs
