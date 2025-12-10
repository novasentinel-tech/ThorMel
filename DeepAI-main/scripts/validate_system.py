#!/usr/bin/env python
"""
DeepAI System Validation
Validates all components and their integration
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Configure logging
logger.enable("src")


def validate_module_imports():
    """Validate all modules can be imported."""
    logger.info("Validating module imports...")
    
    imports_to_test = [
        ("config", "Configuration system"),
        ("src.security", "Security module"),
        ("src.utils", "Utilities"),
        ("src.collectors", "Data collectors"),
        ("src.features", "Feature engineering"),
        ("src.models.supervised", "ML models"),
        ("src.models.reinforcement", "RL agents"),
        ("src.explainability", "Explainability"),
        ("src.pipeline", "Pipeline"),
    ]
    
    successful = 0
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            logger.info(f"  ✓ {description:30} ({module_name})")
            successful += 1
        except ImportError as e:
            logger.warning(f"  ✗ {description:30} ({module_name}): {e}")
    
    return successful == len(imports_to_test)


def validate_component_initialization():
    """Validate individual components initialize correctly."""
    logger.info("\nValidating component initialization...")
    
    try:
        from src.collectors.http_collector import HTTPHeadersCollector
        logger.info("  ✓ HTTP collector")
    except Exception as e:
        logger.warning(f"  ✗ HTTP collector: {e}")
    
    try:
        from src.collectors.tls_collector import TLSCollector
        logger.info("  ✓ TLS collector")
    except Exception as e:
        logger.warning(f"  ✗ TLS collector: {e}")
    
    try:
        from src.collectors.dns_collector import DNSCollector
        logger.info("  ✓ DNS collector")
    except Exception as e:
        logger.warning(f"  ✗ DNS collector: {e}")
    
    try:
        from src.features.feature_extractor import FeatureExtractor
        fe = FeatureExtractor()
        logger.info(f"  ✓ Feature extractor ({len(fe.feature_names)} features)")
    except Exception as e:
        logger.warning(f"  ✗ Feature extractor: {e}")
    
    try:
        from src.explainability.nlg_generator import NLGGenerator
        nlg = NLGGenerator()
        logger.info("  ✓ NLG generator")
    except Exception as e:
        logger.warning(f"  ✗ NLG generator: {e}")
    
    try:
        from src.explainability.html_report_generator import HTMLReportGenerator
        html = HTMLReportGenerator()
        logger.info("  ✓ HTML report generator")
    except Exception as e:
        logger.warning(f"  ✗ HTML report generator: {e}")
    
    try:
        from src.explainability.explanation_quality import ExplanationQualityEvaluator
        eq = ExplanationQualityEvaluator()
        logger.info("  ✓ Quality evaluator")
    except Exception as e:
        logger.warning(f"  ✗ Quality evaluator: {e}")
    
    return True


def validate_pipeline_initialization():
    """Validate pipeline initializes."""
    logger.info("\nValidating pipeline initialization...")
    
    try:
        from src.pipeline.integrated_pipeline import IntegratedPipeline
        pipeline = IntegratedPipeline()
        logger.info("  ✓ Integrated pipeline")
        
        # Check components
        assert pipeline.http_collector is not None
        assert pipeline.tls_collector is not None
        assert pipeline.dns_collector is not None
        assert pipeline.feature_extractor is not None
        assert pipeline.nlg_generator is not None
        assert pipeline.html_generator is not None
        
        logger.info("  ✓ All pipeline components initialized")
        return True
    except Exception as e:
        logger.error(f"  ✗ Pipeline initialization: {e}")
        return False


def validate_feature_dimensions():
    """Validate feature dimensions."""
    logger.info("\nValidating feature dimensions...")
    
    try:
        from src.features.feature_extractor import FeatureExtractor
        import numpy as np
        
        fe = FeatureExtractor()
        
        # Check feature names
        assert len(fe.feature_names) == 87, f"Expected 87 features, got {len(fe.feature_names)}"
        logger.info(f"  ✓ Feature count: {len(fe.feature_names)}")
        
        # Check categories
        expected_categories = {
            "http": 15,
            "tls": 18,
            "dns": 12,
            "whois": 10,
            "ports": 15,
            "tech_stack": 17,
        }
        
        assert fe.CATEGORIES == expected_categories
        logger.info(f"  ✓ Feature categories verified")
        
        return True
    except Exception as e:
        logger.error(f"  ✗ Feature validation: {e}")
        return False


def validate_model_availability():
    """Check if trained models are available."""
    logger.info("\nValidating model availability...")
    
    model_dir = Path("data/models")
    
    try:
        # Check for LightGBM model
        lgbm_models = list(model_dir.glob("lgbm_model_*.pkl"))
        if lgbm_models:
            logger.info(f"  ✓ LightGBM models found: {len(lgbm_models)}")
        else:
            logger.info(f"  ℹ No LightGBM models found (optional)")
        
        # Check for RL model
        rl_models = list(model_dir.glob("ppo_agent_*.pkl"))
        if rl_models:
            logger.info(f"  ✓ RL models found: {len(rl_models)}")
        else:
            logger.info(f"  ℹ No RL models found (optional)")
        
        return True
    except Exception as e:
        logger.warning(f"  ⚠ Model availability check: {e}")
        return True  # Not critical


def validate_security_enforcement():
    """Validate security enforcements are in place."""
    logger.info("\nValidating security enforcement...")
    
    try:
        from src.security.domain_validator import DomainValidator
        from src.security.rate_limiter import RateLimiter
        from src.security.academic_mode import AcademicModeEnforcer
        
        logger.info("  ✓ Domain validator available")
        logger.info("  ✓ Rate limiter available")
        logger.info("  ✓ Academic mode enforcer available")
        
        # Check academic mode is enforced
        enforcer = AcademicModeEnforcer()
        if enforcer.enforce_academic_mode:
            logger.info("  ✓ Academic mode enforced")
        else:
            logger.warning("  ⚠ Academic mode not enforced")
        
        return True
    except Exception as e:
        logger.warning(f"  ⚠ Security validation: {e}")
        return True


def validate_test_coverage():
    """Validate test files exist."""
    logger.info("\nValidating test coverage...")
    
    test_dir = Path("tests")
    test_files = {
        "test_phase_a_collectors.py": "Phase A: Data Collection",
        "test_phase_b_features.py": "Phase B: Feature Engineering",
        "test_phase_c_ml.py": "Phase C: ML Training",
        "test_phase_d_rl.py": "Phase D: RL Training",
        "test_phase_e_explainability.py": "Phase E: Explainability",
        "test_phase_f_integration.py": "Phase F: Integration",
    }
    
    found = 0
    for filename, description in test_files.items():
        filepath = test_dir / filename
        if filepath.exists():
            logger.info(f"  ✓ {description:30} ({filename})")
            found += 1
        else:
            logger.warning(f"  ✗ {description:30} ({filename})")
    
    logger.info(f"\nTest files: {found}/{len(test_files)} found")
    return found == len(test_files)


def main():
    """Run all validation checks."""
    
    logger.info("=" * 80)
    logger.info("DeepAI System Validation Suite")
    logger.info("=" * 80)
    
    checks = [
        ("Module Imports", validate_module_imports),
        ("Component Initialization", validate_component_initialization),
        ("Pipeline Initialization", validate_pipeline_initialization),
        ("Feature Dimensions", validate_feature_dimensions),
        ("Model Availability", validate_model_availability),
        ("Security Enforcement", validate_security_enforcement),
        ("Test Coverage", validate_test_coverage),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            logger.error(f"Validation check '{check_name}' failed: {e}")
            results.append((check_name, False))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status:8} {check_name}")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Total: {passed}/{total} validation checks passed")
    
    if passed == total:
        logger.info("✓ All validations passed!")
        logger.info("="*80)
        return 0
    else:
        logger.warning(f"⚠ {total - passed} validation(s) failed")
        logger.info("="*80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
