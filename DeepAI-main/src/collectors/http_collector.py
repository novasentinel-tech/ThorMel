"""
HTTP headers collector.
Gathers HTTP headers and analyzes security implications.
"""

from typing import Dict, Any, List, Tuple
import requests
from urllib.parse import urlparse

from src.collectors.base_collector import BaseCollector
from config.logging_config import get_logger
from src.utils import DeepAIException, HoneypotDetectedException, TimeoutException

logger = get_logger(__name__)


class HTTPHeadersCollector(BaseCollector):
    """Collects and analyzes HTTP headers for security."""

    # Security headers to check
    SECURITY_HEADERS = {
        "Strict-Transport-Security": "HSTS",
        "Content-Security-Policy": "CSP",
        "X-Frame-Options": "X-Frame-Options",
        "X-Content-Type-Options": "X-Content-Type-Options",
        "X-XSS-Protection": "X-XSS-Protection",
        "Referrer-Policy": "Referrer-Policy",
        "Permissions-Policy": "Permissions-Policy",
        "Expect-CT": "Expect-CT",
    }

    # User agent that identifies as research bot
    USER_AGENT = "Academic-Security-Research-Bot/1.0 (+https://deepai-security.edu/bot)"

    def __init__(self, timeout: int = 10):
        """Initialize HTTP collector."""
        super().__init__(timeout=timeout)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect and analyze HTTP headers from target.

        Args:
            target: Target domain

        Returns:
            Dictionary with HTTP analysis results
        """
        self._log_collection_start(target)

        try:
            # Ensure target has protocol
            if not target.startswith(("http://", "https://")):
                target = f"https://{target}"

            # Prepare URL
            url = target if target.endswith("/") else f"{target}/"

            # Request headers
            response = self._fetch_with_timeout(url)

            # Detect honeypot
            if self._detect_honeypot(response):
                raise HoneypotDetectedException(
                    f"Honeypot detected at {target}"
                )

            # Extract and analyze headers
            headers = dict(response.headers)
            security_headers = self._analyze_security_headers(headers)
            cookies = self._analyze_cookies(response)

            result = {
                "status": "success",
                "url": str(response.url),
                "status_code": response.status_code,
                "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                "headers": headers,
                "security_headers": security_headers,
                "cookies": cookies,
                "server": headers.get("Server", "Unknown"),
                "powered_by": headers.get("X-Powered-By"),
                "has_redirect_chain": len(response.history) > 0,
                "redirect_count": len(response.history),
            }

            self._log_collection_end(target)
            return result

        except HoneypotDetectedException as e:
            logger.warning(f"Honeypot detected: {e}")
            return {"status": "honeypot_detected", "error": str(e)}

        except requests.Timeout:
            logger.error(f"HTTP request timed out for {target}")
            return {"status": "timeout", "error": "Request timeout"}

        except Exception as e:
            logger.error(f"HTTP header collection failed for {target}: {e}")
            self._log_collection_end(target, success=False)
            return {"status": "error", "error": str(e)}

    def _fetch_with_timeout(self, url: str) -> requests.Response:
        """
        Fetch URL with timeout and validation.

        Args:
            url: URL to fetch

        Returns:
            Response object
        """
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True,
                stream=False,
            )
            return response
        except requests.RequestException as e:
            raise DeepAIException(f"HTTP request failed: {e}")

    def _analyze_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze presence and quality of security headers.

        Args:
            headers: Response headers dictionary

        Returns:
            Security header analysis
        """
        security_analysis = {}

        for header_name, display_name in self.SECURITY_HEADERS.items():
            present = header_name in headers
            security_analysis[display_name] = {
                "present": present,
                "value": headers.get(header_name, None),
            }

        # Special analysis for HSTS
        if "Strict-Transport-Security" in headers:
            hsts_value = headers["Strict-Transport-Security"]
            # Extract max-age
            try:
                max_age = int(
                    hsts_value.split("max-age=")[1].split(";")[0].strip()
                )
                security_analysis["HSTS"]["max_age"] = max_age
                security_analysis["HSTS"]["is_strong"] = max_age >= 31536000
            except (IndexError, ValueError):
                security_analysis["HSTS"]["max_age"] = None

        # Special analysis for CSP
        if "Content-Security-Policy" in headers:
            csp_value = headers["Content-Security-Policy"]
            directives = len(csp_value.split(";"))
            security_analysis["CSP"]["directive_count"] = directives

        return security_analysis

    def _analyze_cookies(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        Analyze cookies for security issues.

        Args:
            response: Response object with cookies

        Returns:
            List of cookie analyses
        """
        cookies_analysis = []

        for cookie in response.cookies:
            cookie_info = {
                "name": cookie.name,
                "secure": cookie.secure,
                "httponly": bool(cookie.has_nonstandard_attr("HttpOnly")),
                "samesite": cookie.has_nonstandard_attr("SameSite"),
                "domain": cookie.domain,
            }
            cookies_analysis.append(cookie_info)

        return cookies_analysis

    def _detect_honeypot(self, response: requests.Response) -> bool:
        """
        Detect if target is a honeypot.

        Args:
            response: Response object

        Returns:
            True if honeypot suspected
        """
        # Check for honeypot indicators
        indicators = [
            "X-Honeypot" in response.headers,
            "tarpit" in response.headers.get("Server", "").lower(),
            response.elapsed.total_seconds() > 30,  # Very slow response
            len(response.content) > 10_000_000,  # Gigantic response
        ]

        return any(indicators)
