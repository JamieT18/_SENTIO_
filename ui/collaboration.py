"""
Collaboration utilities for team-based portfolio management in Sentio 2.0
"""
from typing import Dict, List
import datetime

class TeamDashboard:
    def __init__(self):
        self.teams = {}
        self.shared_dashboards = {}
        self.notes = {}

    def create_team(self, team_name: str, members: List[str]):
        self.teams[team_name] = members
        self.shared_dashboards[team_name] = {}
        self.notes[team_name] = []

    def add_dashboard(self, team_name: str, dashboard: Dict):
        if team_name in self.shared_dashboards:
            self.shared_dashboards[team_name].update(dashboard)

    def add_note(self, team_name: str, author: str, note: str):
        entry = {
            'author': author,
            'note': note,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        if team_name in self.notes:
            self.notes[team_name].append(entry)

    def get_notes(self, team_name: str) -> List[Dict]:
        return self.notes.get(team_name, [])

    def get_dashboard(self, team_name: str) -> Dict:
        return self.shared_dashboards.get(team_name, {})

class StrategyBacktester:
    def backtest(self, strategy_fn, historical_data):
        # Simple backtest: apply strategy_fn to historical_data
        results = []
        for data_point in historical_data:
            result = strategy_fn(data_point)
            results.append(result)
        return results
