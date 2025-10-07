import React, { useEffect, useState } from 'react';
import api from '../services/api';
import './DeeperAnalytics.css';

export default function DeeperAnalytics({ userId }) {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchMetrics() {
      try {
        setLoading(true);
        // Replace with actual API call for deeper analytics
        const perf = await api.getPortfolioHistory(userId, 90);
        const trades = await api.getTradePerformance(userId);
        const activity = await api.getUserActivity(userId, 90);
        setMetrics([
          { label: 'Sharpe Ratio', value: perf.summary?.sharpe_ratio },
          { label: 'Sortino Ratio', value: perf.summary?.sortino_ratio },
          { label: 'Max Drawdown', value: perf.summary?.max_drawdown },
          { label: 'Win Rate', value: trades.overall?.overall_win_rate },
          { label: 'Avg Trades/Day', value: activity.summary?.avg_trades_per_day },
          { label: 'Total Session Time (hrs)', value: activity.summary?.total_session_time_hours },
        ]);
        setError(null);
      } catch (err) {
        setError('Failed to load deeper analytics');
      } finally {
        setLoading(false);
      }
    }
    fetchMetrics();
  }, [userId]);

  if (loading) return <div className="deeper-analytics-widget">Loading deeper analytics...</div>;
  if (error) return <div className="deeper-analytics-widget error">{error}</div>;

  return (
    <div className="deeper-analytics-widget">
      <h3>Deeper Analytics</h3>
      <ul>
        {metrics.map((m, idx) => (
          <li key={idx}><strong>{m.label}:</strong> {m.value !== undefined ? m.value : 'N/A'}</li>
        ))}
      </ul>
    </div>
  );
}
