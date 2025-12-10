"""
Academic mode enforcer.
Ensures system operates ONLY in passive, non-exploitative mode.
This is mandatory and cannot be disabled.
"""

from config.settings import settings
from config.logging_config import get_logger
from src.utils import AcademicModeViolationException

logger = get_logger(__name__)


class AcademicModeEnforcer:
    """
    Enforces academic mode constraints.
    System can ONLY perform passive observation.
    """

    # Allowed (passive) actions
    ALLOWED_ACTIONS = {
        "passive_scan",
        "header_collection",
        "tls_inspection",
        "dns_query",
        "whois_lookup",
        "banner_grab",
        "robots_txt_check",
        "dns_analysis",
        "ip_reputation_check",
        "technology_detection",
    }

    # Forbidden (active/exploitative) actions
    FORBIDDEN_ACTIONS = {
        "exploit",
        "bruteforce",
        "password_attempt",
        "dos",
        "ddos",
        "sql_injection",
        "xss_test",
        "csrf_test",
        "directory_traversal",
        "command_injection",
        "deserialization_attack",
        "active_scan",
        "vulnerability_exploitation",
        "payload_injection",
        "reverse_shell",
        "privilege_escalation",
        "code_execution",
        "data_exfiltration",
    }

    def __init__(self):
        """Initialize enforcer (validates academic mode is enabled)."""
        settings.validate_academic_mode()
        logger.info("Academic mode enforcer initialized - System is in PASSIVE mode only")

    def validate_action(self, action: str) -> None:
        """
        Validate if action is allowed in academic mode.

        Args:
            action: Action to validate

        Raises:
            AcademicModeViolationException: If action is forbidden
        """
        action = action.lower().strip()

        # Check if explicitly forbidden
        if action in self.FORBIDDEN_ACTIONS:
            error_msg = (
                f"Action '{action}' is FORBIDDEN in academic mode. "
                f"System operates in strict passive mode only. "
                f"No active exploitation is permitted."
            )
            logger.critical(error_msg)
            raise AcademicModeViolationException(error_msg)

        # Warn if not in allowed list
        if action not in self.ALLOWED_ACTIONS:
            logger.warning(f"Action '{action}' not in approved list")

    def validate_payload(self, payload: str, context: str = "") -> None:
        """
        Validate that payload doesn't contain exploitative code.

        Args:
            payload: Payload to validate
            context: Context for error message

        Raises:
            AcademicModeViolationException: If payload appears exploitative
        """
        dangerous_patterns = [
            "eval(",
            "exec(",
            "system(",
            "shell_exec(",
            "passthru(",
            "system();",
            "/bin/sh",
            "/bin/bash",
            "nc -l",  # netcat listener
            "wget http",  # downloading malware
            "curl | bash",  # piping to bash
            "DROP TABLE",  # SQL injection
            "'OR'1'='1",  # SQL injection
            "<script>",  # XSS
            "onclick=",  # XSS event handler
        ]

        payload_lower = payload.lower()

        for pattern in dangerous_patterns:
            if pattern.lower() in payload_lower:
                error_msg = (
                    f"Dangerous pattern '{pattern}' detected in {context}. "
                    f"This violates academic mode rules."
                )
                logger.critical(error_msg)
                raise AcademicModeViolationException(error_msg)

    def get_summary(self) -> dict:
        """Get summary of academic mode constraints."""
        return {
            "mode": "ACADEMIC (Passive Observation Only)",
            "enforcement": "MANDATORY and UNBYPASSABLE",
            "allowed_actions_count": len(self.ALLOWED_ACTIONS),
            "forbidden_actions_count": len(self.FORBIDDEN_ACTIONS),
            "key_rules": [
                "No exploitation of vulnerabilities",
                "No active scanning or fuzzing",
                "No payload injection",
                "No bruteforce attempts",
                "No DoS/DDoS",
                "Passive information gathering only",
                "Respect rate limits and timeouts",
                "Full audit trail required",
            ],
        }


# Global instance (enforces academic mode immediately on import)
academic_mode = AcademicModeEnforcer()
