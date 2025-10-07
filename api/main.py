# --- Imports (move all to top for clarity and fix dependency order) ---
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
from functools import lru_cache
from sentio.ai.reinforcement_learning import AdaptiveLearningEngine
from sentio.strategies.optimizer import advanced_optimizer
from sentio.billing.subscription_manager import SubscriptionManager
from sentio.billing.integration import process_payment, get_subscription_status
from sentio.risk.analytics import calculate_var, calculate_cvar, dynamic_risk_model
from sentio.analysis.patterns import detect_candlestick_patterns, detect_chart_patterns
from sentio.strategies.strategy import BaseStrategy
from sentio.strategies import run_multi_strategy_engine, STRATEGY_PERFORMANCE_HISTORY
from sentio.strategies.enhanced_strategies import get_strategies, run_strategy
from sentio.execution.backtesting import run_backtest, run_multi_strategy_backtest
from sentio.data.market_data import MarketDataManager
from sentio.risk.risk_manager import RiskManager
from sentio.analysis.explainable_ai import ExplainableAI
from sentio.long_term_investment.portfolio import PortfolioOptimizer
from sentio.core.compliance import ComplianceChecker
from sentio.ui.accessibility import Accessibility
from sentio.monitoring.prometheus_config import start_metrics_server
from sentio.monitoring.sentry_init import init_sentry
from sentio.core.logger import SentioLogger

from sentio.api.admin import router as admin_router
from sentio.api.admin_ws import router as admin_ws_router
from sentio.api.metrics import router as metrics_router

import logging
import time
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil
import threading
import gc
import json
from collections import deque

# --- FastAPI app instance ---
app = FastAPI(title="Sentio API")
executor = ThreadPoolExecutor(max_workers=8)

# --- Market Data Manager Instance ---
market_data_mgr = MarketDataManager()



# --- API key and roles ---
API_KEYS = {
    "sentio-demo-key": "admin",
    "sentio-user-key": "user"
}
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30    # max requests per window

def api_key_auth(x_api_key: str = None, request: Request = None, required_role: str = None):
    # API key check
    role = API_KEYS.get(x_api_key)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    # Role check
    if required_role and role != required_role:
        raise HTTPException(status_code=403, detail="Insufficient role.")
    # Rate limiting
    ip = request.client.host if request else "unknown"
    now = int(time.time())
    window = now // RATE_LIMIT_WINDOW
    key = f"{ip}:{x_api_key}:{window}"
    RATE_LIMIT[key] = RATE_LIMIT.get(key, 0) + 1
    if RATE_LIMIT[key] > RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    # Logging
    logging.info(f"API request from {ip} with key {x_api_key} for role {role}")
    # Audit log
    log_audit(ip, x_api_key, request.url.path if request else "unknown", "accepted")
    return x_api_key

# --- FastAPI app instance ---
app = FastAPI(title="Sentio 2.0 API")
executor = ThreadPoolExecutor(max_workers=8)

# --- Market Data Manager Instance ---
market_data_mgr = MarketDataManager()

# --- Strategy Performance Monitoring API ---
from sentio.strategies import STRATEGY_PERFORMANCE_HISTORY

@app.get("/api/v1/strategy/performance-history")
def get_strategy_performance_history(limit: int = 20, x_api_key: str = Depends(api_key_auth)):
    """
    Returns recent strategy performance and error history for diagnostics and analytics.
    """
    history = STRATEGY_PERFORMANCE_HISTORY[-limit:]
    return {"history": history, "count": len(history)}

# --- AI Engine Instance ---
ai_engine = AdaptiveLearningEngine(ensemble_size=3)

class TransferLearningRequest(BaseModel):
    market_data: List[Dict[str, Any]]
    user_profile: Dict[str, Any] = {}

@app.post("/api/v1/ai/transfer-learn")
def api_transfer_learn(req: TransferLearningRequest):
    df = pd.DataFrame(req.market_data)
    ai_engine.online_transfer_learn(df, req.user_profile)
    return {"status": "transfer learning complete"}

class ExternalDataRequest(BaseModel):
    market_state: Dict[str, Any]
    external_data: Dict[str, Any]

