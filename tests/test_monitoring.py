"""
Basic backend monitoring and error tracking tests for Sentio
"""
from sentio.monitoring.prometheus_config import start_metrics_server
from sentio.monitoring.sentry_init import init_sentry
import pytest

def test_prometheus_metrics_server():
    try:
        start_metrics_server(port=8010)
    except Exception as e:
        pytest.fail(f"Prometheus metrics server failed: {e}")

def test_sentry_init():
    try:
        init_sentry()
    except Exception as e:
        pytest.fail(f"Sentry init failed: {e}")
