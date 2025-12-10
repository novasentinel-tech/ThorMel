#!/usr/bin/env python3
"""
Security audit verification script.
Checks system integrity and security enforcement.
"""

import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import get_logger
from src.security import (
    domain_validator,
    rate_limiter,
    timeout_manager,
    academic_mode,
    audit_log,
)

logger = get_logger(__name__)


def check_domain_blocking():
    """Verify domain blacklist is functional."""
    print("\n[CHECK] Domain Blocking")
    print("-" * 60)
    
    test_cases = [
        ("whitehouse.gov", False, ".gov blocking"),
        ("fbi.gov", False, ".gov blocking"),
        ("example.com", True, "example.com whitelisted"),
        ("test.com", True, "test.com whitelisted"),
    ]
    
    for domain, should_pass, description in test_cases:
        is_valid, reason = domain_validator.validate(domain)
        status = "✓ PASS" if is_valid == should_pass else "✗ FAIL"
        print(f"  {status}: {description}")
        print(f"         Domain: {domain}")
        print(f"         Result: {reason}\n")


def check_rate_limiting():
    """Verify rate limiting is enforced."""
    print("\n[CHECK] Rate Limiting")
    print("-" * 60)
    
    print("  Testing IP rate limits...")
    ip = "203.0.113.42"
    
    # First 5 should pass
    for i in range(5):
        allowed, reason = rate_limiter.check_ip_limit(ip)
        print(f"    Request {i+1}: {'✓ PASS' if allowed else '✗ FAIL'}")
    
    # 6th should fail (per-minute limit)
    allowed, reason = rate_limiter.check_ip_limit(ip)
    print(f"    Request 6 (should fail): {'✓ PASS' if not allowed else '✗ FAIL'}")
    print(f"    Reason: {reason}")


def check_academic_mode():
    """Verify academic mode enforcement."""
    print("\n[CHECK] Academic Mode Enforcement")
    print("-" * 60)
    
    from src.utils import AcademicModeViolationException
    
    # Test forbidden action
    try:
        academic_mode.validate_action("exploit")
        print("  ✗ FAIL: Should have blocked 'exploit' action")
    except AcademicModeViolationException:
        print("  ✓ PASS: 'exploit' action blocked")
    
    # Test allowed action
    try:
        academic_mode.validate_action("passive_scan")
        print("  ✓ PASS: 'passive_scan' action allowed")
    except AcademicModeViolationException:
        print("  ✗ FAIL: 'passive_scan' should be allowed")
    
    # Print summary
    summary = academic_mode.get_summary()
    print(f"\n  Mode: {summary['mode']}")
    print(f"  Enforcement: {summary['enforcement']}")
    print(f"  Allowed actions: {summary['allowed_actions_count']}")
    print(f"  Forbidden actions: {summary['forbidden_actions_count']}")


def check_audit_log():
    """Verify audit log integrity."""
    print("\n[CHECK] Audit Log Integrity")
    print("-" * 60)
    
    # Verify integrity
    is_valid, message = audit_log.verify_integrity()
    status = "✓ PASS" if is_valid else "✗ FAIL"
    print(f"  {status}: {message}")
    
    # Test logging
    event_id = audit_log.log_event(
        event_type="security_check",
        details={"check": "audit_log_verification"}
    )
    print(f"  ✓ Event logged with ID: {event_id}")
    
    # Verify again
    is_valid, message = audit_log.verify_integrity()
    status = "✓ PASS" if is_valid else "✗ FAIL"
    print(f"  {status}: {message} (after logging)")


def check_timeout_management():
    """Verify timeout configuration."""
    print("\n[CHECK] Timeout Management")
    print("-" * 60)
    
    timeouts = {
        "http": timeout_manager.get_timeout("http"),
        "tls": timeout_manager.get_timeout("tls"),
        "dns": timeout_manager.get_timeout("dns"),
        "total_scan": timeout_manager.get_timeout("total_scan"),
    }
    
    for op, timeout in timeouts.items():
        within_limit = timeout <= 60 if op == "total_scan" else timeout <= 20
        status = "✓ PASS" if within_limit else "✗ FAIL"
        print(f"  {status}: {op}: {timeout}s")


def run_all_checks():
    """Run all security checks."""
    print("\n" + "="*60)
    print("DeepAI SECURITY AUDIT VERIFICATION")
    print("="*60)
    
    try:
        check_domain_blocking()
        check_rate_limiting()
        check_academic_mode()
        check_audit_log()
        check_timeout_management()
        
        print("\n" + "="*60)
        print("AUDIT COMPLETE")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        print(f"\n✗ CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_checks()
