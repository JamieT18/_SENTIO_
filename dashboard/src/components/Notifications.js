import React from 'react';
import { useNotificationsWebSocket } from '../hooks/useWebSocket';
import './Notifications.css';

const Notifications = ({ userId }) => {
  const { notifications, clearNotifications, isConnected } = useNotificationsWebSocket(userId);

  if (!userId) {
    return null;
  }

  const getNotificationStyle = (type) => {
    switch (type) {
      case 'success':
        return 'notification-success';
      case 'warning':
        return 'notification-warning';
      case 'error':
        return 'notification-error';
      case 'info':
      default:
        return 'notification-info';
    }
  };

  return (
    <div className="notifications-container" role="region" aria-label="Notifications">
      <div className="notifications-header">
        <h3>
          Notifications
          {isConnected && (
            <span className="live-indicator" role="status" aria-label="Live notifications enabled" title="Live notifications enabled">🟢</span>
          )}
        </h3>
        {notifications.length > 0 && (
          <button 
            className="btn-clear" 
            onClick={clearNotifications}
            aria-label={`Clear all ${notifications.length} notifications`}
          >
            Clear All
          </button>
        )}
      </div>
      
      <div className="notifications-list" role="list" aria-live="polite" aria-atomic="false">
        {notifications.length === 0 ? (
          <div className="no-notifications" role="status">No new notifications</div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              className={`notification-item ${getNotificationStyle(notification.type)}`}
              role="listitem"
              aria-label={`${notification.type} notification: ${notification.title || notification.message}`}
            >
              <div className="notification-content">
                {notification.title && (
                  <div className="notification-title">{notification.title}</div>
                )}
                <div className="notification-message">{notification.message}</div>
                {notification.timestamp && (
                  <div className="notification-time">
                    {new Date(notification.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Notifications;
