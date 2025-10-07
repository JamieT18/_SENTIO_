import React, { useState } from 'react';
import PortfolioChart from './PortfolioChart';
import TradePerformanceChart from './TradePerformanceChart';
import ActivityHeatmap from './ActivityHeatmap';
import api from '../services/api';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = ({ userId }) => {
  const [activeTab, setActiveTab] = useState('performance');
  const [timePeriod, setTimePeriod] = useState(30);
  const [exporting, setExporting] = useState(false);
  // Accept external widget toggling and report status
  // Optionally, props: visibleWidgets, reportStatus

  const handleExport = async (format) => {
    try {
      setExporting(true);
      await api.exportAnalyticsReport(userId, format, true);
      alert(`Analytics report downloaded successfully as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Error exporting report:', error);
      alert('Failed to export analytics report');
    } finally {
      setExporting(false);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'performance':
        return (
          <div className="tab-content">
            <PortfolioChart userId={userId} days={timePeriod} />
          </div>
        );
      case 'trades':
        return (
          <div className="tab-content">
            <TradePerformanceChart userId={userId} />
          </div>
        );
      case 'activity':
        return (
          <div className="tab-content">
            <ActivityHeatmap userId={userId} days={timePeriod} />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h2>Analytics & Reports</h2>
        <div className="analytics-controls">
          <div className="time-period-selector">
            <label>Time Period:</label>
            <select 
              value={timePeriod} 
              onChange={(e) => setTimePeriod(Number(e.target.value))}
            >
              <option value={7}>7 Days</option>
              <option value={30}>30 Days</option>
              <option value={60}>60 Days</option>
              <option value={90}>90 Days</option>
            </select>
          </div>
          <div className="export-controls">
            <button 
              onClick={() => handleExport('json')} 
              disabled={exporting}
              className="export-btn"
            >
              {exporting ? 'Exporting...' : 'Export JSON'}
            </button>
            <button 
              onClick={() => handleExport('csv')} 
              disabled={exporting}
              className="export-btn"
            >
              {exporting ? 'Exporting...' : 'Export CSV'}
            </button>
          </div>
        </div>
      </div>
      {/* Optionally show external report status */}
      {/* {reportStatus && <div className="report-status">{reportStatus}</div>} */}
      <div className="analytics-tabs">
        <button
          className={`tab-button ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          Portfolio Performance
        </button>
        <button
          className={`tab-button ${activeTab === 'trades' ? 'active' : ''}`}
          onClick={() => setActiveTab('trades')}
        >
          Trade Analysis
        </button>
        <button
          className={`tab-button ${activeTab === 'activity' ? 'active' : ''}`}
          onClick={() => setActiveTab('activity')}
        >
          Activity Trends
        </button>
      </div>
      {renderTabContent()}
    </div>
  );
};

export default AnalyticsDashboard;
