# Admin Dashboard Documentation

## Overview
The Sentio 2.0 Admin Dashboard provides a comprehensive interface for managing subscriptions, pricing, users, and analytics.

## Features

### 1. Overview & Analytics
- **Monthly Recurring Revenue (MRR)**: View total recurring revenue across all tiers
- **Total Users**: Track total number of registered users
- **Active Subscriptions**: Monitor currently active subscriptions
- **Revenue by Tier**: Breakdown of revenue by subscription tier
- **Subscribers by Tier**: Distribution of users across subscription tiers

### 2. User Management
- View all users with their subscription details
- Filter and search users
- Display key metrics:
  - User ID
  - Subscription tier
  - Account status
  - Start date
  - Profit sharing balance
  - Total profits shared

### 3. Subscriber Details
- Detailed view of each subscriber
- Feature access breakdown
- Subscription status tracking
- Usage metrics per user

### 4. Pricing & Plans Management
- View current pricing for all tiers
- Update pricing for individual tiers
- View feature breakdown per tier
- Real-time pricing updates

## Admin API Endpoints

### Authentication
All admin endpoints require an admin token in the Authorization header:
```
Authorization: Bearer admin-token
```

### 1. Get All Users
**GET** `/api/v1/admin/users`

Returns a list of all users with their subscription details.

**Response:**
```json
{
  "users": [
    {
      "user_id": "user_001",
      "tier": "professional",
      "status": "active",
      "start_date": "2024-01-01T00:00:00",
      "end_date": null,
      "profit_sharing_balance": 150.75,
      "total_profits_shared": 450.25
    }
  ],
  "total_users": 1,
  "timestamp": "2024-10-05T12:00:00"
}
```

### 2. Get Revenue Analytics
**GET** `/api/v1/admin/analytics/revenue`

Get revenue analytics including MRR and breakdown by tier.

**Response:**
```json
{
  "monthly_recurring_revenue": 1449.95,
  "revenue_by_tier": {
    "free": 0.0,
    "basic": 49.99,
    "professional": 399.98,
    "enterprise": 999.99
  },
  "subscribers_by_tier": {
    "free": 1,
    "basic": 1,
    "professional": 2,
    "enterprise": 1
  },
  "timestamp": "2024-10-05T12:00:00"
}
```

### 3. Get User Analytics
**GET** `/api/v1/admin/analytics/users`

Get user growth and distribution analytics.

**Response:**
```json
{
  "total_users": 5,
  "by_status": {
    "active": 4,
    "trial": 1
  },
  "by_tier": {
    "free": 1,
    "basic": 1,
    "professional": 2,
    "enterprise": 1
  },
  "timestamp": "2024-10-05T12:00:00"
}
```

### 4. Update Pricing
**POST** `/api/v1/admin/pricing/update`

Update pricing for a specific tier.

**Request:**
```json
{
  "tier": "professional",
  "new_price": 249.99
}
```

**Response:**
```json
{
  "tier": "professional",
  "old_price": 199.99,
  "new_price": 249.99,
  "timestamp": "2024-10-05T12:00:00"
}
```

### 5. Update User Subscription
**POST** `/api/v1/admin/subscription/update`

Update a user's subscription tier (admin override).

**Request:**
```json
{
  "user_id": "user_001",
  "new_tier": "enterprise"
}
```

**Response:**
```json
{
  "user_id": "user_001",
  "old_tier": "professional",
  "new_tier": "enterprise",
  "status": "active",
  "timestamp": "2024-10-05T12:00:00"
}
```

### 6. Get Subscribers
**GET** `/api/v1/admin/subscribers?tier={tier}&status={status}`

Get filtered list of subscribers with detailed information.

**Query Parameters:**
- `tier` (optional): Filter by tier (free, basic, professional, enterprise)
- `status` (optional): Filter by status (active, trial, canceled, expired)

**Response:**
```json
{
  "subscribers": [
    {
      "user_id": "user_001",
      "tier": "professional",
      "status": "active",
      "start_date": "2024-01-01T00:00:00",
      "end_date": null,
      "profit_sharing_balance": 150.75,
      "total_profits_shared": 450.25,
      "features": {
        "max_concurrent_trades": 10,
        "max_strategies": 8,
        "day_trading": true,
        "api_access": true
      }
    }
  ],
  "count": 1,
  "filters": {
    "tier": "professional",
    "status": "active"
  },
  "timestamp": "2024-10-05T12:00:00"
}
```

## Frontend Setup

### Environment Variables
Create a `.env` file in the `dashboard` directory:
```
REACT_APP_API_URL=http://localhost:8000
```

### Running the Dashboard

1. Install dependencies:
```bash
cd dashboard
npm install
```

2. Start development server:
```bash
npm start
```

3. Build for production:
```bash
npm run build
```

## Usage Examples

### Starting the Backend API
```bash
python sentio/ui/api.py
```

### Using the Admin Dashboard
1. Navigate to `http://localhost:3001`
2. Use the tab navigation to switch between sections
3. Update pricing by selecting a tier and entering a new price
4. View analytics in real-time

## Security Notes

⚠️ **Important Security Considerations:**

1. **Authentication**: The current implementation uses a placeholder admin token. In production:
   - Implement proper JWT token verification
   - Add role-based access control (RBAC)
   - Use secure token storage

2. **Authorization**: 
   - Verify admin role in token claims
   - Implement proper session management
   - Add rate limiting for admin endpoints

3. **Data Protection**:
   - Use HTTPS in production
   - Implement CORS restrictions
   - Add request validation and sanitization

## Customization

### Adding New Analytics
Edit `sentio/ui/api.py` and add new endpoints under the `# Admin Endpoints` section.

### Modifying UI Components
Edit `dashboard/src/App.js` to add new tabs or modify existing components.

### Styling
Modify `dashboard/src/App.css` to customize the dashboard appearance.

## Troubleshooting

### API Connection Issues
- Ensure the backend API is running on port 8000
- Check that CORS is properly configured
- Verify the `REACT_APP_API_URL` environment variable

### No Data Showing
- Create test users using the subscription manager
- Ensure admin token is properly formatted
- Check browser console for error messages

### Build Errors
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check for Node.js version compatibility

## Next Steps

1. **Database Integration**: Add persistent storage for user data
2. **Real-time Updates**: Implement WebSocket for live analytics
3. **Enhanced Filtering**: Add more filter options for users and subscribers
4. **Export Features**: Add CSV/PDF export for analytics and reports
5. **User Actions**: Add ability to suspend/activate users directly from dashboard
6. **Email Integration**: Send notifications for tier changes or payment issues
7. **Audit Logs**: Track all admin actions for compliance

## Support

For issues or questions, please refer to:
- Main README: `README.md`
- API Documentation: `DASHBOARD_API.md`
- Architecture Guide: `ARCHITECTURE.md`
