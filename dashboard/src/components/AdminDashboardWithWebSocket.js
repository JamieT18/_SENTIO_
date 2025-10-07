import React, { useState, useEffect } from 'react';
import { useAdminWebSocket } from '../hooks/useWebSocket';

const ADMIN_TOKEN = 'admin-token'; // In production, use secure storage
const API_BASE = '/admin';
const API_HEADERS = { 'X-Admin-Token': ADMIN_TOKEN };

const AdminDashboardWithWebSocket = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [subscribers, setSubscribers] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [systemStatus, setSystemStatus] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [logs, setLogs] = useState([]);
  const [liveStatus, setLiveStatus] = useState(null);
  const [liveLogs, setLiveLogs] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [config, setConfig] = useState(null);
  const [editConfig, setEditConfig] = useState({});
  const [metrics, setMetrics] = useState(null);

  // WebSocket integration
  const { adminData, isConnected } = useAdminWebSocket(ADMIN_TOKEN);

  // Update local state when WebSocket data arrives
  useEffect(() => {
    if (adminData.users) {
      setUsers(adminData.users.users || []);
    }
    if (adminData.subscribers) {
      setSubscribers(adminData.subscribers.subscribers || []);
    }
    if (adminData.revenue || adminData.user_analytics) {
      setAnalytics({
        revenue: adminData.revenue,
        users: adminData.user_analytics
      });
    }
  }, [adminData]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/admin');
    ws.onopen = () => ws.send(ADMIN_TOKEN);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLiveStatus(data.status);
      setLiveLogs(data.logs);
    };
    ws.onerror = () => setSystemStatus('WebSocket error');
    ws.onclose = () => setSystemStatus('WebSocket closed');
    return () => ws.close();
  }, []);

  const runPerformanceTests = async () => {
    setSystemStatus('Running performance tests...');
    try {
      const res = await fetch(`${API_BASE}/run-tests`, { method: 'POST', headers: API_HEADERS });
      const data = await res.json();
      setTestResults({
        passed: data.passed,
        exitCode: data.exit_code,
        output: data.output,
        errors: data.errors
      });
      setSystemStatus('Performance tests completed');
    } catch (err) {
      setSystemStatus('Error running tests');
    }
  };

  const restartBackend = async () => {
    setSystemStatus('Restarting backend...');
    try {
      const res = await fetch(`${API_BASE}/restart`, { method: 'POST', headers: API_HEADERS });
      const data = await res.json();
      setSystemStatus(data.status || 'Restart requested');
    } catch (err) {
      setSystemStatus('Error requesting restart');
    }
  };

  const runAutoFixes = async () => {
    setSystemStatus('Running auto-fix scripts...');
    try {
      const res = await fetch(`${API_BASE}/auto-fix`, { method: 'POST', headers: API_HEADERS });
      const data = await res.json();
      setSystemStatus('Auto-fixes applied');
      setTestResults({
        output: data.output,
        errors: data.errors,
        exitCode: data.exit_code
      });
    } catch (err) {
      setSystemStatus('Error running auto-fixes');
    }
  };

  const fetchLogs = async () => {
    setSystemStatus('Fetching logs...');
    try {
      const res = await fetch(`${API_BASE}/logs`, { headers: API_HEADERS });
      const data = await res.json();
      setLogs(data.logs || []);
      setSystemStatus('Logs updated');
    } catch (err) {
      setSystemStatus('Error fetching logs');
    }
  };

  const fetchAuditLogs = async () => {
    setSystemStatus('Fetching audit logs...');
    try {
      const res = await fetch(`${API_BASE}/audit-logs`, { headers: API_HEADERS });
      const data = await res.json();
      setAuditLogs(data.audit_logs || []);
      setSystemStatus('Audit logs updated');
    } catch (err) {
      setSystemStatus('Error fetching audit logs');
    }
  };

  const fetchConfig = async () => {
    setSystemStatus('Fetching config...');
    try {
      const res = await fetch(`${API_BASE}/config`, { headers: API_HEADERS });
      const data = await res.json();
      setConfig(data.config || {});
      setEditConfig(data.config || {});
      setSystemStatus('Config loaded');
    } catch (err) {
      setSystemStatus('Error fetching config');
    }
  };

  const updateConfig = async () => {
    setSystemStatus('Updating config...');
    try {
      const res = await fetch(`${API_BASE}/config`, {
        method: 'POST',
        headers: { ...API_HEADERS, 'Content-Type': 'application/json' },
        body: JSON.stringify(editConfig)
      });
      const data = await res.json();
      setConfig(data.config || {});
      setSystemStatus(data.status || 'Config updated');
    } catch (err) {
      setSystemStatus('Error updating config');
    }
  };

  const blueGreenDeploy = async () => {
    setSystemStatus('Triggering blue/green deployment...');
    try {
      const res = await fetch(`${API_BASE}/deploy/blue-green`, { method: 'POST', headers: API_HEADERS });
      const data = await res.json();
      setSystemStatus(data.status);
    } catch (err) {
      setSystemStatus('Error triggering deployment');
    }
  };

  const rollbackDeploy = async () => {
    setSystemStatus('Triggering rollback...');
    try {
      const res = await fetch(`${API_BASE}/deploy/rollback`, { method: 'POST', headers: API_HEADERS });
      const data = await res.json();
      setSystemStatus(data.status);
    } catch (err) {
      setSystemStatus('Error triggering rollback');
    }
  };

  const triggerBackup = async () => {
    setSystemStatus('Starting backup...');
    try {
      const res = await fetch(`${API_BASE}/backup`, { method: 'POST', headers: API_HEADERS });
      const data = await res.json();
      setSystemStatus(data.status);
    } catch (err) {
      setSystemStatus('Error starting backup');
    }
  };

  const triggerRestore = async () => {
    setSystemStatus('Starting restore...');
    try {
      const res = await fetch(`${API_BASE}/restore`, { method: 'POST', headers: API_HEADERS });
      const data = await res.json();
      setSystemStatus(data.status);
    } catch (err) {
      setSystemStatus('Error starting restore');
    }
  };

  const fetchMetrics = async () => {
    setSystemStatus('Fetching metrics...');
    try {
      const res = await fetch(`${API_BASE}/metrics`, { headers: API_HEADERS });
      const data = await res.json();
      setMetrics(data);
      setSystemStatus('Metrics updated');
    } catch (err) {
      setSystemStatus('Error fetching metrics');
    }
  };

  const renderOverview = () => {
    if (!analytics) return <p>Loading analytics...</p>;

    const { revenue, users } = analytics;

    return (
      <div className="overview-section">
        <div className="analytics-cards">
          <div className="card">
            <h3>Monthly Recurring Revenue</h3>
            <p className="metric">${revenue?.monthly_recurring_revenue?.toFixed(2) || '0.00'}</p>
          </div>
          <div className="card">
            <h3>Total Users</h3>
            <p className="metric">{users?.total_users || 0}</p>
          </div>
          <div className="card">
            <h3>Active Subscriptions</h3>
            <p className="metric">{users?.by_status?.active || 0}</p>
          </div>
        </div>

        <div className="charts-row">
          <div className="chart-card">
            <h3>Revenue by Tier</h3>
            <div className="revenue-breakdown">
              {Object.entries(revenue?.revenue_by_tier || {}).map(([tier, amount]) => (
                <div key={tier} className="revenue-item">
                  <span className="tier-name">{tier}:</span>
                  <span className="tier-revenue">${amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="chart-card">
            <h3>Subscribers by Tier</h3>
            <div className="subscriber-breakdown">
              {Object.entries(users?.by_tier || {}).map(([tier, count]) => (
                <div key={tier} className="subscriber-item">
                  <span className="tier-name">{tier}:</span>
                  <span className="tier-count">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderUsers = () => (
    <div className="users-section">
      <h2>User Management</h2>
      {users.length === 0 ? (
        <p>No users found</p>
      ) : (
        <table className="users-table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Tier</th>
              <th>Status</th>
              <th>Start Date</th>
              <th>Profit Sharing Balance</th>
              <th>Total Shared</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.user_id}>
                <td>{user.user_id}</td>
                <td><span className={`badge tier-${user.tier}`}>{user.tier}</span></td>
                <td><span className={`badge status-${user.status}`}>{user.status}</span></td>
                <td>{new Date(user.start_date).toLocaleDateString()}</td>
                <td>${user.profit_sharing_balance?.toFixed(2)}</td>
                <td>${user.total_profits_shared?.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  const renderSubscribers = () => (
    <div className="subscribers-section">
      <h2>Subscriber Details</h2>
      {subscribers.length === 0 ? (
        <p>No subscribers found</p>
      ) : (
        <div className="subscribers-grid">
          {subscribers.map(sub => (
            <div key={sub.user_id} className="subscriber-card">
              <div className="subscriber-header">
                <h4>{sub.user_id}</h4>
                <span className={`badge tier-${sub.tier}`}>{sub.tier}</span>
              </div>
              <div className="subscriber-details">
                <p><strong>Status:</strong> {sub.status}</p>
                <p><strong>Start Date:</strong> {new Date(sub.start_date).toLocaleDateString()}</p>
                <p><strong>Max Trades:</strong> {sub.features?.max_concurrent_trades}</p>
                <p><strong>Max Strategies:</strong> {sub.features?.max_strategies}</p>
                <p><strong>Day Trading:</strong> {sub.features?.day_trading ? 'Yes' : 'No'}</p>
                <p><strong>API Access:</strong> {sub.features?.api_access ? 'Yes' : 'No'}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderSystemTools = () => (
    <div className="system-tools-section">
      <h2>System Tools</h2>
      <div className="tools-row">
        <button onClick={runPerformanceTests}>Run Performance Tests</button>
        <button onClick={restartBackend}>Restart Backend</button>
        <button onClick={runAutoFixes}>Run Auto-Fixes</button>
        <button onClick={fetchLogs}>View Logs</button>
        <button onClick={fetchAuditLogs}>View Audit Logs</button>
        <button onClick={fetchConfig}>View/Edit Config</button>
        <button onClick={blueGreenDeploy}>Blue/Green Deploy</button>
        <button onClick={rollbackDeploy}>Rollback Deploy</button>
        <button onClick={triggerBackup}>Backup</button>
        <button onClick={triggerRestore}>Restore</button>
        <button onClick={fetchMetrics}>View Metrics</button>
      </div>
      <div className="system-status">
        <strong>Status:</strong> {systemStatus}
      </div>
      {testResults && (
        <div className="test-results">
          <h3>Diagnostics/Test Results</h3>
          {testResults.passed !== undefined && (
            <p><strong>Passed:</strong> {String(testResults.passed)}</p>
          )}
          {testResults.exitCode !== undefined && (
            <p><strong>Exit Code:</strong> {testResults.exitCode}</p>
          )}
          {testResults.output && (
            <pre className="test-output">{testResults.output}</pre>
          )}
          {testResults.errors && testResults.errors.length > 0 && (
            <pre className="test-errors">{testResults.errors}</pre>
          )}
        </div>
      )}
      {logs.length > 0 && (
        <div className="logs-section">
          <h3>Recent Logs</h3>
          <ul>
            {logs.map((log, idx) => <li key={idx}>{log}</li>)}
          </ul>
        </div>
      )}
      {auditLogs.length > 0 && (
        <div className="audit-logs-section">
          <h3>Recent Audit Logs</h3>
          <ul>
            {auditLogs.map((log, idx) => <li key={idx}>{log}</li>)}
          </ul>
        </div>
      )}
      {config && (
        <div className="config-section">
          <h3>System Config</h3>
          <form onSubmit={e => { e.preventDefault(); updateConfig(); }}>
            {Object.entries(editConfig).map(([key, value]) => (
              <div key={key} className="config-item">
                <label>{key}</label>
                <input
                  type="text"
                  value={value}
                  onChange={e => setEditConfig({ ...editConfig, [key]: e.target.value })}
                />
              </div>
            ))}
            <button type="submit">Update Config</button>
          </form>
        </div>
      )}
      <div className="live-system-status">
        <h3>Live System Status</h3>
        {liveStatus && (
          <pre>{JSON.stringify(liveStatus, null, 2)}</pre>
        )}
        <h3>Live Logs</h3>
        <ul>
          {liveLogs.map((log, idx) => <li key={idx}>{log}</li>)}
        </ul>
      </div>
      {metrics && (
        <div className="metrics-section">
          <h3>Advanced Analytics</h3>
          <pre>{JSON.stringify(metrics, null, 2)}</pre>
        </div>
      )}
    </div>
  );

  // Admin pricing control stub
  function AdminPricingControl({ pricing, onUpdate }) {
    return (
      <section className="admin-pricing-control">
        <h2>Pricing Control</h2>
        {/* ...render pricing controls... */}
        <button onClick={() => onUpdate({ price: 99 })}>Set Price $99</button>
      </section>
    );
  }

  // User plans and subscription gating stub
  function UserPlans({ plans, user }) {
    return (
      <section className="user-plans">
        <h2>User Plans</h2>
        {/* ...render plans and gating... */}
        <ul>
          {plans?.map((p, i) => (
            <li key={i}>{p.name} - {p.features.join(", ")}</li>
          ))}
        </ul>
        <div>Current: {user?.plan || 'Free'}</div>
      </section>
    );
  }

  // Profit-sharing model config stub
  function ProfitSharingConfig({ percent, onChange }) {
    return (
      <section className="profit-sharing-config">
        <h2>Profit Sharing Configuration</h2>
        <label>
          Dashboard %:
          <input type="number" value={percent} onChange={e => onChange(Number(e.target.value))} min={0} max={100} />
        </label>
      </section>
    );
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>
          Sentio Admin Dashboard
          {isConnected && (
            <span className="live-indicator" title="Live updates enabled">🟢</span>
          )}
        </h1>
        <p>Manage pricing, plans, subscriptions, and analytics in real-time</p>
      </header>

      <nav className="tab-navigation">
        <button 
          className={activeTab === 'overview' ? 'active' : ''} 
          onClick={() => setActiveTab('overview')}
        >
          Overview & Analytics
        </button>
        <button 
          className={activeTab === 'users' ? 'active' : ''} 
          onClick={() => setActiveTab('users')}
        >
          User Management
        </button>
        <button 
          className={activeTab === 'subscribers' ? 'active' : ''} 
          onClick={() => setActiveTab('subscribers')}
        >
          Subscriber Details
        </button>
        <button 
          className={activeTab === 'system' ? 'active' : ''} 
          onClick={() => setActiveTab('system')}
        >
          System Tools
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'users' && renderUsers()}
        {activeTab === 'subscribers' && renderSubscribers()}
        {activeTab === 'system' && renderSystemTools()}
      </main>

      <footer className="admin-footer">
        <p>
          Last update: {adminData.lastUpdate ? new Date(adminData.lastUpdate).toLocaleTimeString() : 'N/A'}
        </p>
      </footer>
    </div>
  );
};

export default AdminDashboardWithWebSocket;
