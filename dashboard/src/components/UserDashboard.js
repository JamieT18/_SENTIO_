import React, { useState, useEffect } from 'react';
import PortfolioChart from './PortfolioChart';
import TradePerformanceChart from './TradePerformanceChart';
import ActivityHeatmap from './ActivityHeatmap';
import AIRecommendations from './AIRecommendations';
import NotificationPreferences from './NotificationPreferences';
import TradeJournal from './TradeJournal';
import SafetyRiskWidget from './SafetyRiskWidget';
import ExplainableAI from './ExplainableAI';
import Onboarding from './Onboarding';
import CommunityLeaderboard from './CommunityLeaderboard';
import StrategySharing from './StrategySharing';
import CommunityChat from './community/chat';
import CommunityQA from './community/qa';
import GamificationWidget from './GamificationWidget';
import DeeperAnalytics from './DeeperAnalytics';
import Notifications from './Notifications';
import UserSuggestions from './UserSuggestions';
import ProfileWidget from './ProfileWidget';
import AvatarUploader from './AvatarUploader';
import BadgesWidget from './BadgesWidget';
import BillingWidget from './BillingWidget';
import ProfitSignalsWidget from './ProfitSignalsWidget';
import ArbitrageWidget from './ArbitrageWidget';
import OffersWidget from './OffersWidget';
import CoreUpgradesWidget from './CoreUpgradesWidget';
import StrategyAnalyticsWidget from './StrategyAnalyticsWidget';
import RealTimeAnalyticsWidget from './RealTimeAnalyticsWidget';
import RealTimeChartWidget from './RealTimeChartWidget';
import RealTimeAlertsWidget from './RealTimeAlertsWidget';
import './GamificationWidget.css';
import './DeeperAnalytics.css';
import './Notifications.css';
import './TradeJournal.css';

const TABS = [
  { label: 'Portfolio', component: PortfolioChart },
  { label: 'Performance', component: TradePerformanceChart },
  { label: 'Activity', component: ActivityHeatmap },
  { label: 'AI Insights', component: AIRecommendations },
  { label: 'Trade Journal', component: TradeJournal },
  { label: 'Notifications', component: Notifications },
  { label: 'Safety & Risk', component: SafetyRiskWidget },
  { label: 'Explainable AI', component: ExplainableAI },
  { label: 'Community', component: ({ userId }) => (
      <div className="community-section">
        <CommunityLeaderboard />
        <StrategySharing userId={userId} />
        <CommunityChat userId={userId} />
        <CommunityQA userId={userId} />
        <UserSuggestions userId={userId} />
      </div>
    )
  },
  { label: 'Advanced Analytics', component: DeeperAnalytics },
  { label: 'Gamification', component: GamificationWidget },
  { label: 'Profile', component: ({ userId }) => (
      <div className="profile-section">
        <ProfileWidget userId={userId} />
        <AvatarUploader userId={userId} />
        <BadgesWidget userBadges={["Top Trader", "Early Adopter", "Challenge Champion"]} />
        <NotificationPreferences userId={userId} />
        {/* Add more profile widgets here: avatar, bio, badges, etc. */}
      </div>
    )
  },
  { label: 'Billing', component: ({ userId }) => (
      <div className="billing-section">
        <BillingWidget userId={userId} />
        {/* Add more monetization widgets here: payment history, referral rewards, etc. */}
      </div>
    )
  },
  { label: 'Profit Signals', component: ({ userId }) => (
      <div className="profit-signals-section">
        <ProfitSignalsWidget userId={userId} />
        {/* Add more profit-boosting widgets here: premium signals, arbitrage, etc. */}
      </div>
    )
  },
  { label: 'Arbitrage', component: ({ userId }) => (
      <div className="arbitrage-section">
        <ArbitrageWidget userId={userId} />
        {/* Add more profit-maximizing widgets here: cross-exchange analytics, etc. */}
      </div>
    )
  },
  { label: 'Offers', component: ({ userId }) => (
      <div className="offers-section">
        <OffersWidget userId={userId} />
        {/* Add more rewards, bonuses, and exclusive deals here */}
      </div>
    )
  },
  { label: 'Core Upgrades', component: () => (
      <div className="core-upgrades-section">
        <CoreUpgradesWidget />
        {/* Add more system-level improvements and diagnostics here */}
      </div>
    )
  },
  { label: 'Strategy Analytics', component: () => (
      <div className="strategy-analytics-section">
        <StrategyAnalyticsWidget />
        {/* Add more analytics, feedback, and optimization tools here */}
      </div>
    )
  },
  { label: 'Real-Time Analytics', component: ({ userId }) => (
      <div className="realtime-analytics-section">
        <RealTimeAnalyticsWidget userId={userId} />
        {/* Add more live data, charts, and streaming analytics here */}
      </div>
    )
  },
  { label: 'Live Chart', component: () => (
      <div className="realtime-chart-section">
        <RealTimeChartWidget />
        {/* Add more live chart types and analytics here */}
      </div>
    )
  },
  { label: 'Live Alerts', component: () => (
      <div className="realtime-alerts-section">
        <RealTimeAlertsWidget />
        {/* Add more alert types and notification settings here */}
      </div>
    )
  },
];

