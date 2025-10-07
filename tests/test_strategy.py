"""
Edge case tests for Sentio strategy engine
"""
import pytest
from sentio.strategies.voting_engine import VotingEngine

def test_voting_engine_empty():
    engine = VotingEngine()
    result = engine.vote([])
    assert result is not None
