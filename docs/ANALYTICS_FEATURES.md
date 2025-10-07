# Enhanced Analytics and Reporting Features

## Overview
This document describes the new enhanced analytics and reporting features added to Sentio 2.0, including advanced charts, performance metrics, historical data analysis, and export options.

## New Features

### 1. Backend API Endpoints

#### Portfolio History Analytics
**GET** `/api/v1/analytics/portfolio-history?user_id={user_id}&days={days}`

Get historical portfolio performance data over a specified time period.

**Query Parameters:**
- `user_id` (required): User identifier
- `days` (optional): Number of days of history (default: 30)

**Response:**
```json
{
  "user_id": "user_123",
  "period_days": 30,
  "history": [
    {
      "date": "2024-01-01",
      "timestamp": "2024-01-01T00:00:00",
      "portfolio_value": 100500.00,
      "daily_change": 500.00,
      "daily_change_pct": 0.50
    }
  ],
  "summary": {
    "initial_value": 100000.00,
    "final_value": 105000.00,
    "total_return": 5000.00,
    "total_return_pct": 5.0,
    "best_day": { "date": "2024-01-15", "daily_change_pct": 2.5 },
    "worst_day": { "date": "2024-01-08", "daily_change_pct": -1.2 }
  },
  "timestamp": "2024-01-30T10:00:00"
}
```

#### Trade Performance Analytics
**GET** `/api/v1/analytics/trade-performance?user_id={user_id}`

Get detailed trade performance analytics broken down by symbol.

**Query Parameters:**
- `user_id` (required): User identifier

**Response:**
```json
{
  "user_id": "user_123",
  "by_symbol": [
    {
      "symbol": "AAPL",
      "total_trades": 15,
      "wins": 10,
      "losses": 5,
      "win_rate": 0.67,
      "total_pnl": 1250.00,
      "avg_win": 200.00,
      "avg_loss": -100.00
    }
  ],
  "overall": {
    "total_trades": 125,
    "total_wins": 85,
    "total_losses": 40,
    "overall_win_rate": 0.68,
    "total_pnl": 8500.00,
    "best_performer": { "symbol": "AAPL", "total_pnl": 2500.00 },
    "worst_performer": { "symbol": "XYZ", "total_pnl": -500.00 }
  },
  "timestamp": "2024-01-30T10:00:00"
}
```

#### User Activity Analytics
**GET** `/api/v1/analytics/user-activity?user_id={user_id}&days={days}`

Get user activity trends and patterns.

**Query Parameters:**
- `user_id` (required): User identifier
- `days` (optional): Number of days to analyze (default: 30)

**Response:**
```json
{
  "user_id": "user_123",
  "period_days": 30,
  "daily_activity": [
    {
      "date": "2024-01-01",
      "day_of_week": "Monday",
      "trades_executed": 5,
      "session_duration_minutes": 120,
      "api_calls": 45
    }
  ],
  "summary": {
    "total_trades": 125,
    "avg_trades_per_day": 4.17,
    "most_active_day": { "date": "2024-01-15", "trades_executed": 12 },
    "total_session_time_hours": 45.5,
    "total_api_calls": 1250
  },
  "by_day_of_week": {
    "Monday": { "trades": 25, "count": 4, "avg_trades": 6.25 },
    "Tuesday": { "trades": 20, "count": 4, "avg_trades": 5.0 }
  },
  "timestamp": "2024-01-30T10:00:00"
}
```

#### Historical Growth Analytics (Admin Only)
**GET** `/api/v1/admin/analytics/historical-growth?days={days}`

Get historical growth analytics for the platform (admin only).

**Query Parameters:**
- `days` (optional): Number of days of history (default: 90)

