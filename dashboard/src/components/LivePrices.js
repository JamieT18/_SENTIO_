import React, { useState, useEffect, useRef } from 'react';
import './LivePrices.css';

const LivePrices = ({ symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA'] }) => {
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const wsRef = useRef(null);

  useEffect(() => {
    // WebSocket connection setup
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/market-data';
    
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('WebSocket connected');
          setConnectionStatus('connected');
          setError(null);
          
          // Subscribe to symbols
          ws.send(JSON.stringify({
            action: 'subscribe',
            symbols: symbols
          }));
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'quotes' || data.type === 'update') {
              const newPrices = {};
              data.data.forEach(quote => {
                newPrices[quote.symbol] = quote;
              });
              
              setPrices(prevPrices => ({
                ...prevPrices,
                ...newPrices
              }));
              
              setLoading(false);
            } else if (data.type === 'error') {
              console.error('WebSocket error:', data.message);
              setError(data.message);
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('Connection error. Retrying...');
          setConnectionStatus('error');
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setConnectionStatus('disconnected');
          
          // Attempt to reconnect after 5 seconds
          setTimeout(() => {
            if (wsRef.current?.readyState === WebSocket.CLOSED) {
              connectWebSocket();
            }
          }, 5000);
        };
      } catch (err) {
        console.error('Error creating WebSocket:', err);
        setError('Failed to establish connection');
        setConnectionStatus('error');
      }
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [symbols]);

  const getChangeColor = (change) => {
    if (change > 0) return 'positive';
    if (change < 0) return 'negative';
    return 'neutral';
  };

  const formatPrice = (price) => {
    return price ? `$${price.toFixed(2)}` : '--';
  };

  const formatChange = (change, changePct) => {
    if (change === undefined || changePct === undefined) return '--';
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)} (${sign}${changePct.toFixed(2)}%)`;
  };

  if (loading && connectionStatus === 'disconnected') {
    return <div className="live-prices loading">Connecting to market data...</div>;
  }

  return (
    <div className="live-prices">
      <div className="live-prices-header">
        <h2>Live Market Prices</h2>
        <div className={`connection-status ${connectionStatus}`}>
          <span className="status-indicator"></span>
          {connectionStatus === 'connected' ? 'Live' : 
           connectionStatus === 'error' ? 'Error' : 'Disconnected'}
        </div>
      </div>

      {error && (
        <div className="live-prices-error">
          {error}
        </div>
      )}

      <div className="prices-grid">
        {symbols.map(symbol => {
          const quote = prices[symbol];
          
          if (!quote) {
            return (
              <div key={symbol} className="price-card loading-card">
                <div className="price-symbol">{symbol}</div>
                <div className="price-loading">Loading...</div>
              </div>
            );
          }

          return (
            <div key={symbol} className="price-card">
              <div className="price-header">
                <div className="price-symbol">{quote.symbol}</div>
                <div className="price-timestamp">
                  {new Date(quote.timestamp).toLocaleTimeString()}
                </div>
              </div>
              
              <div className="price-main">
                <div className="price-value">
                  {formatPrice(quote.price)}
                </div>
                <div className={`price-change ${getChangeColor(quote.change)}`}>
                  {formatChange(quote.change, quote.change_pct)}
                </div>
              </div>

              <div className="price-details">
                <div className="price-detail">
                  <span className="label">High:</span>
                  <span className="value">{formatPrice(quote.high)}</span>
                </div>
                <div className="price-detail">
                  <span className="label">Low:</span>
                  <span className="value">{formatPrice(quote.low)}</span>
                </div>
                <div className="price-detail">
                  <span className="label">Volume:</span>
                  <span className="value">
                    {quote.volume ? (quote.volume / 1000000).toFixed(2) + 'M' : '--'}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LivePrices;
