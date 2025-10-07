import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function AIRecommendations({ userId }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchRecommendations() {
      try {
        setLoading(true);
        // Replace with actual API call for AI recommendations
        const result = await api.getAiSummary();
        setRecommendations(result.recommendations || []);
        setError(null);
      } catch (err) {
        setError('Failed to load AI recommendations');
      } finally {
        setLoading(false);
      }
    }
    fetchRecommendations();
  }, [userId]);

  if (loading) return <div className="ai-recommendations-widget">Loading AI recommendations...</div>;
  if (error) return <div className="ai-recommendations-widget error">{error}</div>;

  return (
    <div className="ai-recommendations-widget">
      <h3>AI-Powered Recommendations</h3>
      {recommendations.length === 0 ? (
        <div>No recommendations available.</div>
      ) : (
        <ul>
          {recommendations.map((rec, idx) => (
            <li key={idx}>
              <strong>{rec.title || rec.symbol}</strong>: {rec.text || rec.recommendation}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
