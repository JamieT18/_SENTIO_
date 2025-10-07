/**
 * Sentio 2.0 JavaScript/TypeScript SDK
 * 
 * Official SDK for the Sentio 2.0 Trading API
 * Supports both Browser and Node.js environments
 */

export interface SentioConfig {
  baseUrl?: string;
  token?: string;
  timeout?: number;
  maxRetries?: number;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface TradeSignal {
  symbol: string;
  signal: 'buy' | 'sell' | 'hold';
  confidence: number;
  consensus_strength: number;
  timestamp: string;
}

export interface Position {
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  unrealized_pnl: number;
}

export interface PerformanceMetrics {
  total_return: number;
  total_return_pct: number;
  win_rate: number;
  total_trades: number;
  avg_profit: number;
}

export interface SubscriptionTier {
  tier: 'free' | 'basic' | 'professional' | 'enterprise';
  price: number;
  features: Record<string, any>;
}

export class SentioAPIError extends Error {
  statusCode?: number;
  response?: any;

  constructor(message: string, statusCode?: number, response?: any) {
    super(message);
    this.name = 'SentioAPIError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

export class SentioClient {
  private baseUrl: string;
  private token: string | null;
  private timeout: number;
  private maxRetries: number;

  /**
   * Create a new Sentio API client
   * 
   * @param config - Client configuration
   * 
   * @example
   * ```typescript
   * const client = new SentioClient({
   *   baseUrl: 'http://localhost:8000',
   *   token: 'your-jwt-token'
   * });
   * ```
   */
  constructor(config: SentioConfig = {}) {
    this.baseUrl = (config.baseUrl || 'http://localhost:8000').replace(/\/$/, '');
    this.token = config.token || null;
    this.timeout = config.timeout || 30000;
    this.maxRetries = config.maxRetries || 3;
  }

  /**
   * Make HTTP request with error handling and retries
   */
  private async request<T = any>(
    method: string,
    endpoint: string,
    data?: any,
    params?: Record<string, any>,
    requireAuth: boolean = true
  ): Promise<T> {
    if (requireAuth && !this.token) {
      throw new SentioAPIError('Authentication required. Please login first.');
    }

    const url = new URL(`${this.baseUrl}${endpoint}`);
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          url.searchParams.append(key, params[key].toString());
        }
      });
    }

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config: RequestInit = {
      method,
      headers,
    };

    if (data) {
      config.body = JSON.stringify(data);
    }

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url.toString(), {
          ...config,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          return await response.json();
        }

        const errorData = response.headers.get('content-type')?.includes('application/json')
          ? await response.json()
          : { detail: await response.text() };

