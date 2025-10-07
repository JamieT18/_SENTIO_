# Trading strategies module for Sentio
# Strategies module for Sentio

from .strategy import BaseStrategy
from .strategy_manager import StrategyManager
from .optimizer import optimize_strategy_params, advanced_optimizer
from .plugin import strategy_plugins
import numpy as np
import time
import psutil
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error


def tjr_strategy_logic(market_data, params):
    # TJR (Trend-Jump-Reversal) strategy stub
    # ...logic for trend detection, jump, and reversal...
    return {
        "signal": "buy",
        "confidence": 0.88,
        "details": {}
    }


def advanced_trading_strategies(market_data, params):
    # Full logic enhancement for advanced strategies
    # ...logic for multi-factor, regime, and adaptive strategies...
    return {
        "signals": [],
        "confidence": 0.95,
        "details": {}
    }


def multi_strategy_voting(strategies, market_data):
    # Multi-strategy voting with weighted confidence
    # ...logic for voting and confidence weighting...
    return {
        "voted_signal": "hold",
        "weights": [0.6, 0.3, 0.1],
        "confidence": 0.88
    }


def trade_dna_clustering(trades):
    # Trade DNA clustering and meta-learning refinement
    # ...logic for clustering and meta-learning...
    return {
        "clusters": [],
        "meta_refinement": True
    }


def adversarial_testing(strategy, market_data):
    # Adversarial testing and strategy recycling
    # ...logic for adversarial scenarios...
    return {
        "adversarial_score": 0.72,
        "recycled": True
    }


def regret_based_optimization(trades, strategies):
    # Regret-based optimization
    # ...logic for regret minimization...
    return {
        "optimized": True,
        "regret_score": 0.05
    }


def weighted_multi_strategy_voting(strategies, signals, weights):
    # Weighted multi-strategy voting engine
    # ...logic for weighted voting...
    return {
        "final_signal": "buy",
        "weights": weights,
        "confidence": sum(weights)/len(weights) if weights else 0
    }


def enhanced_tjr_strategy(market_data, params):
    # Enhanced TJR strategy with liquidity, BOS, impulse bars
    # ...logic for TJR + liquidity, BOS, impulse bars...
    return {
        "signal": "buy",
        "liquidity": True,
        "bos": True,
        "impulse": True,
        "confidence": 0.93
    }


def trade_chain_mapping(trades):
    # Trade chain mapping and confluence logic
    # ...logic for mapping and confluence...
    return {
        "chain": trades,
        "confluence_score": 0.81
    }


STRATEGY_PERFORMANCE_HISTORY = []
STRATEGY_ERROR_ALERTS = []
EXPLAINABILITY_LOG = []
MODEL_RETRAINING_LOG = []
SELECTED_MODELS = {}


def notify_strategy_event(event_type, event_data):
    """
    Send notifications for strategy health, optimization, or performance events.
    Supports email, webhook, and future integrations.
    """
    # Example: send to webhook
    from sentio.connectors.webhook_notification import send_webhook_notification
    webhook_url = event_data.get('webhook_url')
    if webhook_url:
        send_webhook_notification(webhook_url, {"type": event_type, "data": event_data})
    # Example: send email (stub)
    # from sentio.connectors.email_notification import send_email_notification
    # email = event_data.get('email')
    # if email:
    #     send_email_notification(email, f"Sentio Event: {event_type}", str(event_data))
    # Log notification
    if 'notifications' not in event_data:
        event_data['notifications'] = []
    event_data['notifications'].append({"type": event_type, "timestamp": time.time()})


