import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function SafetyRiskWidget({ userId }) {
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchDashboardSummary() {
      setLoading(true);
      setError(null);
      try {
        const summary = await api.getRiskDashboardSummary(userId);
        setDashboardSummary(summary);
      } catch (err) {
        setError('Failed to load risk dashboard summary');
      } finally {
        setLoading(false);
      }
    }
    fetchDashboardSummary();
  }, [userId]);

  if (loading) return <div className="safety-risk-widget">Loading safety & risk...</div>;
  if (error) return <div className="safety-risk-widget error">{error}</div>;

  return (
    <div className="safety-risk-widget">
      <h3>Safety & Risk</h3>
      {dashboardSummary && (
        <>
          <div className="risk-section">
            <strong>Key Metrics:</strong>
            <ul>
              {Object.entries(dashboardSummary).filter(([k]) => !['recent_events','mitigation_recommendations','scenario_simulation'].includes(k)).map(([k, v]) => (
                <li key={k}>{k}: <span>{typeof v === 'number' ? v.toFixed(3) : v}</span></li>
              ))}
            </ul>
          </div>
          {dashboardSummary.recent_events && dashboardSummary.recent_events.length > 0 && (
            <div className="risk-section">
              <strong>Recent Risk Events:</strong>
              <ul>
                {dashboardSummary.recent_events.map((event, idx) => (
                  <li key={idx}>{event.type}: <span>{event.message || event.state || event.value}</span> <span style={{color:'#64748b'}}>{event.timestamp}</span></li>
                ))}
              </ul>
            </div>
          )}
          {dashboardSummary.mitigation_recommendations && dashboardSummary.mitigation_recommendations.length > 0 && (
            <div className="risk-section">
              <strong>Mitigation Recommendations:</strong>
              <ul>
                {dashboardSummary.mitigation_recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
          {dashboardSummary.scenario_simulation && dashboardSummary.scenario_simulation.length > 0 && (
            <div className="risk-section">
              <strong>Scenario Simulation:</strong>
              <ul>
                {dashboardSummary.scenario_simulation.map((sim, idx) => (
                  <li key={idx}>{sim.scenario}: <span>{sim.impact.toFixed(2)}</span></li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}