@app.post("/api/v1/ai/integrate-external-data")
def api_integrate_external_data(req: ExternalDataRequest):
    result = ai_engine.integrate_external_data(req.market_state, req.external_data)
    return {"integrated_state": result}

class PretrainRequest(BaseModel):
    unlabeled_data: List[Dict[str, Any]]
    epochs: int = 5

@app.post("/api/v1/ai/self-supervised-pretrain")
def api_self_supervised_pretrain(req: PretrainRequest):
    df = pd.DataFrame(req.unlabeled_data)
    ai_engine.self_supervised_pretrain(df, req.epochs)
    return {"status": "pretraining complete"}

class AnomalyDetectionRequest(BaseModel):
    trade_outcomes: List[Dict[str, Any]]

@app.post("/api/v1/ai/detect-anomalies")
def api_detect_anomalies(req: AnomalyDetectionRequest):
    anomalies = ai_engine.detect_anomalies(req.trade_outcomes)
    return {"anomalies": anomalies}

class DistributedTrainRequest(BaseModel):
    data_splits: List[List[Dict[str, Any]]]

@app.post("/api/v1/ai/distributed-train")
def api_distributed_train(req: DistributedTrainRequest):
    dfs = [pd.DataFrame(split) for split in req.data_splits]
    ai_engine.distributed_train(dfs)
    return {"status": "distributed training complete"}

class HyperOptRequest(BaseModel):
    market_data: List[Dict[str, Any]]
    n_trials: int = 20

@app.post("/api/v1/ai/optimize-hyperparameters")
def api_optimize_hyperparameters(req: HyperOptRequest):
    df = pd.DataFrame(req.market_data)
    best_params = ai_engine.optimize_hyperparameters(df, req.n_trials)
    return {"best_params": best_params}

class RewardShapingRequest(BaseModel):
    trade_outcome: Dict[str, Any]

@app.post("/api/v1/ai/advanced-reward-shaping")
def api_advanced_reward_shaping(req: RewardShapingRequest):
    reward = ai_engine.advanced_reward_shaping(req.trade_outcome)
    return {"shaped_reward": reward}
from sentio.billing.subscription_manager import SubscriptionManager
from sentio.billing.integration import process_payment, get_subscription_status

billing_manager = SubscriptionManager()

class BillingRequest(BaseModel):
    user_id: str
    amount: float
    diagnostics: Dict[str, Any] = {}

@app.post("/api/v1/billing/process-payment")
def api_process_payment(req: BillingRequest, x_api_key: str = Depends(api_key_auth)):
    try:
        result = process_payment(req.user_id, req.amount, diagnostics=req.diagnostics)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/billing/subscription-status")