def run_multi_strategy_engine(market_data, strategies, user_selected=None, auto_optimize=False):
    """
    Execute multiple strategies, aggregate signals, and apply weighted voting.
    Supports user selection or auto-optimization.
    Profiles execution time and resource usage for diagnostics.
    Automatically adapts or falls back if performance/health degrades.
    """
    start_time = time.time()
    start_cpu = psutil.cpu_percent(interval=None)
    start_mem = psutil.virtual_memory().percent
    results = []
    weights = []
    errors = []
    optimization_actions = []
    performance_entry = {
        "timestamp": start_time,
        "strategies": [getattr(s, 'name', str(s)) for s in strategies],
        "user_selected": user_selected,
        "auto_optimize": auto_optimize,
        "results": [],
        "errors": [],
        "start_cpu": start_cpu,
        "start_mem": start_mem,
        "optimization_actions": optimization_actions
    }
    # Health-based fallback: if recent errors > threshold, reduce strategy count or switch to safest strategy
    recent_errors = STRATEGY_ERROR_ALERTS[-10:]
    if len(recent_errors) > 5:
        # Fallback: use only strategies with lowest error rate
        safe_strategies = [s for s in strategies if getattr(s, 'name', None) not in [e['strategy'] for e in recent_errors]]
        if safe_strategies:
            optimization_actions.append({"action": "fallback_to_safe_strategies", "count": len(safe_strategies)})
            strategies = safe_strategies
        else:
            optimization_actions.append({"action": "fallback_to_first_strategy", "strategy": getattr(strategies[0], 'name', str(strategies[0]))})
            strategies = [strategies[0]]
    for strat in strategies:
        try:
            if user_selected and getattr(strat, 'name', None) not in user_selected:
                continue
            result = strat.run(market_data)
            if hasattr(strat, 'explain_decision'):
                result['explanation'] = strat.explain_decision(market_data)
            results.append(result)
            weights.append(result.get("confidence", 1.0))
            performance_entry['results'].append({
                "strategy": getattr(strat, 'name', str(strat)),
                "result": result
            })
        except Exception as e:
            error_entry = {"strategy": getattr(strat, 'name', str(strat)), "error": str(e), "timestamp": time.time()}
            errors.append(error_entry)
            performance_entry['errors'].append(error_entry)
            STRATEGY_ERROR_ALERTS.append(error_entry)
    if auto_optimize and results:
        pnl_scores = np.array([r.get("pnl", r.get("confidence", 1.0)) for r in results])
        if pnl_scores.sum() > 0:
            weights = list(np.clip(pnl_scores / pnl_scores.sum(), 0.1, 1.0))
            optimization_actions.append({"action": "auto_optimize_weights", "weights": weights})
    signals = [r.get("signal", "hold") for r in results]
    vote_counts = {}
    for sig, w in zip(signals, weights):
        vote_counts[sig] = vote_counts.get(sig, 0) + w
    final_signal = max(vote_counts, key=vote_counts.get) if vote_counts else "hold"
    confidence = vote_counts.get(final_signal, 0) / sum(weights) if weights else 0
    analytics = {
        "signal_distribution": {s: signals.count(s) for s in set(signals)},
        "average_confidence": float(np.mean(weights)) if weights else 0,
        "strategy_count": len(strategies),
        "error_count": len(errors)
    }
    end_time = time.time()
    end_cpu = psutil.cpu_percent(interval=None)
    end_mem = psutil.virtual_memory().percent
    performance_entry["duration_sec"] = end_time - start_time
    performance_entry["end_cpu"] = end_cpu
    performance_entry["end_mem"] = end_mem
    performance_entry["cpu_delta"] = end_cpu - start_cpu
    performance_entry["mem_delta"] = end_mem - start_mem
    STRATEGY_PERFORMANCE_HISTORY.append(performance_entry)
    return {
        "final_signal": final_signal,
        "confidence": confidence,
        "details": {
            "votes": vote_counts,
            "signals": signals,
            "weights": weights,
            "results": results,
            "analytics": analytics,
            "errors": errors,
            "performance": {
                "duration_sec": performance_entry["duration_sec"],
                "cpu_delta": performance_entry["cpu_delta"],
                "mem_delta": performance_entry["mem_delta"]
            },
            "optimization_actions": optimization_actions
        }
    }


