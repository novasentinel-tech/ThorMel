"""
Timeout management for scan operations.
Ensures no operation exceeds maximum allowed duration.
"""

import signal
from contextlib import contextmanager
from typing import Optional

from config.settings import settings
from config.logging_config import get_logger
from src.utils import TimeoutException

logger = get_logger(__name__)


class TimeoutException(Exception):
    """Raised when operation exceeds timeout."""

    pass


@contextmanager
def timeout_context(seconds: int, operation_name: str = "Operation"):
    """
    Context manager for enforcing operation timeout.

    Args:
        seconds: Timeout duration in seconds
        operation_name: Name of operation (for logging)

    Raises:
        TimeoutException: If operation exceeds timeout

    Usage:
        with timeout_context(10, "data_collection"):
            perform_slow_operation()
    """

    def timeout_handler(signum, frame):
        raise TimeoutException(
            f"{operation_name} timed out after {seconds} seconds"
        )

    # Set alarm signal
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)  # Disable alarm
        signal.signal(signal.SIGALRM, old_handler)


class TimeoutManager:
    """
    Manages timeouts for various scan operations.
    """

    def __init__(self):
        """Initialize timeout manager with configured limits."""
        from src.utils.constants import (
            TIMEOUT_HTTP,
            TIMEOUT_TLS,
            TIMEOUT_DNS,
            TIMEOUT_TOTAL_SCAN,
        )

        self.timeouts = {
            "http": TIMEOUT_HTTP,
            "tls": TIMEOUT_TLS,
            "dns": TIMEOUT_DNS,
            "total_scan": TIMEOUT_TOTAL_SCAN,
        }

    def get_timeout(self, operation: str) -> int:
        """
        Get timeout for specific operation.

        Args:
            operation: Operation type (http, tls, dns, total_scan)

        Returns:
            Timeout in seconds
        """
        return self.timeouts.get(operation, settings.max_scan_timeout)

    def enforce_scan_timeout(self):
        """
        Context manager to enforce total scan timeout.

        Usage:
            with timeout_manager.enforce_scan_timeout():
                perform_complete_scan()
        """
        timeout_seconds = self.get_timeout("total_scan")
        return timeout_context(timeout_seconds, "Complete scan")

    def enforce_http_timeout(self):
        """Context manager for HTTP operations."""
        timeout_seconds = self.get_timeout("http")
        return timeout_context(timeout_seconds, "HTTP operation")

    def enforce_tls_timeout(self):
        """Context manager for TLS operations."""
        timeout_seconds = self.get_timeout("tls")
        return timeout_context(timeout_seconds, "TLS inspection")

    def enforce_dns_timeout(self):
        """Context manager for DNS operations."""
        timeout_seconds = self.get_timeout("dns")
        return timeout_context(timeout_seconds, "DNS query")


# Global instance
timeout_manager = TimeoutManager()
