import React, { useState, useEffect } from 'react';
import { dashboardApi } from '../services/api';

const AiSummary = ({ symbol }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        const data = await dashboardApi.getAiSummary(symbol);
        setSummary(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching AI summary:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, [symbol]);

  if (loading) {
    return <div className="ai-summary loading">Loading AI insights...</div>;
  }

  if (error) {
    return <div className="ai-summary error">Error: {error}</div>;
  }

  if (!summary) {
    return null;
  }

  return (
    <div className="ai-summary">
      <h2>AI Trading Insights</h2>
      {summary.symbol && (
        <div className="summary-header">
          <h3>{summary.symbol}</h3>
          <div className={`recommendation ${summary.recommendation}`}>
            {summary.recommendation?.toUpperCase()}
          </div>
          <div className="confidence">
            Confidence: {(summary.confidence * 100)?.toFixed(1)}%
          </div>
        </div>
      )}
      <div className="summary-content">
        {summary.reasoning && (
          <div className="reasoning">
            <h4>Analysis</h4>
            <p>{summary.reasoning}</p>
          </div>
        )}
        {summary.summary && (
          <div className="market-summary">
            <h4>Market Overview</h4>
            <p>{summary.summary}</p>
          </div>
        )}
        {summary.key_factors && summary.key_factors.length > 0 && (
          <div className="key-factors">
            <h4>Key Factors</h4>
            <ul>
              {summary.key_factors.map((factor, index) => (
                <li key={index}>{factor}</li>
              ))}
            </ul>
          </div>
        )}
        {summary.key_metrics && (
          <div className="key-metrics">
            <h4>Key Metrics</h4>
            <div className="metrics-grid">
              {Object.entries(summary.key_metrics).map(([key, value]) => (
                <div key={key} className="metric-item">
                  <div className="metric-label">{key.replace(/_/g, ' ')}</div>
                  <div className="metric-value">{value}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AiSummary;
