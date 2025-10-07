import React, { useState } from 'react';

const SIGNALS = [
  { name: 'AI Buy Signal', description: 'High-confidence buy opportunity', profitPotential: '+12%' },
  { name: 'Risk Alert', description: 'Market volatility warning', profitPotential: 'Risk Mitigation' },
  { name: 'Elite Strategy', description: 'Exclusive algorithmic strategy', profitPotential: '+18%' }
];

export default function ProfitSignalsWidget({ userId }) {
  const [claimed, setClaimed] = useState([]);
  const [message, setMessage] = useState('');

  function handleClaim(signal) {
    setClaimed([...claimed, signal.name]);
    setMessage(`You claimed: ${signal.name}`);
    setTimeout(() => setMessage(''), 1200);
  }

  return (
    <div className="profit-signals-widget">
      <h3>Profit Signals & Opportunities</h3>
      <ul className="signals-list">
        {SIGNALS.map(signal => (
          <li key={signal.name} className="signal-item">
            <div className="signal-header">
              <strong>{signal.name}</strong>
              <span className="profit-potential">{signal.profitPotential}</span>
            </div>
            <div className="signal-description">{signal.description}</div>
            <button
              onClick={() => handleClaim(signal)}
              disabled={claimed.includes(signal.name)}
            >
              {claimed.includes(signal.name) ? 'Claimed' : 'Claim Signal'}
            </button>
          </li>
        ))}
      </ul>
      {message && <div className="signal-message">{message}</div>}
    </div>
  );
}
