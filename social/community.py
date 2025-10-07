"""
Social/Community Features for Sentio
Strategy sharing, leaderboards, collaborative analytics
"""
from typing import List, Dict, Any

class CommunityManager:
    def __init__(self):
        self.strategies: List[Dict[str, Any]] = []
        self.leaderboard: List[Dict[str, Any]] = []

    def share_strategy(self, strategy: Dict[str, Any]):
        self.strategies.append(strategy)

    def get_strategies(self) -> List[Dict[str, Any]]:
        return self.strategies[-20:]

    def update_leaderboard(self, entry: Dict[str, Any]):
        self.leaderboard.append(entry)
        self.leaderboard = sorted(self.leaderboard, key=lambda x: x.get('score', 0), reverse=True)[:10]

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        return self.leaderboard
