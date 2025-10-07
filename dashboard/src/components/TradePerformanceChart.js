import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import api from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658'];

const TradePerformanceChart = ({ userId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartType, setChartType] = useState('bar'); // 'bar' or 'pie'

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.getTradePerformance(userId);
        setData(response);
        setError(null);
      } catch (err) {
        console.error('Error fetching trade performance:', err);
        setError('Failed to load trade performance data');
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchData();
    }
  }, [userId]);

  if (loading) {
    return <div className="chart-loading">Loading trade performance...</div>;
  }

  if (error) {
    return <div className="chart-error">{error}</div>;
  }

  if (!data || !data.by_symbol) {
    return <div className="chart-error">No trade data available</div>;
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
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip" style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <p className="label" style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>
            {data.symbol}
          </p>
          <p style={{ margin: '0', color: data.total_pnl >= 0 ? '#00C49F' : '#FF6B6B' }}>
            P&L: {formatCurrency(data.total_pnl)}
          </p>
          <p style={{ margin: '5px 0 0 0' }}>
            Trades: {data.total_trades} ({data.wins}W / {data.losses}L)
          </p>
          <p style={{ margin: '5px 0 0 0' }}>
            Win Rate: {(data.win_rate * 100).toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data.by_symbol} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="symbol" tick={{ fontSize: 12 }} />
        <YAxis tickFormatter={formatCurrency} tick={{ fontSize: 12 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar dataKey="total_pnl" name="Total P&L">
          {data.by_symbol.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.total_pnl >= 0 ? '#00C49F' : '#FF6B6B'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );

  const renderPieChart = () => {
    const pieData = data.by_symbol.map(item => ({
      name: item.symbol,
      value: item.total_trades
    }));

    return (
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="trade-performance-chart">
      <div className="chart-header">
        <h3>Trade Performance by Symbol</h3>
        <div className="chart-controls">
          <button 
            onClick={() => setChartType('bar')} 
            className={chartType === 'bar' ? 'active' : ''}
          >
            P&L Chart
          </button>
          <button 
            onClick={() => setChartType('pie')} 
            className={chartType === 'pie' ? 'active' : ''}
          >
            Distribution
          </button>
        </div>
      </div>

      {data.overall && (
        <div className="performance-summary">
          <div className="summary-card">
            <span className="summary-label">Total Trades</span>
            <span className="summary-value">{data.overall.total_trades}</span>
          </div>
          <div className="summary-card">
            <span className="summary-label">Win Rate</span>
            <span className="summary-value">{(data.overall.overall_win_rate * 100).toFixed(1)}%</span>
          </div>
          <div className="summary-card">
            <span className="summary-label">Total P&L</span>
            <span className={`summary-value ${data.overall.total_pnl >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(data.overall.total_pnl)}
            </span>
          </div>
          <div className="summary-card">
            <span className="summary-label">Best Performer</span>
            <span className="summary-value">{data.overall.best_performer.symbol}</span>
          </div>
        </div>
      )}

      {chartType === 'bar' ? renderBarChart() : renderPieChart()}
    </div>
  );
};

export default TradePerformanceChart;
