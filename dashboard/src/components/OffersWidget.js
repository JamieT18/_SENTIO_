import React, { useState } from 'react';

const OFFERS = [
  { name: 'Referral Bonus', description: 'Invite friends and earn $10 credit per signup', expires: '2025-12-31' },
  { name: 'Elite Upgrade Discount', description: '20% off Elite plan for first 3 months', expires: '2025-11-15' },
  { name: 'Premium Signal Trial', description: 'Try premium signals free for 7 days', expires: '2025-10-31' }
];

export default function OffersWidget({ userId }) {
  const [claimed, setClaimed] = useState([]);
  const [message, setMessage] = useState('');

  function handleClaim(offer) {
    setClaimed([...claimed, offer.name]);
    setMessage(`Offer claimed: ${offer.name}`);
    setTimeout(() => setMessage(''), 1200);
  }

  return (
    <div className="offers-widget">
      <h3>Exclusive Offers & Rewards</h3>
      <ul className="offers-list">
        {OFFERS.map(offer => (
          <li key={offer.name} className="offer-item">
            <div className="offer-header">
              <strong>{offer.name}</strong>
              <span className="offer-expiry">Expires: {offer.expires}</span>
            </div>
            <div className="offer-description">{offer.description}</div>
            <button
              onClick={() => handleClaim(offer)}
              disabled={claimed.includes(offer.name)}
            >
              {claimed.includes(offer.name) ? 'Claimed' : 'Claim Offer'}
            </button>
          </li>
        ))}
      </ul>
      {message && <div className="offer-message">{message}</div>}
    </div>
  );
}
