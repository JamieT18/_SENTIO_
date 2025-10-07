"""
Multi-Broker Support for Sentio
Integrate with multiple brokers for live trading and data feeds
"""
from typing import Dict, Any

class BrokerManager:
    def __init__(self):
        self.brokers: Dict[str, Any] = {}

    def register_broker(self, name: str, broker_api: Any):
        self.brokers[name] = broker_api

    def place_order(self, broker_name: str, order: Dict[str, Any]) -> Dict[str, Any]:
        broker = self.brokers.get(broker_name)
        if not broker:
            return {"error": "Broker not found"}
        return broker.place_order(order)

    def get_quote(self, broker_name: str, symbol: str) -> Dict[str, Any]:
        broker = self.brokers.get(broker_name)
        if not broker:
            return {"error": "Broker not found"}
        return broker.get_quote(symbol)
