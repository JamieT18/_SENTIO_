import axios from 'axios';

// API Base URL - defaults to localhost:8000, can be overridden via environment variable
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout for better performance
});

// Request cache for deduplication and performance
const requestCache = new Map();
const CACHE_TTL = 30000; // 30 seconds default cache TTL

// Clear expired cache entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of requestCache.entries()) {
    if (now - value.timestamp > value.ttl) {
      requestCache.delete(key);
    }
  }
}, 60000); // Clean up every minute

// Helper to create cache key
const createCacheKey = (url, params) => {
  const paramsStr = params ? JSON.stringify(params) : '';
  return `${url}?${paramsStr}`;
};

// Cached GET request wrapper
const cachedGet = async (url, options = {}, ttl = CACHE_TTL) => {
  const cacheKey = createCacheKey(url, options.params);
  
  // Check cache first
  const cached = requestCache.get(cacheKey);
  if (cached && (Date.now() - cached.timestamp) < cached.ttl) {
    return cached.data;
  }
  
  // Make request
  const response = await apiClient.get(url, options);
  
  // Cache the response
  requestCache.set(cacheKey, {
    data: response.data,
    timestamp: Date.now(),
    ttl: ttl
  });
  
  return response.data;
};

// Debounce helper for API calls
const debounceTimers = new Map();
const debounce = (key, fn, delay = 300) => {
  return (...args) => {
    if (debounceTimers.has(key)) {
      clearTimeout(debounceTimers.get(key));
    }
    
    return new Promise((resolve, reject) => {
      const timer = setTimeout(async () => {
        try {
          const result = await fn(...args);
          resolve(result);
        } catch (error) {
          reject(error);
        }
        debounceTimers.delete(key);
      }, delay);
      
      debounceTimers.set(key, timer);
    });
  };
};

// Add authentication token to requests if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Dashboard API endpoints
export const dashboardApi = {
  // Get performance cards for dashboard (cached for 60s)
  getPerformanceCards: async (userId) => {
    return cachedGet(`/api/v1/dashboard/performance-cards`, {
      params: { user_id: userId }
    }, 60000);
  },

  // Get trade signals (cached for 30s)
  getTradeSignals: async (symbols = null) => {
    return cachedGet(`/api/v1/dashboard/trade-signals`, {
      params: symbols ? { symbols } : {}
    }, 30000);
  },

  // Get earnings summary (cached for 60s)
  getEarnings: async (userId) => {
    return cachedGet(`/api/v1/dashboard/earnings`, {
      params: { user_id: userId }
    }, 60000);
  },

  // Get AI trade summary (cached for 120s)
  getAiSummary: async (symbol = null) => {
    return cachedGet(`/api/v1/dashboard/ai-summary`, {
      params: symbol ? { symbol } : {}
    }, 120000);
  },

  // Get strength signal (cached for 60s)
  getStrengthSignal: async (symbol) => {
    return cachedGet(`/api/v1/dashboard/strength-signal`, {
      params: { symbol }
    }, 60000);
  },

  // Get trade journal entries (cached for 30s)
  getTradeJournal: async (userId, limit = 50) => {
    return cachedGet(`/api/v1/dashboard/trade-journal`, {
      params: { user_id: userId, limit }
    }, 30000);
  },

  // Add trade journal entry (no caching for POST)
  addTradeJournalEntry: async (userId, entry) => {
    const response = await apiClient.post(`/api/v1/dashboard/trade-journal`, entry, {
      params: { user_id: userId }
    });
    // Invalidate journal cache
    requestCache.delete(createCacheKey(`/api/v1/dashboard/trade-journal`, { user_id: userId, limit: 50 }));
    return response.data;
  },
};

// Subscription API endpoints
export const subscriptionApi = {
  // Get pricing information (cached for 5 minutes)
  getPricing: async () => {
    return cachedGet(`/api/v1/subscription/pricing`, {}, 300000);
  },

  // Get user subscription (cached for 60s)
  getUserSubscription: async (userId) => {
    return cachedGet(`/api/v1/subscription/${userId}`, {}, 60000);
  },

  // Calculate profit sharing (no caching)
  calculateProfitSharing: async (userId, tradingProfit) => {
    const response = await apiClient.post(`/api/v1/subscription/profit-sharing/calculate`, {
      user_id: userId,
      trading_profit: tradingProfit
    });
    return response.data;
  },

  // Get profit sharing balance (cached for 60s)
  getProfitSharingBalance: async (userId) => {
    return cachedGet(`/api/v1/subscription/profit-sharing/${userId}`, {}, 60000);
  },
};

