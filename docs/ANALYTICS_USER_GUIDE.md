# Enhanced Analytics and Reporting - User Guide

## What's New

Sentio 2.0 now includes comprehensive analytics and reporting features that give you deep insights into your trading performance.

## Features at a Glance

### 📊 Portfolio Performance
- **Historical tracking** over 7, 30, 60, or 90 days
- **Daily changes** with percentage gains/losses
- **Best and worst days** identification
- **Total return** calculation with percentage
- **Interactive charts** with hover tooltips

### 📈 Trade Analysis
- **Performance by symbol** - see which stocks perform best
- **Win/loss breakdown** - understand your success rate
- **P&L visualization** - color-coded profits and losses
- **Trade distribution** - pie chart of trading activity
- **Detailed statistics** - average wins, losses, and more

### 🗓️ Activity Patterns
- **Calendar heatmap** showing your trading activity
- **Day-of-week analysis** - identify your most productive days
- **Session time tracking** - monitor time spent trading
- **API usage stats** - understand your platform usage
- **Activity trends** - spot patterns in your trading behavior

### 📥 Export & Reporting
- **JSON export** - complete data in structured format
- **CSV export** - open in Excel/Google Sheets
- **Automatic downloads** - one-click report generation
- **Customizable reports** - include or exclude chart data
- **Timestamped files** - organized by date

## How to Access

### For Users

#### Option 1: Integrated Dashboard
```
Navigate to: Dashboard → Analytics & Reports
```

#### Option 2: Using the API Directly
```bash
# Get portfolio history
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/analytics/portfolio-history?user_id=YOUR_ID&days=30"

# Export analytics report
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/export/analytics-report?user_id=YOUR_ID&format=json" \
  --output my_analytics.json
```

### For Admins

#### Admin Analytics Dashboard
```
Navigate to: Admin Dashboard → Analytics Tab
```

View platform-wide metrics:
- User growth over time
- Revenue growth trends
- Daily signup rates
- Active user statistics

## Understanding the Charts

### Portfolio Performance Chart
**What it shows:** Your portfolio value over time

**How to read it:**
- **Blue area** = Portfolio value
- **Higher is better** = More value
- **Trend line** = Growth trajectory
- **Tooltips** = Exact values on hover

**Key metrics:**
- Initial Value: Starting portfolio value
- Final Value: Current portfolio value
- Total Return: Gain/loss in dollars
- Total Return %: Gain/loss as percentage
- Best Day: Highest single-day gain
- Worst Day: Largest single-day loss

### Trade Performance Chart
**What it shows:** Your trading results by symbol

**How to read it:**
- **Green bars** = Profitable symbols
- **Red bars** = Losing symbols
- **Height** = Total P&L amount
- **Pie chart** = Distribution of trades

**Key metrics:**
- Total Trades: Number of completed trades
- Win Rate: Percentage of profitable trades
- Best Performer: Most profitable symbol
- Worst Performer: Least profitable symbol

### Activity Heatmap
**What it shows:** When you trade most actively

**How to read it:**
- **Dark green** = High activity
- **Light green** = Medium activity
- **Gray** = Low/no activity
- **Numbers** = Trades per day

**Key metrics:**
- Total Trades: All trades in period
- Avg Trades/Day: Daily trading average
- Total Session Time: Hours spent trading
- Most Active Day: Peak trading day

## Exporting Reports

### Step-by-Step Guide

1. **Navigate to Analytics Dashboard**
   - Click on "Analytics & Reports" in your dashboard

2. **Select Time Period**
   - Choose from: 7, 30, 60, or 90 days

3. **Review Your Analytics**
   - Browse through the Performance, Trades, and Activity tabs

4. **Export Your Data**
   - Click "Export JSON" for structured data
   - Click "Export CSV" for spreadsheet analysis

5. **Open Your Report**
   - File downloads automatically
   - Filename format: `analytics_report_[userid]_[date].[format]`

### What's Included in Exports

**JSON Format includes:**
```json
{
  "report_metadata": { ... },
  "subscription": { "tier": "professional", "status": "active" },
  "portfolio_summary": {
    "current_value": 105000.00,
    "total_return": 5000.00,
    "total_return_pct": 5.0
  },
  "trading_statistics": {
    "total_trades": 125,
    "win_rate": 0.68,
    "avg_profit": 285.50
  },
  "chart_data": { ... }
}
```

