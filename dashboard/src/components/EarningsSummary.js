import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { dashboardApi } from '../services/api';
import { useEarningsWebSocket } from '../hooks/useWebSocket';

const EarningsSummary = ({ userId, useWebSocket = true }) => {
  const [earnings, setEarnings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // WebSocket integration
  const wsData = useEarningsWebSocket(useWebSocket ? userId : null);

  // Use WebSocket data if available
  useEffect(() => {
    if (useWebSocket && wsData.earnings) {
      setEarnings(wsData.earnings);
      setLoading(wsData.loading);
      setError(wsData.error);
    }
  }, [useWebSocket, wsData.earnings, wsData.loading, wsData.error]);

  // Memoized fetch function
  const fetchEarnings = useCallback(async () => {
    try {
      setLoading(true);
      const data = await dashboardApi.getEarnings(userId);
      setEarnings(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching earnings:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Fallback to REST API if WebSocket is disabled or not connected
  useEffect(() => {
    if (!useWebSocket || !wsData.isConnected) {
      if (userId) {
        fetchEarnings();
      }
    }
  }, [userId, useWebSocket, wsData.isConnected, fetchEarnings]);

  // Memoized earnings grid rendering
  const earningsGrid = useMemo(() => {
    if (!earnings) return null;

    return (
      <div className="earnings-grid">
        <div className="earnings-item">
          <div className="earnings-label">Portfolio Value</div>
          <div className="earnings-value">${earnings.portfolio_value?.toFixed(2)}</div>
        </div>
        <div className="earnings-item">
          <div className="earnings-label">Total Return</div>
          <div className="earnings-value">${earnings.total_return?.toFixed(2)}</div>
          <div className="earnings-percentage">{earnings.total_return_pct?.toFixed(2)}%</div>
        </div>
        <div className="earnings-item">
          <div className="earnings-label">Daily P&L</div>
          <div className={`earnings-value ${earnings.daily_pnl >= 0 ? 'positive' : 'negative'}`}>
            ${earnings.daily_pnl?.toFixed(2)}
          </div>
        </div>
        <div className="earnings-item">
          <div className="earnings-label">Win Rate</div>
          <div className="earnings-value">{(earnings.win_rate * 100)?.toFixed(1)}%</div>
        </div>
        <div className="earnings-item">
          <div className="earnings-label">Total Trades</div>
          <div className="earnings-value">{earnings.total_trades}</div>
        </div>
        {earnings.profit_sharing && earnings.profit_sharing.enabled && (
          <div className="earnings-item profit-sharing">
            <div className="earnings-label">Profit Sharing</div>
            <div className="earnings-value">${earnings.profit_sharing.total_shared?.toFixed(2)}</div>
            <div className="earnings-detail">Rate: {(earnings.profit_sharing.rate * 100)}%</div>
          </div>
        )}
      </div>
    );
  }, [earnings]);

  if (loading) {
    return <div className="earnings-summary loading">Loading earnings...</div>;
  }

  if (error) {
    return <div className="earnings-summary error">Error: {error}</div>;
  }

  if (!earnings) {
    return null;
  }

  return (
    <div className="earnings-summary">
      <h2>
        Earnings Summary
        {useWebSocket && wsData.isConnected && (
          <span className="live-indicator" title="Live updates enabled">🟢</span>
        )}
      </h2>
      {earningsGrid}
    </div>
  );
};

// Memoize component to prevent unnecessary re-renders
export default React.memo(EarningsSummary);
