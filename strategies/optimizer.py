from skopt import gp_minimize
from skopt.space import Real, Integer, Categorical
from skopt.utils import use_named_args
from deap import base, creator, tools, algorithms
from sentio.long_term_investment.portfolio import PortfolioOptimizer
"""
Strategy parameter optimization for Sentio
"""
import numpy as np
from typing import Any, List, Dict
import logging

logger = logging.getLogger("sentio.strategies.optimizer")

def optimize_strategy_params(
    strategy: Any,
    market_data: Any,
    param_grid: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Optimize parameters for a trading strategy.
    Args:
        strategy: Trading strategy instance with set_params and generate_signals
        market_data: Historical market data
        param_grid: List of parameter dicts to try
    Returns:
        dict: Best parameters found
    Raises:
        ValueError: If param_grid is empty or strategy is missing methods
    """
    if not param_grid:
        raise ValueError("param_grid must not be empty")
    if not hasattr(strategy, 'set_params') or not hasattr(strategy, 'generate_signals'):
        raise ValueError("strategy must have 'set_params' and 'generate_signals' methods")
    best_params = None
    best_score = -np.inf
    for params in param_grid:
        strategy.set_params(**params)
        signals = strategy.generate_signals(market_data)
        # Calculate profit
        profit = sum(1 for s in signals if s == 'buy') - sum(1 for s in signals if s == 'sell')
        # Calculate Sharpe ratio (stub: use profit as return, 1 as std)
        returns = [1 if s == 'buy' else -1 if s == 'sell' else 0 for s in signals]
        mean_return = np.mean(returns)
        std_return = np.std(returns) if np.std(returns) > 0 else 1
        sharpe = mean_return / std_return
        # Calculate expectancy
        win_count = sum(1 for s in signals if s == 'buy')
        loss_count = sum(1 for s in signals if s == 'sell')
        expectancy = (win_count * mean_return - loss_count * abs(mean_return)) / max(win_count + loss_count, 1)
        # Regime adaptation and external context
        regime = params.get('macro_trend', None)
        regime_boost = 0.0
        if regime == 'bull':
            regime_boost += 0.2
        elif regime == 'bear':
            regime_boost -= 0.2
        ext_score = params.get('external_score', 0.0)
        # Multi-objective optimization
        score = profit + sharpe + expectancy + regime_boost + ext_score
        logger.debug(f"Tested params: {params}, profit: {profit}, sharpe: {sharpe:.2f}, expectancy: {expectancy:.2f}, regime_boost: {regime_boost:.2f}, ext_score: {ext_score:.2f}, score: {score:.2f}")
        if score > best_score:
            best_score = score
            best_params = params
    logger.info(f"Best params found: {best_params} with score {best_score}")
    return best_params

def advanced_optimizer(
    strategy: Any,
    market_data: Any,
    search_space: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stub for advanced optimization (e.g., Bayesian, genetic algorithms).
    Args:
        strategy: Trading strategy instance
        market_data: Historical market data
        search_space: Parameter search space
    Returns:
        dict: Best parameters found
    """
    # Bayesian Optimization implementation
    logger.info("Running Bayesian optimizer...")
    param_names = list(search_space.keys())
    dimensions = []
    for k, v in search_space.items():
        if isinstance(v, list):
            if all(isinstance(i, int) for i in v):
                dimensions.append(Integer(min(v), max(v), name=k))
            elif all(isinstance(i, float) for i in v):
                dimensions.append(Real(min(v), max(v), name=k))
            else:
                dimensions.append(Categorical(v, name=k))
        else:
            dimensions.append(Categorical([v], name=k))

    @use_named_args(dimensions)
    def bayes_objective(**params):
        strategy.set_params(**params)
        signals = strategy.generate_signals(market_data)
        profit = sum(1 for s in signals if s == 'buy') - sum(1 for s in signals if s == 'sell')
        returns = [1 if s == 'buy' else -1 if s == 'sell' else 0 for s in signals]
        mean_return = np.mean(returns)
        std_return = np.std(returns) if np.std(returns) > 0 else 1
        sharpe = mean_return / std_return
        win_count = sum(1 for s in signals if s == 'buy')
        loss_count = sum(1 for s in signals if s == 'sell')
        expectancy = (win_count * mean_return - loss_count * abs(mean_return)) / max(win_count + loss_count, 1)
        score = profit + sharpe + expectancy
        return -score  # minimize

    res = gp_minimize(bayes_objective, dimensions, n_calls=30, random_state=42)
    bayes_best_params = dict(zip(param_names, res.x))
    logger.info(f"Bayesian optimizer best params: {bayes_best_params}")

    # Genetic Algorithm implementation
    logger.info("Running genetic algorithm optimizer...")
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    # Attribute generators
    for i, dim in enumerate(dimensions):
        if isinstance(dim, Integer):
            toolbox.register(f"attr_{i}", np.random.randint, dim.low, dim.high+1)
        elif isinstance(dim, Real):
            toolbox.register(f"attr_{i}", np.random.uniform, dim.low, dim.high)
        elif isinstance(dim, Categorical):
            toolbox.register(f"attr_{i}", lambda: np.random.choice(dim.categories))
    toolbox.register("individual", tools.initCycle, creator.Individual, [toolbox.__getattribute__(f"attr_{i}") for i in range(len(dimensions))], n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def ga_objective(individual):
        params = dict(zip(param_names, individual))
        strategy.set_params(**params)
        signals = strategy.generate_signals(market_data)
        profit = sum(1 for s in signals if s == 'buy') - sum(1 for s in signals if s == 'sell')
        returns = [1 if s == 'buy' else -1 if s == 'sell' else 0 for s in signals]
        mean_return = np.mean(returns)
        std_return = np.std(returns) if np.std(returns) > 0 else 1
        sharpe = mean_return / std_return
        win_count = sum(1 for s in signals if s == 'buy')
        loss_count = sum(1 for s in signals if s == 'sell')
        expectancy = (win_count * mean_return - loss_count * abs(mean_return)) / max(win_count + loss_count, 1)
        score = profit + sharpe + expectancy
        return (score,)

    toolbox.register("evaluate", ga_objective)
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=20)
    hof = tools.HallOfFame(1)
    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=20, halloffame=hof, verbose=False)
    ga_best_params = dict(zip(param_names, hof[0]))
    logger.info(f"Genetic algorithm best params: {ga_best_params}")

    # PortfolioOptimizer integration
    logger.info("Integrating with PortfolioOptimizer...")
    portfolio_optimizer = PortfolioOptimizer()
    # Example: use ML-based allocation for strategy params (stub)
    # This would require historical_data, expected_returns, cov_matrix
    # allocation = portfolio_optimizer.ml_based_allocation(historical_data, expected_returns, cov_matrix)
    # logger.info(f"PortfolioOptimizer allocation: {allocation}")

    return {
        "bayesian_best_params": bayes_best_params,
        "genetic_best_params": ga_best_params,
        # "portfolio_optimizer_allocation": allocation
    }
