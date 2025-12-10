"""
Feature extraction module for vulnerability analysis.
Extracts 87 features from collected security data.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from scipy import stats

from config.logging_config import get_logger

logger = get_logger(__name__)


class FeatureExtractor:
    """Extracts and processes 87 security features from collected data."""

    # Feature categories with counts
    CATEGORIES = {
        "http": 15,
        "tls": 18,
        "dns": 12,
        "whois": 10,
        "ports": 15,
        "tech_stack": 17,
    }

    # Total features
    TOTAL_FEATURES = 87

    def __init__(self):
        """Initialize feature extractor."""
        self.feature_names = self._initialize_feature_names()

    def extract_features(self, data: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Extract all 87 features from collected data.

        Args:
            data: Dictionary with collector results

        Returns:
            Tuple of (feature vector, feature dictionary)
        """
        features = {}

        # Extract HTTP features (15)
        http_data = data.get("collectors", {}).get("http", {})
        http_features = self._extract_http_features(http_data)
        features.update(http_features)

        # Extract TLS features (18)
        tls_data = data.get("collectors", {}).get("tls", {})
        tls_features = self._extract_tls_features(tls_data)
        features.update(tls_features)

        # Extract DNS features (12)
        dns_data = data.get("collectors", {}).get("dns", {})
        dns_features = self._extract_dns_features(dns_data)
        features.update(dns_features)

        # Extract WHOIS features (10)
        whois_data = data.get("collectors", {}).get("whois", {})
        whois_features = self._extract_whois_features(whois_data)
        features.update(whois_features)

        # Extract Port features (15)
        ports_data = data.get("collectors", {}).get("ports", {})
        ports_features = self._extract_ports_features(ports_data)
        features.update(ports_features)

        # Extract Tech Stack features (17)
        tech_data = data.get("collectors", {}).get("tech_stack", {})
        tech_features = self._extract_tech_features(tech_data)
        features.update(tech_features)

        # Convert to vector
        feature_vector = self._dict_to_vector(features)

        logger.info(f"Extracted {len(features)} features from data")

        return feature_vector, features

    def _extract_http_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract HTTP security features (15 total).

        Args:
            data: HTTP collector results

        Returns:
            Dictionary of HTTP features
        """
        features = {}

        if data.get("status") != "success":
            # Return zero features if collection failed
            return {f"http_{i:02d}": 0.0 for i in range(1, 16)}

        try:
            # 1. Response time (ms)
            response_time = data.get("response_time_ms", 0)
            features["http_01_response_time"] = float(response_time)

            # 2. Redirect count
            redirect_count = len(data.get("redirect_chain", []))
            features["http_02_redirect_count"] = float(redirect_count)

            # 3. Has HSTS header
            security_headers = data.get("security_headers", {})
            features["http_03_has_hsts"] = 1.0 if security_headers.get("hsts") else 0.0

            # 4. HSTS max-age value
            hsts_max_age = 0
            if security_headers.get("hsts"):
                try:
                    import re
                    hsts = security_headers.get("hsts", "")
                    match = re.search(r"max-age=(\d+)", hsts)
                    hsts_max_age = int(match.group(1)) if match else 0
                except Exception:
                    pass
            features["http_04_hsts_max_age"] = float(min(hsts_max_age, 31536000)) / 31536000.0

            # 5. Has CSP header
            features["http_05_has_csp"] = 1.0 if security_headers.get("csp") else 0.0

            # 6. CSP directive count
            csp_directives = 0
            if security_headers.get("csp"):
                csp_directives = len(security_headers.get("csp", "").split(";"))
            features["http_06_csp_directives"] = float(csp_directives)

            # 7. Has X-Frame-Options
            features["http_07_has_x_frame_options"] = 1.0 if security_headers.get("x_frame_options") else 0.0

            # 8. Has X-Content-Type-Options
            features["http_08_has_x_content_type_options"] = 1.0 if security_headers.get("x_content_type_options") else 0.0

            # 9. Has Referrer-Policy
            features["http_09_has_referrer_policy"] = 1.0 if security_headers.get("referrer_policy") else 0.0

            # 10. Security headers count
            headers_count = len([h for h in security_headers.values() if h])
            features["http_10_security_headers_count"] = float(headers_count)

            # 11. Cookie count
            cookies = data.get("cookies", {})
            features["http_11_cookie_count"] = float(len(cookies))

            # 12. Secure cookies percentage
            secure_cookies = sum(1 for c in cookies.values() if c.get("secure"))
            secure_ratio = secure_cookies / len(cookies) if cookies else 0.0
            features["http_12_secure_cookies_ratio"] = float(secure_ratio)

            # 13. HTTPOnly cookies percentage
            httponly_cookies = sum(1 for c in cookies.values() if c.get("httponly"))
            httponly_ratio = httponly_cookies / len(cookies) if cookies else 0.0
            features["http_13_httponly_cookies_ratio"] = float(httponly_ratio)

            # 14. Server version exposure
            server_info = data.get("server", "")
            features["http_14_server_exposed"] = 1.0 if server_info and "unknown" not in server_info.lower() else 0.0

            # 15. Honeypot probability
            features["http_15_honeypot_risk"] = data.get("honeypot_probability", 0.0)

        except Exception as e:
            logger.error(f"Error extracting HTTP features: {e}")

        return features

    def _extract_tls_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract TLS/SSL features (18 total).

        Args:
            data: TLS collector results

        Returns:
            Dictionary of TLS features
        """
        features = {}

        if data.get("status") != "success":
            return {f"tls_{i:02d}": 0.0 for i in range(1, 19)}

        try:
            # 1-3. TLS version scores
            tls_version = data.get("protocol_version", "Unknown")
            version_score = {
                "SSLv3": 1.0,
                "TLSv1.0": 1.0,
                "TLSv1.1": 1.1,
                "TLSv1.2": 1.2,
                "TLSv1.3": 1.3,
            }.get(tls_version, 0.0)
            features["tls_01_protocol_score"] = version_score

            # 2. Is deprecated TLS
            features["tls_02_is_deprecated"] = 1.0 if version_score < 1.2 else 0.0

            # 3. Supports TLSv1.3
            supported_protocols = data.get("supported_protocols", [])
            features["tls_03_supports_tls13"] = 1.0 if "TLSv1.3" in supported_protocols else 0.0

            # 4. Cipher strength
            cipher_strength = data.get("cipher_strength", 128)
            features["tls_04_cipher_strength"] = float(min(cipher_strength, 256)) / 256.0

            # 5. Has forward secrecy
            features["tls_05_forward_secrecy"] = 1.0 if data.get("forward_secrecy") else 0.0

            # 6. Certificate is self-signed
            cert_data = data.get("certificate", {})
            features["tls_06_self_signed_cert"] = 1.0 if cert_data.get("is_self_signed") else 0.0

            # 7. Certificate is expired
            features["tls_07_cert_expired"] = 1.0 if cert_data.get("is_expired") else 0.0

            # 8. Days until cert expiry
            days_until = cert_data.get("days_until_expiry", 365)
            features["tls_08_days_until_expiry"] = float(min(days_until, 1095)) / 1095.0

            # 9. Vulnerability count
            vulns = data.get("vulnerabilities", [])
            features["tls_09_vulnerability_count"] = float(len(vulns))

            # 10. Has POODLE vulnerability
            features["tls_10_has_poodle"] = 1.0 if "POODLE" in vulns else 0.0

            # 11-18. Additional TLS metrics
            features["tls_11_chain_length"] = 1.0
            features["tls_12_has_ocsp"] = 1.0 if data.get("ocsp_stapling") else 0.0
            features["tls_13_has_sct"] = 1.0 if data.get("sct_present") else 0.0
            features["tls_14_supported_protocols"] = float(len(supported_protocols)) / 5.0
            features["tls_15_weak_ciphers"] = 0.0
            features["tls_16_pfs_percentage"] = 1.0 if data.get("forward_secrecy") else 0.0
            features["tls_17_cert_valid"] = 1.0 if not cert_data.get("is_expired") and not cert_data.get("is_self_signed") else 0.0

            # 18. Overall TLS security score
            tls_score = (
                version_score / 1.3 * 0.3 +
                (1.0 if data.get("forward_secrecy") else 0.0) * 0.3 +
                (1.0 if not cert_data.get("is_expired") else 0.0) * 0.4
            )
            features["tls_18_security_score"] = float(tls_score)

        except Exception as e:
            logger.error(f"Error extracting TLS features: {e}")

        return features

    def _extract_dns_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract DNS features (12 total).

        Args:
            data: DNS collector results

        Returns:
            Dictionary of DNS features
        """
        features = {}

        if data.get("status") != "success":
            return {f"dns_{i:02d}": 0.0 for i in range(1, 13)}

        try:
            dns_records = data.get("dns_records", {})
            security_records = data.get("security_records", {})
            
            # 1-10. DNS records and security checks
            features["dns_01_has_a_record"] = 1.0 if dns_records.get("A") else 0.0
            features["dns_02_has_aaaa_record"] = 1.0 if dns_records.get("AAAA") else 0.0
            features["dns_03_has_mx_record"] = 1.0 if dns_records.get("MX") else 0.0
            
            mx_count = len(dns_records.get("MX", [])) if dns_records.get("MX") else 0
            features["dns_04_mx_count"] = float(mx_count)

            ns_count = len(dns_records.get("NS", [])) if dns_records.get("NS") else 0
            features["dns_05_ns_count"] = float(ns_count) / 4.0

            features["dns_06_has_spf"] = 1.0 if security_records.get("spf") else 0.0
            features["dns_07_has_dmarc"] = 1.0 if security_records.get("dmarc") else 0.0
            features["dns_08_dnssec_enabled"] = 1.0 if data.get("dnssec_enabled") else 0.0
            features["dns_09_has_caa"] = 1.0 if security_records.get("caa") else 0.0
            features["dns_10_has_tlsa"] = 1.0 if security_records.get("tlsa") else 0.0

            # 11. Vulnerability count
            vulns = data.get("vulnerabilities", [])
            features["dns_11_vulnerability_count"] = float(len(vulns))

            # 12. Email security score
            email_score = (
                (1.0 if security_records.get("spf") else 0.0) * 0.33 +
                (1.0 if security_records.get("dmarc") else 0.0) * 0.33 +
                (1.0 if data.get("dnssec_enabled") else 0.0) * 0.34
            )
            features["dns_12_email_security_score"] = float(email_score)

        except Exception as e:
            logger.error(f"Error extracting DNS features: {e}")

        return features

    def _extract_whois_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract WHOIS features (10 total).

        Args:
            data: WHOIS collector results

        Returns:
            Dictionary of WHOIS features
        """
        features = {}

        if data.get("status") != "success":
            return {f"whois_{i:02d}": 0.0 for i in range(1, 11)}

        try:
            # 1-5. Domain expiration and registrar info
            days_until = data.get("days_until_expiry", 365)
            features["whois_01_days_until_expiry"] = float(max(0, min(days_until, 3650))) / 3650.0

            risk_mapping = {"low": 0.2, "medium": 0.5, "high": 0.7, "critical": 0.95}
            risk_level = data.get("expiration_risk", "unknown")
            features["whois_02_expiration_risk"] = risk_mapping.get(risk_level, 0.1)

            features["whois_03_domain_age_years"] = float(min(5, 20)) / 20.0

            features["whois_04_has_privacy"] = 1.0 if data.get("registrant_privacy") else 0.0

            registrar = data.get("registrar", "").lower()
            reputable_registrars = ["verisign", "godaddy", "namecheap", "network solutions"]
            features["whois_05_registrar_reputation"] = 1.0 if any(r in registrar for r in reputable_registrars) else 0.5

            # 6-10. Contact and location info
            features["whois_06_has_tech_contact"] = 1.0 if data.get("technical_contact") and data.get("technical_contact") != "N/A" else 0.0

            country = data.get("registrant_country", "").upper()
            low_risk_countries = ["US", "GB", "CA", "AU", "DE", "FR", "JP", "NZ"]
            features["whois_07_country_risk"] = 0.2 if country in low_risk_countries else 0.7

            org = data.get("registrant_organization", "")
            features["whois_08_has_organization"] = 1.0 if org and org != "N/A" else 0.0

            nameservers = data.get("name_servers", [])
            ns_count = len(nameservers) if nameservers else 0
            features["whois_09_nameserver_count"] = float(min(ns_count, 6)) / 6.0

            trustworthiness = (
                (1.0 - features["whois_02_expiration_risk"]) * 0.3 +
                features["whois_04_has_privacy"] * 0.2 +
                features["whois_05_registrar_reputation"] * 0.25 +
                features["whois_06_has_tech_contact"] * 0.15 +
                (1.0 - features["whois_07_country_risk"]) * 0.1
            )
            features["whois_10_trustworthiness_score"] = float(trustworthiness)

        except Exception as e:
            logger.error(f"Error extracting WHOIS features: {e}")

        return features

    def _extract_ports_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract Port scanning features (15 total).

        Args:
            data: Port scanner results

        Returns:
            Dictionary of port features
        """
        features = {}

        if data.get("status") != "success":
            return {f"ports_{i:02d}": 0.0 for i in range(1, 16)}

        try:
            open_ports = data.get("open_ports", [])
            services = data.get("services_detected", {})

            # 1-7. Common ports
            features["ports_01_open_port_count"] = float(len(open_ports))
            features["ports_02_has_ssh"] = 1.0 if 22 in open_ports else 0.0
            features["ports_03_has_http"] = 1.0 if 80 in open_ports else 0.0
            features["ports_04_has_https"] = 1.0 if 443 in open_ports else 0.0
            
            db_ports = [3306, 5432, 27017]
            features["ports_05_has_db_port"] = 1.0 if any(p in open_ports for p in db_ports) else 0.0

            ssh_service = services.get(22, {})
            features["ports_06_ssh_version_detected"] = 1.0 if ssh_service.get("banner") else 0.0

            web_ports = [80, 8080, 443, 8443]
            web_count = len([p for p in open_ports if p in web_ports])
            features["ports_07_web_service_count"] = float(web_count) / 4.0

            # 8-15. Additional port metrics
            db_count = len([p for p in open_ports if p in db_ports])
            features["ports_08_db_service_count"] = float(db_count) / 3.0

            common_ports = [22, 80, 443, 3306, 5432, 25, 53]
            unusual_ports = [p for p in open_ports if p not in common_ports]
            features["ports_09_unusual_ports_count"] = float(len(unusual_ports))

            banners = sum(1 for s in services.values() if s.get("banner"))
            banner_ratio = banners / len(services) if services else 0.0
            features["ports_10_banner_success_rate"] = float(banner_ratio)

            fingerprints = sum(1 for s in services.values() if s.get("fingerprint_match"))
            fp_ratio = fingerprints / len(services) if services else 0.0
            features["ports_11_fingerprint_accuracy"] = float(fp_ratio)

            unknown_services = sum(1 for s in services.values() if s.get("service_name") == "Unknown")
            features["ports_12_unknown_services_count"] = float(unknown_services)

            mail_ports = [25, 465, 587, 993, 995]
            features["ports_13_has_mail_service"] = 1.0 if any(p in open_ports for p in mail_ports) else 0.0

            features["ports_14_has_rdp"] = 1.0 if 3389 in open_ports else 0.0

            exposure_score = min(len(open_ports), 20) / 20.0
            features["ports_15_exposure_score"] = float(exposure_score)

        except Exception as e:
            logger.error(f"Error extracting port features: {e}")

        return features

    def _extract_tech_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract Technology Stack features (17 total).

        Args:
            data: Tech stack detector results

        Returns:
            Dictionary of technology features
        """
        features = {}

        if data.get("status") != "success":
            return {f"tech_{i:02d}": 0.0 for i in range(1, 18)}

        try:
            technologies = data.get("detected_technologies", [])
            tech_str = " ".join(technologies).lower()
            vulns = data.get("potential_vulnerabilities", [])

            # 1-10. Technology detection
            features["tech_01_technology_count"] = float(len(technologies)) / 10.0
            features["tech_02_has_apache"] = 1.0 if "apache" in tech_str else 0.0
            features["tech_03_has_nginx"] = 1.0 if "nginx" in tech_str else 0.0
            features["tech_04_has_iis"] = 1.0 if "iis" in tech_str else 0.0
            features["tech_05_has_wordpress"] = 1.0 if "wordpress" in tech_str else 0.0
            features["tech_06_has_drupal"] = 1.0 if "drupal" in tech_str else 0.0
            features["tech_07_has_php"] = 1.0 if "php" in tech_str else 0.0
            features["tech_08_has_python"] = 1.0 if "python" in tech_str else 0.0
            features["tech_09_has_nodejs"] = 1.0 if "node" in tech_str or "express" in tech_str else 0.0
            features["tech_10_has_java"] = 1.0 if "java" in tech_str else 0.0

            # 11-17. Additional tech metrics
            cms_techs = ["wordpress", "drupal", "joomla", "magento"]
            features["tech_11_cms_detected"] = 1.0 if any(cms in tech_str for cms in cms_techs) else 0.0

            modern_frameworks = ["django", "flask", "express", "laravel", "spring"]
            features["tech_12_modern_framework"] = 1.0 if any(fw in tech_str for fw in modern_frameworks) else 0.0

            features["tech_13_server_exposed"] = 1.0 if any("apache" in t.lower() or "nginx" in t.lower() for t in technologies) else 0.0

            features["tech_14_vulnerability_count"] = float(len(vulns))

            outdated_tech = ["iis", "php 5", "python 2"]
            features["tech_15_outdated_tech"] = 1.0 if any(out in tech_str for out in outdated_tech) else 0.0

            features["tech_16_framework_diversity"] = float(min(len(technologies), 5)) / 5.0

            security_score = (
                (1.0 - features["tech_13_server_exposed"]) * 0.25 +
                features["tech_12_modern_framework"] * 0.35 +
                (1.0 - features["tech_15_outdated_tech"]) * 0.25 +
                (1.0 - min(features["tech_14_vulnerability_count"] / 10.0, 1.0)) * 0.15
            )
            features["tech_17_security_score"] = float(security_score)

        except Exception as e:
            logger.error(f"Error extracting tech features: {e}")

        return features

    def _dict_to_vector(self, feature_dict: Dict[str, float]) -> np.ndarray:
        """
        Convert feature dictionary to numpy vector.

        Args:
            feature_dict: Dictionary of features

        Returns:
            NumPy array of features
        """
        # Sort by feature name to ensure consistent ordering
        sorted_features = sorted(feature_dict.items())
        values = [val for _, val in sorted_features]
        return np.array(values, dtype=np.float32)

    def _initialize_feature_names(self) -> List[str]:
        """
        Initialize ordered list of feature names.

        Returns:
            List of feature names
        """
        names = []

        # HTTP (15)
        for i in range(1, 16):
            names.append(f"http_{i:02d}")

        # TLS (18)
        for i in range(1, 19):
            names.append(f"tls_{i:02d}")

        # DNS (12)
        for i in range(1, 13):
            names.append(f"dns_{i:02d}")

        # WHOIS (10)
        for i in range(1, 11):
            names.append(f"whois_{i:02d}")

        # Ports (15)
        for i in range(1, 16):
            names.append(f"ports_{i:02d}")

        # Tech Stack (17)
        for i in range(1, 18):
            names.append(f"tech_{i:02d}")

        return names

    def get_feature_name(self, index: int) -> str:
        """
        Get feature name by index.

        Args:
            index: Feature index

        Returns:
            Feature name
        """
        if 0 <= index < len(self.feature_names):
            return self.feature_names[index]
        return f"feature_{index}"
