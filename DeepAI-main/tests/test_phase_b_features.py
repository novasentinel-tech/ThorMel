"""
Phase B Feature Engineering - Comprehensive test suite.
Tests feature extraction, normalization, validation, and anomaly detection.
"""

import unittest
import numpy as np
from src.features.feature_extractor import FeatureExtractor
from src.features.feature_normalizer import FeatureNormalizer
from src.features.feature_validator import FeatureValidator
from src.features.anomaly_detector import AnomalyDetector


class TestFeatureExtractor(unittest.TestCase):
    """Test feature extraction functionality."""

    def setUp(self):
        """Setup test fixtures."""
        self.extractor = FeatureExtractor()
        self.test_data = {
            "collectors": {
                "http": {
                    "status": "success",
                    "response_time_ms": 150,
                    "redirect_chain": [],
                    "security_headers": {"hsts": "max-age=31536000"},
                    "cookies": {},
                    "server": "Apache/2.4.41",
                    "honeypot_probability": 0.0,
                },
                "tls": {
                    "status": "success",
                    "protocol_version": "TLSv1.3",
                    "cipher_strength": 256,
                    "forward_secrecy": True,
                    "certificate": {"is_self_signed": False, "is_expired": False, "days_until_expiry": 365},
                    "vulnerabilities": [],
                    "supported_protocols": ["TLSv1.3", "TLSv1.2"],
                    "ocsp_stapling": True,
                    "sct_present": True,
                },
                "dns": {
                    "status": "success",
                    "dns_records": {"A": ["93.184.216.34"], "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"]},
                    "dnssec_enabled": True,
                    "security_records": {"spf": "v=spf1 ~all", "dmarc": "v=DMARC1", "caa": []},
                    "vulnerabilities": [],
                },
                "whois": {
                    "status": "success",
                    "days_until_expiry": 180,
                    "expiration_risk": "low",
                    "registrant_privacy": True,
                    "registrar": "VeriSign",
                    "technical_contact": "Yes",
                    "registrant_country": "US",
                    "registrant_organization": "Example Corp",
                    "name_servers": ["ns1.example.com", "ns2.example.com"],
                },
                "ports": {
                    "status": "success",
                    "open_ports": [22, 80, 443],
                    "services_detected": {
                        22: {"service_name": "SSH", "banner": "SSH-2.0", "fingerprint_match": True},
                        80: {"service_name": "HTTP", "banner": None, "fingerprint_match": False},
                        443: {"service_name": "HTTPS", "banner": None, "fingerprint_match": False},
                    },
                },
                "tech_stack": {
                    "status": "success",
                    "detected_technologies": ["Apache", "PHP"],
                    "potential_vulnerabilities": [],
                },
            }
        }

    def test_initialization(self):
        """Test extractor initialization."""
        self.assertEqual(len(self.extractor.feature_names), 87)
        self.assertEqual(self.extractor.TOTAL_FEATURES, 87)

    def test_extract_features(self):
        """Test feature extraction."""
        feature_vector, feature_dict = self.extractor.extract_features(self.test_data)

        self.assertEqual(len(feature_vector), 87)
        self.assertAlmostEqual(len(feature_dict), 87)

    def test_http_features(self):
        """Test HTTP feature extraction."""
        http_features = self.extractor._extract_http_features(self.test_data["collectors"]["http"])

        self.assertEqual(len(http_features), 15)
        self.assertIn("http_01_response_time", http_features)

    def test_tls_features(self):
        """Test TLS feature extraction."""
        tls_features = self.extractor._extract_tls_features(self.test_data["collectors"]["tls"])

        self.assertEqual(len(tls_features), 18)
        self.assertGreater(tls_features["tls_01_protocol_score"], 0)

    def test_dns_features(self):
        """Test DNS feature extraction."""
        dns_features = self.extractor._extract_dns_features(self.test_data["collectors"]["dns"])

        self.assertEqual(len(dns_features), 12)
        self.assertEqual(dns_features["dns_01_has_a_record"], 1.0)

    def test_feature_vector_shape(self):
        """Test feature vector shape."""
        feature_vector, _ = self.extractor.extract_features(self.test_data)

        self.assertEqual(feature_vector.shape, (87,))
        self.assertEqual(feature_vector.dtype, np.float32)

    def test_feature_names(self):
        """Test feature name generation."""
        names = self.extractor.feature_names

        self.assertEqual(len(names), 87)
        self.assertTrue(all(isinstance(n, str) for n in names))


