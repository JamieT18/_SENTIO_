import React, { useState } from 'react';

const ARBITRAGE_OPPORTUNITIES = [
  { name: 'BTC/USD Arbitrage', exchanges: ['Binance', 'Coinbase'], profitPotential: '+2.1%' },
  { name: 'ETH/USDT Spread', exchanges: ['Kraken', 'Bitfinex'], profitPotential: '+1.7%' },
  { name: 'SOL/USD Cross', exchanges: ['FTX', 'Binance'], profitPotential: '+2.5%' }
];

export default function ArbitrageWidget({ userId }) {
  const [executed, setExecuted] = useState([]);
  const [message, setMessage] = useState('');

  function handleExecute(opportunity) {
    setExecuted([...executed, opportunity.name]);
    setMessage(`Arbitrage executed: ${opportunity.name}`);
    setTimeout(() => setMessage(''), 1200);
  }

  return (
    <div className="arbitrage-widget">
      <h3>Arbitrage Opportunities</h3>
      <ul className="arbitrage-list">
        {ARBITRAGE_OPPORTUNITIES.map(op => (
          <li key={op.name} className="arbitrage-item">
            <div className="arbitrage-header">
              <strong>{op.name}</strong>
              <span className="arbitrage-profit">{op.profitPotential}</span>
            </div>
            <div className="arbitrage-exchanges">Exchanges: {op.exchanges.join(', ')}</div>
            <button
              onClick={() => handleExecute(op)}
              disabled={executed.includes(op.name)}
            >
              {executed.includes(op.name) ? 'Executed' : 'Execute'}
            </button>
          </li>
        ))}
      </ul>
      {message && <div className="arbitrage-message">{message}</div>}
    </div>
  );
}
