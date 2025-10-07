"""
Basic trading engine tests for Sentio
"""
import pytest
import sentio.core.config

class DummyRiskConfig:
    def model_dump(self):
        return {}

class DummyStrategyConfig:
    max_concurrent_trades = 1

class DummyConfig:
    risk_management = DummyRiskConfig()
    strategy = DummyStrategyConfig()


def test_trading_engine_init(monkeypatch):
    monkeypatch.setattr(sentio.core.config, "get_config", lambda: DummyConfig())
    from sentio.execution.trading_engine import TradingEngine
    engine = TradingEngine(strategies=[])
    assert engine is not None
