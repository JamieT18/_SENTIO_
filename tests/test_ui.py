"""
Unit tests for Sentio UI module
"""
import unittest
from sentio.ui import render_dashboard, advanced_dashboard_features

class TestDashboard(unittest.TestCase):
    def test_render_dashboard(self):
        data = {'portfolio': 100, 'risk': 0.1}
        try:
            render_dashboard(data)
        except Exception as e:
            self.fail(f"render_dashboard raised exception: {e}")

    def test_advanced_dashboard_features_stub(self):
        try:
            advanced_dashboard_features()
        except Exception as e:
            self.fail(f"advanced_dashboard_features raised exception: {e}")

if __name__ == "__main__":
    unittest.main()
