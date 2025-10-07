"""
Sandbox/demo broker for Sentio
"""
class SandboxBroker:
    def place_order(self, order):
        return {"status": "demo", "order": order}
    def get_quote(self, symbol):
        return {"symbol": symbol, "price": 100.0}
