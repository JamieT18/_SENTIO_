import React from 'react';

export default function ProfileWidget({ userId }) {
  // Placeholder data, replace with API integration
  const user = {
    avatar: '/default-avatar.png',
    bio: 'Passionate trader and Sentio enthusiast.',
    badges: ['Top Trader', 'Early Adopter']
  };

  return (
    <div className="profile-section">
      <h2>Your Profile</h2>
      <img src={user.avatar} alt="User avatar" className="avatar" />
      <div className="bio">{user.bio}</div>
      <div className="badges">
        {user.badges.map((badge, idx) => (
          <span key={idx} className="badge">{badge}</span>
        ))}
      </div>
      {/* Add more profile customization features here */}
    </div>
  );
}
