import React, { useState, useEffect } from 'react';
import './NotificationPreferences.css';

const NotificationPreferences = ({ userId, onClose }) => {
  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    pushNotifications: true,
    tradingAlerts: true,
    systemUpdates: true,
    marketingEmails: false,
    priceChanges: true,
    subscriptionUpdates: true,
    weeklyReports: true,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    // Load preferences from localStorage
    const savedPreferences = localStorage.getItem(`notification_preferences_${userId}`);
    if (savedPreferences) {
      try {
        setPreferences(JSON.parse(savedPreferences));
      } catch (e) {
        console.error('Failed to load preferences:', e);
      }
    }
  }, [userId]);

  const handleToggle = (key) => {
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage('');

    try {
      // Save to localStorage (in production, this would be an API call)
      localStorage.setItem(`notification_preferences_${userId}`, JSON.stringify(preferences));
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setSaveMessage('Preferences saved successfully!');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      setSaveMessage('Failed to save preferences. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div 
      className="preferences-overlay" 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="preferences-title"
      onKeyDown={handleKeyDown}
    >
      <div className="preferences-modal">
        <div className="preferences-header">
          <h2 id="preferences-title">Notification Preferences</h2>
          <button 
            className="preferences-close" 
            onClick={onClose}
            aria-label="Close notification preferences"
          >
            ✕
          </button>
        </div>

        <div className="preferences-content">
          <div className="preference-section">
            <h3>Communication Channels</h3>
            <div className="preference-item">
              <div className="preference-info">
                <label htmlFor="email-notifications">
                  <strong>Email Notifications</strong>
                  <span className="preference-description">Receive notifications via email</span>
                </label>
              </div>
              <button
                id="email-notifications"
                className={`toggle-switch ${preferences.emailNotifications ? 'active' : ''}`}
                onClick={() => handleToggle('emailNotifications')}
                role="switch"
                aria-checked={preferences.emailNotifications}
                aria-label="Toggle email notifications"
              >
                <span className="toggle-slider" />
              </button>
            </div>

            <div className="preference-item">
              <div className="preference-info">
                <label htmlFor="push-notifications">
                  <strong>Push Notifications</strong>
                  <span className="preference-description">Receive browser push notifications</span>
                </label>
              </div>
              <button
                id="push-notifications"
                className={`toggle-switch ${preferences.pushNotifications ? 'active' : ''}`}
                onClick={() => handleToggle('pushNotifications')}
                role="switch"
                aria-checked={preferences.pushNotifications}
                aria-label="Toggle push notifications"
              >
                <span className="toggle-slider" />
              </button>
            </div>
          </div>

          <div className="preference-section">
            <h3>Alert Types</h3>
            <div className="preference-item">
              <div className="preference-info">
                <label htmlFor="trading-alerts">
                  <strong>Trading Alerts</strong>
                  <span className="preference-description">Get notified about trade executions and signals</span>
                </label>
              </div>
              <button
                id="trading-alerts"
                className={`toggle-switch ${preferences.tradingAlerts ? 'active' : ''}`}
                onClick={() => handleToggle('tradingAlerts')}
                role="switch"
                aria-checked={preferences.tradingAlerts}
                aria-label="Toggle trading alerts"
              >
                <span className="toggle-slider" />
              </button>
            </div>

            <div className="preference-item">
              <div className="preference-info">
                <label htmlFor="price-changes">
                  <strong>Price Changes</strong>
                  <span className="preference-description">Alerts for significant price movements</span>
                </label>
              </div>
              <button
                id="price-changes"
                className={`toggle-switch ${preferences.priceChanges ? 'active' : ''}`}
                onClick={() => handleToggle('priceChanges')}
                role="switch"
                aria-checked={preferences.priceChanges}
                aria-label="Toggle price change alerts"
              >
                <span className="toggle-slider" />
              </button>
            </div>

            <div className="preference-item">
              <div className="preference-info">
                <label htmlFor="system-updates">
                  <strong>System Updates</strong>
                  <span className="preference-description">Important system and platform updates</span>
                </label>
              </div>
              <button
                id="system-updates"
                className={`toggle-switch ${preferences.systemUpdates ? 'active' : ''}`}
                onClick={() => handleToggle('systemUpdates')}
                role="switch"
                aria-checked={preferences.systemUpdates}
                aria-label="Toggle system update notifications"
              >
                <span className="toggle-slider" />
              </button>
            </div>

            <div className="preference-item">
              <div className="preference-info">
                <label htmlFor="subscription-updates">
                  <strong>Subscription Updates</strong>
                  <span className="preference-description">Billing and subscription changes</span>
                </label>
              </div>
              <button
                id="subscription-updates"
                className={`toggle-switch ${preferences.subscriptionUpdates ? 'active' : ''}`}
                onClick={() => handleToggle('subscriptionUpdates')}
                role="switch"
                aria-checked={preferences.subscriptionUpdates}
                aria-label="Toggle subscription update notifications"
              >
                <span className="toggle-slider" />
              </button>
            </div>
          </div>

          <div className="preference-section">
            <h3>Reports & Marketing</h3>
            <div className="preference-item">
              <div className="preference-info">
                <label htmlFor="weekly-reports">
                  <strong>Weekly Reports</strong>
                  <span className="preference-description">Receive weekly performance summaries</span>
                </label>
              </div>
              <button
                id="weekly-reports"
                className={`toggle-switch ${preferences.weeklyReports ? 'active' : ''}`}
                onClick={() => handleToggle('weeklyReports')}
                role="switch"
                aria-checked={preferences.weeklyReports}
                aria-label="Toggle weekly reports"
              >
                <span className="toggle-slider" />
              </button>
            </div>

            <div className="preference-item">
              <div className="preference-info">
                <label htmlFor="marketing-emails">
                  <strong>Marketing Emails</strong>
                  <span className="preference-description">Product updates, tips, and promotions</span>
                </label>
              </div>
              <button
                id="marketing-emails"
                className={`toggle-switch ${preferences.marketingEmails ? 'active' : ''}`}
                onClick={() => handleToggle('marketingEmails')}
                role="switch"
                aria-checked={preferences.marketingEmails}
                aria-label="Toggle marketing emails"
              >
                <span className="toggle-slider" />
              </button>
            </div>
          </div>
        </div>

        <div className="preferences-footer">
          {saveMessage && (
            <div className="save-message" role="status" aria-live="polite">
              {saveMessage}
            </div>
          )}
          <div className="preferences-actions">
            <button 
              className="btn-secondary" 
              onClick={onClose}
              aria-label="Cancel and close preferences"
            >
              Cancel
            </button>
            <button 
              className="btn-primary" 
              onClick={handleSave}
              disabled={isSaving}
              aria-label="Save notification preferences"
            >
              {isSaving ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationPreferences;
