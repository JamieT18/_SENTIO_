"""
Real-Time Alerts & Notifications for Sentio
Push alerts for trade signals, risk events, and system health
"""
from typing import List, Dict, Any
import threading

class AlertManager:
    def __init__(self):
        self.subscribers: List[str] = []
        self.alerts: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def subscribe(self, user_id: str):
        with self.lock:
            if user_id not in self.subscribers:
                self.subscribers.append(user_id)

    def push_alert(self, alert: Dict[str, Any]):
        with self.lock:
            self.alerts.append(alert)
        # In production: push to websocket, email, or mobile

    def get_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        # Return alerts for user (stub)
        return self.alerts[-10:]
