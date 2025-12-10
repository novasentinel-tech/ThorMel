"""
Rate limiting implementation.
Prevents abuse and excessive scanning.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Tuple

from config.settings import settings
from config.logging_config import get_logger
from src.utils import RateLimitException

logger = get_logger(__name__)


class RateLimiter:
    """
    Rate limiter for IP addresses and target domains.
    Uses in-memory storage (use Redis for production).
    """

    def __init__(self):
        """Initialize rate limiter with configured limits."""
        self.ip_requests = defaultdict(list)
        self.target_requests = defaultdict(list)

        # Load limits from settings
        self.ip_limits = {
            "per_minute": settings.rate_limit_per_minute,
            "per_hour": settings.rate_limit_per_hour,
            "per_day": settings.rate_limit_per_day,
        }

        self.target_limits = {
            "per_hour": settings.rate_limit_target_per_hour,
            "per_day": 5,
        }

    def check_ip_limit(self, ip_address: str) -> Tuple[bool, str]:
        """
        Check if IP has exceeded rate limits.

        Args:
            ip_address: Client IP address

        Returns:
            Tuple of (is_allowed, reason)
        """
        now = datetime.now()

        # Clean old requests
        self.ip_requests[ip_address] = [
            req_time
            for req_time in self.ip_requests[ip_address]
            if now - req_time < timedelta(days=1)
        ]

        requests = self.ip_requests[ip_address]

        # Count by time window
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        requests_last_minute = sum(1 for t in requests if t > minute_ago)
        requests_last_hour = sum(1 for t in requests if t > hour_ago)
        requests_last_day = len(requests)

        # Check limits
        if requests_last_minute >= self.ip_limits["per_minute"]:
            logger.warning(f"IP rate limit (per minute) exceeded: {ip_address}")
            return False, "Rate limit exceeded: too many requests per minute"

        if requests_last_hour >= self.ip_limits["per_hour"]:
            logger.warning(f"IP rate limit (per hour) exceeded: {ip_address}")
            return False, "Rate limit exceeded: too many requests per hour"

        if requests_last_day >= self.ip_limits["per_day"]:
            logger.warning(f"IP rate limit (per day) exceeded: {ip_address}")
            return False, "Rate limit exceeded: daily limit reached"

        # Record request
        self.ip_requests[ip_address].append(now)
        return True, "IP rate limit OK"

    def check_target_limit(self, target_domain: str) -> Tuple[bool, str]:
        """
        Check if target domain has been scanned too recently.

        Args:
            target_domain: Target domain to scan

        Returns:
            Tuple of (is_allowed, reason)
        """
        now = datetime.now()

        # Clean old requests
        self.target_requests[target_domain] = [
            req_time
            for req_time in self.target_requests[target_domain]
            if now - req_time < timedelta(days=1)
        ]

        requests = self.target_requests[target_domain]

        # Count by time window
        hour_ago = now - timedelta(hours=1)

        requests_last_hour = sum(1 for t in requests if t > hour_ago)
        requests_last_day = len(requests)

        # Check limits
        if requests_last_hour >= self.target_limits["per_hour"]:
            logger.warning(f"Target rate limit (per hour) exceeded: {target_domain}")
            return False, f"Target recently scanned: {target_domain}"

        if requests_last_day >= self.target_limits["per_day"]:
            logger.warning(f"Target rate limit (per day) exceeded: {target_domain}")
            return False, f"Target daily limit reached: {target_domain}"

        # Record request
        self.target_requests[target_domain].append(now)
        return True, "Target rate limit OK"

    def check_all_limits(self, ip_address: str, target_domain: str) -> Tuple[bool, str]:
        """
        Check both IP and target limits.

        Args:
            ip_address: Client IP
            target_domain: Target domain

        Returns:
            Tuple of (is_allowed, reason)
        """
        # Check IP limit first
        ip_allowed, ip_reason = self.check_ip_limit(ip_address)
        if not ip_allowed and settings.enforce_rate_limits:
            return False, ip_reason

        # Check target limit
        target_allowed, target_reason = self.check_target_limit(target_domain)
        if not target_allowed and settings.enforce_rate_limits:
            return False, target_reason

        return True, "All rate limits OK"

    def check_and_raise(self, ip_address: str, target_domain: str) -> None:
        """
        Check limits and raise exception if exceeded.

        Args:
            ip_address: Client IP
            target_domain: Target domain

        Raises:
            RateLimitException: If any limit is exceeded
        """
        allowed, reason = self.check_all_limits(ip_address, target_domain)

        if not allowed:
            logger.error(f"Rate limit check failed for {ip_address} -> {target_domain}")
            raise RateLimitException(reason)


# Global instance
rate_limiter = RateLimiter()
