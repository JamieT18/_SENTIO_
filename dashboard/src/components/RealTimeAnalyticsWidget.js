import React, { useEffect, useState } from 'react';

export default function RealTimeAnalyticsWidget({ userId }) {
  const [analytics, setAnalytics] = useState({
    price: 0,
    volume: 0,
    volatility: 0,
    timestamp: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simulate real-time data stream
    const interval = setInterval(() => {
      setAnalytics({
        price: (100 + Math.random() * 20).toFixed(2),
        volume: Math.floor(1000 + Math.random() * 500),
        volatility: (Math.random() * 2.5).toFixed(2),
        timestamp: new Date().toLocaleTimeString()
      });
      setLoading(false);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="realtime-analytics-widget">
      <h3>Real-Time Market Analytics</h3>
      {loading ? (
        <div>Loading analytics...</div>
      ) : (
        <ul className="analytics-list">
          <li><strong>Price:</strong> ${analytics.price}</li>
          <li><strong>Volume:</strong> {analytics.volume}</li>
          <li><strong>Volatility:</strong> {analytics.volatility}%</li>
          <li><strong>Timestamp:</strong> {analytics.timestamp}</li>
        </ul>
      )}
    </div>
  );
}
