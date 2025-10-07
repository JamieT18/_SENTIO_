"""
Risk-adjusted return analytics and reporting for long-term investment.
"""


import numpy as np

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    returns = np.array(returns)
    excess = returns - risk_free_rate / 252
    sharpe = np.mean(excess) / (np.std(excess) + 1e-8) * np.sqrt(252)
    return float(sharpe)


def calculate_sortino_ratio(returns, target_return=0.0):
    returns = np.array(returns)
    downside = returns[returns < target_return]
    downside_std = np.std(downside) if len(downside) > 0 else 1e-8
    sortino = (np.mean(returns) - target_return) / downside_std * np.sqrt(252)
    return float(sortino)

def calculate_calmar_ratio(returns):
    returns = np.array(returns)
    cumulative = np.cumprod(1 + returns) - 1
    max_drawdown = np.max(np.maximum.accumulate(cumulative) - cumulative)
    annual_return = np.mean(returns) * 252
    calmar = annual_return / (max_drawdown + 1e-8)
    return float(calmar)

def calculate_omega_ratio(returns, threshold=0.0):
    returns = np.array(returns)
    gain = np.sum(returns[returns > threshold])
    loss = -np.sum(returns[returns < threshold]) + 1e-8
    omega = gain / loss
    return float(omega)

def detect_market_regime(returns, window=20):
    returns = np.array(returns)
    rolling_mean = np.convolve(returns, np.ones(window)/window, mode='valid')
    bull = rolling_mean > 0.01
    bear = rolling_mean < -0.01
    neutral = ~(bull | bear)
    return {'bull': bull.tolist(), 'bear': bear.tolist(), 'neutral': neutral.tolist()}

def esg_score(assets: dict) -> float:
    # Dummy ESG scoring: average of provided ESG values
    scores = [v.get('esg', 0.5) for v in assets.values()]
    return float(np.mean(scores))

def simulate_scenarios(portfolio, scenarios):
    # Simulate portfolio value under different market scenarios
    results = {}
    for name, scenario in scenarios.items():
        values = [v * scenario.get(asset, 1.0) for asset, v in portfolio.items()]
        results[name] = float(np.sum(values))
    return results