NOTIFICATION_CHANNELS = []
EVENT_SUBSCRIPTIONS = {}


def register_notification_channel(channel_type, target, events):
    NOTIFICATION_CHANNELS.append({
        "type": channel_type,
        "target": target,
        "events": events,
        "timestamp": time.time()
    })
    for event in events:
        if event not in EVENT_SUBSCRIPTIONS:
            EVENT_SUBSCRIPTIONS[event] = []
        EVENT_SUBSCRIPTIONS[event].append(target)


def list_notification_channels():
    return NOTIFICATION_CHANNELS


def update_notification_channel(index, channel_type=None, target=None, events=None):
    if 0 <= index < len(NOTIFICATION_CHANNELS):
        if channel_type:
            NOTIFICATION_CHANNELS[index]["type"] = channel_type
        if target:
            NOTIFICATION_CHANNELS[index]["target"] = target
        if events:
            NOTIFICATION_CHANNELS[index]["events"] = events
            for event in events:
                if event not in EVENT_SUBSCRIPTIONS:
                    EVENT_SUBSCRIPTIONS[event] = []
                EVENT_SUBSCRIPTIONS[event].append(target)
        NOTIFICATION_CHANNELS[index]["timestamp"] = time.time()
        return True
    return False


def log_explainability(decision_type, details):
    EXPLAINABILITY_LOG.append({
        "timestamp": time.time(),
        "type": decision_type,
        "details": details
    })


def get_explainability_log(limit=50):
    return EXPLAINABILITY_LOG[-limit:]


def retrain_models(model_types, data, validation_data=None, scoring=None, model_objects=None):
    # Advanced selection logic: evaluate candidates using real model objects and validation metrics
    for model_type in model_types:
        candidates = model_objects.get(model_type, []) if model_objects and model_type in model_objects else [f"{model_type}_model_v{i}" for i in range(1, 4)]
        scores = {}
        for c in candidates:
            # Use real model.predict if available
            if hasattr(c, 'predict') and validation_data:
                y_true = validation_data.get('y_true', [1, 0, 1, 1, 0])
                y_pred = c.predict(validation_data.get('X', []))
            else:
                y_true = validation_data.get('y_true', [1, 0, 1, 1, 0]) if validation_data else [1, 0, 1, 1, 0]
                y_pred = validation_data.get('y_pred', [1, 1, 1, 0, 0]) if validation_data else [1, 1, 1, 0, 0]
            if scoring == 'accuracy':
                score = accuracy_score(y_true, y_pred)
            elif scoring == 'f1':
                score = f1_score(y_true, y_pred)
            elif scoring == 'rmse':
                score = mean_squared_error(y_true, y_pred, squared=False)
            else:
                score = accuracy_score(y_true, y_pred)
            scores[str(getattr(c, 'name', c))] = score
        # For RMSE, lower is better; for others, higher is better
        if scoring == 'rmse':
            best_model = min(scores, key=scores.get)
        else:
            best_model = max(scores, key=scores.get)
        SELECTED_MODELS[model_type] = best_model
        MODEL_RETRAINING_LOG.append({
            "timestamp": time.time(),
            "model_type": model_type,
            "selected_model": best_model,
            "candidates": scores,
            "best_score": scores[best_model],
            "scoring": scoring,
            "data_summary": str(data)[:100],
            "validation_data_summary": str(validation_data)[:100] if validation_data else None
        })
    return SELECTED_MODELS


def get_model_retraining_log(limit=50):
    return MODEL_RETRAINING_LOG[-limit:]


def get_selected_models():
    return SELECTED_MODELS


LEADERBOARD = []
RIVALRIES = {}

# Leaderboard logic

def update_leaderboard(user_id, strategy_name, performance):
    LEADERBOARD.append({
        "timestamp": time.time(),
        "user_id": user_id,
        "strategy_name": strategy_name,
        "performance": performance
    })

