"""
As Configurações da Máquina
Aqui a gente ajusta os 'parafusos' do scanner.
"""

# =============================================================================
# AJUSTES FINOS - Pra máquina não explodir
# =============================================================================

REQUEST_TIMEOUT = 5
MAX_WORKERS = 8
DEFAULT_USER_AGENT = "Security-Scanner/3.0"
SCAN_DELAY = 0.3
MAX_CONCURRENT_REQUESTS = 10
RATE_LIMIT_DELAY = 0.5
MAX_RETRIES = 3
VERIFY_SSL = True
SCAN_TIMEOUT = 5

# =============================================================================
# CONFIGURAÇÕES DO SCANNER BASE (O 'PAI' de todos)
# =============================================================================

BASE_SCANNER_CONFIG = {
    'timeout': REQUEST_TIMEOUT,
    'max_redirects': 5,
    'rate_limit_delay': RATE_LIMIT_DELAY,
    'max_retries': MAX_RETRIES,
    'verify_ssl': VERIFY_SSL,
    'debug': False,
    'safe_mode': True
}

# Nossos disfarces pra não parecermos um robô
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Security-Scanner/3.0 (Compatible; Security Audit)"
]

# =============================================================================
# SQL INJECTION - Os truques clássicos
# =============================================================================

SQL_INJECTION_CONFIG = {
    'aggressive': False,
    'detect_blind': True,
    'test_nosql': True,
    'timeout': REQUEST_TIMEOUT,
    'test_post_params': True,
    'test_headers': True,
    'max_payloads_per_param': 10
}

# As 'iscas' que a gente joga pra ver se o banco de dados morde
SQL_PAYLOADS = {
    'error_based': [
        "'", "''", "`", "\"",
        "' AND 1=1 -- ",
        "' AND 1=2 -- ",
        "' OR '1'='1",
    ],
    'union_based': [
        "' UNION SELECT 1,2,3 -- ",
        "' UNION SELECT null,version(),user() -- ",
    ],
    'time_based': [
        "' AND SLEEP(5) -- ",
        "' AND pg_sleep(5) -- ",
        "' AND WAITFOR DELAY '0:0:5' -- ",
    ],
    'boolean_based': [
        "' AND 1=1 -- ",
        "' AND 1=2 -- ",
        "' AND 'a'='a",
        "' AND 'a'='b",
    ],
    'waf_bypass': [
        "/*!50000'*/",
        "'/*!50000OR*/1=1--",
        "'%20OR%201=1--",
        "'/**/OR/**/1=1--",
    ]
}

# Payloads pra zoar bancos NoSQL (tipo MongoDB)
NOSQL_PAYLOADS = {
    'mongo_operator': [
        '{"$ne": "invalid"}',
        '{"$gt": ""}',
        '{"$regex": ".*"}',
        '{"$where": "true"}',
    ],
    'json_injection': [
        '{"username": {"$ne": null}, "password": {"$ne": null}}',
        '{"$or": [{"username": "admin"}, {"password": "admin"}]}',
    ]
}

# =============================================================================
# XSS - Fazendo o site 'falar' o que a gente quer
# =============================================================================

XSS_SCAN_CONFIG = {
    'request_delay': 0.5,
    'max_payloads_per_param': 15,
    'test_json': True,
    'test_cookies': True,
    'test_headers': True,
    'test_dom_based': True,
    'advanced_evasion': True,
    'timeout': REQUEST_TIMEOUT,
    'safe_mode': True,
    'max_requests_per_minute': 30
}

# Payloads de XSS pra cada situação
XSS_PAYLOADS = {
    'html_context': [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "<ScRiPt>alert(1)</sCrIpT>",
    ],
    'attribute_context': [
        "\" onmouseover=\"alert(1)",
        "' onfocus='alert(1)'",
        " onload=\"alert(1)\"",
        " autofocus onfocus=alert(1)",
    ],
    'javascript_context': [
        "'; alert(1); //",
        "\"; alert(1); //",
        "`; alert(1); //",
        "</script><script>alert(1)</script>",
    ],
    'dom_context': [
        "#<img src=x onerror=alert(1)>",
        "?test=<script>alert(1)</script>",
        "#javascript:alert(1)",
    ],
    'waf_bypass': [
        "<scr<script>ipt>alert(1)</scr</script>ipt>",
        "<img\tsrc=x\tonerror=alert(1)>",
        "%3Cscript%3Ealert(1)%3C/script%3E",
    ]
}

# =============================================================================
# DIRECTORY TRAVERSAL - Espiando onde não devemos
# =============================================================================

