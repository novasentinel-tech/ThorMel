"""
Constants used throughout the DeepAI system.
"""

# Feature-related constants
TOTAL_FEATURE_COUNT = 87

# Risk classification levels
RISK_LEVELS = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH",
    3: "CRITICAL",
}

RISK_LEVEL_SCORES = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}

# Default thresholds for classification
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_CRITICAL_THRESHOLD = 0.3  # Lower threshold for CRITICAL (conservative)

# RL Actions
RL_ACTIONS = {
    0: "PRIORITY_CRITICAL",
    1: "PRIORITY_HIGH",
    2: "PRIORITY_MEDIUM",
    3: "PRIORITY_LOW",
    4: "PRIORITY_IGNORE",
    5: "REQUEST_RESCAN",
    6: "REQUEST_DEEP_SCAN",
    7: "FLAG_FOR_REVIEW",
    8: "ADJUST_THRESHOLD_UP",
    9: "ADJUST_THRESHOLD_DOWN",
}

# Feedback outcome types
FEEDBACK_OUTCOMES = {
    "true_positive": 1,
    "false_positive": 0,
    "true_negative": -1,
    "false_negative": -2,
}

# HTTP status codes
HTTP_STATUS = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "TIMEOUT": 408,
    "TOO_MANY_REQUESTS": 429,
    "SERVER_ERROR": 500,
}

# Default timeouts (seconds)
TIMEOUT_HTTP = 10
TIMEOUT_TLS = 15
TIMEOUT_DNS = 5
TIMEOUT_WHOIS = 10
TIMEOUT_PORT = 20
TIMEOUT_TOTAL_SCAN = 60

# TLS versions
TLS_VERSIONS = {
    "SSLv3": 1.0,
    "TLSv1.0": 1.0,
    "TLSv1.1": 1.1,
    "TLSv1.2": 1.2,
    "TLSv1.3": 1.3,
}

# Common ports for service detection
COMMON_PORTS = {
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    465: "SMTPS",
    587: "SMTP_SUBMISSION",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    27017: "MongoDB",
    8080: "HTTP_PROXY",
    8443: "HTTPS_ALT",
}

# Database detection ports
DATABASE_PORTS = {3306, 5432, 27017, 6379, 1433, 1521, 5984}

# Admin panel paths
ADMIN_PATHS = {
    "/admin",
    "/wp-admin",
    "/administrator",
    "/admin.php",
    "/admin/login",
    "/login",
    "/user/login",
    "/access",
    "/sign-in",
}

# Sensitive file extensions
SENSITIVE_EXTENSIONS = {
    ".bak",
    ".old",
    ".sql",
    ".db",
    ".backup",
    ".config",
    ".ini",
    ".env",
    ".git",
    ".svn",
}

# Model versions
ML_MODEL_VERSION = "2.3.1"
RL_MODEL_VERSION = "1.2.0"
SHAP_EXPLAINER_VERSION = "1.0.0"

# Feature groups (for organization)
FEATURE_GROUPS = {
    "TLS_SSL": 12,
    "HTTP_HEADERS": 18,
    "DNS_CONFIG": 10,
    "TECH_STACK": 15,
    "PORTS_SERVICES": 12,
    "WEB_APP": 10,
    "INFRASTRUCTURE": 10,
}

# Severity scores for different vulnerability types
SEVERITY_SCORES = {
    "expired_certificate": 0.7,
    "tls_weak_cipher": 0.6,
    "missing_hsts": 0.5,
    "database_exposed": 0.95,
    "admin_panel_exposed": 0.8,
    "outdated_cms": 0.7,
    "outdated_framework": 0.5,
    "missing_csp": 0.4,
}
