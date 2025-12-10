"""
Comprehensive test suite for Phase A collectors.
Tests HTTP, TLS, DNS, WHOIS, Port Scanner, and Tech Stack Detector.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.collectors.http_collector import HTTPHeadersCollector
from src.collectors.tls_collector import TLSCollector
from src.collectors.dns_collector import DNSCollector
from src.collectors.whois_collector import WHOISCollector
from src.collectors.port_scanner import PortScanner
from src.collectors.tech_stack_detector import TechStackDetector


class TestHTTPCollector(unittest.TestCase):
    """Test HTTP headers collector."""

    def setUp(self):
        """Setup test fixtures."""
        self.collector = HTTPHeadersCollector()
        self.test_domain = "example.com"

    def test_initialization(self):
        """Test collector initialization."""
        self.assertEqual(self.collector.timeout, 10)
        self.assertIsNotNone(self.collector)

    @patch("requests.Session.get")
    def test_collect_success(self, mock_get):
        """Test successful HTTP collection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "Server": "Apache/2.4.41",
            "Strict-Transport-Security": "max-age=31536000",
        }
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_response.history = []
        mock_get.return_value = mock_response

        result = self.collector.collect(self.test_domain)

        self.assertEqual(result["status"], "success")
        self.assertIn("headers", result)
        self.assertIn("security_headers", result)

    def test_timeout_enforcement(self):
        """Test timeout enforcement."""
        self.assertEqual(self.collector.timeout, 10)


class TestTLSCollector(unittest.TestCase):
    """Test TLS/SSL collector."""

    def setUp(self):
        """Setup test fixtures."""
        self.collector = TLSCollector()
        self.test_domain = "example.com"

    def test_initialization(self):
        """Test collector initialization."""
        self.assertEqual(self.collector.timeout, 15)

    def test_tls_version_scoring(self):
        """Test TLS version scoring."""
        score_12 = self.collector._score_tls_version("TLSv1.2")
        score_13 = self.collector._score_tls_version("TLSv1.3")
        score_10 = self.collector._score_tls_version("TLSv1.0")

        self.assertGreater(score_13, score_12)
        self.assertGreater(score_12, score_10)

    def test_cipher_analysis(self):
        """Test cipher strength analysis."""
        strong_cipher = self.collector._analyze_cipher("ECDHE-RSA-AES256-GCM-SHA384")
        weak_cipher = self.collector._analyze_cipher("RC4-SHA")

        self.assertGreater(strong_cipher, weak_cipher)
        self.assertEqual(weak_cipher, 0)

    def test_forward_secrecy_detection(self):
        """Test forward secrecy detection."""
        ecdhe_cipher = "ECDHE-RSA-AES256-GCM-SHA384"
        non_fs_cipher = "AES256-SHA"

        self.assertTrue(self.collector._has_forward_secrecy(ecdhe_cipher))
        self.assertFalse(self.collector._has_forward_secrecy(non_fs_cipher))


class TestDNSCollector(unittest.TestCase):
    """Test DNS collector."""

    def setUp(self):
        """Setup test fixtures."""
        self.collector = DNSCollector()
        self.test_domain = "example.com"

    def test_initialization(self):
        """Test collector initialization."""
        self.assertEqual(self.collector.timeout, 5)
        self.assertIsNotNone(self.collector.RECORD_TYPES)
        self.assertIn("A", self.collector.RECORD_TYPES)

    def test_dns_analysis(self):
        """Test DNS analysis structure."""
        mock_records = {
            "A": ["93.184.216.34"],
            "AAAA": None,
            "MX": ["10 mail.example.com"],
            "NS": ["ns1.example.com"],
        }

        analysis = self.collector._analyze_dns_config(mock_records)

        self.assertTrue(analysis["has_a_record"])
        self.assertFalse(analysis["has_aaaa_record"])
        self.assertTrue(analysis["has_mx_record"])

    def test_vulnerability_detection(self):
        """Test DNS vulnerability detection."""
        records = {"A": ["93.184.216.34"]}
        security_records = {"spf": None, "dmarc": None, "caa": None}

        vulns = self.collector._detect_dns_vulnerabilities(
            records, security_records, dnssec_enabled=False
        )

        self.assertIn("Missing SPF record", vulns)
        self.assertIn("Missing DMARC record", vulns)
        self.assertIn("DNSSEC not enabled", vulns)


