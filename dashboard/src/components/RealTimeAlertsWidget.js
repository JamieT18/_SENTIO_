import React, { useEffect, useState } from 'react';

const ALERTS = [
  { type: 'Price Spike', message: 'BTC/USD spiked +5% in 10min!' },
  { type: 'Volume Surge', message: 'ETH/USDT volume up 30% in 5min!' },
  { type: 'Volatility Drop', message: 'SOL/USD volatility dropped below 1%.' }
];

export default function RealTimeAlertsWidget() {
  const [activeAlert, setActiveAlert] = useState(null);

  useEffect(() => {
    // Simulate real-time alerts
    const interval = setInterval(() => {
      setActiveAlert(ALERTS[Math.floor(Math.random() * ALERTS.length)]);
      setTimeout(() => setActiveAlert(null), 1200);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="realtime-alerts-widget">
      <h3>Real-Time Alerts</h3>
      {activeAlert ? (
        <div className={`alert-message ${activeAlert.type.replace(/\s/g, '').toLowerCase()}`}>
          <strong>{activeAlert.type}:</strong> {activeAlert.message}
        </div>
      ) : (
        <div>No active alerts</div>
      )}
    </div>
  );
}