class TestFeatureNormalizer(unittest.TestCase):
    """Test feature normalization."""

    def setUp(self):
        """Setup test fixtures."""
        self.X_train = np.random.randn(100, 87) * 10 + 50
        self.X_test = np.random.randn(20, 87) * 10 + 50

    def test_minmax_normalization(self):
        """Test Min-Max normalization."""
        normalizer = FeatureNormalizer(method="minmax")
        normalizer.fit(self.X_train)

        X_normalized = normalizer.transform(self.X_test)

        # Check bounds
        self.assertGreaterEqual(np.min(X_normalized), -0.01)  # Allow small numerical error
        self.assertLessEqual(np.max(X_normalized), 1.01)

    def test_standard_normalization(self):
        """Test StandardScaler normalization."""
        normalizer = FeatureNormalizer(method="standard")
        normalizer.fit(self.X_train)

        X_normalized = normalizer.transform(self.X_test)

        # Standardized data should have mean ~0 and std ~1
        self.assertAlmostEqual(np.mean(X_normalized), 0.0, places=1)
        self.assertAlmostEqual(np.std(X_normalized), 1.0, places=1)

    def test_fit_transform(self):
        """Test fit_transform chaining."""
        normalizer = FeatureNormalizer()

        X_transformed = normalizer.fit_transform(self.X_train)

        self.assertEqual(X_transformed.shape, self.X_train.shape)
        self.assertTrue(normalizer._is_fitted)

    def test_inverse_transform(self):
        """Test inverse transformation."""
        normalizer = FeatureNormalizer(method="minmax")
        normalizer.fit(self.X_train)

        X_normalized = normalizer.transform(self.X_test)
        X_reconstructed = normalizer.inverse_transform(X_normalized)

        np.testing.assert_array_almost_equal(X_reconstructed, self.X_test, decimal=5)


class TestFeatureValidator(unittest.TestCase):
    """Test feature validation."""

    def setUp(self):
        """Setup test fixtures."""
        self.valid_features = np.random.rand(87) * 0.5 + 0.25
        self.invalid_features = np.random.randn(87) * 100

    def test_valid_features(self):
        """Test valid feature detection."""
        validator = FeatureValidator()

        is_valid = validator.validate(self.valid_features)

        self.assertTrue(is_valid)

    def test_nan_detection(self):
        """Test NaN detection."""
        features_with_nan = self.valid_features.copy()
        features_with_nan[0] = np.nan

        validator = FeatureValidator()
        is_valid = validator.validate(features_with_nan)

        self.assertFalse(is_valid)
        self.assertGreater(len(validator.get_warnings()), 0)

    def test_inf_detection(self):
        """Test infinite value detection."""
        features_with_inf = self.valid_features.copy()
        features_with_inf[0] = np.inf

        validator = FeatureValidator()
        is_valid = validator.validate(features_with_inf)

        self.assertFalse(is_valid)

    def test_shape_validation(self):
        """Test shape validation."""
        wrong_shape = np.random.rand(100)

        validator = FeatureValidator()
        is_valid = validator.validate(wrong_shape)

        self.assertFalse(is_valid)

    def test_outlier_detection(self):
        """Test outlier detection."""
        features = np.random.randn(87) * 0.5
        features[0] = 10.0  # Extreme outlier

        validator = FeatureValidator()
        outliers = validator.detect_outliers(features)

        self.assertIn(0, outliers)

    def test_anomaly_detection_isolation_forest(self):
        """Test anomaly detection with IsolationForest."""
        validator = FeatureValidator()

        # Fit on normal data
        normal_data = np.random.randn(100, 87) * 0.5
        validator.validate_batch(normal_data)

        # Check anomaly
        anomaly_data = np.ones((1, 87)) * 10.0
        result = validator.detect_anomalies(anomaly_data)

        self.assertTrue(result["is_anomaly"])


