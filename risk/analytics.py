"""
Advanced risk analytics and scenario analysis for Sentio
"""
import numpy as np
from typing import Dict, List, Any, Optional
import logging
logger = logging.getLogger("sentio.risk.analytics")

def calculate_var(portfolio_returns: List[float], confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) for a portfolio.
    Args:
        portfolio_returns: List or array of returns
        confidence_level: Confidence level for VaR
    Returns:
        float: Value at Risk
    Raises:
        ValueError: If portfolio_returns is empty
    """
    returns = np.array(portfolio_returns)
    if returns.size == 0:
        raise ValueError("portfolio_returns must not be empty")
    var = np.percentile(returns, (1 - confidence_level) * 100)
    logger.debug(f"Calculated VaR: {var}")
    return float(var)

def dynamic_risk_model(portfolio: Dict[str, float], market_data: Optional[List[float]] = None) -> Dict[str, float]:
    """
    Dynamic risk model using ML regression for risk prediction.
    Args:
        portfolio: Portfolio weights
        market_data: Historical market data (list of floats)
    Returns:
        dict: Risk metrics
    """
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        if market_data is None or len(market_data) == 0:
            logger.warning("No market data provided to dynamic risk model.")
            return {"risk_score": 0.0}
        X = np.array(market_data).reshape(-1, 1)
        y = np.random.rand(len(market_data))  # Placeholder for actual risk labels
        model = RandomForestRegressor().fit(X, y)
        pred_risk = model.predict(X)
        risk_metric = float(np.mean(pred_risk))
        logger.info(f"Dynamic risk model predicted risk: {risk_metric}")
        return {'predicted_risk': risk_metric}
    except Exception as e:
        logger.error(f"Dynamic risk model error: {e}")
        return {"risk_score": 0.0}

def calculate_cvar(portfolio_returns: List[float], confidence_level: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) for a portfolio.
    Args:
        portfolio_returns: List or array of returns
        confidence_level: Confidence level for CVaR
    Returns:
        float: CVaR
    Raises:
        ValueError: If portfolio_returns is empty
    """
    returns = np.array(portfolio_returns)
    if returns.size == 0:
        raise ValueError("portfolio_returns must not be empty")
    var = calculate_var(returns.tolist(), confidence_level)
    cvar = returns[returns <= var].mean() if np.any(returns <= var) else var
    logger.debug(f"Calculated CVaR: {cvar}")
    return float(cvar)

def monte_carlo_simulation(
    portfolio: Dict[str, float],
    n_simulations: int = 1000,
    horizon: int = 252
) -> np.ndarray:
    """
    Simulate portfolio returns using Monte Carlo method.
    Args:
        portfolio: dict with 'expected_return' and 'volatility'
        n_simulations: Number of simulations
        horizon: Number of days to simulate
    Returns:
        np.ndarray: Simulated portfolio returns
    """
    expected_return = portfolio.get('expected_return', 0.08)
    volatility = portfolio.get('volatility', 0.15)
    results = np.zeros(n_simulations)
    for i in range(n_simulations):
        daily_returns = np.random.normal(expected_return / horizon, volatility / np.sqrt(horizon), horizon)
        results[i] = np.prod(1 + daily_returns) - 1
    logger.debug(f"Monte Carlo simulation completed: mean={results.mean():.4f}, std={results.std():.4f}")
    return results

