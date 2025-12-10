"""Initialize security module."""

from src.security.domain_validator import domain_validator, DomainValidator
from src.security.rate_limiter import rate_limiter, RateLimiter
from src.security.timeout_manager import timeout_manager, TimeoutManager
from src.security.academic_mode import academic_mode, AcademicModeEnforcer
from src.security.audit_log import audit_log, ImmutableAuditLog

__all__ = [
    # Validators
    "domain_validator",
    "DomainValidator",
    # Rate limiting
    "rate_limiter",
    "RateLimiter",
    # Timeout management
    "timeout_manager",
    "TimeoutManager",
    # Academic mode enforcement
    "academic_mode",
    "AcademicModeEnforcer",
    # Audit logging
    "audit_log",
    "ImmutableAuditLog",
]
