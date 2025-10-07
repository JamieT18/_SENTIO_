"""
Demo trading environment stub for Sentio
"""
class DemoBroker:
    def place_order(self, order):
        return {"status": "demo", "order": order}
    def get_quote(self, symbol):
        return {"symbol": symbol, "price": 99.0}
