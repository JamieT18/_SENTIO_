import React, { useState } from 'react';

const BADGES = [
  { name: 'Top Trader', description: 'Highest profit in a week', color: '#ffd700' },
  { name: 'Early Adopter', description: 'Joined Sentio in the first month', color: '#1976d2' },
  { name: 'Challenge Champion', description: 'Completed 10 challenges', color: '#43a047' },
  { name: 'Community Leader', description: 'Most upvoted suggestion', color: '#e57373' }
];

export default function BadgesWidget({ userBadges }) {
  const [showDetails, setShowDetails] = useState(null);

  return (
    <div className="badges-widget">
      <h3>Your Badges</h3>
      <div className="badges-list">
        {userBadges.map((badge, idx) => {
          const badgeInfo = BADGES.find(b => b.name === badge) || { name: badge, color: '#bfc8d6', description: '' };
          return (
            <span
              key={idx}
              className="badge"
              style={{ background: badgeInfo.color }}
              onMouseEnter={() => setShowDetails(idx)}
              onMouseLeave={() => setShowDetails(null)}
              tabIndex={0}
              aria-label={badgeInfo.description}
            >
              {badgeInfo.name}
              {showDetails === idx && (
                <div className="badge-details">{badgeInfo.description}</div>
              )}
            </span>
          );
        })}
      </div>
    </div>
  );
}
