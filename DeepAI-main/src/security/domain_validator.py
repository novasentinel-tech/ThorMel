"""
Domain validator with security enforcement.
This module ensures only allowed domains are scanned.
"""

import re
from typing import Tuple
import ipaddress

from config.blocked_domains import (
    BLOCKED_TLDS,
    BLOCKED_KEYWORDS,
    WHITELISTED_DOMAINS,
    CRITICAL_INFRASTRUCTURE_DOMAINS,
)
from config.logging_config import get_logger
from src.utils import (
    ValidationException,
    DomainBlockedException,
    is_valid_domain_format,
    is_private_ip,
    normalize_domain,
)

logger = get_logger(__name__)


class DomainValidator:
    """
    Validates domains before scanning.
    Enforces security policy to prevent scanning critical/sensitive infrastructure.
    """

    def __init__(self):
        """Initialize domain validator with blacklists and whitelists."""
        self.blocked_tlds = BLOCKED_TLDS
        self.blocked_keywords = BLOCKED_KEYWORDS
        self.whitelist = WHITELISTED_DOMAINS
        self.critical_infra = CRITICAL_INFRASTRUCTURE_DOMAINS

    def validate(self, domain: str) -> Tuple[bool, str]:
        """
        Validate domain and return (is_valid, reason).

        Args:
            domain: Domain name or IP to validate

        Returns:
            Tuple of (is_valid, reason_or_error)
        """
        domain = normalize_domain(domain)

        # 1. Check whitelist first (override all other checks)
        if domain in self.whitelist:
            logger.info(f"Domain {domain} is whitelisted")
            return True, "Domain is whitelisted"

        # 2. Validate format
        if not is_valid_domain_format(domain):
            return False, "Invalid domain format"

        # 3. Check if private IP
        if is_private_ip(domain):
            return False, "Private/internal IP address"

        # 4. Check TLD blocklist
        for blocked_tld in self.blocked_tlds:
            if domain.endswith(blocked_tld):
                logger.warning(f"Domain {domain} blocked by TLD: {blocked_tld}")
                return False, f"Blocked TLD: {blocked_tld}"

        # 5. Check keyword blocklist (case-insensitive)
        domain_lower = domain.lower()
        for keyword in self.blocked_keywords:
            if keyword in domain_lower:
                logger.warning(f"Domain {domain} blocked by keyword: {keyword}")
                return False, f"Blocked keyword detected: {keyword}"

        # 6. Check critical infrastructure
        if self._is_critical_infrastructure(domain):
            logger.warning(f"Domain {domain} is critical infrastructure")
            return False, "Critical infrastructure (CISA list)"

        logger.info(f"Domain {domain} passed validation")
        return True, "Domain validated"

    def _is_critical_infrastructure(self, domain: str) -> bool:
        """Check if domain is in critical infrastructure list."""
        for critical_domain in self.critical_infra:
            if domain.endswith(critical_domain):
                return True
        return False

    def validate_strict(self, domain: str) -> None:
        """
        Validate domain and raise exception if invalid.

        Args:
            domain: Domain to validate

        Raises:
            ValidationException: If domain format is invalid
            DomainBlockedException: If domain is blocked
        """
        is_valid, reason = self.validate(domain)

        if not is_valid:
            if any(keyword in reason for keyword in ["Blocked", "Critical"]):
                logger.error(f"Blocking domain: {domain}. Reason: {reason}")
                raise DomainBlockedException(
                    f"Domain '{domain}' cannot be scanned: {reason}"
                )
            else:
                raise ValidationException(f"Domain validation failed: {reason}")


# Global instance
domain_validator = DomainValidator()
