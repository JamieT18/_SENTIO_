import React, { useEffect, useState } from 'react';

export default function RealTimeChartWidget() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simulate real-time chart data
    const interval = setInterval(() => {
      setData(prev => [
        ...prev.slice(-19),
        {
          price: 100 + Math.random() * 20,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
      setLoading(false);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="realtime-chart-widget">
      <h3>Live Price Chart</h3>
      {loading ? (
        <div>Loading chart...</div>
      ) : (
        <svg width="100%" height="120" viewBox="0 0 320 120">
          {data.length > 1 && data.map((point, idx) => {
            if (idx === 0) return null;
            const prev = data[idx - 1];
            return (
              <line
                key={idx}
                x1={16 * (idx - 1)}
                y1={120 - (prev.price - 100) * 5}
                x2={16 * idx}
                y2={120 - (point.price - 100) * 5}
                stroke="#1976d2"
                strokeWidth="2"
              />
            );
          })}
        </svg>
      )}
      <div className="chart-timestamps">
        {data.length > 0 && <span>Latest: {data[data.length - 1].timestamp}</span>}
      </div>
    </div>
  );
}
