import React, { useState } from 'react';

function StrategyBuilder() {
  const [steps, setSteps] = useState([]);
  const [name, setName] = useState('');
  const [backtestResult, setBacktestResult] = useState(null);

  const addStep = () => setSteps([...steps, { indicator: '', condition: '', value: '' }]);
  const updateStep = (idx, field, val) => {
    const newSteps = steps.slice();
    newSteps[idx][field] = val;
    setSteps(newSteps);
  };
  const runBacktest = async () => {
    // Stub: Replace with actual API call
    setBacktestResult({ profit: 1200, winRate: 0.67 });
  };

  return (
    <div className="strategy-builder">
      <h3>Custom Strategy Builder</h3>
      <input value={name} onChange={e => setName(e.target.value)} placeholder="Strategy Name" />
      <button onClick={addStep}>Add Step</button>
      {steps.map((step, idx) => (
        <div key={idx} className="strategy-step">
          <input value={step.indicator} onChange={e => updateStep(idx, 'indicator', e.target.value)} placeholder="Indicator" />
          <input value={step.condition} onChange={e => updateStep(idx, 'condition', e.target.value)} placeholder="Condition" />
          <input value={step.value} onChange={e => updateStep(idx, 'value', e.target.value)} placeholder="Value" />
        </div>
      ))}
      <button onClick={runBacktest}>Backtest</button>
      {backtestResult && (
        <div className="backtest-result">
          <strong>Profit:</strong> ${backtestResult.profit}<br />
          <strong>Win Rate:</strong> {backtestResult.winRate * 100}%
        </div>
      )}
    </div>
  );
}

export default StrategyBuilder;
