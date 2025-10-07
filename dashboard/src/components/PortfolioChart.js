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

const PortfolioChart = ({ userId, days = 30 }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.getPortfolioHistory(userId, days);
        
        // Format data for chart
        const chartData = response.history.map(item => ({
          date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          value: item.portfolio_value,
          change: item.daily_change
        }));
        
        setData(chartData);
        setSummary(response.summary);
        setError(null);
      } catch (err) {
        console.error('Error fetching portfolio history:', err);
        setError('Failed to load portfolio history');
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchData();
    }
  }, [userId, days]);

  if (loading) {
    return <div className="chart-loading">Loading chart...</div>;
  }

  if (error) {
    return <div className="chart-error">{error}</div>;
  }

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
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p className="label" style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>
            {payload[0].payload.date}
          </p>
          <p style={{ margin: '0', color: '#8884d8' }}>
            Value: {formatCurrency(payload[0].value)}
          </p>
          {payload[0].payload.change !== undefined && (
            <p style={{ 
              margin: '5px 0 0 0', 
              color: payload[0].payload.change >= 0 ? '#00C49F' : '#FF6B6B' 
            }}>
              Change: {formatCurrency(payload[0].payload.change)} 
              ({payload[0].payload.change >= 0 ? '+' : ''}{((payload[0].payload.change / payload[0].value) * 100).toFixed(2)}%)
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="portfolio-chart">
      <div className="chart-header">
        <h3>Portfolio Performance ({days} Days)</h3>
        {summary && (
          <div className="chart-summary">
            <div className="summary-item">
              <span className="summary-label">Total Return:</span>
              <span className={`summary-value ${summary.total_return >= 0 ? 'positive' : 'negative'}`}>
                {formatCurrency(summary.total_return)} ({summary.total_return_pct >= 0 ? '+' : ''}{summary.total_return_pct.toFixed(2)}%)
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Best Day:</span>
              <span className="summary-value positive">
                +{summary.best_day.daily_change_pct.toFixed(2)}%
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Worst Day:</span>
              <span className="summary-value negative">
                {summary.worst_day.daily_change_pct.toFixed(2)}%
              </span>
            </div>
          </div>
        )}
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            tickFormatter={formatCurrency}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area 
            type="monotone" 
            dataKey="value" 
            stroke="#8884d8" 
            fillOpacity={1} 
            fill="url(#colorValue)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PortfolioChart;
