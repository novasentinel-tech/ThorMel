"""
Blocked domains list for security enforcement.
This list is loaded on startup and cannot be circumvented.
"""

# TLDs (Top-Level Domains) that are completely blocked
BLOCKED_TLDS = {
    ".gov",
    ".mil",
    ".gov.br",
    ".gov.uk",
    ".gov.au",
    ".gov.in",
    ".gob.es",
    ".gob.mx",
    ".mil.br",
    ".army.mil",
    ".navy.mil",
    ".defense.gov",
    ".nsa.gov",
    ".fbi.gov",
    ".cia.gov",
}

# Keywords that trigger blocking (case-insensitive matching)
BLOCKED_KEYWORDS = {
    # Financial institutions
    "bank",
    "banco",
    "hsbc",
    "chase",
    "wellsfargo",
    "citibank",
    "credit",
    "creditsuisse",
    # Healthcare
    "hospital",
    "health",
    "medic",
    "clinic",
    "pharmacy",
    # Critical infrastructure
    "utility",
    "power",
    "electric",
    "water",
    "gas",
    "nuclear",
    "dam",
    "grid",
    # Government & election
    "election",
    "voting",
    "vote",
    "congress",
    "parliament",
    "senate",
    # Emergency services
    "police",
    "fire",
    "emergency",
    "911",
    # Military & defense
    "defense",
    "military",
    "pentagon",
    "war",
}

# Explicitly whitelisted domains (for testing)
# Only use these for academic testing with consent
WHITELISTED_DOMAINS = {
    "example.com",
    "test.com",
    "localhost",
    "127.0.0.1",
    "example.org",
    "example.net",
}

# Critical infrastructure domains (CISA list subset)
# These should NOT be scanned without explicit authorization
CRITICAL_INFRASTRUCTURE_DOMAINS = {
    "faa.gov",
    "tsa.gov",
    "cdc.gov",
    "nih.gov",
    "fda.gov",
    "usda.gov",
    "energy.gov",
    "water.usgs.gov",
}
