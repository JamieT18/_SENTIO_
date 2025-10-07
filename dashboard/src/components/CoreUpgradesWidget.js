import React, { useState } from 'react';

const CORE_UPGRADES = [
  { name: 'Real-Time Data Sync', description: 'Instant updates across all modules for seamless experience.' },
  { name: 'Advanced Error Handling', description: 'Automatic recovery and user-friendly error messages.' },
  { name: 'Performance Boost', description: 'Optimized backend and frontend for faster load times.' },
  { name: 'Security Hardening', description: 'Multi-factor authentication and enhanced data protection.' },
  { name: 'Scalable Architecture', description: 'Effortless scaling for high user loads and future growth.' }
];

export default function CoreUpgradesWidget() {
  const [applied, setApplied] = useState([]);
  const [message, setMessage] = useState('');

  function handleApply(upgrade) {
    setApplied([...applied, upgrade.name]);
    setMessage(`Upgrade applied: ${upgrade.name}`);
    setTimeout(() => setMessage(''), 1200);
  }

  return (
    <div className="core-upgrades-widget">
      <h3>Core System Upgrades</h3>
      <ul className="upgrades-list">
        {CORE_UPGRADES.map(upgrade => (
          <li key={upgrade.name} className="upgrade-item">
            <div className="upgrade-header">
              <strong>{upgrade.name}</strong>
            </div>
            <div className="upgrade-description">{upgrade.description}</div>
            <button
              onClick={() => handleApply(upgrade)}
              disabled={applied.includes(upgrade.name)}
            >
              {applied.includes(upgrade.name) ? 'Applied' : 'Apply Upgrade'}
            </button>
          </li>
        ))}
      </ul>
      {message && <div className="upgrade-message">{message}</div>}
    </div>
  );
}
