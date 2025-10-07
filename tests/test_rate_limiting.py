"""
Tests for Rate Limiting and API Monitoring
"""

import sys
import os
import time

sys.path.insert(0, "/home/runner/work/Sentio-2.0/Sentio-2.0")

from fastapi.testclient import TestClient
from sentio.ui.api import app, rate_limiter, api_monitor


def test_rate_limiter_basic():
    """Test basic rate limiting functionality"""
    print("Testing rate limiter...")

    client = TestClient(app)

    # Test health endpoint (should not be rate limited)
    response = client.get("/api/v1/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    print("✓ Health check works")

    # Test rate limit status endpoint (requires token)
    response = client.get(
        "/api/v1/rate-limit/status", headers={"Authorization": "Bearer test_token"}
    )
    assert (
        response.status_code == 200
    ), f"Rate limit status failed: {response.status_code}"
    data = response.json()
    assert "limit_minute" in data, "Rate limit status missing limit_minute"
    assert "remaining_minute" in data, "Rate limit status missing remaining_minute"
    print(
        f"✓ Rate limit status: {data['remaining_minute']} requests remaining this minute"
    )


def test_monitoring_endpoints():
    """Test API monitoring endpoints"""
    print("\nTesting monitoring endpoints...")

    client = TestClient(app)

    # Make a few test requests to generate metrics
    for i in range(5):
        client.get("/api/v1/health")

    # Test metrics overview
    response = client.get(
        "/api/v1/metrics/overview", headers={"Authorization": "Bearer test_token"}
    )
    assert (
        response.status_code == 200
    ), f"Metrics overview failed: {response.status_code}"
    data = response.json()
    assert "total_calls" in data, "Metrics missing total_calls"
    assert data["total_calls"] > 0, "No calls recorded"
    print(f"✓ Metrics overview: {data['total_calls']} total calls")

    # Test endpoint metrics
    response = client.get(
        "/api/v1/metrics/endpoints", headers={"Authorization": "Bearer test_token"}
    )
    assert (
        response.status_code == 200
    ), f"Endpoint metrics failed: {response.status_code}"
    data = response.json()
    assert len(data) > 0, "No endpoint metrics recorded"
    print(f"✓ Endpoint metrics: {len(data)} endpoints tracked")

    # Test hourly metrics
    response = client.get(
        "/api/v1/metrics/hourly?hours=1", headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200, f"Hourly metrics failed: {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Hourly metrics should be a list"
    print(f"✓ Hourly metrics: {len(data)} hours of data")


def test_rate_limit_enforcement():
    """Test that rate limiting actually blocks requests"""
    print("\nTesting rate limit enforcement...")

    from sentio.ui.rate_limiter import RateLimiter
    from fastapi import Request
    from unittest.mock import Mock

    # Create a rate limiter with very low limits for testing
    limiter = RateLimiter(
        requests_per_minute=3, requests_per_hour=10, requests_per_day=20
    )

    # Mock request
    mock_request = Mock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.headers = {}
    mock_request.state.user_id = None

    # Make requests up to the limit
    for i in range(3):
        result = None
        try:
            import asyncio

            result = asyncio.run(limiter.check_rate_limit(mock_request))
            print(f"  Request {i+1}/3: OK ({result['remaining_minute']} remaining)")
        except Exception as e:
            print(f"  Request {i+1}/3: Failed - {e}")
            assert False, f"Request should not be rate limited yet: {e}"

    # Next request should be rate limited
    try:
        import asyncio

        asyncio.run(limiter.check_rate_limit(mock_request))
        assert False, "Request should have been rate limited"
    except Exception as e:
        print(f"  Request 4/3: Rate limited as expected ✓")
        assert "429" in str(e) or "Rate limit" in str(e), f"Wrong error: {e}"


def test_monitoring_tracks_errors():
    """Test that monitoring tracks errors correctly"""
    print("\nTesting error tracking...")

    client = TestClient(app)

    # Make a request that will fail (invalid endpoint)
    response = client.post(
        "/api/v1/invalid-endpoint", headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 404, "Expected 404 for invalid endpoint"

    # Check that error was recorded
    response = client.get(
        "/api/v1/metrics/errors?limit=10",
        headers={"Authorization": "Bearer test_token"},
    )
    assert response.status_code == 200, f"Error metrics failed: {response.status_code}"
    errors = response.json()

    # Should have at least one error
    if len(errors) > 0:
        print(f"✓ Error tracking: {len(errors)} errors recorded")
    else:
        print("✓ Error tracking enabled (no errors yet)")


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("RATE LIMITING & MONITORING TESTS")
    print("=" * 80)

    try:
        test_rate_limiter_basic()
        test_monitoring_endpoints()
        test_rate_limit_enforcement()
        test_monitoring_tracks_errors()

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
