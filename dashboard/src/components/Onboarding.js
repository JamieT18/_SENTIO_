import React, { useState, useEffect } from 'react';
import './Onboarding.css';

const Onboarding = ({ onComplete, userName = 'User' }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if user has completed onboarding
    const hasCompletedOnboarding = localStorage.getItem('onboarding_completed');
    if (!hasCompletedOnboarding) {
      setIsVisible(true);
    }
  }, []);

  const steps = [
    {
      title: 'Welcome to Sentio Dashboard! 🎉',
      content: `Hi ${userName}! We're excited to have you here. This quick tour will help you get started with managing your subscriptions and analytics.`,
      icon: '👋',
    },
    {
      title: 'Overview & Analytics',
      content: 'View your monthly recurring revenue, total users, and active subscriptions at a glance. Track your business metrics in real-time.',
      icon: '📊',
    },
    {
      title: 'User Management',
      content: 'Manage all your users, view their subscription tiers, and monitor their profit-sharing balances in one place.',
      icon: '👥',
    },
    {
      title: 'Subscriber Details',
      content: 'Dive deep into individual subscriber information, including their features, trading limits, and subscription status.',
      icon: '📋',
    },
    {
      title: 'Pricing & Plans',
      content: 'Update pricing for different subscription tiers and manage your pricing strategy with ease.',
      icon: '💰',
    },
    {
      title: 'Keyboard Navigation',
      content: 'Use Tab to navigate, Enter to select, and Escape to close dialogs. Press Ctrl+K for quick search (coming soon).',
      icon: '⌨️',
    },
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    localStorage.setItem('onboarding_completed', 'true');
    setIsVisible(false);
    if (onComplete) {
      onComplete();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      handleSkip();
    } else if (e.key === 'ArrowRight') {
      handleNext();
    } else if (e.key === 'ArrowLeft') {
      handlePrevious();
    }
  };

  if (!isVisible) {
    return null;
  }

  const currentStepData = steps[currentStep];

  return (
    <div 
      className="onboarding-overlay" 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="onboarding-title"
      onKeyDown={handleKeyDown}
    >
      <div className="onboarding-modal">
        <button 
          className="onboarding-close" 
          onClick={handleSkip}
          aria-label="Close onboarding and skip tour"
        >
          ✕
        </button>

        <div className="onboarding-content">
          <div className="onboarding-icon" aria-hidden="true">{currentStepData.icon}</div>
          <h2 id="onboarding-title">{currentStepData.title}</h2>
          <p>{currentStepData.content}</p>
        </div>

        <div className="onboarding-progress" role="progressbar" aria-valuenow={currentStep + 1} aria-valuemin="1" aria-valuemax={steps.length}>
          <div className="progress-dots" aria-label={`Step ${currentStep + 1} of ${steps.length}`}>
            {steps.map((_, index) => (
              <span
                key={index}
                className={`progress-dot ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
                aria-current={index === currentStep ? 'step' : undefined}
              />
            ))}
          </div>
          <span className="progress-text" aria-live="polite">
            Step {currentStep + 1} of {steps.length}
          </span>
        </div>

        <div className="onboarding-actions">
          <button
            className="btn-secondary"
            onClick={handleSkip}
            aria-label="Skip onboarding tour"
          >
            Skip Tour
          </button>
          <div className="nav-buttons">
            {currentStep > 0 && (
              <button
                className="btn-secondary"
                onClick={handlePrevious}
                aria-label="Go to previous step"
              >
                ← Previous
              </button>
            )}
            <button
              className="btn-primary"
              onClick={handleNext}
              aria-label={currentStep === steps.length - 1 ? 'Complete onboarding tour' : 'Go to next step'}
            >
              {currentStep === steps.length - 1 ? 'Get Started' : 'Next →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
