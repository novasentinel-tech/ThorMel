"""
Technology stack detection module.
Detects frameworks, CMS, and technology signatures.
"""

from typing import Dict, Any, List
import re
from urllib.parse import urlparse

from src.collectors.base_collector import BaseCollector
from config.logging_config import get_logger

logger = get_logger(__name__)


class TechStackDetector(BaseCollector):
    """Detects technology stack of target application."""

    # Signature patterns for common technologies
    SIGNATURES = {
        # Web Servers
        "Apache": [
            r"Apache",
            r"Server: Apache",
        ],
        "Nginx": [
            r"nginx",
            r"Server: nginx",
        ],
        "IIS": [
            r"IIS",
            r"X-Powered-By: ASP.NET",
            r"X-AspNet-Version",
        ],
        # Frameworks
        "Django": [
            r"Django",
            r"django",
        ],
        "Flask": [
            r"Flask",
            r"Werkzeug",
        ],
        "Laravel": [
            r"Laravel",
            r"XSRF-TOKEN",
        ],
        "Ruby on Rails": [
            r"Rails",
            r"X-Runtime",
        ],
        "Express": [
            r"Express",
            r"X-Powered-By: Express",
        ],
        "Spring": [
            r"Spring",
            r"tomcat",
        ],
        "ASP.NET": [
            r"ASP.NET",
            r"X-AspNet-Version",
        ],
        # CMS
        "WordPress": [
            r"wordpress",
            r"wp-content",
            r"wp-includes",
        ],
        "Drupal": [
            r"drupal",
            r"Drupal",
        ],
        "Joomla": [
            r"joomla",
            r"Joomla",
        ],
        "Magento": [
            r"magento",
            r"Magento",
        ],
        # Others
        "Node.js": [
            r"Node.js",
            r"nodejs",
        ],
        "Python": [
            r"Python",
            r"python",
        ],
        "PHP": [
            r"PHP",
            r"php",
        ],
        "Java": [
            r"Java",
            r"java",
        ],
    }

    # Common header indicators
    TECH_HEADERS = {
        "X-Powered-By": "Application",
        "X-AspNet-Version": "ASP.NET",
        "X-AspNetMvc-Version": "ASP.NET MVC",
        "X-Runtime": "Runtime",
        "Server": "Web Server",
        "X-Drupal-Cache": "Drupal",
    }

    def __init__(self, timeout: int = 10):
        """Initialize tech stack detector."""
        super().__init__(timeout=timeout)

    def collect(self, target: str, http_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Detect technology stack of target.

        Args:
            target: Target domain
            http_data: Optional HTTP headers from HTTP collector
            **kwargs: Additional arguments

        Returns:
            Dictionary with detected technologies
        """
        self._log_collection_start(target)

        try:
            detected_tech = []

            # Use provided HTTP data or fetch new
            if http_data:
                headers = http_data.get("headers", {})
            else:
                # In real scenario, would fetch headers
                headers = {}

            # Detect from headers
            tech_from_headers = self._detect_from_headers(headers)
            detected_tech.extend(tech_from_headers)

            # Detect from response content (if available)
            if http_data and "content" in http_data:
                tech_from_content = self._detect_from_content(
                    http_data["content"]
                )
                detected_tech.extend(tech_from_content)

            # Detect from common paths
            tech_from_paths = self._detect_from_paths(target)
            detected_tech.extend(tech_from_paths)

            # Deduplicate
            detected_tech = list(set(detected_tech))

            # Assess vulnerabilities
            vulnerabilities = self._assess_tech_vulnerabilities(detected_tech)

            result = {
                "status": "success",
                "target": target,
                "detected_technologies": detected_tech,
                "technology_count": len(detected_tech),
                "potential_vulnerabilities": vulnerabilities,
            }

            self._log_collection_end(target)
            return result

        except Exception as e:
            logger.error(f"Tech stack detection failed for {target}: {e}")
            self._log_collection_end(target, success=False)
            return {"status": "error", "error": str(e)}

    def _detect_from_headers(self, headers: Dict[str, str]) -> List[str]:
        """
        Detect technologies from HTTP headers.

        Args:
            headers: HTTP headers dictionary

        Returns:
            List of detected technologies
        """
        detected = []

        for header_name, header_value in headers.items():
            # Check tech headers
            if header_name in self.TECH_HEADERS:
                detected.append(f"{header_name}: {header_value}")

            # Check signatures
            for tech, patterns in self.SIGNATURES.items():
                for pattern in patterns:
                    if re.search(pattern, header_value, re.IGNORECASE):
                        detected.append(tech)
                        break

        return list(set(detected))

    def _detect_from_content(self, content: str) -> List[str]:
        """
        Detect technologies from HTML content.

        Args:
            content: HTML content

        Returns:
            List of detected technologies
        """
        detected = []

        for tech, patterns in self.SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected.append(tech)
                    break

        return list(set(detected))

    def _detect_from_paths(self, target: str) -> List[str]:
        """
        Detect technologies from common paths.

        Args:
            target: Target URL

        Returns:
            List of detected CMS/technologies
        """
        detected = []

        # Parse domain
        parsed = urlparse(target if "://" in target else f"https://{target}")
        domain = parsed.netloc

        # Check common CMS paths
        cms_indicators = {
            "WordPress": ["/wp-content", "/wp-includes", "/wp-admin"],
            "Drupal": ["/modules", "/themes", "/sites/all"],
            "Joomla": ["/components", "/modules", "/administrator"],
            "Magento": ["/app", "/skin", "/var/log"],
        }

        # In real implementation, would check actual paths
        # For now, return empty list
        return detected

    def _assess_tech_vulnerabilities(self, tech_list: List[str]) -> List[str]:
        """
        Assess known vulnerabilities for detected technologies.

        Args:
            tech_list: List of detected technologies

        Returns:
            List of potential vulnerabilities
        """
        vulnerabilities = []

        # Known vulnerability patterns
        vuln_patterns = {
            "Apache": ["CVE-2021-34429", "CVE-2021-33193"],
            "PHP": ["Type Juggling", "Serialization"],
            "WordPress": ["Plugin Vulnerabilities", "Theme Vulnerabilities"],
            "Drupal": ["Module Vulnerabilities"],
            "Django": ["SQL Injection", "CSRF"],
        }

        for tech in tech_list:
            for name, vulns in vuln_patterns.items():
                if name.lower() in tech.lower():
                    vulnerabilities.extend(vulns)

        return list(set(vulnerabilities))
