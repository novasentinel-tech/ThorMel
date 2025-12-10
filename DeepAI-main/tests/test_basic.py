"""
Basic test suite to verify system integrity.
"""

import pytest
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSecurityEnforcement:
    """Tests for security enforcement."""
    
    def test_academic_mode_enabled(self):
        """Verify academic mode is enabled."""
        from config import settings
        assert settings.academic_mode == True, "Academic mode must be enabled"
    
    def test_domain_validator_blocks_gov(self):
        """Test that .gov domains are blocked."""
        from src.security import domain_validator
        is_valid, reason = domain_validator.validate("whitehouse.gov")
        assert is_valid == False, ".gov domains should be blocked"
    
    def test_domain_validator_allows_example(self):
        """Test that example.com is allowed."""
        from src.security import domain_validator
        is_valid, reason = domain_validator.validate("example.com")
        assert is_valid == True, "example.com should be allowed"
    
    def test_rate_limiter_exists(self):
        """Test rate limiter is initialized."""
        from src.security import rate_limiter
        assert rate_limiter is not None
        assert hasattr(rate_limiter, 'check_ip_limit')
    
    def test_audit_log_integrity(self):
        """Test audit log integrity checking."""
        from src.security import audit_log
        is_valid, msg = audit_log.verify_integrity()
        assert is_valid in [True, False], "Should return valid boolean"


class TestUtils:
    """Tests for utility functions."""
    
    def test_is_valid_domain_format(self):
        """Test domain format validation."""
        from src.utils import is_valid_domain_format
        assert is_valid_domain_format("example.com") == True
        assert is_valid_domain_format("sub.example.org") == True
        assert is_valid_domain_format("192.168.1.1") == True
        assert is_valid_domain_format("invalid..domain") == False
    
    def test_normalize_domain(self):
        """Test domain normalization."""
        from src.utils import normalize_domain
        assert normalize_domain("EXAMPLE.COM") == "example.com"
        assert normalize_domain(" example.com ") == "example.com"
    
    def test_calculate_gini(self):
        """Test Gini coefficient calculation."""
        from src.utils import calculate_gini_coefficient
        # Perfectly equal distribution
        gini = calculate_gini_coefficient([1, 1, 1, 1])
        assert gini < 0.1, "Equal dist should have low Gini"
        
        # Highly unequal distribution
        gini = calculate_gini_coefficient([1, 1, 1, 100])
        assert gini > 0.5, "Unequal dist should have high Gini"


class TestConfiguration:
    """Tests for configuration."""
    
    def test_settings_loaded(self):
        """Test settings are loaded."""
        from config import settings
        assert settings is not None
        assert settings.repo_root.exists()
        assert settings.data_dir.exists()
    
    def test_blocked_domains_defined(self):
        """Test blocked domains are defined."""
        from config import (
            BLOCKED_TLDS, 
            BLOCKED_KEYWORDS, 
            WHITELISTED_DOMAINS
        )
        assert len(BLOCKED_TLDS) > 0
        assert len(BLOCKED_KEYWORDS) > 0
        assert len(WHITELISTED_DOMAINS) > 0


class TestAcademicMode:
    """Tests for academic mode enforcement."""
    
    def test_academic_mode_enforcer_exists(self):
        """Test academic mode enforcer initialized."""
        from src.security import academic_mode
        assert academic_mode is not None
        summary = academic_mode.get_summary()
        assert "ACADEMIC" in summary["mode"]
    
    def test_forbidden_actions_blocked(self):
        """Test that forbidden actions are rejected."""
        from src.security import academic_mode
        from src.utils import AcademicModeViolationException
        
        with pytest.raises(AcademicModeViolationException):
            academic_mode.validate_action("exploit")
        
        with pytest.raises(AcademicModeViolationException):
            academic_mode.validate_action("bruteforce")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
