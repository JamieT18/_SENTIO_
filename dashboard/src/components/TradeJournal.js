import React, { useState, useEffect } from 'react';
import { dashboardApi } from '../services/api';
import './TradeJournal.css';

const TradeJournal = ({ userId, limit = 10 }) => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJournal = async () => {
      try {
        setLoading(true);
        const data = await dashboardApi.getTradeJournal(userId, limit);
        setEntries(data.entries || []);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching trade journal:', err);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchJournal();
    }
  }, [userId, limit]);

  if (loading) {
    return <div className="trade-journal loading">Loading trade history...</div>;
  }

  if (error) {
    return <div className="trade-journal error">Error: {error}</div>;
  }

  return (
    <div className="trade-journal">
      <h2>Recent Trades</h2>
      {entries.length === 0 ? (
        <p>No trades to display</p>
      ) : (
        <div className="journal-table">
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Action</th>
                <th>Quantity</th>
                <th>Entry Price</th>
                <th>Exit Price</th>
                <th>P&L</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, index) => (
                <tr key={index}>
                  <td>{entry.symbol}</td>
                  <td className={`action ${entry.action}`}>{entry.action}</td>
                  <td>{entry.quantity}</td>
                  <td>${entry.entry_price?.toFixed(2)}</td>
                  <td>${entry.exit_price?.toFixed(2)}</td>
                  <td className={entry.pnl >= 0 ? 'positive' : 'negative'}>
                    ${entry.pnl?.toFixed(2)}
                  </td>
                  <td>{new Date(entry.timestamp).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TradeJournal;
