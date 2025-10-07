import random

STRATEGY_PERFORMANCE_HISTORY = []

class TradingStrategy:

    def __init__(self, name, description, risk_level, win_rate, avg_profit):
        self.name = name
        self.description = description
        self.risk_level = risk_level
        self.win_rate = win_rate
        self.avg_profit = avg_profit
        self.performance_history = []
        self.dynamic_params = {
            "risk_level": risk_level,
            "win_rate": win_rate,
            "avg_profit": avg_profit
        }

    def simulate_trade(self, market_context=None, regime=None, external_context=None, diagnostics=None):
        # Adaptive win_rate and avg_profit based on recent performance
        if self.performance_history:
            recent = self.performance_history[-10:]
            avg_win_rate = sum(1 for r in recent if r[0]) / len(recent)
            self.dynamic_params["win_rate"] = 0.5 * self.win_rate + 0.5 * avg_win_rate
            self.dynamic_params["avg_profit"] = 0.5 * self.avg_profit + 0.5 * (sum(r[1] for r in recent) / len(recent))
        win = random.random() < self.dynamic_params["win_rate"]
        profit = self.dynamic_params["avg_profit"] if win else -self.dynamic_params["avg_profit"] * 0.7
        self.performance_history.append((win, profit))
        STRATEGY_PERFORMANCE_HISTORY.append({
            "strategy": self.name,
            "win": win,
            "profit": profit,
            "timestamp": datetime.now().isoformat(),
            "context": market_context or {},
            "regime": regime,
            "external_context": external_context,
            "diagnostics": diagnostics,
        })
        # Meta-learning hook: strategies can learn from each other's results
        self.meta_learn(regime=regime, external_context=external_context, diagnostics=diagnostics)
        return win, profit

    def meta_learn(self, regime=None, external_context=None, diagnostics=None):
        # Example: adjust win_rate if other strategies outperform
        if len(STRATEGY_PERFORMANCE_HISTORY) > 20:
            recent = STRATEGY_PERFORMANCE_HISTORY[-20:]
            strat_wins = {r["strategy"]: [] for r in recent}
            for r in recent:
                strat_wins[r["strategy"]].append(r["win"])
            avg_wins = {k: sum(v)/len(v) if v else 0 for k, v in strat_wins.items()}
            best = max(avg_wins, key=avg_wins.get)
            if best != self.name and avg_wins[best] > self.dynamic_params["win_rate"]:
                self.dynamic_params["win_rate"] += 0.01  # small adaptive boost
                self.dynamic_params["win_rate"] = min(self.dynamic_params["win_rate"], 0.99)
        # Regime/context/diagnostics adjustment
        if regime == "bull":
            self.dynamic_params["win_rate"] += 0.01
        elif regime == "bear":
            self.dynamic_params["win_rate"] -= 0.01
        if diagnostics and diagnostics.get("error_rate", 0) > 0.1:
            self.dynamic_params["win_rate"] -= 0.01
        if external_context and external_context.get("macro") == "positive":
            self.dynamic_params["win_rate"] += 0.005

# Enhanced strategies
from datetime import datetime
STRATEGIES = [
    TradingStrategy(
        name="AI Momentum",
        description="Uses AI to detect momentum shifts and enter trades early. Auto-tunes parameters for changing market regimes.",
        risk_level="Medium",
        win_rate=0.62,
        avg_profit=8.5
    ),
    TradingStrategy(
        name="Risk-Managed Arbitrage",
        description="Executes cross-exchange arbitrage with dynamic risk controls and latency-aware execution.",
        risk_level="Low",
        win_rate=0.78,
        avg_profit=4.2
    ),
    TradingStrategy(
        name="Elite Swing",
        description="Combines technical, sentiment, and macro analysis for swing trades. Adapts to volatility spikes.",
        risk_level="High",
        win_rate=0.54,
        avg_profit=15.1
    ),
    TradingStrategy(
        name="Market Neutral",
        description="Hedges positions to minimize market risk and maximize stable returns. Uses options flow and external data.",
        risk_level="Low",
        win_rate=0.81,
        avg_profit=3.7
    ),
    TradingStrategy(
        name="Adaptive Trend",
        description="Adapts to changing market conditions using real-time analytics and meta-learning from other strategies.",
        risk_level="Medium",
        win_rate=0.66,
        avg_profit=7.9
    )
]

def get_strategies():
    return [{
        "name": s.name,
        "description": s.description,
        "risk_level": s.risk_level,
        "win_rate": s.win_rate,
        "avg_profit": s.avg_profit
    } for s in STRATEGIES]

def run_strategy(name):
    for s in STRATEGIES:
        if s.name == name:
            win, profit = s.simulate_trade()
            return {"strategy": name, "win": win, "profit": profit}
    return {"error": "Strategy not found"}
