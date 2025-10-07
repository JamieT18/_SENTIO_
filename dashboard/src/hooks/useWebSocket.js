/**
 * Custom React Hooks for WebSocket Integration
 * Provides easy-to-use hooks for real-time updates
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import wsService from '../services/websocket';

/**
 * Hook for trade signals WebSocket updates
 * @param {Array} symbols - Array of symbols to subscribe to
 * @param {string} userId - User identifier
 * @returns {Object} { signals, loading, error, subscribe, unsubscribe }
 */
export const useTradeSignalsWebSocket = (symbols = [], userId = 'anonymous') => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  const subscribe = useCallback((newSymbols) => {
    if (isConnected) {
      wsService.send('trade-signals', {
        action: 'subscribe',
        symbols: newSymbols
      });
    }
  }, [isConnected]);

  const unsubscribe = useCallback((symbolsToRemove) => {
    if (isConnected) {
      wsService.send('trade-signals', {
        action: 'unsubscribe',
        symbols: symbolsToRemove
      });
    }
  }, [isConnected]);

  useEffect(() => {
    const handleMessage = (data) => {
      if (data.type === 'trade_signals') {
        setSignals(data.data);
        setLoading(false);
        setError(null);
      } else if (data.type === 'error') {
        setError(data.message);
      }
    };

    const handleError = (err) => {
      setError('WebSocket connection error');
      setLoading(false);
    };

    const handleClose = () => {
      setIsConnected(false);
    };

    wsService.connect('trade-signals', {
      onMessage: handleMessage,
      onError: handleError,
      onClose: handleClose,
      initialMessage: {
        action: 'subscribe',
        symbols: symbols,
        user_id: userId
      }
    });

    setIsConnected(true);

    return () => {
      wsService.disconnect('trade-signals');
    };
  }, [symbols.join(','), userId]);

  return { signals, loading, error, subscribe, unsubscribe, isConnected };
};

/**
 * Hook for earnings WebSocket updates
 * @param {string} userId - User identifier
 * @returns {Object} { earnings, loading, error, isConnected }
 */
export const useEarningsWebSocket = (userId) => {
  const [earnings, setEarnings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!userId) {
      setLoading(false);
      return;
    }

    const handleMessage = (data) => {
      if (data.type === 'earnings') {
        setEarnings(data.data);
        setLoading(false);
        setError(null);
      } else if (data.type === 'error') {
        setError(data.message);
      }
    };

    const handleError = (err) => {
      setError('WebSocket connection error');
      setLoading(false);
    };

    const handleClose = () => {
      setIsConnected(false);
    };

    wsService.connect('earnings', {
      onMessage: handleMessage,
      onError: handleError,
      onClose: handleClose,
      initialMessage: {
        action: 'subscribe',
        user_id: userId
      }
    });

    setIsConnected(true);

    return () => {
      wsService.disconnect('earnings');
    };
  }, [userId]);

  return { earnings, loading, error, isConnected };
};

/**
 * Hook for notifications WebSocket updates
 * @param {string} userId - User identifier
 * @returns {Object} { notifications, addNotification, clearNotifications, isConnected }
 */
export const useNotificationsWebSocket = (userId) => {
  const [notifications, setNotifications] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  const addNotification = useCallback((notification) => {
    setNotifications(prev => [notification, ...prev].slice(0, 50)); // Keep last 50
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  useEffect(() => {
    if (!userId) {
      return;
    }

    const handleMessage = (data) => {
      if (data.type === 'notification') {
        addNotification({
          ...data.data,
          timestamp: data.timestamp,
          id: Date.now()
        });
      }
    };

    const handleError = (err) => {
      console.error('Notifications WebSocket error:', err);
    };

    const handleClose = () => {
      setIsConnected(false);
    };

    wsService.connect('notifications', {
      onMessage: handleMessage,
      onError: handleError,
      onClose: handleClose,
      initialMessage: {
        action: 'subscribe',
        user_id: userId
      }
    });

    setIsConnected(true);

    return () => {
      wsService.disconnect('notifications');
    };
  }, [userId, addNotification]);

  return { notifications, addNotification, clearNotifications, isConnected };
};

/**
 * Hook for admin dashboard WebSocket updates
 * @param {string} adminToken - Admin authentication token
 * @returns {Object} { adminData, loading, error, isConnected }
 */
export const useAdminWebSocket = (adminToken) => {
  const [adminData, setAdminData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!adminToken) {
      setLoading(false);
      return;
    }

    const handleMessage = (data) => {
      // Handle different admin update types
      if (data.type.startsWith('admin_')) {
        const updateType = data.type.replace('admin_', '');
        setAdminData(prev => ({
          ...prev,
          [updateType]: data.data,
          lastUpdate: data.timestamp
        }));
        setLoading(false);
        setError(null);
      } else if (data.type === 'error') {
        setError(data.message);
      }
    };

    const handleError = (err) => {
      setError('WebSocket connection error');
      setLoading(false);
    };

    const handleClose = () => {
      setIsConnected(false);
    };

    wsService.connect('admin', {
      onMessage: handleMessage,
      onError: handleError,
      onClose: handleClose,
      initialMessage: {
        action: 'subscribe',
        admin_token: adminToken
      }
    });

    setIsConnected(true);

    return () => {
      wsService.disconnect('admin');
    };
  }, [adminToken]);

  return { adminData, loading, error, isConnected };
};
