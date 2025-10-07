import React, { useState } from 'react';

export default function StrategyAnalyticsWidget() {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const strategies = [
    {
      name: 'AI Momentum',
      description: 'Uses AI to detect momentum shifts and enter trades early.',
      risk_level: 'Medium',
      win_rate: 0.62,
      avg_profit: 8.5
    },
    {
      name: 'Risk-Managed Arbitrage',
      description: 'Executes cross-exchange arbitrage with dynamic risk controls.',
      risk_level: 'Low',
      win_rate: 0.78,
      avg_profit: 4.2
    },
    {
      name: 'Elite Swing',
      description: 'Combines technical and sentiment analysis for swing trades.',
      risk_level: 'High',
      win_rate: 0.54,
      avg_profit: 15.1
    },
    {
      name: 'Market Neutral',
      description: 'Hedges positions to minimize market risk and maximize stable returns.',
      risk_level: 'Low',
      win_rate: 0.81,
      avg_profit: 3.7
    },
    {
      name: 'Adaptive Trend',
      description: 'Adapts to changing market conditions using real-time analytics.',
      risk_level: 'Medium',
      win_rate: 0.66,
      avg_profit: 7.9
    }
  ];

  async function runStrategy(name) {
    setLoading(true);
    setResult(null);
    // Simulate API call
    setTimeout(() => {
      const strat = strategies.find(s => s.name === name);
      const win = Math.random() < strat.win_rate;
      const profit = win ? strat.avg_profit : -strat.avg_profit * 0.7;
      setResult({ strategy: name, win, profit });
      setLoading(false);
    }, 1200);
  }

  return (
    <div className="strategy-analytics-widget">
      <h3>Strategy Analytics & Simulation</h3>
      <ul className="strategy-list">
        {strategies.map(s => (
          <li key={s.name} className="strategy-item">
            <div className="strategy-header">
              <strong>{s.name}</strong>
              <span className={`risk-badge ${s.risk_level.toLowerCase()}`}>{s.risk_level}</span>
            </div>
            <div className="strategy-description">{s.description}</div>
            <div className="strategy-metrics">
              Win Rate: {(s.win_rate * 100).toFixed(1)}% | Avg Profit: {s.avg_profit}%
            </div>
            <button onClick={() => { setSelected(s.name); runStrategy(s.name); }} disabled={loading}>
              {loading && selected === s.name ? 'Simulating...' : 'Simulate'}
            </button>
          </li>
        ))}
      </ul>
      {result && (
        <div className="strategy-result">
          <strong>Simulation Result:</strong> {result.strategy} - {result.win ? 'Win' : 'Loss'} ({result.profit > 0 ? '+' : ''}{result.profit.toFixed(2)}%)
        </div>
      )}
    </div>
  );
}
