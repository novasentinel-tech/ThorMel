"""
DNS records analyzer and DNSSEC validator.
Inspects DNS configuration and detects vulnerabilities.
"""

from typing import Dict, Any, List, Optional
import dns.resolver
import dns.dnssec
import dns.query
import dns.zone
import dns.flags
import dns.rdatatype
import dns.message

from src.collectors.base_collector import BaseCollector
from config.logging_config import get_logger

logger = get_logger(__name__)


class DNSCollector(BaseCollector):
    """Collects and analyzes DNS configuration."""

    # Record types to query
    RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "SOA"]

    # Security-related records
    SECURITY_RECORDS = ["SPF", "DKIM", "DMARC", "CAA", "TLSA"]

    def __init__(self, timeout: int = 5):
        """Initialize DNS collector."""
        super().__init__(timeout=timeout)

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Inspect DNS records and configuration of target.

        Args:
            target: Target domain

        Returns:
            Dictionary with DNS analysis
        """
        self._log_collection_start(target)

        try:
            # Extract domain
            domain = target.split("://")[-1].split(":")[0]

            # Collect basic records
            dns_records = self._collect_dns_records(domain)

            # Check DNS security features
            dnssec_enabled = self._check_dnssec(domain)

            # Check security records
            security_records = self._collect_security_records(domain)

            # Analyze DNS configuration
            dns_config = self._analyze_dns_config(dns_records)

            result = {
                "status": "success",
                "domain": domain,
                "dns_records": dns_records,
                "dnssec_enabled": dnssec_enabled,
                "security_records": security_records,
                "dns_config_analysis": dns_config,
                "vulnerabilities": self._detect_dns_vulnerabilities(
                    dns_records, security_records, dnssec_enabled
                ),
            }

            self._log_collection_end(target)
            return result

        except Exception as e:
            logger.error(f"DNS inspection failed for {target}: {e}")
            self._log_collection_end(target, success=False)
            return {"status": "error", "error": str(e)}

    def _collect_dns_records(self, domain: str) -> Dict[str, Any]:
        """
        Collect standard DNS records.

        Args:
            domain: Target domain

        Returns:
            Dictionary with DNS records
        """
        records = {}
        resolver = dns.resolver.Resolver()
        resolver.timeout = self.timeout

        for record_type in self.RECORD_TYPES:
            try:
                answers = resolver.resolve(domain, record_type)
                records[record_type] = []
                for rdata in answers:
                    records[record_type].append(str(rdata))
            except Exception as e:
                records[record_type] = None

        return records

    def _collect_security_records(self, domain: str) -> Dict[str, Any]:
        """
        Collect security-related DNS records.

        Args:
            domain: Target domain

        Returns:
            Dictionary with security records
        """
        security = {}
        resolver = dns.resolver.Resolver()
        resolver.timeout = self.timeout

        # SPF record
        try:
            answers = resolver.resolve(domain, "TXT")
            for rdata in answers:
                if "v=spf1" in str(rdata):
                    security["spf"] = str(rdata)
                    break
        except Exception:
            security["spf"] = None

        # DMARC record
        try:
            answers = resolver.resolve(f"_dmarc.{domain}", "TXT")
            for rdata in answers:
                security["dmarc"] = str(rdata)
                break
        except Exception:
            security["dmarc"] = None

        # CAA records
        try:
            answers = resolver.resolve(domain, "CAA")
            security["caa"] = [str(rdata) for rdata in answers]
        except Exception:
            security["caa"] = None

        # TLSA records
        try:
            answers = resolver.resolve(f"_443._tcp.{domain}", "TLSA")
            security["tlsa"] = [str(rdata) for rdata in answers]
        except Exception:
            security["tlsa"] = None

        return security

    def _check_dnssec(self, domain: str) -> bool:
        """
        Check if DNSSEC is enabled.

        Args:
            domain: Target domain

        Returns:
            True if DNSSEC is enabled
        """
        try:
            request = dns.message.make_query(
                domain, dns.rdatatype.A, want_dnssec=True
            )
            response = dns.query.udp(request, "8.8.8.8", timeout=self.timeout)
            return (
                response.flags & dns.flags.AD
            ) != 0  # Authenticated Data flag
        except Exception:
            return False

    def _analyze_dns_config(self, records: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze DNS configuration for issues.

        Args:
            records: DNS records dictionary

        Returns:
            Configuration analysis
        """
        analysis = {
            "has_a_record": records.get("A") is not None,
            "has_aaaa_record": records.get("AAAA") is not None,
            "has_mx_record": records.get("MX") is not None,
            "has_ns_record": records.get("NS") is not None,
            "ipv6_support": records.get("AAAA") is not None,
            "mail_server_count": len(records.get("MX", [])) or 0,
            "nameserver_count": len(records.get("NS", [])) or 0,
        }
        return analysis

    def _detect_dns_vulnerabilities(
        self,
        records: Dict[str, Any],
        security_records: Dict[str, Any],
        dnssec_enabled: bool,
    ) -> List[str]:
        """
        Detect DNS vulnerabilities.

        Args:
            records: DNS records
            security_records: Security records
            dnssec_enabled: DNSSEC status

        Returns:
            List of detected vulnerabilities
        """
        vulnerabilities = []

        # Check for missing SPF
        if security_records.get("spf") is None:
            vulnerabilities.append("Missing SPF record")

        # Check for missing DMARC
        if security_records.get("dmarc") is None:
            vulnerabilities.append("Missing DMARC record")

        # Check for missing CAA
        if security_records.get("caa") is None:
            vulnerabilities.append("Missing CAA records")

        # Check DNSSEC
        if not dnssec_enabled:
            vulnerabilities.append("DNSSEC not enabled")

        # Check for zone transfer vulnerability
        # (attempted in real implementation)

        return vulnerabilities