        if (response.status === 401) {
          throw new SentioAPIError(
            'Authentication failed. Token may be expired.',
            401,
            errorData
          );
        } else if (response.status === 404) {
          throw new SentioAPIError(
            `Endpoint not found: ${endpoint}`,
            404,
            errorData
          );
        } else if (response.status >= 500) {
          if (attempt < this.maxRetries - 1) {
            console.warn(`Server error, retrying... (attempt ${attempt + 1}/${this.maxRetries})`);
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
            continue;
          }
          throw new SentioAPIError(
            `Server error: ${response.status}`,
            response.status,
            errorData
          );
        } else {
          throw new SentioAPIError(
            errorData.detail || `Request failed with status ${response.status}`,
            response.status,
            errorData
          );
        }
      } catch (error) {
        if (error instanceof SentioAPIError) {
          throw error;
        }
        if (attempt < this.maxRetries - 1) {
          console.warn(`Request failed, retrying... (attempt ${attempt + 1}/${this.maxRetries})`);
          await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
          continue;
        }
        throw new SentioAPIError(`Request failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }

    throw new SentioAPIError('Max retries exceeded');
  }

  // Authentication Methods

  /**
   * Login and obtain JWT token
   * 
   * @param username - Username
   * @param password - Password
   * @returns Login response with access token
   * 
   * @example
   * ```typescript
   * const response = await client.login('username', 'password');
   * console.log(`Token: ${response.access_token}`);
   * ```
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>(
      'POST',
      '/api/v1/auth/login',
      { username, password },
      undefined,
      false
    );
    this.token = response.access_token;
    return response;
  }

  // General Endpoints

  /**
   * Check API health status
   */
  async healthCheck(): Promise<any> {
    return this.request('GET', '/api/v1/health', undefined, undefined, false);
  }

  /**
   * Get system status and metrics
   */
  async getStatus(): Promise<any> {
    return this.request('GET', '/api/v1/status');
  }

  // Trading Operations

  /**
   * Analyze a stock symbol
   * 
   * @param symbol - Stock symbol (e.g., "AAPL")
   * @returns Analysis results with signal and confidence
   */
  async analyzeSymbol(symbol: string): Promise<any> {
    return this.request('POST', '/api/v1/analyze', { symbol });
  }

  /**
   * Execute a trade
   * 
   * @param symbol - Stock symbol
   * @param action - Trade action ("buy" or "sell")
   * @param quantity - Number of shares
   * @param price - Optional limit price
   * @returns Trade execution result
   */
  async executeTrade(
    symbol: string,
    action: 'buy' | 'sell',
    quantity: number,
    price?: number
  ): Promise<any> {
    const data: any = { symbol, action, quantity };
    if (price !== undefined) {
      data.price = price;
    }
    return this.request('POST', '/api/v1/trade', data);
  }

  /**
   * Get open positions
   * 
   * @param userId - Optional user ID filter
   * @returns List of open positions
   */
  async getPositions(userId?: string): Promise<{ positions: Position[] }> {
    const params = userId ? { user_id: userId } : undefined;
    return this.request('GET', '/api/v1/positions', undefined, params);
  }

  /**
   * Get performance metrics
   * 
   * @param userId - Optional user ID filter
   * @returns Performance metrics and statistics
   */
  async getPerformance(userId?: string): Promise<PerformanceMetrics> {
    const params = userId ? { user_id: userId } : undefined;
    return this.request('GET', '/api/v1/performance', undefined, params);
  }

  // Strategy Management

  /**
   * Get list of available trading strategies
   */
  async getStrategies(): Promise<any> {
    return this.request('GET', '/api/v1/strategies');
  }

  /**
   * Enable or disable a trading strategy
   * 
   * @param strategyName - Name of the strategy
   * @param enabled - True to enable, false to disable
   * @returns Updated strategy status
   */
  async toggleStrategy(strategyName: string, enabled: boolean): Promise<any> {
    return this.request('POST', `/api/v1/strategies/${strategyName}/toggle`, { enabled });
  }

  // Analysis & Intelligence

  /**
   * Get insider trades for a symbol
   * 
   * @param symbol - Stock symbol
   * @param limit - Maximum number of trades to return
   * @returns List of insider trades
   */
  async getInsiderTrades(symbol: string, limit: number = 50): Promise<any> {
    return this.request('GET', `/api/v1/insider-trades/${symbol}`, undefined, { limit });
  }

  /**
   * Get top symbols traded by insiders
   * 
   * @param limit - Number of symbols to return
   * @returns List of top insider-traded symbols
   */
  async getTopInsiderSymbols(limit: number = 10): Promise<any> {
    return this.request('GET', '/api/v1/insider-trades/top', undefined, { limit });
  }

  /**
   * Get fundamental analysis for a symbol
   * 
   * @param symbol - Stock symbol
   * @returns Fundamental analysis scores and recommendation
   */
  async getFundamentalAnalysis(symbol: string): Promise<any> {
    return this.request('GET', `/api/v1/fundamental/${symbol}`);
  }

  // Dashboard Endpoints

  /**
   * Get trade signals for multiple symbols
   * 
   * @param symbols - Array of stock symbols
   * @returns Trade signals for each symbol
   */
  async getTradeSignals(symbols?: string[]): Promise<{ signals: TradeSignal[]; count: number }> {
    const params = symbols ? { symbols: symbols.join(',') } : undefined;
    return this.request('GET', '/api/v1/dashboard/trade-signals', undefined, params);
  }

  /**
   * Get earnings summary for a user
   * 
   * @param userId - User identifier
   * @returns Comprehensive earnings and performance data
   */
  async getEarnings(userId: string): Promise<any> {
    return this.request('GET', '/api/v1/dashboard/earnings', undefined, { user_id: userId });
  }

  /**
   * Get AI-generated trade summary
   * 
   * @param symbol - Optional stock symbol for focused analysis
   * @returns AI-generated insights and recommendations
   */
  async getAISummary(symbol?: string): Promise<any> {
    const params = symbol ? { symbol } : undefined;
    return this.request('GET', '/api/v1/dashboard/ai-summary', undefined, params);
  }

  /**
   * Get market strength signal
   * 
   * @param symbol - Optional stock symbol
   * @returns Market strength indicators
   */
  async getStrengthSignal(symbol?: string): Promise<any> {
    const params = symbol ? { symbol } : undefined;
    return this.request('GET', '/api/v1/dashboard/strength-signal', undefined, params);
  }

  /**
   * Get trade journal entries
   * 
   * @param userId - User identifier
   * @param limit - Maximum number of entries
   * @returns List of trade journal entries
   */
  async getTradeJournal(userId: string, limit: number = 50): Promise<any> {
    return this.request('GET', '/api/v1/dashboard/trade-journal', undefined, {
      user_id: userId,
      limit,
    });
  }

  /**
   * Add a manual trade journal entry
   * 
   * @param entry - Journal entry details
   * @returns Created journal entry
   */
  async addTradeJournalEntry(entry: {
    userId: string;
    symbol: string;
    action: string;
    quantity: number;
    price: number;
    notes?: string;
  }): Promise<any> {
    const data: any = {
      user_id: entry.userId,
      symbol: entry.symbol,
      action: entry.action,
      quantity: entry.quantity,
      price: entry.price,
    };
    if (entry.notes) {
      data.notes = entry.notes;
    }
    return this.request('POST', '/api/v1/dashboard/trade-journal', data);
  }

  /**
   * Get performance metrics as dashboard cards
   * 
   * @param userId - User identifier
   * @returns Performance metrics formatted as dashboard cards
   */
  async getPerformanceCards(userId: string): Promise<any> {
    return this.request('GET', '/api/v1/dashboard/performance-cards', undefined, {
      user_id: userId,
    });
  }

  // Subscription & Billing

  /**
   * Get subscription pricing information
   * 
   * @returns Available subscription tiers and pricing
   */
  async getPricing(): Promise<{ tiers: SubscriptionTier[] }> {
    return this.request('GET', '/api/v1/subscription/pricing', undefined, undefined, false);
  }

  /**
   * Get user subscription details
   * 
   * @param userId - User identifier
   * @returns Subscription details and features
   */
  async getSubscription(userId: string): Promise<any> {
    return this.request('GET', `/api/v1/subscription/${userId}`);
  }

  /**
   * Calculate profit sharing fee
   * 
   * @param userId - User identifier
   * @param profit - Trading profit amount
   * @returns Profit sharing calculation
   */
  async calculateProfitSharing(userId: string, profit: number): Promise<any> {
    return this.request('POST', '/api/v1/subscription/profit-sharing/calculate', {
      user_id: userId,
      profit,
    });
  }

  /**
   * Get profit sharing balance
   * 
   * @param userId - User identifier
   * @returns Profit sharing balance and history
   */
  async getProfitSharingBalance(userId: string): Promise<any> {
    return this.request('GET', `/api/v1/subscription/profit-sharing/${userId}`);
  }

  // Utility Methods

  /**
   * Load all dashboard data in a single operation
   * 
   * @param userId - User identifier
   * @param symbols - Optional list of symbols for trade signals
   * @returns Object containing all dashboard data
   */
  async loadDashboardData(userId: string, symbols?: string[]): Promise<any> {
    const [performanceCards, tradeSignals, earnings, aiSummary, strengthSignal] = await Promise.all([
      this.getPerformanceCards(userId),
      this.getTradeSignals(symbols),
      this.getEarnings(userId),
      this.getAISummary(),
      this.getStrengthSignal(),
    ]);

    return {
      performanceCards,
      tradeSignals,
      earnings,
      aiSummary,
      strengthSignal,
    };
  }
}

// Export types for convenience
export type {
  SentioConfig as Config,
  TradeSignal as Signal,
  Position,
  PerformanceMetrics,
  SubscriptionTier as Tier,
};
