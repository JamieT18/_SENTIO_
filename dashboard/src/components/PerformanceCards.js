import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { dashboardApi } from '../services/api';

const PerformanceCards = ({ userId }) => {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Memoized fetch function
  const fetchCards = useCallback(async () => {
    try {
      setLoading(true);
      const data = await dashboardApi.getPerformanceCards(userId);
      setCards(data.cards || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching performance cards:', err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (userId) {
      fetchCards();
    }
  }, [userId, fetchCards]);

  // Memoized card rendering
  const cardElements = useMemo(() => {
    return cards.map((card) => (
      <div key={card.id} className="card">
        <h3>{card.title}</h3>
        <div className="card-value">{card.value}</div>
        {card.subtitle && <div className="card-subtitle">{card.subtitle}</div>}
        {card.change_label && (
          <div className={`card-change ${card.trend}`}>
            {card.change_label}
          </div>
        )}
      </div>
    ));
  }, [cards]);

  if (loading) {
    return <div className="performance-cards loading">Loading performance data...</div>;
  }

  if (error) {
    return <div className="performance-cards error">Error: {error}</div>;
  }

  return (
    <div className="performance-cards">
      <h2>Performance Overview</h2>
      <div className="cards-grid">
        {cardElements}
      </div>
    </div>
  );
};

// Memoize component to prevent unnecessary re-renders
export default React.memo(PerformanceCards);
