import React, { useState, useEffect } from 'react';
import api from '../services/api';

const ActivityHeatmap = ({ userId, days = 30 }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.getUserActivity(userId, days);
        setData(response);
        setError(null);
      } catch (err) {
        console.error('Error fetching user activity:', err);
        setError('Failed to load activity data');
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchData();
    }
  }, [userId, days]);

  if (loading) {
    return <div className="chart-loading">Loading activity data...</div>;
  }

  if (error) {
    return <div className="chart-error">{error}</div>;
  }

  if (!data || !data.daily_activity) {
    return <div className="chart-error">No activity data available</div>;
  }

  // Calculate intensity for heatmap coloring
  const maxTrades = Math.max(...data.daily_activity.map(d => d.trades_executed));
  
  const getIntensityColor = (trades) => {
    if (trades === 0) return '#ebedf0';
    const intensity = trades / maxTrades;
    if (intensity < 0.25) return '#c6e48b';
    if (intensity < 0.5) return '#7bc96f';
    if (intensity < 0.75) return '#239a3b';
    return '#196127';
  };

  const dayOfWeekOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <div className="activity-heatmap">
      <div className="chart-header">
        <h3>Trading Activity ({days} Days)</h3>
      </div>

      {data.summary && (
        <div className="activity-summary">
          <div className="summary-item">
            <span className="summary-label">Total Trades:</span>
            <span className="summary-value">{data.summary.total_trades}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Avg Trades/Day:</span>
            <span className="summary-value">{data.summary.avg_trades_per_day.toFixed(1)}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Total Session Time:</span>
            <span className="summary-value">{data.summary.total_session_time_hours.toFixed(1)}h</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Most Active:</span>
            <span className="summary-value">
              {new Date(data.summary.most_active_day.date).toLocaleDateString()}
            </span>
          </div>
        </div>
      )}

      <div className="heatmap-container">
        <div className="heatmap-grid">
          {data.daily_activity.map((day, index) => (
            <div
              key={index}
              className="heatmap-cell"
              style={{
                backgroundColor: getIntensityColor(day.trades_executed)
              }}
              title={`${day.date}: ${day.trades_executed} trades`}
            >
              <div className="cell-date">{new Date(day.date).getDate()}</div>
              <div className="cell-value">{day.trades_executed}</div>
            </div>
          ))}
        </div>
        
        <div className="heatmap-legend">
          <span>Less</span>
          <div className="legend-colors">
            <div className="legend-color" style={{ backgroundColor: '#ebedf0' }}></div>
            <div className="legend-color" style={{ backgroundColor: '#c6e48b' }}></div>
            <div className="legend-color" style={{ backgroundColor: '#7bc96f' }}></div>
            <div className="legend-color" style={{ backgroundColor: '#239a3b' }}></div>
            <div className="legend-color" style={{ backgroundColor: '#196127' }}></div>
          </div>
          <span>More</span>
        </div>
      </div>

      {data.by_day_of_week && (
        <div className="day-of-week-breakdown">
          <h4>Activity by Day of Week</h4>
          <div className="day-breakdown-grid">
            {dayOfWeekOrder.map(day => {
              const dayData = data.by_day_of_week[day];
              if (!dayData) return null;
              
              return (
                <div key={day} className="day-breakdown-item">
                  <div className="day-name">{day.slice(0, 3)}</div>
                  <div className="day-trades">{dayData.avg_trades.toFixed(1)}</div>
                  <div className="day-label">avg trades</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityHeatmap;