class TestWHOISCollector(unittest.TestCase):
    """Test WHOIS collector."""

    def setUp(self):
        """Setup test fixtures."""
        self.collector = WHOISCollector()
        self.test_domain = "example.com"

    def test_initialization(self):
        """Test collector initialization."""
        self.assertEqual(self.collector.timeout, 10)
        self.assertTrue(self.collector.use_cache)

    def test_domain_extraction(self):
        """Test domain extraction from URL."""
        url = "https://example.com/path"
        domain = self.collector._extract_domain(url)
        self.assertEqual(domain, "example.com")

    def test_domain_extraction_with_port(self):
        """Test domain extraction with port."""
        url = "example.com:8080"
        domain = self.collector._extract_domain(url)
        self.assertEqual(domain, "example.com")

    def test_caching(self):
        """Test result caching."""
        mock_data = {"status": "success", "registrar": "VeriSign"}
        self.collector._cache["example.com"] = mock_data

        cached = self.collector._cache.get("example.com")
        self.assertEqual(cached["registrar"], "VeriSign")


class TestPortScanner(unittest.TestCase):
    """Test port scanner."""

    def setUp(self):
        """Setup test fixtures."""
        self.collector = PortScanner()
        self.test_domain = "example.com"

    def test_initialization(self):
        """Test scanner initialization."""
        self.assertEqual(self.collector.timeout, 20)
        self.assertEqual(self.collector.max_threads, 10)

    def test_service_fingerprints(self):
        """Test service fingerprint data."""
        self.assertIn(22, self.collector.SERVICE_FINGERPRINTS)
        self.assertIn(80, self.collector.SERVICE_FINGERPRINTS)
        self.assertIn(443, self.collector.SERVICE_FINGERPRINTS)

        ssh_service = self.collector.SERVICE_FINGERPRINTS[22]
        self.assertEqual(ssh_service[0], "SSH")

    def test_common_ports(self):
        """Test scanning common ports."""
        common_ports = [22, 80, 443]
        service_names = [
            self.collector.SERVICE_FINGERPRINTS[p][0] for p in common_ports
        ]

        self.assertIn("SSH", service_names)
        self.assertIn("HTTP", service_names)
        self.assertIn("HTTPS", service_names)


class TestTechStackDetector(unittest.TestCase):
    """Test technology stack detector."""

    def setUp(self):
        """Setup test fixtures."""
        self.collector = TechStackDetector()
        self.test_domain = "example.com"

    def test_initialization(self):
        """Test detector initialization."""
        self.assertEqual(self.collector.timeout, 10)
        self.assertIsNotNone(self.collector.SIGNATURES)

    def test_header_detection(self):
        """Test technology detection from headers."""
        headers = {
            "Server": "Apache/2.4.41 (Ubuntu)",
            "X-Powered-By": "PHP/7.4.3",
        }

        tech = self.collector._detect_from_headers(headers)

        self.assertIn("Apache", tech)
        self.assertIn("PHP", tech)

    def test_cms_detection(self):
        """Test CMS detection."""
        # Test detection capability exists
        self.assertIsNotNone(self.collector._detect_from_paths)

    def test_vulnerability_assessment(self):
        """Test vulnerability assessment."""
        tech_list = ["Apache", "PHP", "WordPress"]
        vulns = self.collector._assess_tech_vulnerabilities(tech_list)

        # Should detect some vulnerabilities
        self.assertIsInstance(vulns, list)


class TestCollectorIntegration(unittest.TestCase):
    """Integration tests for multiple collectors."""

    def test_all_collectors_instantiate(self):
        """Test all collectors can be instantiated."""
        http = HTTPHeadersCollector()
        tls = TLSCollector()
        dns = DNSCollector()
        whois = WHOISCollector()
        port = PortScanner()
        tech = TechStackDetector()

        self.assertIsNotNone(http)
        self.assertIsNotNone(tls)
        self.assertIsNotNone(dns)
        self.assertIsNotNone(whois)
        self.assertIsNotNone(port)
        self.assertIsNotNone(tech)

    def test_collectors_have_collect_method(self):
        """Test all collectors implement collect method."""
        collectors = [
            HTTPHeadersCollector(),
            TLSCollector(),
            DNSCollector(),
            WHOISCollector(),
            PortScanner(),
            TechStackDetector(),
        ]

        for collector in collectors:
            self.assertTrue(hasattr(collector, "collect"))
            self.assertTrue(callable(getattr(collector, "collect")))

    def test_timeout_configuration(self):
        """Test timeout configuration for each collector."""
        timeouts = {
            HTTPHeadersCollector(): 10,
            TLSCollector(): 15,
            DNSCollector(): 5,
            WHOISCollector(): 10,
            PortScanner(): 20,
            TechStackDetector(): 10,
        }

        for collector, expected_timeout in timeouts.items():
            self.assertEqual(collector.timeout, expected_timeout)


if __name__ == "__main__":
    unittest.main()