**Response:**
```json
{
  "period_days": 90,
  "history": [
    {
      "date": "2024-01-01",
      "timestamp": "2024-01-01T00:00:00",
      "total_users": 100,
      "new_users": 2,
      "total_revenue": 5000.00,
      "active_users": 85
    }
  ],
  "summary": {
    "starting_users": 100,
    "current_users": 250,
    "total_growth": 150,
    "starting_revenue": 5000.00,
    "current_revenue": 15000.00,
    "revenue_growth": 10000.00
  },
  "timestamp": "2024-03-31T10:00:00"
}
```

#### Analytics Report Export
**GET** `/api/v1/export/analytics-report?user_id={user_id}&format={format}&include_charts={bool}`

Export comprehensive analytics report in JSON or CSV format.

**Query Parameters:**
- `user_id` (required): User identifier
- `format` (optional): Export format - `json` or `csv` (default: json)
- `include_charts` (optional): Include chart data (default: true)

**Response:**
- Returns a downloadable file with comprehensive analytics
- Filename format: `analytics_report_{user_id}_{date}.{format}`

### 2. Frontend Components

#### PortfolioChart Component
Location: `dashboard/src/components/PortfolioChart.js`

A line/area chart showing portfolio performance over time with the following features:
- Historical portfolio values
- Daily changes and percentages
- Summary statistics (total return, best/worst days)
- Interactive tooltips
- Responsive design
- Configurable time periods (7, 30, 60, 90 days)

**Usage:**
```jsx
import PortfolioChart from './components/PortfolioChart';

<PortfolioChart userId="user_123" days={30} />
```

#### TradePerformanceChart Component
Location: `dashboard/src/components/TradePerformanceChart.js`

Visualizes trade performance by symbol with:
- Bar chart showing P&L by symbol
- Pie chart showing trade distribution
- Color-coded wins/losses
- Performance summary cards
- Switchable chart types

**Usage:**
```jsx
import TradePerformanceChart from './components/TradePerformanceChart';

<TradePerformanceChart userId="user_123" />
```

#### ActivityHeatmap Component
Location: `dashboard/src/components/ActivityHeatmap.js`

Shows user activity patterns with:
- Calendar-style heatmap
- Activity intensity visualization
- Day-of-week breakdown
- Summary statistics
- Interactive cells with tooltips

**Usage:**
```jsx
import ActivityHeatmap from './components/ActivityHeatmap';

<ActivityHeatmap userId="user_123" days={30} />
```

#### AnalyticsDashboard Component
Location: `dashboard/src/components/AnalyticsDashboard.js`

Integrated analytics dashboard that combines all charts:
- Tabbed interface for different analytics views
- Time period selector
- Export functionality (JSON/CSV)
- Responsive layout

**Usage:**
```jsx
import AnalyticsDashboard from './components/AnalyticsDashboard';

<AnalyticsDashboard userId="user_123" />
```

#### AdminAnalytics Component
Location: `dashboard/src/components/AdminAnalytics.js`

Admin-only analytics with historical growth data:
- User growth charts
- Revenue growth charts
- Key insights cards
- Configurable time periods
- Summary statistics

**Usage:**
```jsx
import AdminAnalytics from './components/AdminAnalytics';

<AdminAnalytics />
```

### 3. Export Features

#### User Analytics Export
Users can export their analytics data in multiple formats:
- **JSON Format**: Complete structured data with all metrics
- **CSV Format**: Simplified tabular format for spreadsheet analysis

Export includes:
- Portfolio summary
- Trading statistics
- Historical performance data (when charts enabled)
- Subscription information

#### Implementation
The export functionality is integrated into the AnalyticsDashboard component:
- Click "Export JSON" or "Export CSV" buttons
- File automatically downloads with timestamped filename
- Format: `analytics_report_{user_id}_{YYYYMMDD}.{format}`

### 4. Chart Library

**Recharts** (v2.x) is used for all visualizations:
- Responsive and mobile-friendly
- Interactive tooltips
- Customizable themes
- Smooth animations
- Accessibility support

Components use:
- `LineChart` - Portfolio performance over time
- `AreaChart` - Revenue/value visualization with gradients
- `BarChart` - P&L comparison by symbol
- `PieChart` - Trade distribution visualization

