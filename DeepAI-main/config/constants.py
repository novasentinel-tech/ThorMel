"""
DeepAI configuration constants.
Centralized constant definitions for the entire system.
"""

# Common ports for scanning
COMMON_PORTS = [
    22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995,
    1433, 3306, 3389, 5432, 5984, 6379, 8080, 8443, 27017
]

# Risk levels
RISK_LEVELS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "informational": 0,
}

# TLS versions mapping
TLS_VERSIONS = {
    "SSLv3": 1.0,
    "TLSv1.0": 1.0,
    "TLSv1.1": 1.1,
    "TLSv1.2": 1.2,
    "TLSv1.3": 1.3,
}

# HTTP response codes
HTTP_SUCCESS_CODES = [200, 201, 202, 204]
HTTP_REDIRECT_CODES = [300, 301, 302, 303, 304, 307, 308]
HTTP_CLIENT_ERROR_CODES = [400, 401, 402, 403, 404, 405, 418, 429]
HTTP_SERVER_ERROR_CODES = [500, 501, 502, 503, 504, 505]

# Security headers to check
SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Content-Security-Policy",
    "X-XSS-Protection",
    "Referrer-Policy",
    "Permissions-Policy",
    "X-Powered-By",
]

# Default timeouts (in seconds)
TIMEOUT_HTTP = 10
TIMEOUT_TLS = 15
TIMEOUT_DNS = 5
TIMEOUT_WHOIS = 10
TIMEOUT_PORT = 20
TIMEOUT_TOTAL_SCAN = 60

# Banner sizes
MIN_BANNER_SIZE = 10
MAX_BANNER_SIZE = 1024

# Default page size for pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Honeypot indicators
HONEYPOT_INDICATORS = [
    "x-honeypot",
    "honeypot",
    "tarpit",
    "canary",
]

# Weak ciphers
WEAK_CIPHERS = [
    "RC4",
    "DES",
    "3DES",
    "MD5",
    "NULL",
    "ANON",
    "EXPORT",
]

# Common CMS/Framework signatures
FRAMEWORK_SIGNATURES = {
    "WordPress": ["wp-content", "wp-includes", "wp-admin"],
    "Drupal": ["modules", "themes", "sites/all"],
    "Joomla": ["components", "modules", "administrator"],
    "Magento": ["app", "skin", "var/log"],
}

# Rate limit defaults (per configuration)
RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_HOUR = 50
RATE_LIMIT_PER_DAY = 200

# Cache configuration
CACHE_WHOIS_HOURS = 24
CACHE_DNS_HOURS = 12
CACHE_PORT_SCAN_HOURS = 6

# Logging configuration
LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "{name}:{function}:{line} - {message}"
)
LOG_LEVEL = "INFO"
LOG_FILE_ROTATION = "500 MB"
LOG_FILE_RETENTION = "7 days"

# Feature engineering
FEATURE_COUNT = 87
FEATURE_CATEGORIES = {
    "http": 15,
    "tls": 18,
    "dns": 12,
    "whois": 10,
    "ports": 15,
    "tech_stack": 17,
}

# ML Model configuration
MODEL_TYPE = "LightGBM"
TARGET_CLASSES = ["secure", "warning", "vulnerable", "critical"]
CLASS_WEIGHTS = {"critical": 4, "vulnerable": 3, "warning": 2, "secure": 1}

# RL Agent configuration
RL_STATE_SIZE = 32
RL_ACTION_COUNT = 10
RL_ACTIONS = [
    "deep_scan_http",
    "deep_scan_tls",
    "deep_scan_dns",
    "deep_scan_whois",
    "port_enumeration",
    "tech_detection",
    "vulnerability_check",
    "manual_review",
    "escalate_alert",
    "skip_target",
]

# Export configuration
EXPORT_FORMATS = ["json", "csv", "html", "pdf"]

# API configuration
API_DEFAULT_TIMEOUT = 30
API_MAX_RESULTS = 1000

# Feature importance thresholds
FEATURE_IMPORTANCE_THRESHOLD = 0.01
ANOMALY_DETECTION_THRESHOLD = 0.95

# Explainability configuration
SHAP_SAMPLE_SIZE = 100
EXPLANATION_WORD_LIMIT = 200

# Database configuration (if needed)
DB_POOL_SIZE = 5
DB_POOL_TIMEOUT = 30
DB_ECHO = False
