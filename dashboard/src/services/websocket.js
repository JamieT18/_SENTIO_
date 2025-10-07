/**
 * WebSocket Service for Real-Time Dashboard Updates
 * Provides hooks for trade signals, earnings, and notifications
 */

const WS_BASE_URL = process.env.REACT_APP_WS_URL || 
  (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace('http', 'ws');

class WebSocketService {
  constructor() {
    this.connections = {};
    this.reconnectAttempts = {};
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  /**
   * Connect to a WebSocket endpoint
   * @param {string} endpoint - WebSocket endpoint (e.g., 'trade-signals', 'earnings')
   * @param {object} config - Configuration object
   * @param {function} config.onMessage - Message handler
   * @param {function} config.onError - Error handler
   * @param {function} config.onClose - Close handler
   * @param {object} config.initialMessage - Initial message to send on connection
   * @returns {WebSocket} WebSocket connection
   */
  connect(endpoint, config = {}) {
    const { onMessage, onError, onClose, initialMessage } = config;
    const url = `${WS_BASE_URL}/ws/${endpoint}`;

    // Close existing connection if any
    if (this.connections[endpoint]) {
      this.connections[endpoint].close();
    }

    const ws = new WebSocket(url);
    this.connections[endpoint] = ws;
    this.reconnectAttempts[endpoint] = 0;

    ws.onopen = () => {
      console.log(`WebSocket connected to ${endpoint}`);
      this.reconnectAttempts[endpoint] = 0;

      // Send initial message if provided
      if (initialMessage) {
        ws.send(JSON.stringify(initialMessage));
      }

      // Start ping interval to keep connection alive
      this.startPingInterval(endpoint);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Ignore pong messages
        if (data.type === 'pong') {
          return;
        }

        if (onMessage) {
          onMessage(data);
        }
      } catch (error) {
        console.error(`Error parsing WebSocket message from ${endpoint}:`, error);
      }
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error on ${endpoint}:`, error);
      if (onError) {
        onError(error);
      }
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected from ${endpoint}`);
      
      // Clear ping interval
      this.stopPingInterval(endpoint);

      if (onClose) {
        onClose();
      }

      // Attempt to reconnect
      this.attemptReconnect(endpoint, config);
    };

    return ws;
  }

  /**
   * Disconnect from a WebSocket endpoint
   * @param {string} endpoint - WebSocket endpoint
   */
  disconnect(endpoint) {
    if (this.connections[endpoint]) {
      this.stopPingInterval(endpoint);
      this.connections[endpoint].close();
      delete this.connections[endpoint];
      delete this.reconnectAttempts[endpoint];
    }
  }

  /**
   * Send a message to a WebSocket endpoint
   * @param {string} endpoint - WebSocket endpoint
   * @param {object} message - Message object to send
   */
  send(endpoint, message) {
    const ws = this.connections[endpoint];
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      console.warn(`WebSocket not connected to ${endpoint}`);
    }
  }

  /**
   * Start ping interval to keep connection alive
   * @param {string} endpoint - WebSocket endpoint
   */
  startPingInterval(endpoint) {
    this.stopPingInterval(endpoint);
    
    this.pingIntervals = this.pingIntervals || {};
    this.pingIntervals[endpoint] = setInterval(() => {
      this.send(endpoint, { action: 'ping' });
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Stop ping interval
   * @param {string} endpoint - WebSocket endpoint
   */
  stopPingInterval(endpoint) {
    if (this.pingIntervals && this.pingIntervals[endpoint]) {
      clearInterval(this.pingIntervals[endpoint]);
      delete this.pingIntervals[endpoint];
    }
  }

  /**
   * Attempt to reconnect to a WebSocket endpoint
   * @param {string} endpoint - WebSocket endpoint
   * @param {object} config - Configuration object
   */
  attemptReconnect(endpoint, config) {
    if (this.reconnectAttempts[endpoint] >= this.maxReconnectAttempts) {
      console.log(`Max reconnection attempts reached for ${endpoint}`);
      return;
    }

    this.reconnectAttempts[endpoint] = (this.reconnectAttempts[endpoint] || 0) + 1;
    
    console.log(`Attempting to reconnect to ${endpoint} (${this.reconnectAttempts[endpoint]}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect(endpoint, config);
    }, this.reconnectDelay * this.reconnectAttempts[endpoint]);
  }

  /**
   * Disconnect all WebSocket connections
   */
  disconnectAll() {
    Object.keys(this.connections).forEach(endpoint => {
      this.disconnect(endpoint);
    });
  }
}

// Create singleton instance
const wsService = new WebSocketService();

export default wsService;
