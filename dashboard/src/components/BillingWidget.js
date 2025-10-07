import React, { useState } from 'react';
import PaymentWidget from './PaymentWidget';

const PLANS = [
  { name: 'Free', price: 0, features: ['Basic analytics', 'Community access'] },
  { name: 'Pro', price: 19, features: ['Advanced analytics', 'AI recommendations', 'Priority support'] },
  { name: 'Elite', price: 49, features: ['All Pro features', 'Exclusive signals', 'Early access to new features'] }
];

export default function BillingWidget({ userId }) {
  const [selected, setSelected] = useState('Free');
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState('');

  async function handleUpgrade(plan) {
    setProcessing(true);
    setMessage('');
    // Simulate API call
    setTimeout(() => {
      setSelected(plan.name);
      setProcessing(false);
      setMessage(`Upgraded to ${plan.name} plan!`);
    }, 1200);
  }

  return (
    <div className="billing-widget">
      <h3>Choose Your Plan</h3>
      <div className="plans-list">
        {PLANS.map(plan => (
          <div key={plan.name} className={`plan-card${selected === plan.name ? ' selected' : ''}`}>
            <h4>{plan.name}</h4>
            <div className="plan-price">${plan.price}/mo</div>
            <ul>
              {plan.features.map((f, idx) => <li key={idx}>{f}</li>)}
            </ul>
            {selected !== plan.name && (
              <button onClick={() => handleUpgrade(plan)} disabled={processing}>
                {processing ? 'Processing...' : 'Upgrade'}
              </button>
            )}
            {selected === plan.name && <span className="current-plan">Current Plan</span>}
          </div>
        ))}
      </div>
      {message && <div className="billing-message">{message}</div>}
      <PaymentWidget userId={userId} selectedPlan={selected} />
    </div>
  );
}
