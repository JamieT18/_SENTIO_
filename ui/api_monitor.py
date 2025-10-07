"""
API Monitoring and Analytics for Sentio API
Tracks API usage, performance metrics, and provides analytics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict
from fastapi import Request, Response
import time
import asyncio

from ..core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class APICallMetrics:
    """Metrics for a single API call"""

    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    error: Optional[str] = None


class APIMonitor:
    """
    Monitor API usage and performance
    Provides analytics and insights into API usage patterns
    """

    def __init__(self, max_history: int = 10000):
        """
        Initialize API monitor

        Args:
            max_history: Maximum number of call records to keep in memory
        """
        self.max_history = max_history

        # Recent API calls
        self._call_history: List[APICallMetrics] = []

        # Aggregated statistics
        self._endpoint_stats: Dict[str, Dict[str, any]] = defaultdict(
            lambda: {
                "total_calls": 0,
                "total_errors": 0,
                "total_response_time": 0.0,
                "status_codes": defaultdict(int),
                "last_called": None,
            }
        )

        # User-specific statistics
        self._user_stats: Dict[str, Dict[str, any]] = defaultdict(
            lambda: {
                "total_calls": 0,
                "total_errors": 0,
                "endpoints_used": set(),
                "last_activity": None,
            }
        )

        # Time-based statistics (hourly buckets)
        self._hourly_stats: Dict[int, Dict[str, int]] = defaultdict(
            lambda: {"total_calls": 0, "total_errors": 0}
        )

    def _get_user_identifier(self, request: Request) -> Optional[str]:
        """Extract user identifier from request"""
        return getattr(request.state, "user_id", None)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        return client_ip

    async def record_request(
        self,
        request: Request,
        response: Response,
        response_time_ms: float,
        error: Optional[str] = None,
    ):
        """
        Record an API request with its metrics

        Args:
            request: FastAPI Request object
            response: FastAPI Response object
            response_time_ms: Response time in milliseconds
            error: Error message if request failed
        """
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        user_id = self._get_user_identifier(request)
        ip_address = self._get_client_ip(request)
        now = datetime.now()

        # Create metrics record
        metrics = APICallMetrics(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            timestamp=now,
            user_id=user_id,
            ip_address=ip_address,
            error=error,
        )

        # Add to history
        self._call_history.append(metrics)

        # Trim history if needed
        if len(self._call_history) > self.max_history:
            self._call_history = self._call_history[-self.max_history :]

        # Update endpoint statistics
        endpoint_key = f"{method} {endpoint}"
        stats = self._endpoint_stats[endpoint_key]
        stats["total_calls"] += 1
        stats["total_response_time"] += response_time_ms
        stats["status_codes"][status_code] += 1
        stats["last_called"] = now

        if error or status_code >= 400:
            stats["total_errors"] += 1

        # Update user statistics
        if user_id:
            user_stats = self._user_stats[user_id]
            user_stats["total_calls"] += 1
            user_stats["endpoints_used"].add(endpoint)
            user_stats["last_activity"] = now

            if error or status_code >= 400:
                user_stats["total_errors"] += 1

        # Update hourly statistics
        hour_bucket = int(now.timestamp() // 3600)
        self._hourly_stats[hour_bucket]["total_calls"] += 1
        if error or status_code >= 400:
            self._hourly_stats[hour_bucket]["total_errors"] += 1

        # Log slow requests
        if response_time_ms > 1000:  # > 1 second
            logger.warning(
                f"Slow API request: {method} {endpoint} took {response_time_ms:.2f}ms",
                extra={
                    "endpoint": endpoint,
                    "method": method,
                    "response_time_ms": response_time_ms,
                    "user_id": user_id,
                },
            )

    def get_endpoint_statistics(self) -> Dict[str, Any]:
        """
        Get aggregated statistics for all endpoints

        Returns:
            Dict with endpoint statistics
        """
        result = {}

        for endpoint, stats in self._endpoint_stats.items():
            avg_response_time = (
                stats["total_response_time"] / stats["total_calls"]
                if stats["total_calls"] > 0
                else 0
            )

            error_rate = (
                stats["total_errors"] / stats["total_calls"] * 100
                if stats["total_calls"] > 0
                else 0
            )

            result[endpoint] = {
                "total_calls": stats["total_calls"],
                "total_errors": stats["total_errors"],
                "error_rate_percent": round(error_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "status_codes": dict(stats["status_codes"]),
                "last_called": (
                    stats["last_called"].isoformat() if stats["last_called"] else None
                ),
            }

        return result

    def get_user_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a specific user or all users

        Args:
            user_id: Optional user ID to filter by

        Returns:
            Dict with user statistics
        """
        if user_id:
            if user_id not in self._user_stats:
                return {
                    "user_id": user_id,
                    "total_calls": 0,
                    "total_errors": 0,
                    "endpoints_used": [],
                    "last_activity": None,
                }

            stats = self._user_stats[user_id]
            return {
                "user_id": user_id,
                "total_calls": stats["total_calls"],
                "total_errors": stats["total_errors"],
                "error_rate_percent": round(
                    (
                        stats["total_errors"] / stats["total_calls"] * 100
                        if stats["total_calls"] > 0
                        else 0
                    ),
                    2,
                ),
                "endpoints_used": sorted(list(stats["endpoints_used"])),
                "last_activity": (
                    stats["last_activity"].isoformat()
                    if stats["last_activity"]
                    else None
                ),
            }
        else:
            # Return all users
            result = {}
            for uid, stats in self._user_stats.items():
                result[uid] = {
                    "total_calls": stats["total_calls"],
                    "total_errors": stats["total_errors"],
                    "error_rate_percent": round(
                        (
                            stats["total_errors"] / stats["total_calls"] * 100
                            if stats["total_calls"] > 0
                            else 0
                        ),
                        2,
                    ),
                    "endpoints_used": len(stats["endpoints_used"]),
                    "last_activity": (
                        stats["last_activity"].isoformat()
                        if stats["last_activity"]
                        else None
                    ),
                }
            return result

    def get_hourly_statistics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get hourly statistics for the last N hours

        Args:
            hours: Number of hours to look back

        Returns:
            List of hourly statistics
        """
        now = datetime.now()
        current_hour = int(now.timestamp() // 3600)

        result = []
        for i in range(hours):
            hour_bucket = current_hour - i
            stats = self._hourly_stats.get(
                hour_bucket, {"total_calls": 0, "total_errors": 0}
            )

            hour_time = datetime.fromtimestamp(hour_bucket * 3600)

            result.append(
                {
                    "hour": hour_time.isoformat(),
                    "total_calls": stats["total_calls"],
                    "total_errors": stats["total_errors"],
                    "error_rate_percent": round(
                        (
                            stats["total_errors"] / stats["total_calls"] * 100
                            if stats["total_calls"] > 0
                            else 0
                        ),
                        2,
                    ),
                }
            )

        return list(reversed(result))

    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent API errors

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of recent errors
        """
        errors = [
            {
                "endpoint": call.endpoint,
                "method": call.method,
                "status_code": call.status_code,
                "error": call.error,
                "timestamp": call.timestamp.isoformat(),
                "user_id": call.user_id,
                "response_time_ms": call.response_time_ms,
            }
            for call in reversed(self._call_history)
            if call.error or call.status_code >= 400
        ]

        return errors[:limit]

    def get_overall_statistics(self) -> Dict[str, Any]:
        """
        Get overall API statistics

        Returns:
            Dict with overall statistics
        """
        total_calls = sum(
            stats["total_calls"] for stats in self._endpoint_stats.values()
        )
        total_errors = sum(
            stats["total_errors"] for stats in self._endpoint_stats.values()
        )

        if self._call_history:
            total_response_time = sum(
                call.response_time_ms for call in self._call_history
            )
            avg_response_time = total_response_time / len(self._call_history)

            # Calculate percentiles
            sorted_times = sorted(call.response_time_ms for call in self._call_history)
            p50_idx = len(sorted_times) // 2
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)

            p50 = sorted_times[p50_idx] if sorted_times else 0
            p95 = sorted_times[p95_idx] if sorted_times else 0
            p99 = sorted_times[p99_idx] if sorted_times else 0
        else:
            avg_response_time = 0
            p50 = p95 = p99 = 0

        return {
            "total_calls": total_calls,
            "total_errors": total_errors,
            "error_rate_percent": round(
                total_errors / total_calls * 100 if total_calls > 0 else 0, 2
            ),
            "avg_response_time_ms": round(avg_response_time, 2),
            "p50_response_time_ms": round(p50, 2),
            "p95_response_time_ms": round(p95, 2),
            "p99_response_time_ms": round(p99, 2),
            "total_endpoints": len(self._endpoint_stats),
            "total_users": len(self._user_stats),
            "history_size": len(self._call_history),
        }


# Global monitor instance
_api_monitor: Optional[APIMonitor] = None


def get_api_monitor(max_history: int = 10000) -> APIMonitor:
    """
    Get or create global API monitor instance

    Args:
        max_history: Maximum number of records to keep

    Returns:
        APIMonitor instance
    """
    global _api_monitor
    if _api_monitor is None:
        _api_monitor = APIMonitor(max_history=max_history)
    return _api_monitor
