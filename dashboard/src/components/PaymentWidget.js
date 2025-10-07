import React, { useState } from 'react';

const PAYMENT_METHODS = [
  { name: 'Credit/Debit Card', icon: '💳' },
  { name: 'PayPal', icon: '🅿️' },
  { name: 'Crypto', icon: '₿' },
  { name: 'Apple Pay', icon: '🍏' },
  { name: 'Google Pay', icon: '🅶' }
];

export default function PaymentWidget({ userId, selectedPlan }) {
  const [selectedMethod, setSelectedMethod] = useState(PAYMENT_METHODS[0].name);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState('');

  async function handlePayment() {
    setProcessing(true);
    setMessage('');
    // Simulate payment API call
    setTimeout(() => {
      setProcessing(false);
      setMessage(`Payment successful via ${selectedMethod}!`);
    }, 1500);
  }

  return (
    <div className="payment-widget">
      <h3>Choose Payment Method</h3>
      <div className="payment-methods">
        {PAYMENT_METHODS.map(method => (
          <button
            key={method.name}
            className={selectedMethod === method.name ? 'selected' : ''}
            onClick={() => setSelectedMethod(method.name)}
            aria-label={method.name}
          >
            <span className="method-icon">{method.icon}</span> {method.name}
          </button>
        ))}
      </div>
      <button
        className="pay-btn"
        onClick={handlePayment}
        disabled={processing}
      >
        {processing ? 'Processing...' : `Pay for ${selectedPlan} with ${selectedMethod}`}
      </button>
      {message && <div className="payment-message">{message}</div>}
    </div>
  );
}