// System API endpoints
export const systemApi = {
  // Health check (no caching)
  healthCheck: async () => {
    const response = await apiClient.get(`/api/v1/health`);
    return response.data;
  },

  // Get system status (cached for 10s)
  getStatus: async () => {
    return cachedGet(`/api/v1/status`, {}, 10000);
  },
};

// Market Data API endpoints
export const marketApi = {
  // Get single quote (cached for 15s)
  getQuote: async (symbol) => {
    return cachedGet(`/api/v1/market/quote/${symbol}`, {}, 15000);
  },

  // Get multiple quotes (cached for 15s)
  getQuotes: async (symbols) => {
    const symbolsParam = Array.isArray(symbols) ? symbols.join(',') : symbols;
    return cachedGet(`/api/v1/market/quotes`, {
      params: { symbols: symbolsParam }
    }, 15000);
  },

  // Get historical data (cached for 5 minutes)
  getHistory: async (symbol, startDate = null, endDate = null, timeframe = '1day') => {
    return cachedGet(`/api/v1/market/history/${symbol}`, {
      params: {
        start_date: startDate,
        end_date: endDate,
        timeframe: timeframe
      }
    }, 300000);
  },
};

// Market Intelligence API endpoints
export const marketIntelligenceApi = {
  getSectorPerformance: async () => {
    return cachedGet('/api/v1/market/sector-performance', {}, 60000);
  },
  getMacroTrends: async () => {
    return cachedGet('/api/v1/market/macro-trends', {}, 60000);
  },
  getNewsSentiment: async (symbol) => {
    return cachedGet(`/api/v1/market/news-sentiment`, { params: { symbol } }, 60000);
  },
  detectMarketAnomalies: async (symbols) => {
    return cachedGet(`/api/v1/market/anomalies`, { params: { symbols: symbols.join(',') } }, 60000);
  },
  getEtfFlows: async () => {
    return cachedGet('/api/v1/market/etf-flows', {}, 60000);
  },
  getGlobalEvents: async () => {
    return cachedGet('/api/v1/market/global-events', {}, 60000);
  },
};