## Integration Guide

### For Users

1. **View Portfolio Performance**
   ```javascript
   import { AnalyticsDashboard } from './components/AnalyticsDashboard';
   
   // In your dashboard
   <AnalyticsDashboard userId={currentUser.id} />
   ```

2. **Export Analytics Report**
   - Navigate to Analytics Dashboard
   - Select desired time period
   - Click "Export JSON" or "Export CSV"
   - File downloads automatically

### For Admins

1. **View Platform Analytics**
   ```javascript
   import { AdminAnalytics } from './components/AdminAnalytics';
   
   // In admin panel
   <AdminAnalytics />
   ```

2. **Access Historical Growth Data**
   - Navigate to Admin Analytics
   - Select time period (30-180 days)
   - Switch between User Growth and Revenue Growth views
   - View key insights and trends

### API Integration

Update your API service to include new analytics endpoints:

```javascript
import api from './services/api';

// Get portfolio history
const portfolioData = await api.getPortfolioHistory(userId, 30);

// Get trade performance
const tradeData = await api.getTradePerformance(userId);

// Get user activity
const activityData = await api.getUserActivity(userId, 30);

// Export report
await api.exportAnalyticsReport(userId, 'json', true);

// Admin: Get historical growth
const growthData = await api.getHistoricalGrowth(90);
```

## Performance Considerations

### Caching
- Portfolio history: 60 second cache
- Trade performance: 60 second cache
- User activity: 60 second cache
- Admin analytics: 120 second cache

### Optimization
- Chart data is paginated for large datasets
- Responsive design uses CSS Grid/Flexbox
- Lazy loading for chart components
- Debounced API calls for time period changes

## Styling

All components include dedicated CSS files:
- `AnalyticsDashboard.css` - Main analytics styling
- `AdminAnalytics.css` - Admin-specific styling
- Responsive breakpoints at 768px
- Dark mode compatible
- Consistent color scheme:
  - Positive values: #00C49F (green)
  - Negative values: #FF6B6B (red)
  - Primary: #3498db (blue)
  - Charts: Multiple colors from Recharts palette

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live data
2. **Custom Date Ranges**: User-defined date range selector
3. **Comparative Analytics**: Compare performance vs benchmarks
4. **PDF Export**: Generate PDF reports with charts
5. **Alerts & Notifications**: Performance-based alerts
6. **Mobile App**: Native mobile analytics views
7. **Machine Learning Insights**: AI-powered trend predictions

## Troubleshooting

### Charts Not Displaying
- Ensure recharts is installed: `npm install recharts --legacy-peer-deps`
- Check browser console for errors
- Verify API endpoints are accessible
- Check that user has valid authentication token

### Export Not Working
- Verify API endpoint returns blob data
- Check browser download permissions
- Ensure popup blockers are disabled
- Verify user authentication

### Performance Issues
- Reduce time period for large datasets
- Clear API cache: `api.cache.clear()`
- Check network throttling
- Verify backend response times

## Testing

### Component Testing
```javascript
import { render, screen } from '@testing-library/react';
import AnalyticsDashboard from './components/AnalyticsDashboard';

test('renders analytics dashboard', () => {
  render(<AnalyticsDashboard userId="test_user" />);
  expect(screen.getByText(/Analytics & Reports/i)).toBeInTheDocument();
});
```

### API Testing
```bash
# Test portfolio history endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/analytics/portfolio-history?user_id=user_123&days=30"

# Test export endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/export/analytics-report?user_id=user_123&format=json" \
  --output report.json
```

## Security

- All endpoints require authentication
- User data is isolated (users can only access their own analytics)
- Admin endpoints require admin token verification
- Export functionality respects user permissions
- No sensitive data in URLs (use POST for sensitive operations)

## Support

For issues or questions:
- API Documentation: `DASHBOARD_API.md`
- Architecture Guide: `ARCHITECTURE.md`
- GitHub Issues: Report bugs and feature requests
