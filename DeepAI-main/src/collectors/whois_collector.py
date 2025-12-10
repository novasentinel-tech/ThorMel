"""
WHOIS domain information collector.
Retrieves domain registration details and ownership information.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import whois
from urllib.parse import urlparse

from src.collectors.base_collector import BaseCollector
from config.logging_config import get_logger

logger = get_logger(__name__)


class WHOISCollector(BaseCollector):
    """Collects and analyzes WHOIS information."""

    def __init__(self, timeout: int = 10, use_cache: bool = True):
        """
        Initialize WHOIS collector.

        Args:
            timeout: Timeout for WHOIS query
            use_cache: Whether to cache WHOIS results
        """
        super().__init__(timeout=timeout)
        self.use_cache = use_cache
        self._cache = {}

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Retrieve WHOIS information for target domain.

        Args:
            target: Target domain or URL

        Returns:
            Dictionary with WHOIS information
        """
        self._log_collection_start(target)

        try:
            # Extract domain
            domain = self._extract_domain(target)

            # Check cache
            if self.use_cache and domain in self._cache:
                result = self._cache[domain]
                self._log_collection_end(target)
                return result

            # Query WHOIS
            try:
                whois_response = whois.whois(domain)
            except Exception as e:
                logger.error(f"WHOIS query failed for {domain}: {e}")
                self._log_collection_end(target, success=False)
                return {"status": "error", "error": str(e)}

            # Parse response
            whois_data = self._parse_whois_response(whois_response)

            # Check for expiration
            expiration_risk = self._check_expiration_risk(whois_data)

            result = {
                "status": "success",
                "domain": domain,
                "registrar": whois_data.get("registrar"),
                "creation_date": whois_data.get("creation_date"),
                "expiration_date": whois_data.get("expiration_date"),
                "updated_date": whois_data.get("updated_date"),
                "registrant_organization": whois_data.get(
                    "registrant_organization"
                ),
                "registrant_country": whois_data.get("registrant_country"),
                "technical_contact": whois_data.get("technical_contact"),
                "name_servers": whois_data.get("name_servers"),
                "dnssec": whois_data.get("dnssec"),
                "days_until_expiry": expiration_risk["days_until_expiry"],
                "expiration_risk": expiration_risk["risk_level"],
                "registrant_privacy": whois_data.get(
                    "registrant_privacy", False
                ),
            }

            # Cache result
            if self.use_cache:
                self._cache[domain] = result

            self._log_collection_end(target)
            return result

        except Exception as e:
            logger.error(f"WHOIS collection failed for {target}: {e}")
            self._log_collection_end(target, success=False)
            return {"status": "error", "error": str(e)}

    def _extract_domain(self, target: str) -> str:
        """
        Extract domain from URL or hostname.

        Args:
            target: Target domain or URL

        Returns:
            Domain name
        """
        if "://" in target:
            parsed = urlparse(target)
            return parsed.netloc.split(":")[0]
        return target.split(":")[0]

    def _parse_whois_response(self, response: Any) -> Dict[str, Any]:
        """
        Parse WHOIS response object.

        Args:
            response: WHOIS response object

        Returns:
            Parsed WHOIS data
        """
        data = {}

        # Safe attribute access
        safe_attrs = [
            "registrar",
            "creation_date",
            "expiration_date",
            "updated_date",
            "organizer",
            "country",
            "dnssec",
        ]

        for attr in safe_attrs:
            try:
                value = getattr(response, attr, None)
                # Handle list of dates
                if isinstance(value, list) and len(value) > 0:
                    value = value[0]
                # Convert datetime to string
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[attr] = value
            except Exception:
                pass

        # Extract name servers
        try:
            ns = getattr(response, "name_servers", [])
            if ns:
                data["name_servers"] = [str(n).lower() for n in ns]
        except Exception:
            data["name_servers"] = []

        # Map extracted fields
        data_mapped = {
            "registrar": data.get("registrar"),
            "creation_date": data.get("creation_date"),
            "expiration_date": data.get("expiration_date"),
            "updated_date": data.get("updated_date"),
            "registrant_organization": data.get("organizer"),
            "registrant_country": data.get("country"),
            "technical_contact": "N/A",
            "name_servers": data.get("name_servers", []),
            "dnssec": data.get("dnssec"),
        }

        return data_mapped

    def _check_expiration_risk(self, whois_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check domain expiration risk.

        Args:
            whois_data: WHOIS data dictionary

        Returns:
            Expiration risk assessment
        """
        risk = {
            "days_until_expiry": None,
            "risk_level": "unknown",
        }

        try:
            exp_date_str = whois_data.get("expiration_date")
            if isinstance(exp_date_str, str):
                # Parse ISO format
                exp_date = datetime.fromisoformat(
                    exp_date_str.replace("Z", "+00:00")
                )
            else:
                exp_date = exp_date_str

            if exp_date:
                now = datetime.utcnow()
                if exp_date.tzinfo is None:
                    # Naive datetime - assume UTC
                    days_left = (exp_date - now).days
                else:
                    # Timezone-aware
                    days_left = (
                        exp_date.replace(tzinfo=None) - now
                    ).days

                risk["days_until_expiry"] = max(0, days_left)

                # Assess risk
                if days_left < 0:
                    risk["risk_level"] = "expired"
                elif days_left < 30:
                    risk["risk_level"] = "critical"
                elif days_left < 90:
                    risk["risk_level"] = "high"
                elif days_left < 180:
                    risk["risk_level"] = "medium"
                else:
                    risk["risk_level"] = "low"
        except Exception as e:
            logger.debug(f"Could not check expiration: {e}")

        return risk