class TestAnomalyDetector(unittest.TestCase):
    """Test anomaly detection."""

    def setUp(self):
        """Setup test fixtures."""
        self.normal_data = np.random.randn(100, 87) * 0.5 + 0.25
        self.detector = AnomalyDetector()
        self.detector.fit(self.normal_data)

    def test_zscore_detection(self):
        """Test Z-score anomaly detection."""
        # Create anomaly
        anomaly = np.ones((1, 87)) * 5.0

        is_anomaly = self.detector.detect_zscore(anomaly)

        self.assertTrue(np.any(is_anomaly))

    def test_iqr_detection(self):
        """Test IQR anomaly detection."""
        anomaly = np.ones((1, 87)) * 5.0

        is_anomaly = self.detector.detect_iqr(anomaly)

        self.assertTrue(np.any(is_anomaly))

    def test_ensemble_detection(self):
        """Test ensemble anomaly detection."""
        anomaly = np.ones((1, 87)) * 5.0

        results = self.detector.detect_ensemble(anomaly)

        self.assertIn("methods", results)
        self.assertGreater(len(results["methods"]), 0)

    def test_report_generation(self):
        """Test anomaly report generation."""
        test_data = np.random.randn(10, 87) * 0.5

        report = self.detector.get_anomaly_report(test_data)

        self.assertIn("total_samples", report)
        self.assertIn("feature_statistics", report)
        self.assertEqual(report["total_samples"], 10)


class TestIntegration(unittest.TestCase):
    """Integration tests for full feature pipeline."""

    def setUp(self):
        """Setup test fixtures."""
        self.extractor = FeatureExtractor()
        self.normalizer = FeatureNormalizer(method="minmax")
        self.validator = FeatureValidator()
        self.anomaly_detector = AnomalyDetector()

        # Create test data
        self.sample_data = {
            "collectors": {
                "http": {"status": "success", "response_time_ms": 100, "redirect_chain": [], "security_headers": {}, "cookies": {}, "server": "", "honeypot_probability": 0.0},
                "tls": {"status": "success", "protocol_version": "TLSv1.2", "cipher_strength": 128, "forward_secrecy": True, "certificate": {}, "vulnerabilities": [], "supported_protocols": []},
                "dns": {"status": "success", "dns_records": {}, "dnssec_enabled": False, "security_records": {}, "vulnerabilities": []},
                "whois": {"status": "success", "days_until_expiry": 180, "expiration_risk": "low"},
                "ports": {"status": "success", "open_ports": [], "services_detected": {}},
                "tech_stack": {"status": "success", "detected_technologies": [], "potential_vulnerabilities": []},
            }
        }

    def test_full_pipeline(self):
        """Test complete feature engineering pipeline."""
        # Extract
        feature_vector, feature_dict = self.extractor.extract_features(self.sample_data)
        self.assertEqual(len(feature_vector), 87)

        # Validate
        is_valid = self.validator.validate(feature_vector)
        self.assertTrue(is_valid)

        # Normalize (fit on batch)
        batch = np.vstack([feature_vector for _ in range(10)])
        self.normalizer.fit(batch)
        normalized = self.normalizer.transform(feature_vector.reshape(1, -1))
        self.assertLessEqual(np.max(normalized), 1.01)

        # Detect anomalies
        self.anomaly_detector.fit(batch)
        anomaly_result = self.anomaly_detector.detect_ensemble(feature_vector.reshape(1, -1))
        self.assertIn("methods", anomaly_result)


if __name__ == "__main__":
    unittest.main()