def api_subscription_status(user_id: str, x_api_key: str = Depends(api_key_auth)):
    try:
        status = get_subscription_status(user_id)
        return {"user_id": user_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/billing/history")
def api_billing_history(user_id: str, x_api_key: str = Depends(api_key_auth)):
    history = billing_manager.get_billing_history(user_id)
    return {"user_id": user_id, "history": history}

@app.get("/api/v1/billing/diagnostics")
def api_billing_diagnostics(user_id: str, x_api_key: str = Depends(api_key_auth)):
    sub = billing_manager.get_subscription(user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {
        "user_id": user_id,
        "tier": sub.tier.value,
        "status": sub.status.value,
        "profit_sharing_balance": sub.profit_sharing_balance,
        "total_profits_shared": sub.total_profits_shared,
        "start_date": sub.start_date.isoformat(),
        "end_date": sub.end_date.isoformat() if sub.end_date else None,
        "trial_end": sub.trial_end.isoformat() if sub.trial_end else None,
    }

@app.post("/api/v1/billing/stripe-webhook")
def api_stripe_webhook(event_type: str, event_data: Dict[str, Any]):
    from sentio.billing.subscription_manager import handle_stripe_webhook
    handle_stripe_webhook(event_type, event_data)
    return {"status": "webhook received", "event_type": event_type}
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
from functools import lru_cache
from sentio.strategies.optimizer import advanced_optimizer
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil
import threading
import gc
import time
import json
from collections import deque

## --- BEGIN: Enhanced FastAPI main.py from improvements ---
# --- Imports (move all to top for clarity and fix dependency order) ---
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
from functools import lru_cache
from sentio.ai.reinforcement_learning import AdaptiveLearningEngine
from sentio.strategies.optimizer import advanced_optimizer
from sentio.billing.subscription_manager import SubscriptionManager
from sentio.billing.integration import process_payment, get_subscription_status
from sentio.risk.analytics import calculate_var, calculate_cvar, dynamic_risk_model
from sentio.analysis.patterns import detect_candlestick_patterns, detect_chart_patterns
from sentio.strategies.strategy import BaseStrategy
from sentio.strategies import run_multi_strategy_engine, STRATEGY_PERFORMANCE_HISTORY
from sentio.strategies.enhanced_strategies import get_strategies, run_strategy
from sentio.execution.backtesting import run_backtest, run_multi_strategy_backtest
from sentio.data.market_data import MarketDataManager
from sentio.risk.risk_manager import RiskManager
from sentio.analysis.explainable_ai import ExplainableAI
from sentio.long_term_investment.portfolio import PortfolioOptimizer
from sentio.core.compliance import ComplianceChecker
from sentio.ui.accessibility import Accessibility
from sentio.monitoring.prometheus_config import start_metrics_server
from sentio.monitoring.sentry_init import init_sentry
from sentio.core.logger import SentioLogger

from sentio.api.admin import router as admin_router
from sentio.api.admin_ws import router as admin_ws_router
from sentio.api.metrics import router as metrics_router

import logging
import time
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil
import threading
import gc
import json
from collections import deque

# --- FastAPI app instance ---
app = FastAPI(title="Sentio 2.0 API")
executor = ThreadPoolExecutor(max_workers=8)

# --- Market Data Manager Instance ---
market_data_mgr = MarketDataManager()

# --- API key and roles ---
API_KEYS = {
    "sentio-demo-key": "admin",
    "sentio-user-key": "user"
}
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30    # max requests per window

def api_key_auth(x_api_key: str = None, request: Request = None, required_role: str = None):
    # API key check
    role = API_KEYS.get(x_api_key)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    # Role check
    if required_role and role != required_role:
        raise HTTPException(status_code=403, detail="Insufficient role.")
    # Rate limiting
    ip = request.client.host if request else "unknown"
    now = int(time.time())
    window = now // RATE_LIMIT_WINDOW
    key = f"{ip}:{x_api_key}:{window}"
    RATE_LIMIT[key] = RATE_LIMIT.get(key, 0) + 1
    if RATE_LIMIT[key] > RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    # Logging
    logging.info(f"API request from {ip} with key {x_api_key} for role {role}")
    # Audit log
    log_audit(ip, x_api_key, request.url.path if request else "unknown", "accepted")
    return x_api_key

# --- Audit log endpoint ---
AUDIT_LOG = []
def log_audit(ip, api_key, endpoint, status):
    AUDIT_LOG.append({"ip": ip, "api_key": api_key, "endpoint": endpoint, "status": status, "timestamp": time.time()})

# --- Strategy Performance Monitoring API ---
from sentio.strategies import STRATEGY_PERFORMANCE_HISTORY

@app.get("/api/v1/strategy/performance-history")
def get_strategy_performance_history(limit: int = 20, x_api_key: str = Depends(api_key_auth)):
    """
    Returns recent strategy performance and error history for diagnostics and analytics.
    """
    history = STRATEGY_PERFORMANCE_HISTORY[-limit:]
    return {"history": history, "count": len(history)}

# --- AI Engine Instance ---
ai_engine = AdaptiveLearningEngine(ensemble_size=3)

class TransferLearningRequest(BaseModel):
    market_data: List[Dict[str, Any]]
    user_profile: Dict[str, Any] = {}

@app.post("/api/v1/ai/transfer-learn")
def api_transfer_learn(req: TransferLearningRequest):
    df = pd.DataFrame(req.market_data)
    ai_engine.online_transfer_learn(df, req.user_profile)
    return {"status": "transfer learning complete"}

class ExternalDataRequest(BaseModel):
    market_state: Dict[str, Any]
    external_data: Dict[str, Any]

@app.post("/api/v1/ai/integrate-external-data")
def api_integrate_external_data(req: ExternalDataRequest):
    result = ai_engine.integrate_external_data(req.market_state, req.external_data)
    return {"integrated_state": result}

class PretrainRequest(BaseModel):
    unlabeled_data: List[Dict[str, Any]]
    epochs: int = 5

@app.post("/api/v1/ai/self-supervised-pretrain")
def api_self_supervised_pretrain(req: PretrainRequest):
    df = pd.DataFrame(req.unlabeled_data)
    ai_engine.self_supervised_pretrain(df, req.epochs)
    return {"status": "pretraining complete"}

class AnomalyDetectionRequest(BaseModel):
    trade_outcomes: List[Dict[str, Any]]

@app.post("/api/v1/ai/detect-anomalies")
def api_detect_anomalies(req: AnomalyDetectionRequest):
    anomalies = ai_engine.detect_anomalies(req.trade_outcomes)
    return {"anomalies": anomalies}

class DistributedTrainRequest(BaseModel):
    data_splits: List[List[Dict[str, Any]]]

@app.post("/api/v1/ai/distributed-train")
def api_distributed_train(req: DistributedTrainRequest):
    dfs = [pd.DataFrame(split) for split in req.data_splits]
    ai_engine.distributed_train(dfs)
    return {"status": "distributed training complete"}

class HyperOptRequest(BaseModel):
    market_data: List[Dict[str, Any]]
    n_trials: int = 20

@app.post("/api/v1/ai/optimize-hyperparameters")
def api_optimize_hyperparameters(req: HyperOptRequest):
    df = pd.DataFrame(req.market_data)
    best_params = ai_engine.optimize_hyperparameters(df, req.n_trials)
    return {"best_params": best_params}

class RewardShapingRequest(BaseModel):
    trade_outcome: Dict[str, Any]

@app.post("/api/v1/ai/advanced-reward-shaping")
def api_advanced_reward_shaping(req: RewardShapingRequest):
    reward = ai_engine.advanced_reward_shaping(req.trade_outcome)
    return {"shaped_reward": reward}

from sentio.billing.subscription_manager import SubscriptionManager
from sentio.billing.integration import process_payment, get_subscription_status

billing_manager = SubscriptionManager()

class BillingRequest(BaseModel):
    user_id: str
    amount: float
    diagnostics: Dict[str, Any] = {}

@app.post("/api/v1/billing/process-payment")
def api_process_payment(req: BillingRequest, x_api_key: str = Depends(api_key_auth)):
    try:
        result = process_payment(req.user_id, req.amount, diagnostics=req.diagnostics)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/billing/subscription-status")
def api_subscription_status(user_id: str, x_api_key: str = Depends(api_key_auth)):
    try:
        status = get_subscription_status(user_id)
        return {"user_id": user_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/billing/history")
def api_billing_history(user_id: str, x_api_key: str = Depends(api_key_auth)):
    history = billing_manager.get_billing_history(user_id)
    return {"user_id": user_id, "history": history}

@app.get("/api/v1/billing/diagnostics")
def api_billing_diagnostics(user_id: str, x_api_key: str = Depends(api_key_auth)):
    sub = billing_manager.get_subscription(user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {
        "user_id": user_id,
        "tier": sub.tier.value,
        "status": sub.status.value,
        "profit_sharing_balance": sub.profit_sharing_balance,
        "total_profits_shared": sub.total_profits_shared,
        "start_date": sub.start_date.isoformat(),
        "end_date": sub.end_date.isoformat() if sub.end_date else None,
        "trial_end": sub.trial_end.isoformat() if sub.trial_end else None,
    }

@app.post("/api/v1/billing/stripe-webhook")
def api_stripe_webhook(event_type: str, event_data: Dict[str, Any]):
    from sentio.billing.subscription_manager import handle_stripe_webhook
    handle_stripe_webhook(event_type, event_data)
    return {"status": "webhook received", "event_type": event_type}

# --- Startup events ---
@app.on_event("startup")
async def startup_event():
    init_sentry()
    start_metrics_server(port=8001)
    logging.info("Application startup completed.")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Application shutdown initiated.")

app.include_router(admin_router)
app.include_router(admin_ws_router)
app.include_router(metrics_router)

structured_logger = SentioLogger.get_structured_logger("api")
## --- END: Enhanced FastAPI main.py from improvements ---
    }


