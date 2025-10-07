import React, { useEffect, useState } from 'react';
import './GamificationWidget.css';

const achievements = [
  { id: 1, name: 'First Trade', desc: 'Complete your first trade.' },
  { id: 2, name: 'Portfolio Milestone', desc: 'Reach $10,000 portfolio value.' },
  { id: 3, name: 'Community Contributor', desc: 'Share a strategy.' },
];

const GamificationWidget = ({ userId }) => {
  const [userAchievements, setUserAchievements] = useState([]);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Fetch user achievements and progress from backend
    fetch(`/api/user/${userId}/achievements`)
      .then(res => res.json())
      .then(data => {
        setUserAchievements(data.achievements || []);
        setProgress(data.progress || 0);
      });
  }, [userId]);

  return (
    <div className="gamification-widget">
      <h3>Achievements & Progress</h3>
      <div className="progress-bar">
        <div className="progress" style={{ width: `${progress}%` }}></div>
      </div>
      <ul className="achievement-list">
        {achievements.map(a => (
          <li key={a.id} className={userAchievements.includes(a.id) ? 'achieved' : ''}>
            <span className="badge">{a.name}</span> - {a.desc}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GamificationWidget;
