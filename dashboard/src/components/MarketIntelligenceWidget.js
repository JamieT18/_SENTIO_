import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function MarketIntelligenceWidget() {
  const [sectorPerf, setSectorPerf] = useState(null);
  const [macroTrends, setMacroTrends] = useState(null);
  const [newsSentiment, setNewsSentiment] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [etfFlows, setEtfFlows] = useState(null);
  const [globalEvents, setGlobalEvents] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchIntelligence() {
      setLoading(true);
      setError(null);
      try {
        // Replace with actual API calls
        const sector = await api.getSectorPerformance();
        const macro = await api.getMacroTrends();
        const news = await api.getNewsSentiment('AAPL');
        const anomaly = await api.detectMarketAnomalies(['AAPL', 'MSFT', 'GOOG', 'TSLA']);
        const etf = await api.getEtfFlows();
        const events = await api.getGlobalEvents();
        setSectorPerf(sector);
        setMacroTrends(macro);
        setNewsSentiment(news);
        setAnomalies(anomaly);
        setEtfFlows(etf);
        setGlobalEvents(events);
      } catch (err) {
        setError('Failed to load market intelligence');
      } finally {
        setLoading(false);
      }
    }
    fetchIntelligence();
  }, []);

  if (loading) return <div className="market-intel-widget">Loading market intelligence...</div>;
  if (error) return <div className="market-intel-widget error">{error}</div>;

  return (
    <div className="market-intel-widget">
      <h3>Market Intelligence</h3>
      {sectorPerf && (
        <div className="intel-section">
          <strong>Sector Performance:</strong>
          <ul>
            {Object.entries(sectorPerf.sector_performance).map(([sector, perf]) => (
              <li key={sector}>{sector}: <span style={{color: perf > 0 ? '#10b981' : '#ef4444'}}>{perf.toFixed(2)}%</span></li>
            ))}
          </ul>
        </div>
      )}
      {macroTrends && (
        <div className="intel-section">
          <strong>Macro Trends:</strong>
          <ul>
            {Object.entries(macroTrends.macro_trends).map(([k, v]) => (
              <li key={k}>{k}: <span>{v.toFixed(2)}</span></li>
            ))}
          </ul>
        </div>
      )}
      {newsSentiment && (
        <div className="intel-section">
          <strong>News Sentiment ({newsSentiment.symbol}):</strong>
          <span style={{color: newsSentiment.sentiment > 0 ? '#10b981' : '#ef4444', marginLeft: 8}}>{newsSentiment.sentiment.toFixed(2)}</span>
          <ul>
            {newsSentiment.headlines.map((h, idx) => <li key={idx}>{h}</li>)}
          </ul>
        </div>
      )}
      {anomalies && (
        <div className="intel-section">
          <strong>Market Anomalies:</strong>
          <ul>
            {Object.entries(anomalies.anomalies).map(([sym, flag]) => (
              <li key={sym}>{sym}: <span style={{color: flag ? '#f59e0b' : '#64748b'}}>{flag ? 'Anomaly' : 'Normal'}</span></li>
            ))}
          </ul>
        </div>
      )}
      {etfFlows && (
        <div className="intel-section">
          <strong>ETF Flows:</strong>
          <ul>
            {Object.entries(etfFlows.etf_flows).map(([etf, flow]) => (
              <li key={etf}>{etf}: <span style={{color: flow > 0 ? '#10b981' : '#ef4444'}}>{flow.toFixed(0)}M</span></li>
            ))}
          </ul>
        </div>
      )}
      {globalEvents && (
        <div className="intel-section">
          <strong>Global Events:</strong>
          <ul>
            {globalEvents.global_events.map((ev, idx) => (
              <li key={idx}>{ev.event}: <span style={{color: ev.impact > 0 ? '#10b981' : '#ef4444'}}>{ev.impact.toFixed(2)}</span></li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