**CSV Format includes:**
```csv
Metric,Value
User ID,user_123
Generated At,2024-10-05T10:30:00
Subscription Tier,professional
Portfolio Value,105000.00
Total Return,5000.00
Total Trades,125
Win Rate,0.68
```

## Interpreting Your Results

### Good Performance Indicators
✅ **Positive total return** - Your portfolio is growing
✅ **Win rate > 50%** - More wins than losses
✅ **Consistent activity** - Regular trading patterns
✅ **Growing portfolio value** - Upward trend line

### Areas to Watch
⚠️ **Negative total return** - Portfolio declining
⚠️ **Win rate < 40%** - Consider strategy adjustment
⚠️ **Volatile daily changes** - High risk levels
⚠️ **Declining activity** - Engagement dropping

### Using Analytics to Improve

1. **Identify Best Symbols**
   - Focus on your top performers
   - Reduce exposure to consistent losers

2. **Find Your Best Trading Days**
   - Trade more on high-success days
   - Understand why certain days work better

3. **Track Progress Over Time**
   - Compare 30-day vs 90-day performance
   - Look for improvement trends

4. **Set Realistic Goals**
   - Use historical data to set targets
   - Track monthly improvements

## Admin Analytics

### Platform Growth Metrics

**User Growth Chart**
- Total users over time
- New signups per day
- Active user trends
- Growth rate percentage

**Revenue Growth Chart**
- Total revenue over time
- Daily revenue increase
- Revenue by tier breakdown
- MRR (Monthly Recurring Revenue)

**Key Insights Cards**
- Average daily user growth
- Average daily revenue
- Current totals
- Growth percentages

## Tips & Best Practices

### 1. Regular Review
- Check analytics weekly
- Compare month-over-month
- Track trend changes

### 2. Export Regularly
- Monthly exports for records
- Share with advisors/accountants
- Keep local backups

### 3. Use Multiple Views
- Portfolio view for big picture
- Trade view for specific symbols
- Activity view for patterns

### 4. Set Baselines
- Know your starting point
- Track from day one
- Measure improvement

### 5. Combine with Strategy
- Use analytics to inform decisions
- Adjust based on data
- Test and measure results

## Troubleshooting

### Charts Not Loading?
1. Check your internet connection
2. Refresh the page
3. Clear browser cache
4. Verify authentication token

### Export Not Working?
1. Disable popup blockers
2. Check browser downloads settings
3. Ensure sufficient disk space
4. Try different format (JSON vs CSV)

### Data Looks Wrong?
1. Verify time period selected
2. Check user ID is correct
3. Ensure recent data is available
4. Contact support if persistent

## Privacy & Security

### Your Data is Protected
- ✅ Encrypted connections (HTTPS)
- ✅ Authentication required
- ✅ User data isolation
- ✅ No sharing without consent

### What We Track
- Portfolio values (daily)
- Trade outcomes (P&L)
- Activity patterns (when you trade)
- Session times (how long)

### What We DON'T Track
- ❌ Specific trade entry/exit points
- ❌ Individual strategy decisions
- ❌ Personal information
- ❌ Third-party integrations

## Getting Help

### Documentation
- **Full API Docs**: `ANALYTICS_FEATURES.md`
- **Technical Guide**: `ANALYTICS_IMPLEMENTATION_SUMMARY.md`
- **Examples**: `examples/analytics_demo.py`

### Support Channels
1. Review the documentation
2. Check troubleshooting section
3. Contact support team
4. Submit GitHub issue

## What's Next

### Upcoming Features
- 🔜 Custom date range selection
- 🔜 Comparative analytics (vs benchmarks)
- 🔜 PDF report generation
- 🔜 Real-time chart updates
- 🔜 AI-powered insights
- 🔜 Mobile app integration

### We Value Your Feedback
Help us improve! Share your thoughts on:
- What analytics are most useful?
- What's missing that you'd like to see?
- How can we make reports better?

---

**Happy Trading! 📈**

For technical details, see [ANALYTICS_FEATURES.md](ANALYTICS_FEATURES.md)
