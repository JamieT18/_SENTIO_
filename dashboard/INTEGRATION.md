# Sentio 2.0 Dashboard - Backend Integration

This dashboard integrates with the Sentio FastAPI backend to provide real-time trading insights, performance metrics, and account management.

## Features

### Connected Dashboard Components

1. **Performance Cards** - Real-time portfolio metrics
   - Portfolio value and returns
   - Daily P&L
   - Win rate statistics
   - Total trades count
   - Subscription tier status

2. **Trade Signals** - Live trading signals
   - Multi-symbol signal aggregation
   - Confidence scores
   - Consensus strength indicators
   - Auto-refresh every 30 seconds

3. **Earnings Summary** - Comprehensive performance overview
   - Portfolio value tracking
   - Total and daily returns
   - Win/loss statistics
   - Profit sharing information

4. **AI Trade Summary** - AI-powered insights
   - Trading recommendations
   - Market analysis
   - Key factors affecting decisions
   - Symbol-specific or general market view

5. **Trade Journal** - Recent trade history
   - Entry/exit prices
   - P&L tracking
   - Trade actions and dates

## Setup

### Prerequisites

- Node.js 14+ installed
- Sentio backend running (see main README)

### Installation

```bash
cd dashboard
npm install
```

### Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Update `.env` with your backend API URL:
```env
REACT_APP_API_URL=http://localhost:8000
```

### Running the Dashboard

```bash
npm start
```

The dashboard will open at [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
npm run build
```

## Authentication

The dashboard uses token-based authentication. For development/demo:

- **User ID**: `demo_user`
- **Token**: `demo_token_123`

In production, integrate with your authentication provider and obtain real JWT tokens.

## API Integration

The dashboard connects to the following backend endpoints:

### Dashboard Endpoints
- `GET /api/v1/dashboard/performance-cards` - Performance metrics
- `GET /api/v1/dashboard/trade-signals` - Current trade signals
- `GET /api/v1/dashboard/earnings` - Earnings summary
- `GET /api/v1/dashboard/ai-summary` - AI insights
- `GET /api/v1/dashboard/trade-journal` - Trade history
- `POST /api/v1/dashboard/trade-journal` - Add trade entry

### Subscription Endpoints
- `GET /api/v1/subscription/pricing` - Pricing tiers
- `GET /api/v1/subscription/{user_id}` - User subscription
- `GET /api/v1/subscription/profit-sharing/{user_id}` - Profit sharing balance

### System Endpoints
- `GET /api/v1/health` - Backend health check
- `GET /api/v1/status` - System status

## Architecture

```
dashboard/
├── src/
│   ├── components/          # React components
│   │   ├── PerformanceCards.js
│   │   ├── TradeSignals.js
│   │   ├── EarningsSummary.js
│   │   ├── AiSummary.js
│   │   └── TradeJournal.js
│   ├── services/           # API service layer
│   │   └── api.js          # Backend API integration
│   ├── context/            # React context
│   │   └── AuthContext.js  # Authentication management
│   ├── App.js              # Main application
│   └── App.css             # Styling
└── package.json
```

## API Service Layer

The `services/api.js` module provides:

- **dashboardApi**: All dashboard-related endpoints
- **subscriptionApi**: Subscription and billing endpoints
- **systemApi**: System health and status endpoints

Example usage:

```javascript
import { dashboardApi } from './services/api';

// Get performance cards
const cards = await dashboardApi.getPerformanceCards('user_123');

// Get trade signals for specific symbols
const signals = await dashboardApi.getTradeSignals('AAPL,GOOGL');

// Get AI summary for a symbol
const summary = await dashboardApi.getAiSummary('AAPL');
```

## Error Handling

All components include:
- Loading states while fetching data
- Error states with user-friendly messages
- Automatic retry on network errors (via axios)
- Token refresh on 401 errors

## Customization

### Updating API URL

Set the environment variable:
```bash
REACT_APP_API_URL=https://your-api-domain.com
```

### Styling

Edit `src/App.css` to customize colors, layout, and responsive behavior.

### Adding New Features

1. Create new component in `src/components/`
2. Add API methods to `src/services/api.js`
3. Integrate in `src/App.js`

## Development Tips

### Testing API Connection

Check the API status indicator in the header:
- Green "healthy" = Backend connected
- Red "error" = Backend unavailable

### Mock Data

If backend is unavailable, components will show error states. For development without backend:
1. Create mock data files
2. Add conditional logic to use mocks when API fails

### Auto-refresh

Trade Signals component auto-refreshes every 30 seconds. Adjust in `TradeSignals.js`:

```javascript
const interval = setInterval(fetchSignals, 30000); // Change interval here
```

## Troubleshooting

### CORS Errors

Ensure backend CORS is configured:
```python
# In sentio/ui/api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication Errors

1. Check token is saved in localStorage
2. Verify token format (Bearer scheme)
3. Ensure backend accepts the token

### Connection Refused

1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Check REACT_APP_API_URL in `.env`
3. Ensure no firewall blocking

## Production Deployment

1. Build the application:
```bash
npm run build
```

2. Serve the `build/` directory with:
   - Nginx
   - Apache
   - Static hosting (Netlify, Vercel, etc.)

3. Configure environment variables for production API URL

4. Enable HTTPS for secure communication

## Related Documentation

- **Backend API**: See `/DASHBOARD_API.md` for complete API documentation
- **Backend Setup**: See main `/README.md` for backend installation
- **Architecture**: See `/ARCHITECTURE.md` for system overview

## Support

For issues or questions:
1. Check `/DASHBOARD_API.md` for API details
2. Review `/examples/dashboard_api_demo.py` for usage examples
3. Verify backend is running and healthy
