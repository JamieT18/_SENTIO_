// JavaScript SDK for Sentio 2.0 API integration
class SentioSDK {
  constructor(baseUrl, apiKey = null) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
  }

  _headers() {
    const headers = { 'Content-Type': 'application/json' };
    if (this.apiKey) headers['Authorization'] = `Bearer ${this.apiKey}`;
    return headers;
  }

  async getOptimizerResults(params) {
    const url = `${this.baseUrl}/api/v1/strategy/optimizer`;
    const resp = await fetch(url, {
      method: 'POST',
      headers: this._headers(),
      body: JSON.stringify(params)
    });
    return resp.ok ? await resp.json() : {};
  }

  async getRiskDashboard() {
    const url = `${this.baseUrl}/api/v1/risk/dashboard-summary`;
    const resp = await fetch(url, {
      method: 'GET',
      headers: this._headers()
    });
    return resp.ok ? await resp.json() : {};
  }

  // Add more endpoints as needed
}

export default SentioSDK;