DIRECTORY_TRAVERSAL_CONFIG = {
    'max_concurrent': 5,
    'safe_mode': True,
    'timeout': REQUEST_TIMEOUT,
    'test_headers': True,
    'max_payloads_per_param': 8
}

# Payloads pra tentar voltar umas pastas e achar arquivos secretos
DIRECTORY_TRAVERSAL_PAYLOADS = {
    'linux': [
        "../../../../etc/passwd",
        "../../../../etc/shadow",
        "../../../../etc/hosts",
        "../../../../proc/self/environ",
        "../../../../var/log/auth.log",
    ],
    'windows': [
        "..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "..\\..\\..\\..\\windows\\win.ini",
        "..\\..\\..\\..\\windows\\system.ini",
    ],
    'web_apps': [
        "../../../../.env",
        "../../../../config.php",
        "../../../../wp-config.php",
        "../../../../web.config",
        "../../../../.htaccess",
    ],
    'encoding': [
        "..%2f..%2f..%2f..%2fetc%2fpasswd",
        "..%252f..%252f..%252f..%252fetc%252fpasswd",
        "%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd",
    ]
}

# Palavras que, se aparecerem, é porque deu bom (ou ruim pro site)
SENSITIVE_CONTENT_PATTERNS = {
    'etc_passwd': [r'root:.*:0:0:', r'\/bin\/(bash|sh)', r'[a-z-]+:x:\d+:\d+:'],
    'etc_shadow': [r'root:.*:\d+:', r'[a-z-]+:\$.\$.*:\d+:'],
    'windows_system': [r'\[boot loader\]', r'\[fonts\]', r'\[extensions\]'],
    'environment_vars': [r'PATH=.*', r'HOME=.*', r'USER=.*'],
    'web_configs': [r'\$db_.*=', r'DATABASE_URL=', r'SECRET_KEY=']
}

# =============================================================================
# PORT SCANNER - Batendo nas portas pra ver quem atende
# =============================================================================

PORT_SCANNER_CONFIG = {
    'timeout': 3,
    'max_workers': 50,
    'stealth_mode': True,
    'port_range': (1, 1000),
    'detect_services': True,
    'scan_delay': 0.1
}

# Portas mais famosinhas pra gente checar
COMMON_PORTS = {
    'web_services': [80, 443, 8080, 8443, 8000, 3000, 5000],
    'remote_access': [22, 23, 3389, 5900, 5901],
    'databases': [1433, 1521, 3306, 5432, 27017, 6379],
    'file_services': [21, 445, 139, 2049],
    'mail_services': [25, 110, 143, 993, 995, 587],
    'management': [161, 162, 514, 902, 623],
    'vpn_services': [500, 1701, 1723, 4500]
}

# Serviços que a gente sabe que costumam dar problema
SERVICE_VULNERABILITIES = {
    'ssh': ['weak_authentication', 'old_protocols', 'crypto_weakness'],
    'ftp': ['clear_text', 'anonymous_access', 'bounce_attack'],
    'telnet': ['clear_text', 'no_encryption'],
    'rdp': ['bluekeep', 'weak_encryption'],
    'smb': ['eternalblue', 'null_session']
}

# =============================================================================
# HEADER SECURITY - Checando os 'seguranças' do site
# =============================================================================

HEADER_SECURITY_CONFIG = {
    'timeout': REQUEST_TIMEOUT,
    'check_cookies': True,
    'check_cache_headers': True,
    'check_cors': True,
    'test_multiple_endpoints': True,
    'max_risk_score': 100
}

# Os seguranças que a gente quer ver na porta
SECURITY_HEADERS = {
    'critical': [
        'Strict-Transport-Security',
        'Content-Security-Policy', 
        'X-Content-Type-Options'
    ],
    'important': [
        'X-Frame-Options',
        'Referrer-Policy',
        'Permissions-Policy'
    ],
    'additional': [
        'Cross-Origin-Opener-Policy',
        'Cross-Origin-Resource-Policy',
        'X-XSS-Protection'
    ]
}

# Como os seguranças deveriam se comportar
HEADER_OPTIMAL_VALUES = {
    'Strict-Transport-Security': ['max-age=31536000', 'includeSubDomains', 'preload'],
    'Content-Security-Policy': ["default-src 'self'"],
    'X-Content-Type-Options': ['nosniff'],
    'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
    'Referrer-Policy': ['strict-origin-when-cross-origin', 'no-referrer']
}

# =============================================================================
# FORM ANALYZER - De olho nos formulários
# =============================================================================

