import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';
import LanguageSelector from './LanguageSelector';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import AIRecommendations from './components/AIRecommendations';
import ExplainableAI from './components/ExplainableAI';
import DeeperAnalytics from './components/DeeperAnalytics';
import IntegrationsWidget from './components/IntegrationsWidget';
import MarketIntelligenceWidget from './components/MarketIntelligenceWidget';
import SafetyRiskWidget from './components/SafetyRiskWidget';
import * as Sentry from '@sentry/react';
import { runAxeAudit } from './accessibility/axe';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const ADMIN_TOKEN = 'admin-token'; // In production, use proper auth

Sentry.init({
  dsn: 'https://examplePublicKey@o0.ingest.sentry.io/0',
  tracesSampleRate: 1.0,
});

runAxeAudit();

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [darkMode, setDarkMode] = useState(() => JSON.parse(localStorage.getItem('darkMode')) || false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [swipeIndicator, setSwipeIndicator] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pricing, setPricing] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [subscribers, setSubscribers] = useState([]);
  const [selectedTier, setSelectedTier] = useState('');
  const [newPrice, setNewPrice] = useState('');
  const [updateMessage, setUpdateMessage] = useState('');
  const [twoFASecret, setTwoFASecret] = useState('');
  const [twoFACode, setTwoFACode] = useState('');
  const [twoFAStatus, setTwoFAStatus] = useState('');
  const [userRole, setUserRole] = useState('');
  const [auditLogs, setAuditLogs] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [onboardingStep, setOnboardingStep] = useState(0);
  const [dashboardWidgets, setDashboardWidgets] = useState(['performance', 'trades', 'activity', 'ai', 'explain', 'deep', 'integrations', 'market', 'risk']);
  const [reportFormat, setReportFormat] = useState('pdf');
  const [reportStatus, setReportStatus] = useState('');
  const [toasts, setToasts] = useState([]);

  const touchStartX = useRef(0);
  const touchEndX = useRef(0);

  const onboardingSteps = [
    'Welcome to Sentio! Your all-in-one trading analytics platform.',
    'Use the tabs above to navigate between analytics, users, pricing, support, and settings.',
    'Enable 2FA and review audit logs in Settings for maximum security.',
    'Need help? Visit Support or start a live chat anytime.',
    'You can change your language preference below.'
  ];

  // Dark mode toggle effect
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  // Swipe gesture support
  useEffect(() => {
    const handleTouchStart = (e) => {
      touchStartX.current = e.touches[0].clientX;
    };

    const handleTouchMove = (e) => {
      touchEndX.current = e.touches[0].clientX;
    };

    const handleTouchEnd = () => {
      const swipeThreshold = 75;
      const diff = touchStartX.current - touchEndX.current;

      if (Math.abs(diff) > swipeThreshold) {
        const tabs = ['overview', 'users', 'subscribers', 'pricing'];
        const currentIndex = tabs.indexOf(activeTab);

        if (diff > 0 && currentIndex < tabs.length - 1) {
          // Swipe left - next tab
          setActiveTab(tabs[currentIndex + 1]);
          showSwipeIndicator('← Swipe');
        } else if (diff < 0 && currentIndex > 0) {
          // Swipe right - previous tab
          setActiveTab(tabs[currentIndex - 1]);
          showSwipeIndicator('Swipe →');
        }
      }
    };

    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchmove', handleTouchMove);
    document.addEventListener('touchend', handleTouchEnd);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, [activeTab]);

  const showSwipeIndicator = (text) => {
    setSwipeIndicator(text);
    setTimeout(() => setSwipeIndicator(''), 1000);
  };

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    setMenuOpen(false); // Close menu on mobile after selection
  };

  const fetchPricing = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/subscription/pricing`);
      const data = await response.json();
      setPricing(data.tiers || []);
    } catch (err) {
      console.error('Error fetching pricing:', err);
    }
  };

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [revenueRes, usersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/admin/analytics/revenue`, {
          headers: { 'Authorization': `Bearer ${ADMIN_TOKEN}` }
        }),
        fetch(`${API_BASE_URL}/api/v1/admin/analytics/users`, {
          headers: { 'Authorization': `Bearer ${ADMIN_TOKEN}` }
        })
      ]);

      const revenue = await revenueRes.json();
      const users = await usersRes.json();

      setAnalytics({ revenue, users });
    } catch (err) {
      setError('Failed to load analytics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/users`, {
        headers: { 'Authorization': `Bearer ${ADMIN_TOKEN}` }
      });
      const data = await response.json();
      setUsers(data.users || []);
    } catch (err) {
      setError('Failed to load users: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubscribers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/subscribers`, {
        headers: { 'Authorization': `Bearer ${ADMIN_TOKEN}` }
      });
      const data = await response.json();
      setSubscribers(data.subscribers || []);
    } catch (err) {
      setError('Failed to load subscribers: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message, duration = 3000) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  };

  const handleUpdatePricing = async (e) => {
    e.preventDefault();
    setUpdateMessage('');
    
    if (!selectedTier || !newPrice) {
      setUpdateMessage('Please select a tier and enter a price');
      showToast('Please select a tier and enter a price');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/pricing/update`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${ADMIN_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tier: selectedTier,
          new_price: parseFloat(newPrice)
        })
      });

      if (response.ok) {
        const data = await response.json();
        setUpdateMessage(`Successfully updated ${data.tier} from $${data.old_price} to $${data.new_price}`);
        showToast(`Pricing updated for ${data.tier}`);
        fetchPricing(); // Refresh pricing
        setSelectedTier('');
        setNewPrice('');
      } else {
        const error = await response.json();
        setUpdateMessage(`Error: ${error.detail}`);
        showToast(`Error: ${error.detail}`);
      }
    } catch (err) {
      setUpdateMessage(`Error: ${err.message}`);
      showToast(`Error: ${err.message}`);
    }
  };

  const fetch2FASecret = useCallback(async () => {
    try {
      const username = 'admin'; // Replace with actual username logic
      const res = await fetch(`${API_BASE_URL}/auth/2fa/secret?username=${username}`);
      const data = await res.json();
      setTwoFASecret(data.secret);
    } catch (e) {
      setTwoFASecret('Error fetching secret');
    }
  }, []);

  const handle2FAVerify = async (e) => {
    e.preventDefault();
    try {
      const username = 'admin'; // Replace with actual username logic
      const res = await fetch(`${API_BASE_URL}/auth/2fa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, code: twoFACode })
      });
      const data = await res.json();
      setTwoFAStatus(data.success ? 'Verified!' : 'Invalid code');
    } catch (e) {
      setTwoFAStatus('Error verifying code');
    }
  };

  const fetchUserRole = useCallback(async () => {
    try {
      const username = 'admin'; // Replace with actual username logic
      const res = await fetch(`${API_BASE_URL}/auth/role?username=${username}`);
      const data = await res.json();
      setUserRole(data.role);
    } catch (e) {
      setUserRole('Error fetching role');
    }
  }, []);

  const fetchAuditLogs = useCallback(async () => {
    try {
      const apiKey = ADMIN_TOKEN;
      const res = await fetch(`${API_BASE_URL}/audit/logs`, {
        headers: { 'x-api-key': apiKey }
      });
      const data = await res.json();
      setAuditLogs(data.logs);
    } catch (e) {
      setAuditLogs([]);
    }
  }, []);

  const renderOverview = () => {
    if (!analytics) return <p>Loading analytics...</p>;

    const { revenue, users } = analytics;

    return (
      <div className="overview-section">
        <div className="analytics-cards">
          <div className="card">
            <h3>Monthly Recurring Revenue</h3>
            <p className="metric">${revenue.monthly_recurring_revenue?.toFixed(2) || '0.00'}</p>
          </div>
          <div className="card">
            <h3>Total Users</h3>
            <p className="metric">{users.total_users || 0}</p>
          </div>
          <div className="card">
            <h3>Active Subscriptions</h3>
            <p className="metric">{users.by_status?.active || 0}</p>
          </div>
        </div>

        <div className="charts-row">
          <div className="chart-card">
            <h3>Revenue by Tier</h3>
            <div className="revenue-breakdown">
              {Object.entries(revenue.revenue_by_tier || {}).map(([tier, amount]) => (
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
              {Object.entries(users.by_tier || {}).map(([tier, count]) => (
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
      {loading ? (
        <p role="status" aria-live="polite">Loading users...</p>
      ) : users.length === 0 ? (
        <p>No users found</p>
      ) : (
        <table className="users-table" role="table" aria-label="User management table">
          <thead>
            <tr>
              <th scope="col">User ID</th>
              <th scope="col">Tier</th>
              <th scope="col">Status</th>
              <th scope="col">Start Date</th>
              <th scope="col">Profit Sharing Balance</th>
              <th scope="col">Total Shared</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.user_id}>
                <td>{user.user_id}</td>
                <td><span className={`badge tier-${user.tier}`} role="status" aria-label={`Tier: ${user.tier}`}>{user.tier}</span></td>
                <td><span className={`badge status-${user.status}`} role="status" aria-label={`Status: ${user.status}`}>{user.status}</span></td>
                <td>{new Date(user.start_date).toLocaleDateString()}</td>
                <td>${user.profit_sharing_balance.toFixed(2)}</td>
                <td>${user.total_profits_shared.toFixed(2)}</td>
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
      {loading ? (
        <p role="status" aria-live="polite">Loading subscribers...</p>
      ) : subscribers.length === 0 ? (
        <p>No subscribers found</p>
      ) : (
        <div className="subscribers-grid" role="list" aria-label="Subscriber cards">
          {subscribers.map(sub => (
            <div key={sub.user_id} className="subscriber-card" role="listitem">
              <div className="subscriber-header">
                <h4>{sub.user_id}</h4>
                <span className={`badge tier-${sub.tier}`} role="status" aria-label={`Tier: ${sub.tier}`}>{sub.tier}</span>
              </div>
              <div className="subscriber-details">
                <p><strong>Status:</strong> {sub.status}</p>
                <p><strong>Start Date:</strong> {new Date(sub.start_date).toLocaleDateString()}</p>
                <p><strong>Max Trades:</strong> {sub.features.max_concurrent_trades}</p>
                <p><strong>Max Strategies:</strong> {sub.features.max_strategies}</p>
                <p><strong>Day Trading:</strong> {sub.features.day_trading ? 'Yes' : 'No'}</p>
                <p><strong>API Access:</strong> {sub.features.api_access ? 'Yes' : 'No'}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderPricing = () => (
    <div className="pricing-section">
      <h2>Pricing Management</h2>
      
      <div className="current-pricing">
        <h3>Current Pricing</h3>
        <div className="pricing-grid">
          {pricing.map(tier => (
            <div key={tier.tier} className={`pricing-card tier-${tier.tier}`}>
              <h4>{tier.tier.toUpperCase()}</h4>
              <p className="price">${tier.price}/month</p>
              <ul className="features-list">
                <li>Max Trades: {tier.features.max_concurrent_trades}</li>
                <li>Max Strategies: {tier.features.max_strategies}</li>
                <li>Day Trading: {tier.features.day_trading ? '✓' : '✗'}</li>
                <li>API Access: {tier.features.api_access ? '✓' : '✗'}</li>
                <li>Advanced Analytics: {tier.features.advanced_analytics ? '✓' : '✗'}</li>
                <li>Priority Support: {tier.features.priority_support ? '✓' : '✗'}</li>
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="pricing-update-form">
        <h3>Update Pricing</h3>
        <form onSubmit={handleUpdatePricing} aria-label="Update pricing form">
          <div className="form-group">
            <label htmlFor="tier-select">Select Tier:</label>
            <select 
              id="tier-select"
              value={selectedTier} 
              onChange={(e) => setSelectedTier(e.target.value)}
              aria-required="true"
              aria-label="Select subscription tier to update"
            >
              <option value="">-- Select Tier --</option>
              {pricing.map(tier => (
                <option key={tier.tier} value={tier.tier}>{tier.tier.toUpperCase()}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="new-price">New Price ($):</label>
            <input 
              id="new-price"
              type="number" 
              step="0.01" 
              value={newPrice}
              onChange={(e) => setNewPrice(e.target.value)}
              placeholder="Enter new price"
              aria-required="true"
              aria-label="Enter new price in dollars"
            />
          </div>
          <button type="submit" className="btn-primary" aria-label="Submit pricing update">Update Price</button>
        </form>
        {updateMessage && <p className="update-message" role="status" aria-live="polite">{updateMessage}</p>}
      </div>
    </div>
  );

  const handleOnboardingClose = () => {
    setShowOnboarding(false);
    localStorage.setItem('onboardingCompleted', 'true');
  };

  useEffect(() => {
    const onboardingCompleted = localStorage.getItem('onboardingCompleted') === 'true';
    if (onboardingCompleted) {
      setShowOnboarding(false);
    }
  }, []);

  // Add/remove widgets
  const toggleWidget = (widget) => {
    setDashboardWidgets((prev) =>
      prev.includes(widget)
        ? prev.filter((w) => w !== widget)
        : [...prev, widget]
    );
  };

  // Export report
  const exportReport = async () => {
    try {
      setReportStatus('Exporting...');
      // Replace with actual API call
      await new Promise((r) => setTimeout(r, 1200));
      setReportStatus(`Report exported as ${reportFormat.toUpperCase()}`);
    } catch {
      setReportStatus('Export failed');
    }
  };

  return (
    <div className={`App${darkMode ? ' dark-mode' : ''}`}>
      {/* Toast notifications */}
      <div className="toast-container" aria-live="polite">
        {toasts.map((toast) => (
          <div key={toast.id} className="toast" role="status">{toast.message}</div>
        ))}
      </div>
      {showOnboarding && (
        <div className="onboarding-modal" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
          <div className="onboarding-card">
            <h2 id="onboarding-title">Getting Started</h2>
            <p>{onboardingSteps[onboardingStep]}</p>
            <div style={{marginTop: '18px'}}>
              <button className="dashboard-btn" onClick={() => setOnboardingStep(onboardingStep + 1)} disabled={onboardingStep >= onboardingSteps.length - 1}>Next</button>
              <button className="dashboard-btn" style={{marginLeft: '8px'}} onClick={handleOnboardingClose}>Close</button>
            </div>
          </div>
        </div>
      )}
      <div className="dashboard-container">
        <header className="dashboard-header">Sentio Admin Dashboard</header>
        <LanguageSelector />
        <nav className="dashboard-tab-bar" role="tablist">
          <button className={`dashboard-tab${activeTab === 'overview' ? ' active' : ''}`} onClick={() => setActiveTab('overview')} role="tab" aria-selected={activeTab === 'overview'}>Overview</button>
          <button className={`dashboard-tab${activeTab === 'users' ? ' active' : ''}`} onClick={() => setActiveTab('users')} role="tab" aria-selected={activeTab === 'users'}>Users</button>
          <button className={`dashboard-tab${activeTab === 'subscribers' ? ' active' : ''}`} onClick={() => setActiveTab('subscribers')} role="tab" aria-selected={activeTab === 'subscribers'}>Subscribers</button>
          <button className={`dashboard-tab${activeTab === 'pricing' ? ' active' : ''}`} onClick={() => setActiveTab('pricing')} role="tab" aria-selected={activeTab === 'pricing'}>Pricing</button>
          <button className={`dashboard-tab support${activeTab === 'support' ? ' active' : ''}`} onClick={() => setActiveTab('support')} role="tab" aria-selected={activeTab === 'support'}>Support</button>
          <button className={`dashboard-tab settings${activeTab === 'settings' ? ' active' : ''}`} onClick={() => setActiveTab('settings')} role="tab" aria-selected={activeTab === 'settings'}>Settings</button>
        </nav>
        {activeTab === 'overview' && (
          <section className="card" aria-labelledby="dashboard-widgets-title">
            <h2 id="dashboard-widgets-title" className="dashboard-section-title">Custom Dashboard</h2>
            <div className="dashboard-actions">
              {['performance', 'trades', 'activity', 'ai', 'explain', 'deep', 'integrations', 'market', 'risk'].map((widget) => (
                <button key={widget} className="dashboard-btn" onClick={() => toggleWidget(widget)} aria-pressed={dashboardWidgets.includes(widget)}>
                  {dashboardWidgets.includes(widget) ? `Hide ${widget}` : `Show ${widget}`}
                </button>
              ))}
            </div>
            <div>
              {dashboardWidgets.includes('performance') && <AnalyticsDashboard userId={1} />}
              {dashboardWidgets.includes('trades') && <div style={{marginTop: '18px'}}><strong>Trade Performance Chart</strong> (Widget placeholder)</div>}
              {dashboardWidgets.includes('activity') && <div style={{marginTop: '18px'}}><strong>Activity Heatmap</strong> (Widget placeholder)</div>}
              {dashboardWidgets.includes('ai') && <AIRecommendations userId={1} />}
              {dashboardWidgets.includes('explain') && <ExplainableAI userId={1} />}
              {dashboardWidgets.includes('deep') && <DeeperAnalytics userId={1} />}
              {dashboardWidgets.includes('integrations') && <IntegrationsWidget userId={1} />}
              {dashboardWidgets.includes('market') && <MarketIntelligenceWidget />}
              {dashboardWidgets.includes('risk') && <SafetyRiskWidget userId={1} />}
            </div>
            <div style={{marginTop: '24px'}}>
              <label htmlFor="report-format">Export Report:</label>
              <select id="report-format" value={reportFormat} onChange={e => setReportFormat(e.target.value)} style={{marginLeft: '8px', marginRight: '8px'}}>
                <option value="pdf">PDF</option>
                <option value="csv">CSV</option>
                <option value="xlsx">Excel</option>
              </select>
              <button className="dashboard-btn" onClick={exportReport}>Export</button>
              {reportStatus && <span style={{marginLeft: '12px'}}>{reportStatus}</span>}
            </div>
          </section>
        )}
        <section className="card" aria-labelledby="section-title">
          <h2 id="section-title" className="dashboard-section-title">{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h2>
          {/* Render tab content here, e.g. analytics, users, etc. */}
          {activeTab === 'support' && (
            <div>
              <h3>Contact Support</h3>
              <p>Need help? Reach out to our support team 24/7 via <a href="mailto:support@sentio.com">support@sentio.com</a> or use the live chat below.</p>
              <button className="dashboard-btn">Start Live Chat</button>
            </div>
          )}
          {activeTab === 'settings' && (
            <div>
              <h3>Settings</h3>
              <p>Customize your Sentio experience. (Profile, notifications, preferences, security, etc.)</p>
              <button className="dashboard-btn">Edit Profile</button>
              <button className="dashboard-btn">Notification Preferences</button>
              <button className="dashboard-btn">Security Settings</button>
              <div style={{marginTop: '24px'}}>
                <h4>Two-Factor Authentication (2FA)</h4>
                <p>Protect your account with 2FA. <button className="dashboard-btn" onClick={() => fetch2FASecret()}>Show 2FA Secret</button></p>
                {twoFASecret && <div><strong>2FA Secret:</strong> {twoFASecret}</div>}
                <form onSubmit={handle2FAVerify} style={{marginTop: '12px'}}>
                  <input type="text" placeholder="Enter 2FA code" value={twoFACode} onChange={e => setTwoFACode(e.target.value)} style={{marginRight: '8px'}} />
                  <button className="dashboard-btn" type="submit">Verify 2FA</button>
                  {twoFAStatus && <span style={{marginLeft: '12px'}}>{twoFAStatus}</span>}
                </form>
              </div>
              <div style={{marginTop: '24px'}}>
                <h4>User Role</h4>
                <button className="dashboard-btn" onClick={fetchUserRole}>Show My Role</button>
                {userRole && <div><strong>Role:</strong> {userRole}</div>}
              </div>
              <div style={{marginTop: '24px'}}>
                <h4>Audit Log</h4>
                <button className="dashboard-btn" onClick={fetchAuditLogs}>View Audit Logs</button>
                {auditLogs && (
                  <div style={{maxHeight: '180px', overflowY: 'auto', marginTop: '8px', background: '#f8fafc', borderRadius: '8px', padding: '8px'}}>
                    <ul style={{fontSize: '0.95rem', paddingLeft: '16px'}}>
                      {auditLogs.map((log, idx) => (
                        <li key={idx}>{log.timestamp}: {log.endpoint} ({log.status})</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
          {/* Render tab content for other tabs */}
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'users' && renderUsers()}
          {activeTab === 'subscribers' && renderSubscribers()}
          {activeTab === 'pricing' && renderPricing()}
        </section>
        <footer className="dashboard-footer">&copy; {new Date().getFullYear()} Sentio. All rights reserved.</footer>
      </div>
    </div>
  );
}

export default App;
