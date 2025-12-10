"""
Scanner de Cabeçalhos de Segurança (v2.0)
Os headers são tipo os 'seguranças' de um site. A gente vai ver se
eles estão fazendo o trabalho direito ou se estão dormindo no ponto.
"""

from scans.base_scanner import BaseScanner
from urllib.parse import urlparse
import re
import ssl
import socket
from datetime import datetime

class HeaderSecurityScanner(BaseScanner):
    def __init__(self, target_url, timeout=10):
        super().__init__(target_url, timeout)
        self.risk_score = 0
        self.max_risk_score = 100
        self.security_headers_checked = 0
        self.cookies_analyzed = 0
    
    def get_security_headers_config(self):
        """A nossa 'lista de chamada' dos seguranças (headers) e o que a gente espera deles."""
        return {
            'critical': {
                'Strict-Transport-Security': {'required': True, 'risk_weight': 25, 'optimal_values': ['max-age=31536000', 'includeSubDomains'], 'description': 'Força o site a usar HTTPS.'},
                'Content-Security-Policy': {'required': True, 'risk_weight': 30, 'optimal_values': ["default-src 'self'"], 'description': 'Controla de onde o site pode carregar coisas (scripts, imagens), prevenindo XSS.'},
                'X-Content-Type-Options': {'required': True, 'risk_weight': 15, 'optimal_values': ['nosniff'], 'description': 'Impede que o navegador tente adivinhar o tipo de um arquivo, o que pode ser perigoso.'}
            },
            'important': {
                'X-Frame-Options': {'required': False, 'risk_weight': 20, 'optimal_values': ['DENY', 'SAMEORIGIN'], 'description': 'Protege contra "clickjacking" (quando alguém coloca seu site dentro de um iframe malicioso).'},
                'Referrer-Policy': {'required': False, 'risk_weight': 15, 'optimal_values': ['strict-origin-when-cross-origin', 'no-referrer'], 'description': 'Controla qual informação de referência é enviada quando você clica num link.'}
            },
            'additional': {
                'Permissions-Policy': {'required': False, 'risk_weight': 15, 'optimal_values': [], 'description': 'Controla o que o site pode fazer no navegador (usar câmera, microfone, etc).'}
            }
        }
    
    def analyze_security_headers(self, headers):
        """Passa a lista de chamada e vê quem faltou ou quem tá fazendo corpo mole."""
        headers_config = self.get_security_headers_config()
        findings = []
        
        for category, header_defs in headers_config.items():
            for header_name, config in header_defs.items():
                self.security_headers_checked += 1
                
                if header_name in headers:
                    header_value = headers[header_name]
                    validation_result = self.validate_header_value(header_name, header_value, config)
                    
                    if validation_result['is_optimal']:
                        self.add_info(f"✅ {header_name}: Configuração ótima - {header_value}")
                    elif validation_result['has_issues']:
                        self.add_warning(f"⚠️ {header_name}: Problemas na configuração - {header_value}")
                        for issue in validation_result['issues']: self.add_warning(f"   - {issue}")
                    else:
                        self.add_info(f"ℹ️ {header_name}: Presente - {header_value}")
                    
                    findings.append({'header': header_name, 'value': header_value, 'category': category, 'validation': validation_result})
                    
                else:
                    if config['required']:
                        self.add_vulnerability(f"🔴 {header_name}: Header crítico ausente")
                        self.risk_score += config['risk_weight']
                    else:
                        self.add_warning(f"🟡 {header_name}: Header recomendado ausente")
                        self.risk_score += config['risk_weight'] // 2
        
        return findings
    
    def validate_header_value(self, header_name, header_value, config):
        """Valida se o valor do header tá configurado do jeito certo."""
        result = {'is_optimal': False, 'has_issues': False, 'issues': []}
        header_value_lower = header_value.lower()
        
        # Lógica de validação simplificada
        if header_name == 'Content-Security-Policy' and ("'unsafe-inline'" in header_value_lower or "'unsafe-eval'" in header_value_lower):
            result['has_issues'] = True
            result['issues'].append("CSP permite 'unsafe-inline' ou 'unsafe-eval', o que é perigoso.")
        
        elif header_name == 'Strict-Transport-Security':
            match = re.search(r'max-age=(\d+)', header_value_lower)
            if match and int(match.group(1)) < 31536000:
                result['has_issues'] = True
                result['issues'].append("HSTS max-age muito curto.")
        
        # Checa se os valores ótimos estão lá
        if config.get('optimal_values') and any(opt.lower() in header_value_lower for opt in config['optimal_values']):
            result['is_optimal'] = True

        return result

    def analyze_cookies(self, response):
        """Dá uma olhada nos cookies pra ver se eles estão bem protegidos."""
        cookies = response.cookies
        self.cookies_analyzed = len(cookies)
        
        if not cookies:
            self.add_info("ℹ️ Nenhum cookie encontrado")
            return
        
        security_issues = []
        for cookie in cookies:
            cookie_issues = []
            if not cookie.secure: cookie_issues.append("Flag Secure ausente")
            if not cookie.has_nonstandard_attr('HttpOnly'):
                if cookie.name in response.headers.get('Set-Cookie', '') and 'HttpOnly' not in response.headers.get('Set-Cookie', ''):
                    cookie_issues.append("Flag HttpOnly ausente")
            
            samesite_value = cookie.get_nonstandard_attr('samesite')
            if not samesite_value or samesite_value.lower() not in ['lax', 'strict']:
                cookie_issues.append(f"SameSite mal configurado (valor: {samesite_value})")

            if cookie_issues:
                security_issues.append(f"Cookie '{cookie.name}': {', '.join(cookie_issues)}")
                self.risk_score += 10
        
        for issue in security_issues: self.add_warning(f"🟡 {issue}")
        if not security_issues: self.add_info("✅ Todos os cookies parecem seguros.")

    def analyze_cache_headers(self, headers):
        """Verifica se o site tá mandando o navegador guardar informações que não deveria."""
        cache_control = headers.get('Cache-Control', '').lower()
        if 'no-store' not in cache_control and 'no-cache' not in cache_control:
            if any(indicator in self.target_url.lower() for indicator in ['login', 'admin', 'user']):
                self.add_warning("🟡 Cache: Página sensível sem diretivas 'no-store' ou 'no-cache'.")
                self.risk_score += 15

    def check_cors_headers(self, headers):
        """Verifica as políticas de CORS pra ver se não tá aberto demais."""
        allow_origin = headers.get('Access-Control-Allow-Origin')
        allow_credentials = headers.get('Access-Control-Allow-Credentials')
        if allow_origin == '*' and allow_credentials == 'true':
            self.add_warning("🟡 CORS: Configuração perigosa que permite qualquer site acessar com credenciais.")
            self.risk_score += 20

    def detect_information_leakage(self, headers):
        """Procura por headers que falam mais do que deveriam (tipo a versão do servidor)."""
        suspicious_headers = ['X-Powered-By', 'Server', 'X-AspNet-Version', 'X-Generator']
        for header in suspicious_headers:
            if header in headers:
                self.add_warning(f"🟡 Header {header} vaza informação: {headers[header]}")
                self.risk_score += 5

    def check_ssl_tls_configuration(self):
        """Verifica o cadeado (SSL/TLS) do site."""
        try:
            hostname = urlparse(self.target_url).hostname
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    protocol = ssock.version()
                    if protocol in ['TLSv1', 'TLSv1.1']:
                        self.add_warning(f"🔴 Protocolo SSL/TLS obsoleto: {protocol}")
                        self.risk_score += 20
        except Exception as e:
            self.add_warning(f"⚠️ Não foi possível verificar SSL/TLS: {e}")
    
    def scan(self):
        """Roda a análise completa dos headers."""
        print(f"    [+] Analisando headers em: {self.target_url}")
        
        if not self.is_valid_url():
            self.add_warning("URL inválida")
            return self.results
        
        response = self.test_endpoint(self.target_url)
        if not response: return self.results
        
        try:
            headers = dict(response.headers)
            
            print("    [+] Analisando headers de segurança...")
            findings = self.analyze_security_headers(headers)
            
            print("    [+] Verificando cookies...")
            self.analyze_cookies(response)
            
            print("    [+] Analisando cache e CORS...")
            self.analyze_cache_headers(headers)
            self.check_cors_headers(headers)
            
            print("    [+] Detectando vazamento de informação...")
            self.detect_information_leakage(headers)
            
            print("    [+] Verificando SSL/TLS...")
            self.check_ssl_tls_configuration()
            
            security_ratio = max(0, (self.security_headers_checked - (self.risk_score / 10)) / self.security_headers_checked)
            security_percentage = min(100, security_ratio * 100)
            
            self.add_info(f"📊 Score de segurança dos headers: {security_percentage:.1f}%")
            
            self.results['security_score'] = security_percentage
            
        except Exception as e:
            self.add_warning(f"Erro durante análise de headers: {str(e)}")
        
        return self.results