FORM_ANALYSIS_CONFIG = {
    'safe_audit': True,
    'check_csrf': True,
    'check_autocomplete': True,
    'analyze_hidden_fields': True,
    'validate_action_urls': True,
    'classify_forms': True,
    'verbose_logging': False
}

# O peso de cada mancada, dependendo do tipo de formulário
FORM_RISK_WEIGHTS = {
    'login': {
        'csrf_missing': 30,
        'password_autocomplete': 25,
        'get_with_sensitive_data': 40,
        'external_action': 35,
        'mixed_content': 45
    },
    'payment': {
        'csrf_missing': 25,
        'password_autocomplete': 20,
        'get_with_sensitive_data': 50,
        'external_action': 45,
        'mixed_content': 50
    },
    'registration': {
        'csrf_missing': 25,
        'password_autocomplete': 25,
        'get_with_sensitive_data': 35,
        'external_action': 30
    },
    'default': {
        'csrf_missing': 20,
        'password_autocomplete': 15,
        'get_with_sensitive_data': 25,
        'external_action': 30
    }
}

# Padrões de nomes de campos que guardam coisa séria
SENSITIVE_FIELD_PATTERNS = {
    'brazilian': {
        'cpf': r'cpf|taxid|identidade',
        'cnpj': r'cnpj|empresa|company',
        'rg': r'rg|registro',
        'cartao': r'cartao|card|credit',
        'senha': r'senha|password'
    },
    'global': {
        'ssn': r'ssn|social.security',
        'national_id': r'national.id|passport|driver.license',
        'credit_card': r'credit.card|card.number|cc.number',
        'bank_account': r'bank.account|iban|routing.number',
        'dob': r'date.of.birth|dob|birth.date'
    }
}

# =============================================================================
# SSL/TLS - O cadeado do site é de verdade?
# =============================================================================

SSL_CHECK_CONFIG = {
    'timeout': 5,
    'check_expiration': True,
    'expiration_warning_days': 30,
    'check_protocols': True,
    'check_ciphers': True
}

# =============================================================================
# MODO RÁPIDO - Pra quando a gente tá com pressa
# =============================================================================

QUICK_MODE_CONFIG = {
    'sql_payloads': ["'", "1' OR '1'='1"],
    'xss_payloads': ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"],
    'ports': [80, 443, 8080, 22, 21],
    'traversal_payloads': ["../../../../etc/passwd"],
    'timeout': 3,
    'workers': 4,
    'max_payloads_per_param': 5,
    'detect_blind': False
}

# =============================================================================
# LIMITES - Pra gente não ser bloqueado (ou derrubar o site)
# =============================================================================

SCAN_LIMITS = {
    'max_requests_per_minute': 60,
    'max_redirects': 5,
    'max_response_size': 10485760,
    'timeout_total': 300,
    'max_ports_per_scan': 1000,
    'max_forms_per_page': 20
}

# =============================================================================
# RELATÓRIOS - Como a gente quer a saída
# =============================================================================

REPORT_CONFIG = {
    'include_info': True,
    'risk_scoring': True,
    'export_json': True,
    'color_output': True,
    'generate_compliance_report': True,
    'save_audit_log': True,
    'owasp_format': True
}

# Regras de 'compliance' (pra ver se o site segue as boas práticas)
COMPLIANCE_FRAMEWORKS = {
    'GDPR_LGPD': {
        'requirements': ['password_autocomplete', 'sensitive_data_exposure'],
        'weight': 30
    },
    'PCI_DSS': {
        'requirements': ['get_with_sensitive_data', 'mixed_content', 'financial_autocomplete'],
        'weight': 40
    },
    'ISO_27001': {
        'requirements': ['csrf_missing', 'external_action', 'sensitive_data_exposure'],
        'weight': 25
    }
}

# =============================================================================
# OPSEC - Coisas pra nossa própria segurança
# =============================================================================

SECURITY_CONFIG = {
    'restricted_hosts': [
        'localhost', '127.0.0.1', '0.0.0.0', '::1',
        '169.254.169.254',
        'metadata.google.internal'
    ],
    'allowed_methods': ['GET', 'POST', 'HEAD', 'OPTIONS'],
    'max_post_size': 1048576,
    'allow_file_uploads': False
}

# =============================================================================
# PERFORMANCE AVANÇADA - Pra quem manja dos paranauê
# =============================================================================

PERFORMANCE_CONFIG = {
    'thread_pool_size': MAX_WORKERS,
    'connection_pool_size': 10,
    'dns_cache_ttl': 300,
    'keep_alive': True,
    'compress_responses': True
}
