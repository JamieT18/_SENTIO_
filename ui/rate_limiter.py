"""
Rate Limiting for Sentio API
Provides rate limiting functionality to prevent API abuse
"""

from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import Request, HTTPException, status
from functools import wraps
import time
import asyncio

from ..core.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for API endpoints
    Tracks requests per user/IP and enforces configurable limits
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
        cleanup_interval: int = 3600,  # Clean up old entries every hour
    ):
        """
        Initialize rate limiter

        Args:
            requests_per_minute: Max requests per minute per user
            requests_per_hour: Max requests per hour per user
            requests_per_day: Max requests per day per user
            cleanup_interval: Interval in seconds to cleanup old entries
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.cleanup_interval = cleanup_interval

        # Storage for request tracking
        # Structure: {identifier: {timestamp: count}}
        self._minute_requests: Dict[str, Dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self._hour_requests: Dict[str, Dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self._day_requests: Dict[str, Dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        self._last_cleanup = time.time()

    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting
        Uses user_id from token if available, otherwise uses IP
        """
        # Try to get user_id from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        return f"ip:{client_ip}"

    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory bloat"""
        if time.time() - self._last_cleanup < self.cleanup_interval:
            return

        now = time.time()
        minute_cutoff = int(now // 60) - 2  # Keep last 2 minutes
        hour_cutoff = int(now // 3600) - 2  # Keep last 2 hours
        day_cutoff = int(now // 86400) - 2  # Keep last 2 days

        # Clean minute buckets
        for identifier in list(self._minute_requests.keys()):
            buckets = self._minute_requests[identifier]
            for bucket_time in list(buckets.keys()):
                if bucket_time < minute_cutoff:
                    del buckets[bucket_time]
            if not buckets:
                del self._minute_requests[identifier]

        # Clean hour buckets
        for identifier in list(self._hour_requests.keys()):
            buckets = self._hour_requests[identifier]
            for bucket_time in list(buckets.keys()):
                if bucket_time < hour_cutoff:
                    del buckets[bucket_time]
            if not buckets:
                del self._hour_requests[identifier]

        # Clean day buckets
        for identifier in list(self._day_requests.keys()):
            buckets = self._day_requests[identifier]
            for bucket_time in list(buckets.keys()):
                if bucket_time < day_cutoff:
                    del buckets[bucket_time]
            if not buckets:
                del self._day_requests[identifier]

        self._last_cleanup = now
        logger.debug("Rate limiter cleanup completed")

    def _check_limit(
        self,
        identifier: str,
        storage: Dict[str, Dict[int, int]],
        bucket_size: int,
        limit: int,
    ) -> tuple[bool, int, int]:
        """
        Check if request exceeds rate limit

        Returns:
            (is_allowed, current_count, limit)
        """
        now = time.time()
        current_bucket = int(now // bucket_size)

        # Count requests in current time window
        count = storage[identifier].get(current_bucket, 0)

        return count < limit, count, limit

    async def check_rate_limit(self, request: Request) -> Dict[str, any]:
        """
        Check if request is within rate limits

        Args:
            request: FastAPI Request object

        Returns:
            Dict with rate limit status

        Raises:
            HTTPException: If rate limit exceeded
        """
        self._cleanup_old_entries()

        identifier = self._get_identifier(request)
        now = time.time()

        # Check minute limit
        minute_allowed, minute_count, _ = self._check_limit(
            identifier, self._minute_requests, 60, self.requests_per_minute
        )

        # Check hour limit
        hour_allowed, hour_count, _ = self._check_limit(
            identifier, self._hour_requests, 3600, self.requests_per_hour
        )

        # Check day limit
        day_allowed, day_count, _ = self._check_limit(
            identifier, self._day_requests, 86400, self.requests_per_day
        )

        # Determine which limit was hit
        if not minute_allowed:
            retry_after = 60 - (now % 60)
            logger.warning(f"Rate limit exceeded for {identifier}: minute limit")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "requests per minute",
                    "retry_after": int(retry_after),
                },
                headers={"Retry-After": str(int(retry_after))},
            )

        if not hour_allowed:
            retry_after = 3600 - (now % 3600)
            logger.warning(f"Rate limit exceeded for {identifier}: hour limit")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "requests per hour",
                    "retry_after": int(retry_after),
                },
                headers={"Retry-After": str(int(retry_after))},
            )

        if not day_allowed:
            retry_after = 86400 - (now % 86400)
            logger.warning(f"Rate limit exceeded for {identifier}: day limit")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "requests per day",
                    "retry_after": int(retry_after),
                },
                headers={"Retry-After": str(int(retry_after))},
            )

        # Record this request
        minute_bucket = int(now // 60)
        hour_bucket = int(now // 3600)
        day_bucket = int(now // 86400)

        self._minute_requests[identifier][minute_bucket] += 1
        self._hour_requests[identifier][hour_bucket] += 1
        self._day_requests[identifier][day_bucket] += 1

        # Return rate limit info
        return {
            "identifier": identifier,
            "requests_minute": minute_count + 1,
            "limit_minute": self.requests_per_minute,
            "requests_hour": hour_count + 1,
            "limit_hour": self.requests_per_hour,
            "requests_day": day_count + 1,
            "limit_day": self.requests_per_day,
        }

    def get_usage_stats(self, identifier: str) -> Dict[str, any]:
        """
        Get current usage stats for an identifier

        Args:
            identifier: User or IP identifier

        Returns:
            Dict with usage statistics
        """
        now = time.time()
        minute_bucket = int(now // 60)
        hour_bucket = int(now // 3600)
        day_bucket = int(now // 86400)

        return {
            "identifier": identifier,
            "current_minute": self._minute_requests[identifier].get(minute_bucket, 0),
            "limit_minute": self.requests_per_minute,
            "current_hour": self._hour_requests[identifier].get(hour_bucket, 0),
            "limit_hour": self.requests_per_hour,
            "current_day": self._day_requests[identifier].get(day_bucket, 0),
            "limit_day": self.requests_per_day,
            "remaining_minute": self.requests_per_minute
            - self._minute_requests[identifier].get(minute_bucket, 0),
            "remaining_hour": self.requests_per_hour
            - self._hour_requests[identifier].get(hour_bucket, 0),
            "remaining_day": self.requests_per_day
            - self._day_requests[identifier].get(day_bucket, 0),
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    requests_per_day: int = 10000,
) -> RateLimiter:
    """
    Get or create global rate limiter instance

    Args:
        requests_per_minute: Max requests per minute
        requests_per_hour: Max requests per hour
        requests_per_day: Max requests per day

    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            requests_per_day=requests_per_day,
        )
    return _rate_limiter
