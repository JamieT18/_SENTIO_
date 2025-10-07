"""
Integration tests for Sentio API endpoints
"""
import unittest
from fastapi.testclient import TestClient
from sentio.api.main import app

client = TestClient(app)

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.market_data = {
            "data": [
                {"open": 100, "high": 105, "low": 99, "close": 104},
                {"open": 104, "high": 106, "low": 103, "close": 105},
                {"open": 105, "high": 107, "low": 104, "close": 106}
            ]
        }

    def test_var_endpoint(self):
        response = client.post("/risk/var", json=self.market_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("var", response.json())

    def test_cvar_endpoint(self):
        response = client.post("/risk/cvar", json=self.market_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("cvar", response.json())

    def test_dynamic_risk_endpoint(self):
        response = client.post("/risk/dynamic", json=self.market_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("predicted_risk", response.json())

    def test_candlestick_endpoint(self):
        response = client.post("/analysis/candlestick", json=self.market_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_chart_patterns_endpoint(self):
        response = client.post("/analysis/chart", json=self.market_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_backtest_basic_endpoint(self):
        response = client.post("/backtest/basic", json=self.market_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("trades", response.json())
        self.assertIn("profit", response.json())

    def test_backtest_multi_endpoint(self):
        response = client.post("/backtest/multi", json=self.market_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

if __name__ == "__main__":
    unittest.main()
