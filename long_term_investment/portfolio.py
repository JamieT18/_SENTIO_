"""
Portfolio optimization and long-term investment analytics for Sentio 2.0
"""
import numpy as np
from typing import Dict, List, Optional, Callable
import logging
from .rl_rebalancer import RLPortfolioRebalancer
from sentio.analysis.explainable_ai import ExplainableAI
from sentio.data.feeds import DataFeed, EventDetector
from sentio.ui.accessibility import Accessibility
from sentio.core.compliance import ComplianceChecker, AuditTrail
from sentio.ui.collaboration import TeamDashboard, StrategyBacktester
from sentio.analysis.scenario_simulation import MonteCarloSimulator, StressTester, WhatIfEngine
from sentio.ui.gamification import QuizModule, ChallengeModule
from sentio.core.performance import ParallelExecutor, BatchProcessor

logger = logging.getLogger("sentio.long_term_investment.portfolio")

class PortfolioOptimizer:
    def ml_based_allocation(
        self,
        historical_data: np.ndarray,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray
    ) -> Dict[str, float]:
        """
        Use machine learning (RandomForest) to predict optimal allocation.
        """
        from sklearn.ensemble import RandomForestRegressor
        n = len(expected_returns)
        X = historical_data
        y = expected_returns
        model = RandomForestRegressor().fit(X, y)
        weights = model.predict(X[-1].reshape(1, -1)).flatten()
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"ML-based allocation: {allocation}")
        return allocation

    def stress_test_allocation(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        stress_scenarios: dict
    ) -> Dict[str, float]:
        """
        Stress test allocation under adverse scenarios.
        """
        n = len(expected_returns)
        worst_score = np.inf
        worst_weights = np.ones(n) / n
        for name, scenario in stress_scenarios.items():
            weights = np.array([scenario.get(f'Asset_{i}', 1.0) for i in range(n)])
            score = np.sum(weights * expected_returns) - np.sum(weights @ cov_matrix @ weights)
            if score < worst_score:
                worst_score = score
                worst_weights = weights / weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(worst_weights)}
        logger.debug(f"Stress-tested allocation: {allocation}")
        return allocation

    def behavioral_adjustment(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_tolerance: float
    ) -> Dict[str, float]:
        """
        Adjust allocation for behavioral biases (loss aversion, overconfidence).
        """
        n = len(expected_returns)
        bias = 1.0 - risk_tolerance
        weights = expected_returns * (1 - bias)
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Behavioral-adjusted allocation: {allocation}")
        return allocation

    def global_diversification(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        region_weights: np.ndarray
    ) -> Dict[str, float]:
        """
        Diversify allocation across global regions.
        """
        n = len(expected_returns)
        weights = expected_returns * region_weights
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Global diversification allocation: {allocation}")
        return allocation

    def automatic_withdrawal_plan(
        self,
        portfolio: dict,
        withdrawal_rate: float
    ) -> dict:
        """
        Plan automatic withdrawals for retirement or income.
        """
        withdrawals = {asset: float(value * withdrawal_rate) for asset, value in portfolio.items()}
        logger.info(f"Automatic withdrawal plan: {withdrawals}")
        return withdrawals
    def lifecycle_allocation(
        self,
        age: int,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray
    ) -> Dict[str, float]:
        """
        Adjust allocation based on investor age (glide path).
        """
        n = len(expected_returns)
        equity_weight = max(0.2, 1.0 - age / 100)
        bond_weight = 1.0 - equity_weight
        weights = np.ones(n) * bond_weight / n
        weights[0] += equity_weight  # Assume Asset_0 is equity
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Lifecycle allocation (age={age}): {allocation}")
        return allocation

    def macro_factor_integration(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        macro_factors: dict
    ) -> Dict[str, float]:
        """
        Integrate macroeconomic factors (GDP, rates, inflation) into allocation.
        """
        n = len(expected_returns)
        macro_score = sum(macro_factors.values()) / (len(macro_factors) + 1e-8)
        weights = expected_returns + macro_score
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Macro factor allocation: {allocation}")
        return allocation

    def tax_optimized_allocation(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        tax_rates: np.ndarray
    ) -> Dict[str, float]:
        """
        Optimize allocation for after-tax returns.
        """
        after_tax_returns = expected_returns * (1 - tax_rates)
        n = len(expected_returns)
        ones = np.ones(n)
        inv_cov = np.linalg.pinv(cov_matrix)
        weights = inv_cov @ after_tax_returns
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Tax-optimized allocation: {allocation}")
        return allocation

    def inflation_hedging_allocation(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        inflation_rate: float
    ) -> Dict[str, float]:
        """
        Adjust allocation to hedge against inflation.
        """
        n = len(expected_returns)
        inflation_adjusted = expected_returns - inflation_rate
        weights = np.clip(inflation_adjusted, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Inflation-hedged allocation: {allocation}")
        return allocation

    def goal_based_investing(
        self,
        goals: dict,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray
    ) -> Dict[str, float]:
        """
        Personalize allocation based on user goals (retirement, education, etc.).
        """
        n = len(expected_returns)
        goal_weights = np.ones(n)
        for i, goal in enumerate(goals.values()):
            goal_weights[i % n] *= goal.get('priority', 1.0)
        weights = expected_returns * goal_weights
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Goal-based allocation: {allocation}")
        return allocation
    def optimize_esg_aware(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        esg_scores: np.ndarray,
        esg_weight: float = 0.5
    ) -> Dict[str, float]:
        """
        ESG-aware portfolio optimization (blend return, risk, ESG).
        """
        n = len(expected_returns)
        ones = np.ones(n)
        inv_cov = np.linalg.pinv(cov_matrix)
        weights = inv_cov @ (expected_returns + esg_weight * esg_scores)
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"ESG-aware allocation: {allocation}")
        return allocation

    def regime_adaptive_allocation(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        regimes: dict
    ) -> Dict[str, float]:
        """
        Adjust allocation based on detected market regime.
        """
        bull_weight = 0.7 if any(regimes.get('bull', [])) else 0.3
        bear_weight = 0.7 if any(regimes.get('bear', [])) else 0.3
        neutral_weight = 1.0 - bull_weight - bear_weight
        n = len(expected_returns)
        weights = np.ones(n) * neutral_weight / n
        if bull_weight > bear_weight:
            weights += bull_weight * expected_returns / np.sum(expected_returns)
        else:
            weights -= bear_weight * expected_returns / np.sum(expected_returns)
        weights = np.clip(weights, 0, 1)
        weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Regime-adaptive allocation: {allocation}")
        return allocation

    def scenario_based_optimization(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        scenarios: dict
    ) -> Dict[str, float]:
        """
        Optimize allocation for best performance across scenarios.
        """
        n = len(expected_returns)
        best_score = -np.inf
        best_weights = np.ones(n) / n
        for name, scenario in scenarios.items():
            weights = np.array([scenario.get(f'Asset_{i}', 1.0) for i in range(n)])
            score = np.sum(weights * expected_returns) - np.sum(weights @ cov_matrix @ weights)
            if score > best_score:
                best_score = score
                best_weights = weights / weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(best_weights)}
        logger.debug(f"Scenario-based allocation: {allocation}")
        return allocation

    def longevity_score(self, portfolio: dict) -> float:
        # Dummy longevity score: diversity + average holding period
        diversity = len(portfolio)
        avg_holding = np.mean([v for v in portfolio.values()])
        score = diversity * avg_holding / (diversity + 1e-8)
        logger.info(f"Longevity score: {score}")
        return float(score)
    """
    Portfolio optimization algorithms (Markowitz mean-variance, risk parity, multi-objective).
    Extensible for custom objective functions and constraints.
    """
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        logger.info(f"PortfolioOptimizer initialized with config: {self.config}")

    def optimize_mean_variance(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_aversion: float = 1.0
    ) -> Dict[str, float]:
        """
        Optimize portfolio allocation using mean-variance (Markowitz).
        Args:
            expected_returns: np.ndarray of expected returns
            cov_matrix: np.ndarray of covariance matrix
            risk_aversion: float, risk aversion parameter
        Returns:
            dict: Optimized allocation (weights)
        Raises:
            ValueError: If input shapes do not match
        """
        if expected_returns.shape[0] != cov_matrix.shape[0]:
            raise ValueError("Shape mismatch between expected_returns and cov_matrix")
        n = len(expected_returns)
        ones = np.ones(n)
        inv_cov = np.linalg.pinv(cov_matrix)
        weights = inv_cov @ expected_returns / (risk_aversion * (ones @ inv_cov @ expected_returns))
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Mean-variance allocation: {allocation}")
        return allocation

    def optimize_risk_parity(
        self,
        cov_matrix: np.ndarray,
        max_iter: int = 1000,
        tol: float = 1e-8
    ) -> Dict[str, float]:
        """
        Optimize portfolio allocation using risk parity.
        Args:
            cov_matrix: np.ndarray of covariance matrix
            max_iter: Maximum iterations
            tol: Tolerance for convergence
        Returns:
            dict: Risk parity allocation (weights)
        Raises:
            ValueError: If cov_matrix is not square
        """
        if cov_matrix.shape[0] != cov_matrix.shape[1]:
            raise ValueError("cov_matrix must be square")
        n = cov_matrix.shape[0]
        weights = np.ones(n) / n
        for _ in range(max_iter):
            portfolio_var = weights @ cov_matrix @ weights
            marginal_contrib = cov_matrix @ weights
            risk_contrib = weights * marginal_contrib / portfolio_var
            diff = risk_contrib - np.mean(risk_contrib)
            if np.linalg.norm(diff) < tol:
                break
            weights -= 0.01 * diff
            weights = np.clip(weights, 0, 1)
            weights /= weights.sum()
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        logger.debug(f"Risk parity allocation: {allocation}")
        return allocation

    def optimize_multi_objective(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        objectives: List[Callable[[np.ndarray], float]],
        weights: Optional[np.ndarray] = None,
        max_iter: int = 1000,
        tol: float = 1e-6
    ) -> Dict[str, float]:
        """
        Multi-objective portfolio optimization (stub).
        Args:
            expected_returns: np.ndarray of expected returns
            cov_matrix: np.ndarray of covariance matrix
            objectives: List of objective functions (e.g., return, risk, ESG)
            weights: Optional initial weights
        Returns:
            dict: Optimized allocation
        """
        n = len(expected_returns)
        if weights is None:
            weights = np.ones(n) / n
        # TODO: Implement multi-objective optimization (Pareto, weighted sum, etc.)
        logger.info("Multi-objective optimization not yet implemented.")
        allocation = {f'Asset_{i}': float(w) for i, w in enumerate(weights)}
        return allocation

    def rl_rebalance(
        self,
        portfolio: dict,
        market_state: dict,
        n_assets: int = None
    ) -> dict:
        """
        Use RL agent to rebalance portfolio based on market state.
        """
        n_assets = n_assets or len(portfolio)
        rl_agent = RLPortfolioRebalancer(n_assets)
        rebalanced = rl_agent.rebalance(portfolio, market_state)
        return rebalanced

    def explain_allocation(
        self,
        model,
        X: np.ndarray,
        method: str = 'shap',
        feature_names: list = None
    ) -> dict:
        """
        Explain allocation decisions using SHAP or LIME.
        """
        explainer = ExplainableAI(model, feature_names)
        if method == 'shap':
            return explainer.shap_explain(X)
        elif method == 'lime':
            return explainer.lime_explain(X)
        else:
            raise ValueError('Unknown explanation method')

    def get_realtime_data(
        self,
        symbol: str,
        api_keys: dict = None
    ) -> dict:
        """
        Fetch real-time market, sentiment, macro, and news data for a symbol.
        """
        feed = DataFeed(api_keys)
        data = {
            'market': feed.get_market_data(symbol),
            'sentiment': feed.get_social_sentiment(symbol),
            'macro': feed.get_macro_indicators(),
            'news': feed.get_news_events(symbol)
        }
        return data

    def detect_portfolio_anomalies(
        self,
        returns: np.ndarray,
        threshold: float = 3.0
    ) -> list:
        """
        Detect anomalies in portfolio returns.
        """
        detector = EventDetector()
        return detector.detect_anomalies(returns, threshold)

    def detect_market_events(
        self,
        news: list
    ) -> list:
        """
        Detect impactful market/news events.
        """
        detector = EventDetector()
        return detector.detect_events(news)

    def set_custom_risk_metric(
        self,
        risk_metric_fn
    ):
        """
        Allow user to set a custom risk metric function.
        """
        self.custom_risk_metric = risk_metric_fn

    def set_custom_optimizer_objective(
        self,
        objective_fn
    ):
        """
        Allow user to set a custom optimizer objective function.
        """
        self.custom_optimizer_objective = objective_fn

    def register_dashboard_widget(
        self,
        widget_name: str,
        widget_fn
    ):
        """
        Register a custom dashboard widget function.
        """
        if not hasattr(self, 'dashboard_widgets'):
            self.dashboard_widgets = {}
        self.dashboard_widgets[widget_name] = widget_fn

    def get_dashboard_widget(
        self,
        widget_name: str
    ):
        """
        Retrieve a registered dashboard widget function.
        """
        return getattr(self, 'dashboard_widgets', {}).get(widget_name)

    def set_language(self, language: str):
        """
        Set language for optimizer and dashboard widgets.
        """
        self.accessibility = Accessibility(language)

    def translate(self, key: str) -> str:
        """
        Translate dashboard/widget labels.
        """
        if hasattr(self, 'accessibility'):
            return self.accessibility.translate(key)
        return key

    def set_compliance_rules(self, rules: list):
        """
        Set compliance rules for portfolio checks.
        """
        self.compliance_checker = ComplianceChecker(rules)

    def check_compliance(self, portfolio: dict) -> list:
        """
        Check portfolio against compliance rules.
        """
        if hasattr(self, 'compliance_checker'):
            return self.compliance_checker.check(portfolio)
        return []

    def log_action(self, action: str, details: dict):
        """
        Log actions for audit trail.
        """
        if not hasattr(self, 'audit_trail'):
            self.audit_trail = AuditTrail()
        self.audit_trail.log(action, details)

    def get_audit_logs(self) -> list:
        """
        Retrieve audit logs.
        """
        if hasattr(self, 'audit_trail'):
            return self.audit_trail.get_logs()
        return []

    def set_team_dashboard(self, team_name: str, members: list):
        """
        Create or update a team dashboard for collaborative management.
        """
        if not hasattr(self, 'team_dashboard'):
            self.team_dashboard = TeamDashboard()
        self.team_dashboard.create_team(team_name, members)

    def add_team_note(self, team_name: str, author: str, note: str):
        if hasattr(self, 'team_dashboard'):
            self.team_dashboard.add_note(team_name, author, note)

    def get_team_notes(self, team_name: str):
        if hasattr(self, 'team_dashboard'):
            return self.team_dashboard.get_notes(team_name)
        return []

    def get_team_dashboard(self, team_name: str):
        if hasattr(self, 'team_dashboard'):
            return self.team_dashboard.get_dashboard(team_name)
        return {}

    def backtest_strategy(self, strategy_fn, historical_data):
        backtester = StrategyBacktester()
        return backtester.backtest(strategy_fn, historical_data)

    def simulate_monte_carlo(self, portfolio: dict, n_simulations: int = 1000, horizon: int = 252):
        simulator = MonteCarloSimulator()
        return simulator.simulate(portfolio, n_simulations, horizon)

    def stress_test_portfolio(self, portfolio: dict, scenarios: dict):
        tester = StressTester()
        return tester.stress_test(portfolio, scenarios)

    def what_if_analysis(self, portfolio: dict, changes: dict):
        engine = WhatIfEngine()
        return engine.what_if(portfolio, changes)

    def get_quiz_question(self):
        quiz = QuizModule()
        return quiz.get_random_question()

    def check_quiz_answer(self, question: dict, choice_idx: int) -> bool:
        quiz = QuizModule()
        return quiz.check_answer(question, choice_idx)

    def get_challenge(self):
        challenge = ChallengeModule()
        return challenge.get_random_challenge()

    def complete_challenge(self, challenge: str) -> bool:
        challenge_mod = ChallengeModule()
        return challenge_mod.complete_challenge(challenge)

    def run_parallel_optimizations(self, func, data, max_workers: int = 4):
        executor = ParallelExecutor(max_workers)
        return executor.run_parallel(func, data)

    def process_in_batches(self, func, data, batch_size: int = 100):
        processor = BatchProcessor()
        return processor.process_batches(func, data, batch_size)

class Rebalancer:
    """
    Simple portfolio rebalancer to target allocation.
    """
    def rebalance(
        self,
        portfolio: Dict[str, float],
        target_allocation: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Rebalance portfolio to target allocation.
        Args:
            portfolio: dict of current asset values
            target_allocation: dict of target weights
        Returns:
            dict: Rebalanced portfolio values
        Raises:
            ValueError: If portfolio is empty or target_allocation is invalid
        """
        if not portfolio or not target_allocation:
            raise ValueError("Portfolio and target_allocation must not be empty")
        total_value = sum(portfolio.values())
        rebalanced = {asset: float(total_value * target_allocation.get(asset, 0)) for asset in portfolio}
        logger.debug(f"Rebalanced portfolio: {rebalanced}")
        return rebalanced
