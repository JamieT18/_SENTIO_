import React, { useEffect, useState } from 'react';
import api from '../services/api';

const INTEGRATION_LIST = [
  { name: 'Broker API', status: 'connected', description: 'Live trading and portfolio sync.' },
  { name: 'Google Sheets', status: 'not_connected', description: 'Export analytics and reports.' },
  { name: 'Slack', status: 'connected', description: 'Trade alerts and notifications.' },
  { name: 'Zapier', status: 'not_connected', description: 'Automate workflows and triggers.' },
  { name: 'MetaTrader', status: 'not_connected', description: 'Advanced trading platform integration.' },
];

export default function IntegrationsWidget({ userId }) {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchIntegrations() {
      try {
        setLoading(true);
        // Replace with actual API call for integrations
        // const result = await api.getIntegrations(userId);
        // setIntegrations(result.integrations || []);
        setIntegrations(INTEGRATION_LIST);
        setError(null);
      } catch (err) {
        setError('Failed to load integrations');
      } finally {
        setLoading(false);
      }
    }
    fetchIntegrations();
  }, [userId]);

  if (loading) return <div className="integrations-widget">Loading integrations...</div>;
  if (error) return <div className="integrations-widget error">{error}</div>;

  return (
    <div className="integrations-widget">
      <h3>Integrations</h3>
      <ul>
        {integrations.map((intg, idx) => (
          <li key={idx}>
            <strong>{intg.name}</strong> - <span className={intg.status}>{intg.status.replace('_', ' ')}</span>
            <div style={{fontSize: '0.97em', color: '#64748b'}}>{intg.description}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
