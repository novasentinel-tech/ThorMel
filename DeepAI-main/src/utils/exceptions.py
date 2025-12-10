"""
Custom exceptions for DeepAI system.
"""


class DeepAIException(Exception):
    """Base exception for all DeepAI errors."""

    pass


class SecurityException(DeepAIException):
    """Raised when security policy is violated."""

    pass


class ValidationException(DeepAIException):
    """Raised when input validation fails."""

    pass


class DomainBlockedException(SecurityException):
    """Raised when attempting to scan a blocked domain."""

    pass


class RateLimitException(SecurityException):
    """Raised when rate limit is exceeded."""

    pass


class TimeoutException(DeepAIException):
    """Raised when operation exceeds timeout."""

    pass


class HoneypotDetectedException(SecurityException):
    """Raised when honeypot is detected during scanning."""

    pass


class DataCollectionException(DeepAIException):
    """Raised when data collection fails."""

    pass


class FeatureExtractionException(DeepAIException):
    """Raised when feature extraction fails."""

    pass


class ModelException(DeepAIException):
    """Raised when model prediction fails."""

    pass


class ExplainabilityException(DeepAIException):
    """Raised when explanation generation fails."""

    pass


class AuditLogException(SecurityException):
    """Raised when audit log integrity check fails."""

    pass


class AcademicModeViolationException(SecurityException):
    """Raised when academic mode rules are violated."""

    pass
