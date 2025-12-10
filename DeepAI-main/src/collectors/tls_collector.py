"""
TLS/SSL security analyzer and certificate inspector.
Inspects TLS configuration and detects vulnerabilities.
"""

from typing import Dict, Any, List, Optional
import ssl
import socket
from datetime import datetime
from OpenSSL import SSL, crypto

from src.collectors.base_collector import BaseCollector
from config.logging_config import get_logger

logger = get_logger(__name__)


class TLSCollector(BaseCollector):
    """Collects and analyzes TLS/SSL configuration."""

    # Known vulnerable ciphers
    WEAK_CIPHERS = {
        "RC4",
        "DES",
        "3DES",
        "MD5",
        "NULL",
        "anon",
        "export",
    }

    # TLS version mappings
    TLS_VERSION_MAP = {
        "TLSv1": 1.0,
        "TLSv1.1": 1.1,
        "TLSv1.2": 1.2,
        "TLSv1.3": 1.3,
        "SSLv3": 1.0,  # Downgrade to 1.0 for risk scoring
    }

    # Known TLS vulnerabilities
    KNOWN_VULNERABILITIES = {
        "TLSv1.0": ["POODLE", "BEAST"],
        "TLSv1.1": ["POODLE", "LUCKY13"],
        "SSLv3": ["POODLE", "HEARTBLEED"],
    }

    def __init__(self, timeout: int = 15):
        """Initialize TLS collector."""
        super().__init__(timeout=timeout)

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Inspect TLS configuration of target.

        Args:
            target: Target domain or IP

        Returns:
            Dictionary with TLS analysis
        """
        self._log_collection_start(target)

        try:
            # Extract domain from potential URL
            domain = target.split("://")[-1].split(":")[0]
            port = 443

            # Get certificate and TLS info
            context = SSL.Context(SSL.TLS_METHOD)
            context.check_hostname = False
            context.verify_mode = SSL.VERIFY_NONE

            conn = SSL.Connection(context, socket.socket(socket.AF_INET))
            conn.settimeout(self.timeout)
            conn.connect((domain, port))
            conn.do_handshake()

            # Get certificate
            cert = conn.get_peer_certificate()
            tls_version = conn.get_protocol_version_name()
            cipher = conn.get_cipher_name()

            # Analyze certificate
            cert_analysis = self._analyze_certificate(cert)

            # Analyze TLS version
            tls_score = self._score_tls_version(tls_version)

            # Analyze cipher
            cipher_strength = self._analyze_cipher(cipher)

            # Get supported protocols
            supported_protocols = self._get_supported_protocols(domain, port)

            result = {
                "status": "success",
                "protocol_version": tls_version,
                "protocol_score": tls_score,
                "cipher_suite": cipher,
                "cipher_strength": cipher_strength,
                "certificate": cert_analysis,
                "supported_protocols": supported_protocols,
                "vulnerabilities": self.KNOWN_VULNERABILITIES.get(
                    tls_version, []
                ),
                "forward_secrecy": self._has_forward_secrecy(cipher),
                "ocsp_stapling": False,  # Would need to check stapling
                "sct_present": False,  # Certificate transparency
            }

            conn.shutdown()
            conn.close()

            self._log_collection_end(target)
            return result

        except Exception as e:
            logger.error(f"TLS inspection failed for {target}: {e}")
            self._log_collection_end(target, success=False)
            return {"status": "error", "error": str(e)}

    def _analyze_certificate(self, cert: crypto.X509) -> Dict[str, Any]:
        """
        Analyze X.509 certificate.

        Args:
            cert: OpenSSL certificate object

        Returns:
            Certificate analysis dictionary
        """
        try:
            subject = cert.get_subject()
            issuer = cert.get_issuer()

            # Get validity dates
            not_before = cert.get_notBefore()
            not_after = cert.get_notAfter()

            if isinstance(not_before, bytes):
                not_before = not_before.decode()
            if isinstance(not_after, bytes):
                not_after = not_after.decode()

            # Parse dates (format: YYYYMMDDhhmmssZ)
            not_before_date = datetime.strptime(not_before, "%Y%m%d%H%M%SZ")
            not_after_date = datetime.strptime(not_after, "%Y%m%d%H%M%SZ")

            now = datetime.utcnow()
            is_expired = now > not_after_date
            days_until_expiry = (not_after_date - now).days

            return {
                "subject": subject.CN if subject.CN else "Unknown",
                "issuer": issuer.CN if issuer.CN else "Unknown",
                "valid_from": not_before,
                "valid_to": not_after,
                "is_expired": is_expired,
                "days_until_expiry": days_until_expiry,
                "is_self_signed": subject == issuer,
                "serial_number": cert.get_serial_number(),
                "version": cert.get_version(),
            }
        except Exception as e:
            logger.error(f"Certificate analysis failed: {e}")
            return {"status": "error"}

    def _score_tls_version(self, version: str) -> float:
        """
        Score TLS version for security.

        Args:
            version: TLS version string

        Returns:
            Score from 1.0 (worst) to 1.3 (best)
        """
        version_map = self.TLS_VERSION_MAP
        return version_map.get(version, 1.0)

    def _analyze_cipher(self, cipher_name: str) -> int:
        """
        Analyze cipher suite strength.

        Args:
            cipher_name: Cipher name

        Returns:
            Cipher strength in bits (estimate)
        """
        # Check if weak cipher
        for weak in self.WEAK_CIPHERS:
            if weak.upper() in cipher_name.upper():
                return 0

        # Default 256 for modern ciphers
        if "256" in cipher_name:
            return 256
        elif "128" in cipher_name:
            return 128
        else:
            return 128  # Default assumed

    def _get_supported_protocols(
        self, domain: str, port: int
    ) -> List[str]:
        """
        Get list of supported TLS versions.

        Args:
            domain: Target domain
            port: Target port

        Returns:
            List of supported protocol versions
        """
        supported = []
        protocols_to_test = [
            ("SSLv3", SSL.SSLv3_METHOD),
            ("TLSv1.0", SSL.TLSv1_METHOD),
            ("TLSv1.1", SSL.TLSv1_1_METHOD),
            ("TLSv1.2", SSL.TLSv1_2_METHOD),
            ("TLSv1.3", SSL.TLS_METHOD),
        ]

        for name, method in protocols_to_test:
            try:
                context = SSL.Context(method)
                context.check_hostname = False
                context.verify_mode = SSL.VERIFY_NONE
                conn = SSL.Connection(context, socket.socket(socket.AF_INET))
                conn.settimeout(3)
                conn.connect((domain, port))
                conn.do_handshake()
                supported.append(name)
                conn.close()
            except Exception:
                pass

        return supported

    def _has_forward_secrecy(self, cipher_name: str) -> bool:
        """
        Check if cipher supports forward secrecy.

        Args:
            cipher_name: Cipher name

        Returns:
            True if forward secrecy supported
        """
        fs_indicators = ["ECDHE", "DHE", "ECDH"]
        return any(
            indicator.upper() in cipher_name.upper()
            for indicator in fs_indicators
        )