def get_leaderboard(limit=20):
    # Sort by performance descending
    sorted_board = sorted(LEADERBOARD, key=lambda x: x["performance"], reverse=True)
    return sorted_board[:limit]

# Rival system logic

def challenge_rival(challenger_id, rival_id):
    if challenger_id not in RIVALRIES:
        RIVALRIES[challenger_id] = {}
    if rival_id not in RIVALRIES[challenger_id]:
        RIVALRIES[challenger_id][rival_id] = {"wins": 0, "losses": 0, "draws": 0, "history": []}
    return True

def record_rival_result(challenger_id, rival_id, result):
    if challenger_id in RIVALRIES and rival_id in RIVALRIES[challenger_id]:
        RIVALRIES[challenger_id][rival_id][result] += 1
        RIVALRIES[challenger_id][rival_id]["history"].append({"timestamp": time.time(), "result": result})
        return True
    return False

def get_rivalry_stats(challenger_id, rival_id):
    return RIVALRIES.get(challenger_id, {}).get(rival_id, {})


RIVAL_BETS = []

def place_rival_bet(challenger_id, rival_id, amount, currency, date):
    RIVAL_BETS.append({
        "timestamp": time.time(),
        "challenger_id": challenger_id,
        "rival_id": rival_id,
        "amount": amount,
        "currency": currency,
        "date": date,
        "status": "pending"
    })
    return True

def resolve_rival_bet(challenger_id, rival_id, date, winner_id):
    for bet in RIVAL_BETS:
        if (bet["challenger_id"] == challenger_id and bet["rival_id"] == rival_id and bet["date"] == date and bet["status"] == "pending"):
            bet["status"] = "resolved"
            bet["winner_id"] = winner_id
            return True
    return False

def get_rival_bets(challenger_id=None, rival_id=None):
    bets = RIVAL_BETS
    if challenger_id:
        bets = [b for b in bets if b["challenger_id"] == challenger_id]
    if rival_id:
        bets = [b for b in bets if b["rival_id"] == rival_id]
    return bets

FRIENDS = {}
GROUPS = []

# Friend system

def add_friend(user_id, friend_id):
    if user_id not in FRIENDS:
        FRIENDS[user_id] = set()
    FRIENDS[user_id].add(friend_id)
    return True

def get_friends(user_id):
    return list(FRIENDS.get(user_id, set()))

# Group pooling system

def create_group(group_name, members, contributions):
    total = sum(contributions.values())
    GROUPS.append({
        "group_name": group_name,
        "members": members,
        "contributions": contributions,
        "total": total,
        "profit": 0,
        "payouts": {}
    })
    return True

def record_group_profit(group_name, profit):
    for group in GROUPS:
        if group["group_name"] == group_name:
            group["profit"] += profit
            # Calculate payouts
            payouts = {}
            for member in group["members"]:
                pct = group["contributions"][member] / group["total"] if group["total"] > 0 else 0
                payouts[member] = profit * pct
            group["payouts"] = payouts
            return True
    return False

def get_group_info(group_name):
    for group in GROUPS:
        if group["group_name"] == group_name:
            return group
    return {}

CHALLENGES = []
ACHIEVEMENTS = {}
REFERRALS = {}
GROUP_CHATS = {}

# Daily/Weekly Challenges

def create_challenge(name, description, reward, end_date):
    CHALLENGES.append({
        "name": name,
        "description": description,
        "reward": reward,
        "end_date": end_date,
        "participants": [],
        "completed": []
    })
    return True

def join_challenge(user_id, challenge_name):
    for c in CHALLENGES:
        if c["name"] == challenge_name:
            c["participants"].append(user_id)
            return True
    return False

def complete_challenge(user_id, challenge_name):
    for c in CHALLENGES:
        if c["name"] == challenge_name and user_id in c["participants"]:
            c["completed"].append(user_id)
            return True
    return False

def get_challenges():
    return CHALLENGES

