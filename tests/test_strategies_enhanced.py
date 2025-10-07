import pytest
from sentio.strategies.enhanced_strategies import get_strategies, run_strategy

def test_get_strategies():
    strategies = get_strategies()
    assert isinstance(strategies, list)
    assert len(strategies) > 0
    for s in strategies:
        assert "name" in s
        assert "win_rate" in s
        assert 0 <= s["win_rate"] <= 1

def test_run_strategy_valid():
    result = run_strategy("AI Momentum")
    assert "strategy" in result
    assert "win" in result
    assert "profit" in result

def test_run_strategy_invalid():
    result = run_strategy("Nonexistent")
    assert "error" in result
