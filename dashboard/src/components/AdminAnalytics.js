import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import api from '../services/api';
import './AdminAnalytics.css';

const AdminAnalytics = () => {
  const [growthData, setGrowthData] = useState(null);
  const [timePeriod, setTimePeriod] = useState(90);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartType, setChartType] = useState('users'); // 'users' or 'revenue'

  useEffect(() => {
    fetchGrowthData();
  }, [timePeriod]);

  const fetchGrowthData = async () => {
    try {
      setLoading(true);
      const response = await api.getHistoricalGrowth(timePeriod);
      setGrowthData(response);
      setError(null);
    } catch (err) {
      console.error('Error fetching growth data:', err);
      setError('Failed to load historical growth data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          padding: '12px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: 'bold' }}>
            {new Date(data.date).toLocaleDateString()}
          </p>
          <p style={{ margin: '0', color: '#8884d8' }}>
            Total Users: {data.total_users}
          </p>
          <p style={{ margin: '5px 0 0 0', color: '#82ca9d' }}>
            New Users: {data.new_users}
          </p>
          <p style={{ margin: '5px 0 0 0', color: '#ffc658' }}>
            Active Users: {data.active_users}
          </p>
          <p style={{ margin: '5px 0 0 0', color: '#ff7c7c' }}>
            Revenue: {formatCurrency(data.total_revenue)}
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return <div className="admin-analytics-loading">Loading analytics...</div>;
  }

  if (error) {
    return <div className="admin-analytics-error">{error}</div>;
  }

  if (!growthData || !growthData.history) {
    return <div className="admin-analytics-error">No data available</div>;
  }

  const chartData = growthData.history.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    users: item.total_users,
    newUsers: item.new_users,
    activeUsers: item.active_users,
    revenue: item.total_revenue
  }));

  return (
    <div className="admin-analytics">
      <div className="admin-analytics-header">
        <h2>Historical Growth Analytics</h2>
        <div className="analytics-controls">
          <div className="time-selector">
            <label>Time Period:</label>
            <select value={timePeriod} onChange={(e) => setTimePeriod(Number(e.target.value))}>
              <option value={30}>30 Days</option>
              <option value={60}>60 Days</option>
              <option value={90}>90 Days</option>
              <option value={180}>180 Days</option>
            </select>
          </div>
          <div className="chart-type-selector">
            <button
              className={chartType === 'users' ? 'active' : ''}
              onClick={() => setChartType('users')}
            >
              User Growth
            </button>
            <button
              className={chartType === 'revenue' ? 'active' : ''}
              onClick={() => setChartType('revenue')}
            >
              Revenue Growth
            </button>
          </div>
        </div>
      </div>

      {growthData.summary && (
        <div className="growth-summary">
          <div className="summary-card">
            <div className="summary-label">User Growth</div>
            <div className="summary-value">
              {growthData.summary.total_growth}
              <span className="summary-change">
                +{((growthData.summary.total_growth / growthData.summary.starting_users) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="summary-subtitle">
              {growthData.summary.starting_users} → {growthData.summary.current_users}
            </div>
          </div>
          <div className="summary-card">
            <div className="summary-label">Revenue Growth</div>
            <div className="summary-value">
              {formatCurrency(growthData.summary.revenue_growth)}
              <span className="summary-change">
                +{((growthData.summary.revenue_growth / growthData.summary.starting_revenue) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="summary-subtitle">
              {formatCurrency(growthData.summary.starting_revenue)} → {formatCurrency(growthData.summary.current_revenue)}
            </div>
          </div>
        </div>
      )}

      <div className="growth-chart">
        {chartType === 'users' ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="users" 
                name="Total Users"
                stroke="#8884d8" 
                strokeWidth={2}
                dot={{ r: 3 }}
              />
              <Line 
                type="monotone" 
                dataKey="activeUsers" 
                name="Active Users"
                stroke="#ffc658" 
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ff7c7c" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#ff7c7c" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={formatCurrency} tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="revenue" 
                name="Total Revenue"
                stroke="#ff7c7c" 
                fillOpacity={1}
                fill="url(#colorRevenue)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="growth-insights">
        <h3>Key Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon">📈</div>
            <div className="insight-content">
              <div className="insight-title">Average Daily Growth</div>
              <div className="insight-value">
                {(growthData.summary.total_growth / timePeriod).toFixed(1)} users/day
              </div>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-icon">💰</div>
            <div className="insight-content">
              <div className="insight-title">Average Daily Revenue</div>
              <div className="insight-value">
                {formatCurrency(growthData.summary.revenue_growth / timePeriod)}/day
              </div>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-icon">👥</div>
            <div className="insight-content">
              <div className="insight-title">Current Total Users</div>
              <div className="insight-value">
                {growthData.summary.current_users}
              </div>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-icon">💵</div>
            <div className="insight-content">
              <div className="insight-title">Current Total Revenue</div>
              <div className="insight-value">
                {formatCurrency(growthData.summary.current_revenue)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminAnalytics;