// Branded dashboard header
function BrandedHeader({ user }) {
  return (
    <header className="branded-header">
      <h1>Sentio Dashboard</h1>
      <span>Welcome, {user?.name || 'User'}!</span>
    </header>
  );
}

// Live trade summary stub
function LiveTradeSummary({ trades }) {
  return (
    <section className="live-trade-summary">
      <h2>Live Trade Summary</h2>
      {/* ...render live trades... */}
      <div>{trades?.length || 0} trades active</div>
    </section>
  );
}

// Profit-sharing and strength signal stub
function ProfitSharingStrength({ stocks }) {
  return (
    <section className="profit-strength">
      <h2>Profit Sharing & Strength Signal</h2>
      {/* ...render profit sharing and strength signals... */}
      <ul>
        {stocks?.map((s, i) => (
          <li key={i}>{s.symbol}: Profit Share {s.profitShare}%, Strength {s.strength}</li>
        ))}
      </ul>
    </section>
  );
}

// Terms of Service acceptance stub
function TermsOfService({ accepted, onAccept }) {
  return (
    <section className="terms-of-service">
      <h2>Terms of Service</h2>
      <p>Please accept the Terms of Service to continue.</p>
      <button disabled={accepted} onClick={onAccept}>
        {accepted ? "Accepted" : "Accept Terms"}
      </button>
    </section>
  );
}

// Secure login system stub
function SecureLogin({ onLogin }) {
  return (
    <section className="secure-login">
      <h2>Secure Login</h2>
      <form onSubmit={e => { e.preventDefault(); onLogin(); }}>
        <input type="text" placeholder="Username" required />
        <input type="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
    </section>
  );
}

const UserDashboard = ({ userId }) => {
  const [userData, setUserData] = useState(null);
  const [activeTab, setActiveTab] = useState(TABS[0].label);
  const [livePortfolio, setLivePortfolio] = useState(null);
  const [livePerformance, setLivePerformance] = useState(null);
  const [liveNotifications, setLiveNotifications] = useState([]);
  const [liveTrades, setLiveTrades] = useState([]);
  const [portfolioStocks, setPortfolioStocks] = useState([]);

  useEffect(() => {
    // Fetch user data from backend
    fetch(`/api/user/${userId}`)
      .then(res => res.json())
      .then(data => {
        setUserData(data);
        setLivePortfolio(data.portfolio);
        setLivePerformance(data.performance);
        setLiveNotifications(data.notifications);
        setLiveTrades(data.trades);
        setPortfolioStocks(data.portfolioStocks);
      });
  }, [userId]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/user/' + userId);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.portfolio) setLivePortfolio(data.portfolio);
      if (data.performance) setLivePerformance(data.performance);
      if (data.notifications) setLiveNotifications(data.notifications);
      if (data.trades) setLiveTrades(data.trades);
      if (data.portfolioStocks) setPortfolioStocks(data.portfolioStocks);
    };
    ws.onerror = () => {};
    ws.onclose = () => {};
    return () => ws.close();
  }, [userId]);

  return (
    <div className="user-dashboard">
      <BrandedHeader user={userData} />
      <nav className="dashboard-tabs" aria-label="Dashboard Navigation">
        {TABS.map(tab => (
          <button
            key={tab.label}
            className={activeTab === tab.label ? 'active' : ''}
            onClick={() => setActiveTab(tab.label)}
            aria-current={activeTab === tab.label ? 'page' : undefined}
            aria-label={`Go to ${tab.label}`}
            tabIndex={0}
          >
            {tab.label}
          </button>
        ))}
      </nav>
      <div className="dashboard-content">
        {TABS.map(tab =>
          activeTab === tab.label ? (
            <div key={tab.label} className="tab-content" role="tabpanel" aria-labelledby={`tab-${tab.label}`}>
              {tab.label === 'Gamification' ? (
                <GamificationWidget userId={userId} />
              ) : (
                <tab.component userId={userId} />
              )}
            </div>
          ) : null
        )}
        <LiveTradeSummary trades={liveTrades} />
        <ProfitSharingStrength stocks={portfolioStocks} />
        <TermsOfService accepted={userData?.termsAccepted} onAccept={() => {}} />
        <SecureLogin onLogin={() => {}} />
      </div>
    </div>
  );
};

export default UserDashboard;