// Analytics API endpoints
export const analyticsApi = {
  // Get portfolio history (cached for 60s)
  getPortfolioHistory: async (userId, days = 30) => {
    return cachedGet(`/api/v1/analytics/portfolio-history`, {
      params: { user_id: userId, days }
    }, 60000);
  },

  // Get trade performance analytics (cached for 60s)
  getTradePerformance: async (userId) => {
    return cachedGet(`/api/v1/analytics/trade-performance`, {
      params: { user_id: userId }
    }, 60000);
  },

  // Get user activity trends (cached for 60s)
  getUserActivity: async (userId, days = 30) => {
    return cachedGet(`/api/v1/analytics/user-activity`, {
      params: { user_id: userId, days }
    }, 60000);
  },

  // Export analytics report (no caching)
  exportAnalyticsReport: async (userId, format = 'json', includeCharts = true) => {
    const response = await apiClient.get(`/api/v1/export/analytics-report`, {
      params: { 
        user_id: userId, 
        format,
        include_charts: includeCharts
      },
      responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `analytics_report_${userId}_${new Date().toISOString().split('T')[0]}.${format}`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    
    return { success: true };
  },
};

// Admin Analytics API endpoints
export const adminAnalyticsApi = {
  // Get historical growth analytics (admin only, cached for 120s)
  getHistoricalGrowth: async (days = 90) => {
    return cachedGet(`/api/v1/admin/analytics/historical-growth`, {
      params: { days }
    }, 120000);
  },

  // Get revenue analytics (admin only, cached for 60s)
  getRevenueAnalytics: async () => {
    return cachedGet(`/api/v1/admin/analytics/revenue`, {}, 60000);
  },

  // Get user analytics (admin only, cached for 60s)
  getUserAnalytics: async () => {
    return cachedGet(`/api/v1/admin/analytics/users`, {}, 60000);
  },
};

// Safety & Risk API endpoints
export const safetyRiskApi = {
  getRiskMetrics: async (userId) => {
    return cachedGet(`/api/v1/risk/metrics`, { params: { user_id: userId } }, 60000);
  },
  getRiskStressTest: async (userId) => {
    return cachedGet(`/api/v1/risk/stress-test`, { params: { user_id: userId } }, 60000);
  },
  getRiskAnomalyScore: async (userId) => {
    return cachedGet(`/api/v1/risk/anomaly-score`, { params: { user_id: userId } }, 60000);
  },
  getRiskAlert: async (userId) => {
    return cachedGet(`/api/v1/risk/alert`, { params: { user_id: userId } }, 60000);
  },
  getRiskDashboardSummary: async (userId) => {
    return fetch(`/api/v1/risk/dashboard-summary?user_id=${userId}`)
      .then((res) => res.json());
  },
};

// Strategy API endpoints
export const strategyApi = {
  // Get strategy optimizer results (no caching)
  getOptimizerResults: async (strategyId, marketData, searchSpace) => {
    return fetch(`/api/v1/strategy/optimizer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategyId, marketData, searchSpace })
    }).then((res) => res.json());
  },
};

// Convenience wrapper combining all analytics functions
const api = {
  // Dashboard APIs
  getPerformanceCards: dashboardApi.getPerformanceCards,
  getTradeSignals: dashboardApi.getTradeSignals,
  getEarnings: dashboardApi.getEarnings,
  getAiSummary: dashboardApi.getAiSummary,
  getStrengthSignal: dashboardApi.getStrengthSignal,
  getTradeJournal: dashboardApi.getTradeJournal,
  addTradeJournalEntry: dashboardApi.addTradeJournalEntry,

  // Subscription APIs
  getPricing: subscriptionApi.getPricing,
  getUserSubscription: subscriptionApi.getUserSubscription,
  calculateProfitSharing: subscriptionApi.calculateProfitSharing,
  getProfitSharingBalance: subscriptionApi.getProfitSharingBalance,

  // System APIs
  healthCheck: systemApi.healthCheck,
  getStatus: systemApi.getStatus,

  // Market APIs
  getQuote: marketApi.getQuote,
  getQuotes: marketApi.getQuotes,
  getHistory: marketApi.getHistory,

  // Market Intelligence APIs
  getSectorPerformance: marketIntelligenceApi.getSectorPerformance,
  getMacroTrends: marketIntelligenceApi.getMacroTrends,
  getNewsSentiment: marketIntelligenceApi.getNewsSentiment,
  detectMarketAnomalies: marketIntelligenceApi.detectMarketAnomalies,
  getEtfFlows: marketIntelligenceApi.getEtfFlows,
  getGlobalEvents: marketIntelligenceApi.getGlobalEvents,

  // Analytics APIs
  getPortfolioHistory: analyticsApi.getPortfolioHistory,
  getTradePerformance: analyticsApi.getTradePerformance,
  getUserActivity: analyticsApi.getUserActivity,
  exportAnalyticsReport: analyticsApi.exportAnalyticsReport,

  // Admin Analytics APIs
  getHistoricalGrowth: adminAnalyticsApi.getHistoricalGrowth,
  getRevenueAnalytics: adminAnalyticsApi.getRevenueAnalytics,
  getUserAnalytics: adminAnalyticsApi.getUserAnalytics,

  // Safety & Risk APIs
  getRiskMetrics: safetyRiskApi.getRiskMetrics,
  getRiskStressTest: safetyRiskApi.getRiskStressTest,
  getRiskAnomalyScore: safetyRiskApi.getRiskAnomalyScore,
  getRiskAlert: safetyRiskApi.getRiskAlert,
  getRiskDashboardSummary: safetyRiskApi.getRiskDashboardSummary,

  // Strategy APIs
  getOptimizerResults: strategyApi.getOptimizerResults,

  // Cache control
  cache: cacheControl,
};

// Export cache control functions
export const cacheControl = {
  clear: () => requestCache.clear(),
  invalidate: (url, params) => requestCache.delete(createCacheKey(url, params)),
  size: () => requestCache.size
};

export default api;
