import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { dashboardApi } from '../services/api';
import { useTradeSignalsWebSocket } from '../hooks/useWebSocket';

const TradeSignals = ({ symbols, userId, useWebSocket = true }) => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // WebSocket integration
  const wsData = useTradeSignalsWebSocket(
    useWebSocket ? symbols : [],
    userId || 'anonymous'
  );

  // Use WebSocket data if available, otherwise fall back to polling
  useEffect(() => {
    if (useWebSocket && wsData.signals && wsData.signals.length > 0) {
      setSignals(wsData.signals);
      setLoading(wsData.loading);
      setError(wsData.error);
    }
  }, [useWebSocket, wsData.signals, wsData.loading, wsData.error]);

  // Memoized fetch function to prevent recreating on every render
  const fetchSignals = useCallback(async () => {
    try {
      setLoading(true);
      const data = await dashboardApi.getTradeSignals(symbols);
      setSignals(data.signals || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching trade signals:', err);
    } finally {
      setLoading(false);
    }
  }, [symbols]);

  // Fallback to REST API polling if WebSocket is disabled or not connected
  useEffect(() => {
    if (!useWebSocket || !wsData.isConnected) {
      fetchSignals();
      // Refresh signals every 30 seconds as fallback
      const interval = setInterval(fetchSignals, 30000);
      return () => clearInterval(interval);
    }
  }, [fetchSignals, useWebSocket, wsData.isConnected]);

  // Memoized signal color function
  const getSignalColor = useCallback((signal) => {
    switch (signal) {
      case 'buy':
        return 'green';
      case 'sell':
        return 'red';
      case 'hold':
        return 'gray';
      default:
        return 'orange';
    }
  }, []);

  // Memoized signals rendering to prevent unnecessary re-renders
  const signalItems = useMemo(() => {
    return signals.map((signal, index) => (
      <div key={`${signal.symbol}-${index}`} className="signal-item">
        <div className="signal-symbol">{signal.symbol}</div>
        <div className={`signal-action ${getSignalColor(signal.signal)}`}>
          {signal.signal.toUpperCase()}
        </div>
        <div className="signal-confidence">
          Confidence: {(signal.confidence * 100).toFixed(1)}%
        </div>
        {signal.consensus_strength && (
          <div className="signal-consensus">
            Consensus: {(signal.consensus_strength * 100).toFixed(1)}%
          </div>
        )}
      </div>
    ));
  }, [signals, getSignalColor]);

  if (loading) {
    return <div className="trade-signals loading">Loading trade signals...</div>;
  }

  if (error) {
    return <div className="trade-signals error">Error: {error}</div>;
  }

  return (
    <div className="trade-signals">
      <h2>
        Trade Signals
        {useWebSocket && wsData.isConnected && (
          <span className="live-indicator" title="Live updates enabled">🟢</span>
        )}
      </h2>
      <div className="signals-list">
        {signalItems}
      </div>
    </div>
  );
};

// Memoize the component to prevent unnecessary re-renders
export default React.memo(TradeSignals);
