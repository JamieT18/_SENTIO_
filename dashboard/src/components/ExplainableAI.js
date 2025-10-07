import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function ExplainableAI({ userId }) {
  const [explanations, setExplanations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchExplanations() {
      try {
        setLoading(true);
        // Replace with actual API call for explainable AI
        const result = await api.getAiSummary();
        setExplanations(result.explanations || []);
        setError(null);
      } catch (err) {
        setError('Failed to load AI explanations');
      } finally {
        setLoading(false);
      }
    }
    fetchExplanations();
  }, [userId]);

  if (loading) return <div className="explainable-ai-widget">Loading explanations...</div>;
  if (error) return <div className="explainable-ai-widget error">{error}</div>;

  return (
    <div className="explainable-ai-widget">
      <h3>Explainable AI Insights</h3>
      {explanations.length === 0 ? (
        <div>No explanations available.</div>
      ) : (
        <ul>
          {explanations.map((exp, idx) => (
            <li key={idx}>
              <strong>{exp.title || exp.symbol}</strong>: {exp.text || exp.explanation}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
