"""
Analisador de Formulários HTML v3.0
A gente fuça nos formulários pra ver se eles são seguros.
É pela porta da frente (os forms) que muitos dados entram.
"""

from scans.base_scanner import BaseScanner
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import time
from datetime import datetime
import hashlib
import json

class FormAnalyzer(BaseScanner):
    def __init__(self, target_url, timeout=10, safe_audit=True, verbose_logging=False, **kwargs):
        super().__init__(target_url, timeout=timeout, debug=verbose_logging)
        self.safe_audit = safe_audit
        self.verbose_logging = verbose_logging
        self.audit_log = []
        self.risk_score = 0
        self.max_risk_score = 100
        self.risk_weights = self.get_adaptive_risk_weights()
        
    def get_adaptive_risk_weights(self):
        """Define o 'peso' de cada erro, dependendo se o form é de login, pagamento, etc."""
        return {
            'login': {'csrf_missing': 30, 'password_autocomplete': 25, 'get_with_sensitive_data': 40, 'external_action': 35, 'mixed_content': 45},
            'payment': {'csrf_missing': 25, 'password_autocomplete': 20, 'get_with_sensitive_data': 50, 'external_action': 45, 'mixed_content': 50, 'sensitive_data_exposure': 40},
            'registration': {'csrf_missing': 25, 'password_autocomplete': 25, 'get_with_sensitive_data': 35, 'external_action': 30, 'mixed_content': 40},
            'contact': {'csrf_missing': 15, 'password_autocomplete': 10, 'get_with_sensitive_data': 20, 'external_action': 25, 'mixed_content': 30},
            'search': {'csrf_missing': 5, 'password_autocomplete': 5, 'get_with_sensitive_data': 15, 'external_action': 20, 'mixed_content': 20},
            'default': {'csrf_missing': 20, 'password_autocomplete': 15, 'get_with_sensitive_data': 25, 'external_action': 30, 'mixed_content': 35, 'sensitive_data_exposure': 25}
        }
    
    def log_audit_event(self, event_type, details):
        """Registra tudo que a gente faz, pra ter um histórico."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'target_url': self.target_url,
            'details': details,
            'response_hash': hashlib.md5(str(details).encode()).hexdigest()[:16]
        }
        self.audit_log.append(log_entry)
        
        if self.verbose_logging:
            print(f"[AUDIT] {event_type}: {details}")
    
    def detect_sensitive_fields_international(self, form):
        """Procura por nomes de campos que parecem guardar dados importantes (CPF, cartão, etc)."""
        sensitive_patterns = {
            'brazilian': {'cpf': r'cpf|taxid', 'cartao': r'cartao|card|credit', 'senha': r'senha|password'},
            'global': {'ssn': r'ssn|social.security', 'credit_card': r'credit.card|card.number', 'dob': r'date.of.birth'},
            'financial': {'salary': r'salary|income', 'tax': r'tax|revenue'}
        }
        
        findings = []
        form_html = str(form).lower()
        
        for category, patterns in sensitive_patterns.items():
            for field_type, pattern in patterns.items():
                if re.search(pattern, form_html, re.IGNORECASE):
                    findings.append({'category': category, 'field_type': field_type, 'pattern': pattern, 'risk_level': 'high' if category in ['financial', 'global'] else 'medium'})
        
        return findings
    
    def check_csrf_protection_advanced(self, form, response_headers):
        """Verifica se o formulário tem proteção contra um ataque chamado CSRF."""
        csrf_findings = []
        hidden_inputs = form.find_all('input', {'type': 'hidden'})
        csrf_indicators = ['csrf', 'token', 'nonce', 'authenticity', '_token']
        
        csrf_found = False
        for input_field in hidden_inputs:
            input_name = input_field.get('name', '').lower()
            if any(indicator in input_name for indicator in csrf_indicators) and len(input_field.get('value', '')) >= 8:
                csrf_found = True
                self.add_info(f"Token CSRF tradicional encontrado: {input_name}")
                break
        
        if not csrf_found:
            soup = BeautifulSoup(str(form), 'html.parser')
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if any(indicator in meta.get('name', '').lower() for indicator in csrf_indicators) and len(meta.get('content', '')) >= 8:
                    csrf_found = True
                    self.add_info(f"Token CSRF em meta tag: {meta.get('name', '')}")
                    break
        
        if not csrf_found:
            for header_name, header_value in response_headers.items():
                if any(indicator in header_name.lower() for indicator in csrf_indicators) and len(str(header_value)) >= 8:
                    csrf_found = True
                    self.add_info(f"Token CSRF em header: {header_name}")
                    break
        
        if not csrf_found:
            csrf_findings.append('csrf_missing')
            self.add_vulnerability("Proteção CSRF não detectada (verificados: inputs, meta tags, headers)")
        
        return csrf_findings
    
    def validate_action_url_advanced(self, form, base_url, form_type):
        """Valida pra onde o formulário envia os dados."""
        action = form.get('action', '').strip()
        findings = []
        
        if not action: action = base_url
        
        try:
            full_action_url = urljoin(base_url, action)
            parsed_action = urlparse(full_action_url)
            parsed_base = urlparse(base_url)
            
            if parsed_base.scheme == 'https' and parsed_action.scheme == 'http':
                findings.append('mixed_content')
                self.add_vulnerability(f"Mixed Content: Formulário HTTPS enviando para HTTP: {full_action_url}")
            
            if parsed_action.netloc and parsed_action.netloc != parsed_base.netloc:
                trusted_domains = ['paypal.com', 'stripe.com']
                if not any(trusted in parsed_action.netloc for trusted in trusted_domains):
                    findings.append('external_action')
                    risk_level = "ALTO" if form_type == 'payment' else "médio"
                    self.add_vulnerability(f"Action para domínio externo ({risk_level}): {full_action_url}")
            
            suspicious_patterns = [r'\.(tk|ml|ga|cf|gq)$', r'(bit\.ly|tinyurl\.com)', r'\d+\.\d+\.\d+\.\d+']
            for pattern in suspicious_patterns:
                if re.search(pattern, full_action_url, re.IGNORECASE):
                    findings.append('suspicious_action')
                    self.add_warning(f"URL de action potencialmente suspeita: {full_action_url}")
                    
        except Exception as e:
            self.add_warning(f"Erro ao validar action URL: {e}")
        
        return findings
    
    def analyze_form_method_contextual(self, form, form_type):
        """Vê se o método (GET/POST) do form faz sentido para o que ele faz."""
        method = form.get('method', 'GET').upper()
        findings = []
        sensitive_form_types = ['login', 'payment', 'registration']
        
        if method == 'GET' and form_type in sensitive_form_types:
            findings.append('get_with_sensitive_data')
            base_risk = self.risk_weights.get(form_type, self.risk_weights['default']).get('get_with_sensitive_data', 25)
            self.add_vulnerability(f"Método GET em formulário de {form_type} - dados sensíveis podem ficar em logs (Risk: {base_risk})")
        
        return findings
    
    def check_autocomplete_security_advanced(self, form, form_type):
        """Verifica se o navegador pode salvar senhas e dados de cartão automaticamente."""
        findings = []
        password_fields = form.find_all('input', {'type': 'password'})
        for pwd_field in password_fields:
            if pwd_field.get('autocomplete', '').lower() not in ['off', 'new-password', 'current-password']:
                findings.append('password_autocomplete')
                self.add_warning(f"Campo de senha '{pwd_field.get('name', 'sem nome')}' sem autocomplete seguro")
        
        financial_patterns = ['card', 'cvv', 'expiry']
        for input_field in form.find_all('input'):
            if any(pattern in input_field.get('name', '').lower() for pattern in financial_patterns):
                if input_field.get('autocomplete', '').lower() != 'off':
                    findings.append('financial_autocomplete')
                    self.add_warning(f"Campo financeiro '{input_field.get('name', '')}' sem autocomplete=off")
        
        return findings
    
    def classify_form_type_advanced(self, form):
        """Tenta adivinhar qual o tipo do formulário (login, pagamento, etc)."""
        form_html = str(form).lower()
        scoring = {'login': 0, 'payment': 0, 'registration': 0, 'contact': 0, 'search': 0}
        
        login_indicators = ['password', 'signin', 'login']
        for indicator in login_indicators:
            if indicator in form_html: scoring['login'] += 2
        
        payment_indicators = ['card', 'payment', 'pagamento', 'cvv']
        for indicator in payment_indicators:
            if indicator in form_html: scoring['payment'] += 3
        
        registration_indicators = ['register', 'signup', 'cadastro']
        for indicator in registration_indicators:
            if indicator in form_html: scoring['registration'] += 2
        
        max_score = max(scoring.values())
        if max_score == 0: return 'general'
        
        for form_type, score in scoring.items():
            if score == max_score: return form_type
        
        return 'general'
    
    def calculate_contextual_risk_score(self, findings, form_type):
        """Calcula uma nota de risco pro formulário, com base nos problemas achados."""
        weights = self.risk_weights.get(form_type, self.risk_weights['default'])
        score = sum(weights.get(finding, 0) for finding in findings)
        return min(score, self.max_risk_score)
    
    def generate_compliance_report(self, form_details):
        """Gera um 'boletim' pra ver se o site tá seguindo as regras (PCI, GDPR)."""
        compliance_frameworks = {
            'GDPR_LGPD': {'requirements': ['password_autocomplete', 'sensitive_data_exposure'], 'weight': 30},
            'PCI_DSS': {'requirements': ['get_with_sensitive_data', 'mixed_content', 'financial_autocomplete'], 'weight': 40}
        }
        
        compliance_scores = {}
        
        for framework, config in compliance_frameworks.items():
            framework_score = 0
            max_possible = len(config['requirements']) * 10
            
            for requirement in config['requirements']:
                if not any(requirement in form_info['findings'] for form_info in form_details):
                    framework_score += 10
            
            score_percent = (framework_score / max_possible) * 100
            compliance_scores[framework] = {'score': score_percent, 'status': 'COMPLIANT' if score_percent >= 80 else 'NON_COMPLIANT'}
        
        return compliance_scores
    
    def scan(self):
        """Roda a análise completa nos formulários da página."""
        print(f"    [+] Analisando formulários em: {self.target_url}")
        if not self.is_valid_url():
            self.add_warning("URL inválida")
            return self.results
        
        response = self.test_endpoint(self.target_url)
        if not response: return self.results
        
        try:
            self.log_audit_event('scan_started', {'url': self.target_url, 'safe_audit': self.safe_audit})
            
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            self.add_info(f"Encontrados {len(forms)} formulário(s)")
            
            form_details = []
            all_findings = []
            
            for i, form in enumerate(forms, 1):
                print(f"    🔍 Analisando formulário {i}/{len(forms)}...")
                
                form_info = {
                    'index': i,
                    'type': self.classify_form_type_advanced(form),
                    'method': form.get('method', 'GET').upper(),
                    'action': form.get('action', ''),
                    'findings': [],
                    'sensitive_fields': self.detect_sensitive_fields_international(form)
                }
                
                checks = [
                    self.check_csrf_protection_advanced(form, response.headers),
                    self.validate_action_url_advanced(form, self.target_url, form_info['type']),
                    self.check_autocomplete_security_advanced(form, form_info['type']),
                    self.analyze_form_method_contextual(form, form_info['type'])
                ]
                
                for check_result in checks:
                    if check_result:
                        form_info['findings'].extend(check_result)
                        all_findings.extend(check_result)
                
                form_info['risk_score'] = self.calculate_contextual_risk_score(form_info['findings'], form_info['type'])
                form_details.append(form_info)
                self.log_audit_event('form_analyzed', form_info)
            
            overall_risk = sum(f['risk_score'] for f in form_details) / len(form_details) if form_details else 0
            compliance_report = self.generate_compliance_report(form_details)
            
            self.add_info(f"📊 Score de risco geral: {overall_risk:.1f}/100")
            for framework, status in compliance_report.items():
                self.add_info(f"🏛️  {framework}: {status['status']} ({status['score']:.1f}%)")
            
            self.results['form_analysis'] = {
                'summary': {'total_forms': len(form_details), 'overall_risk_score': overall_risk},
                'forms': form_details,
                'compliance': compliance_report,
                'audit_log': self.audit_log
            }
            
            self.log_audit_event('scan_completed', {'total_forms': len(form_details), 'overall_risk': overall_risk})
            
        except Exception as e:
            self.add_warning(f"Erro durante análise de formulários: {str(e)}")
        
        return self.results