def stress_test_portfolio(portfolio: Dict[str, float], scenarios: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Perform stress testing on a portfolio under given scenarios.
    Args:
        portfolio: dict of asset values
        scenarios: list of scenario dicts
    Returns:
        dict: Impact of each scenario
    """
    results = {}
    for scenario in scenarios:
        impact = sum(portfolio.get(asset, 0) * scenario.get(asset, 1) for asset in portfolio)
        results[scenario.get('name', 'Scenario')] = float(impact)
    logger.debug(f"Stress test results: {results}")
    return results

def performance_metrics(trade_history: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate performance metrics from trade history.
    Args:
        trade_history: List of trade dicts with 'pnl' key
    Returns:
        dict: Metrics (win_rate, avg_win, avg_loss, sharpe_ratio)
    """
    if not trade_history:
        return {"win_rate": 0.0, "avg_win": 0.0, "avg_loss": 0.0, "sharpe_ratio": 0.0}
    wins = [t['pnl'] for t in trade_history if t['pnl'] > 0]
    losses = [t['pnl'] for t in trade_history if t['pnl'] < 0]
    win_rate = len(wins) / len(trade_history)
    avg_win = np.mean(wins) if wins else 0.0
    avg_loss = np.mean(losses) if losses else 0.0
    returns = [t['pnl'] for t in trade_history]
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0.0
    logger.debug(f"Performance metrics: win_rate={win_rate:.2f}, sharpe={sharpe_ratio:.2f}")
    return {"win_rate": win_rate, "avg_win": avg_win, "avg_loss": avg_loss, "sharpe_ratio": sharpe_ratio}
"""
Advanced risk analytics and scenario analysis for Sentio
"""
import numpy as np
from typing import Dict, List, Any, Optional
import logging
logger = logging.getLogger("sentio.risk.analytics")
def dynamic_risk_model(portfolio: Dict[str, float], market_data: Optional[List[float]] = None) -> Dict[str, float]:
    """
    Dynamic risk model using ML regression for risk prediction.
    Args:
        portfolio: Portfolio weights
        market_data: Historical market data (list of floats)
    Returns:
        dict: Risk metrics
    """
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        if market_data is None or len(market_data) == 0:
            logger.warning("No market data provided to dynamic risk model.")
            return {"risk_score": 0.0}
        X = np.array(market_data).reshape(-1, 1)
        y = np.random.rand(len(market_data))  # Placeholder for actual risk labels
        model = RandomForestRegressor().fit(X, y)
        pred_risk = model.predict(X)
        risk_metric = float(np.mean(pred_risk))
        logger.info(f"Dynamic risk model predicted risk: {risk_metric}")
        return {'predicted_risk': risk_metric}
    except Exception as e:
        logger.error(f"Dynamic risk model error: {e}")
        return {"risk_score": 0.0}

def calculate_cvar(portfolio_returns: List[float], confidence_level: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) for a portfolio.
    Args:
        portfolio_returns: List or array of returns
        confidence_level: Confidence level for CVaR
    Returns:
        float: CVaR
    Raises:
        ValueError: If portfolio_returns is empty
    """
    returns = np.array(portfolio_returns)
    if returns.size == 0:
        raise ValueError("portfolio_returns must not be empty")
    var = calculate_var(returns.tolist(), confidence_level)
    cvar = returns[returns <= var].mean() if np.any(returns <= var) else var
    logger.debug(f"Calculated CVaR: {cvar}")
    return float(cvar)

def monte_carlo_simulation(
    portfolio: Dict[str, float],
    n_simulations: int = 1000,
    horizon: int = 252
) -> np.ndarray:
    """
    Simulate portfolio returns using Monte Carlo method.
    Args:
        portfolio: dict with 'expected_return' and 'volatility'
        n_simulations: Number of simulations
        horizon: Number of days to simulate
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor
        if market_data is None or len(market_data) == 0:
            logger.warning("No market data provided to dynamic risk model.")
            return {'predicted_risk': 0.0}
        X = np.array(market_data).reshape(-1, 1)
        y = np.random.rand(len(market_data))  # Placeholder for actual risk labels
        model = RandomForestRegressor().fit(X, y)
        pred_risk = model.predict(X)
        risk_metric = float(np.mean(pred_risk))
        logger.info(f"Dynamic risk model predicted risk: {risk_metric}")
        return {'predicted_risk': risk_metric}
    except Exception as e:
        logger.error(f"Dynamic risk model error: {e}")
        return {'predicted_risk': 0.0}
def stress_test_portfolio(portfolio: Dict[str, float], scenarios: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    # ...function definition is already present below...

