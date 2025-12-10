"""Initialize config package."""

from config.settings import settings
from config.logging_config import get_logger
from config.blocked_domains import (
    BLOCKED_TLDS,
    BLOCKED_KEYWORDS,
    WHITELISTED_DOMAINS,
    CRITICAL_INFRASTRUCTURE_DOMAINS,
)
from config.constants import COMMON_PORTS

__all__ = [
    "settings",
    "get_logger",
    "BLOCKED_TLDS",
    "BLOCKED_KEYWORDS",
    "WHITELISTED_DOMAINS",
    "CRITICAL_INFRASTRUCTURE_DOMAINS",
    "COMMON_PORTS",
]
