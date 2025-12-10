"""
DeepAI - AI-Powered Vulnerability Analysis System
Academic research system for cybersecurity vulnerability analysis.

OPERATIONAL CONSTRAINTS:
- MANDATORY academic mode (passive observation only)
- NO exploitation of vulnerabilities
- NO unauthorized access
- FULL audit trail maintained
- Rate limiting enforced
- Timeout enforcement active

USE ONLY:
- For authorized security testing
- On systems you own or have explicit permission
- For academic research and education
- In compliance with all applicable laws
"""

__version__ = "1.0.0"
__author__ = "NovaS Sentinel Tech"
__license__ = "Apache 2.0"

# Ensure config loads first (includes academic mode validation)
from config import settings, get_logger
from config import BLOCKED_TLDS, BLOCKED_KEYWORDS, WHITELISTED_DOMAINS

# Security enforcement (cannot be bypassed)
from src.security import (
    domain_validator,
    rate_limiter,
    timeout_manager,
    academic_mode,
    audit_log,
)

# Main system components (implemented later)
# from src.collectors import BaseCollector
# from src.features import FeatureExtractor
# from src.models.supervised import LightGBMClassifier
# from src.models.reinforcement import PPOAgent
# from src.explainability import SHAPExplainer, NLGGenerator
# from src.pipeline import ScanPipeline

__all__ = [
    # Core
    "settings",
    "get_logger",
    # Security
    "domain_validator",
    "rate_limiter",
    "timeout_manager",
    "academic_mode",
    "audit_log",
    # Configuration
    "BLOCKED_TLDS",
    "BLOCKED_KEYWORDS",
    "WHITELISTED_DOMAINS",
]

logger = get_logger(__name__)
logger.info(f"DeepAI v{__version__} initialized - Academic mode ACTIVE")
