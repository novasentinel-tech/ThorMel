"""
Utility functions and helpers for DeepAI system.
"""

import re
import hashlib
import json
from typing import Tuple, Optional
from urllib.parse import urlparse
import ipaddress

from config.logging_config import get_logger

logger = get_logger(__name__)


def is_valid_domain_format(domain: str) -> bool:
    """
    Validate domain or IP address format.
    
    Args:
        domain: Domain name or IP address to validate
        
    Returns:
        True if format is valid, False otherwise
    """
    # Remove whitespace
    domain = domain.strip().lower()
    
    # Check IP address format
    try:
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        pass
    
    # Check domain format
    domain_regex = r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
    return bool(re.match(domain_regex, domain))


def is_private_ip(domain: str) -> bool:
    """
    Check if domain resolves to a private IP address.
    
    Args:
        domain: Domain name or IP address
        
    Returns:
        True if private/internal IP, False otherwise
    """
    try:
        ip = ipaddress.ip_address(domain)
        return ip.is_private or ip.is_loopback
    except ValueError:
        # Try DNS resolution (simplified)
        # In production, use proper DNS resolution with caching
        return False


def extract_base_domain(domain: str) -> str:
    """
    Extract base domain from full domain.
    
    Examples:
        - "www.example.com" -> "example.com"
        - "sub.example.co.uk" -> "example.co.uk"
    """
    parts = domain.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain


def get_tld(domain: str) -> str:
    """Extract TLD from domain."""
    parts = domain.split(".")
    if parts:
        return f".{parts[-1]}"
    return ""


def calculate_hash(data: str) -> str:
    """Calculate SHA256 hash of string."""
    return hashlib.sha256(data.encode()).hexdigest()


def normalize_domain(domain: str) -> str:
    """
    Normalize domain to lowercase and remove whitespace.
    
    Args:
        domain: Domain to normalize
        
    Returns:
        Normalized domain
    """
    return domain.strip().lower()


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL format is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Domain name or None if invalid
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def json_serialize_helper(obj):
    """
    Helper for JSON serialization of uncommon types.
    Used for audit logs and reports.
    """
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, (set, tuple)):
        return list(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    else:
        return str(obj)


def safe_json_dumps(obj, **kwargs) -> str:
    """Safely dump object to JSON string."""
    return json.dumps(obj, default=json_serialize_helper, **kwargs)


def calculate_gini_coefficient(values) -> float:
    """
    Calculate Gini coefficient for distribution analysis.
    Used to detect dataset bias.
    
    Args:
        values: List of numeric values
        
    Returns:
        Gini coefficient (0-1, higher = more unequal)
    """
    if not values or len(values) < 2:
        return 0.0
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cumsum = 0
    
    for i, val in enumerate(sorted_vals):
        cumsum += (i + 1) * val
    
    return (2 * cumsum) / (n * sum(sorted_vals)) - (n + 1) / n


class AttributeDict(dict):
    """Dictionary that supports attribute-style access."""
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"No attribute '{name}'")
    
    def __setattr__(self, name, value):
        self[name] = value
    
    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"No attribute '{name}'")