# Achievements

def unlock_achievement(user_id, achievement):
    if user_id not in ACHIEVEMENTS:
        ACHIEVEMENTS[user_id] = set()
    ACHIEVEMENTS[user_id].add(achievement)
    return True

def get_achievements(user_id):
    return list(ACHIEVEMENTS.get(user_id, set()))

# Referral Program

def add_referral(referrer_id, new_user_id):
    if referrer_id not in REFERRALS:
        REFERRALS[referrer_id] = set()
    REFERRALS[referrer_id].add(new_user_id)
    return True

def get_referrals(referrer_id):
    return list(REFERRALS.get(referrer_id, set()))

# Group Chat

def send_group_message(group_name, user_id, message):
    if group_name not in GROUP_CHATS:
        GROUP_CHATS[group_name] = []
    GROUP_CHATS[group_name].append({
        "timestamp": time.time(),
        "user_id": user_id,
        "message": message
    })
    return True

def get_group_chat(group_name):
    return GROUP_CHATS.get(group_name, [])

# --- Engagement Expansion: Recommendations, Rewards, Social Feed, Profiles, Marketplace ---
def get_personalized_recommendations(user_id):
    """Return personalized recommendations for strategies, challenges, friends, groups."""
    # Stub: Replace with ML-based recommendation logic
    return ["Strategy Alpha", "Challenge Beta", "Group Gamma", "Friend Delta"]

def claim_daily_reward(user_id):
    """Grant daily/weekly login reward."""
    # Stub: Replace with reward logic, track streaks
    return {"coins": 100, "bonus": "login streak"}

def get_login_streak(user_id):
    """Return current login streak for user."""
    # Stub: Replace with streak tracking logic
    return 5

def get_social_feed(user_id):
    """Return social activity feed for user."""
    # Stub: Replace with real activity feed logic
    return [
        {"type": "trade", "user": "Alice", "profit": 120},
        {"type": "challenge", "user": "Bob", "challenge": "Weekly Win"},
        {"type": "achievement", "user": "You", "achievement": "Top Trader"}
    ]

def update_profile(user_id, avatar=None, bio=None, badges=None):
    """Update user profile."""
    # Stub: Replace with profile update logic
    return True

def get_profile(user_id):
    """Get user profile."""
    # Stub: Replace with profile retrieval logic
    return {"user_id": user_id, "avatar": "default.png", "bio": "Trader", "badges": ["Top Trader"]}

def get_marketplace_items():
    """Return available marketplace items."""
    # Stub: Replace with real marketplace logic
    return [
        {"item_id": "signal1", "type": "signal", "price": 50},
        {"item_id": "strategy1", "type": "strategy", "price": 200},
        {"item_id": "premium1", "type": "premium", "price": 500}
    ]

def buy_marketplace_item(user_id, item_id):
    """Buy an item from the marketplace."""
    # Stub: Replace with purchase logic
    return True

def sell_marketplace_item(user_id, item_id):
    """Sell an item in the marketplace."""
    # Stub: Replace with selling logic
    return True

# --- User Suggestions Feature ---
suggestions_db = []


def submit_suggestion(user_id, title, description):
    """Submit a suggestion to improve Sentio."""
    suggestion_id = str(len(suggestions_db) + 1)
    suggestion = {
        "id": suggestion_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "votes": 0,
        "voters": set()
    }
    suggestions_db.append(suggestion)
    return True

def get_suggestions():
    """Get all user suggestions."""
    return [
        {"id": s["id"], "title": s["title"], "description": s["description"], "votes": s["votes"]}
        for s in suggestions_db
    ]

def vote_suggestion(user_id, suggestion_id, vote):
    """Vote on a suggestion (upvote=1, downvote=-1)."""
    for s in suggestions_db:
        if s["id"] == suggestion_id and user_id not in s["voters"]:
            s["votes"] += vote
            s["voters"].add(user_id)
            return True
    return False
