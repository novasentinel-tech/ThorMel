"""
Scanner de Cross-Site Scripting (XSS) v3.0
A gente tenta injetar uns códigos no site e vê se ele 'reflete'
de volta pra gente. Se refletir, é um sinal de perigo.
"""

from scans.base_scanner import BaseScanner
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote, unquote
from html.parser import HTMLParser
import re
import time
import json
import hashlib
from datetime import datetime

class ContextAwareHTMLParser(HTMLParser):
    """Um parser de HTML que entende onde nosso texto foi parar."""
    def __init__(self):
        super().__init__()
        self.reflection_points = []
        self.context_stack = []
    
    def handle_starttag(self, tag, attrs):
        self.context_stack.append(('tag', tag))
        for attr, value in attrs:
            if value:
                self.reflection_points.append({'type': 'attribute', 'tag': tag, 'attribute': attr, 'value': value})
    
    def handle_endtag(self, tag):
        self.context_stack = [ctx for ctx in self.context_stack if ctx[0] != 'tag' or ctx[1] != tag]
    
    def handle_data(self, data):
        if self.context_stack and self.context_stack[-1][0] == 'tag':
            tag = self.context_stack[-1][1]
            context_type = 'javascript' if tag == 'script' else 'html_text'
            self.reflection_points.append({'type': context_type, 'tag': tag, 'content': data.strip()})

class XSSScanner(BaseScanner):
    def __init__(self, target_url, timeout=10, max_requests_per_minute=30, safe_mode=True, verbose_logging=False):
        super().__init__(target_url, timeout)
        self.max_requests_per_minute = max_requests_per_minute
        self.last_request_time = time.time()
        self.audit_log = []
        self.confirmed_vulnerabilities = []
        self.safe_mode = safe_mode
        self.verbose_logging = verbose_logging
        
    def safe_request(self, url, method='GET', data=None):
        """Faz requisições com cuidado, respeitando o limite de velocidade."""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < (60 / self.max_requests_per_minute):
            time.sleep((60 / self.max_requests_per_minute) - time_since_last)
        
        try:
            response = self.session.request(method, url, data=data, timeout=self.timeout, allow_redirects=False)
            self.last_request_time = time.time()
            self.audit_log.append({'timestamp': datetime.now().isoformat(), 'url': url, 'status': response.status_code})
            
            if response.status_code in [403, 429]:
                self.add_warning("Possível bloqueio/WAF detectado - recuando.")
                time.sleep(2)
            
            return response
        except Exception as e:
            self.add_warning(f"Erro na requisição para {url}: {str(e)}")
            return None
    
    def analyze_reflection_context(self, response, test_string):
        """Tenta descobrir 'onde' no HTML o nosso texto foi parar."""
        if test_string not in response.text:
            return None
        
        try:
            parser = ContextAwareHTMLParser()
            parser.feed(response.text)
            for point in parser.reflection_points:
                if test_string in str(point.get('content', '')) or test_string in str(point.get('value', '')):
                    return {'type': point['type'], 'tag': point.get('tag'), 'attribute': point.get('attribute')}
            return self.fallback_context_analysis(response.text, test_string)
        except Exception:
            return self.fallback_context_analysis(response.text, test_string)

    def fallback_context_analysis(self, html, test_string):
        """Se o parser falhar, a gente tenta adivinhar com regex."""
        if re.search(r'<script[^>]*>.*?' + re.escape(test_string), html, re.I | re.S):
            return {'type': 'javascript', 'confidence': 'high'}
        elif re.search(r'<[^>]+\s\w+=(["\']).*?' + re.escape(test_string), html, re.I):
            return {'type': 'attribute', 'confidence': 'medium'}
        return {'type': 'html_text', 'confidence': 'low'}

    def get_context_specific_payloads(self, context_info):
        """Escolhe os melhores payloads dependendo de onde o texto apareceu."""
        payloads = {
            'javascript': ["';alert(1)//", "</script><script>alert(1)</script>"],
            'attribute': ["\" onmouseover=\"alert(1)", "' onfocus='alert(1)'"],
            'html_text': ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"],
            'html_comment': ["--><script>alert(1)</script><!--"]
        }
        return payloads.get(context_info.get('type', 'html_text'), payloads['html_text'])

    def confirm_vulnerability(self, attack_response, payload):
        """Verifica com mais certeza se a vulnerabilidade é real."""
        normalized_attack = unquote(attack_response.text)
        if payload not in normalized_attack:
            return False
        
        # Procura por sinais de que o script seria executado
        if re.search(r'<script[^>]*>.*?' + re.escape(payload), normalized_attack, re.I | re.S):
            return True
        if re.search(r'on\w+=\s*["\']?' + re.escape(payload), normalized_attack, re.I):
            return True
            
        return False
    
    def calculate_vulnerability_score(self, context, reflection_type='reflected'):
        """Dá uma nota para a vulnerabilidade, de 0 a 100."""
        score = 60 # Base score
        if context.get('type') == 'javascript': score *= 1.3
        if context.get('confidence') == 'high': score *= 1.2
        return min(int(score), 100)

    def test_parameter_xss(self, param, context_info):
        """Testa um parâmetro específico pra ver se é vulnerável."""
        payloads = self.get_context_specific_payloads(context_info)
        
        for payload in payloads[:3]: # Limita pra não sobrecarregar
            if self.safe_mode and tested_payloads >= 1: break

            parsed = urlparse(self.target_url)
            params = parse_qs(parsed.query)
            params[param] = [payload]
            test_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(params, doseq=True), parsed.fragment))
            
            attack_response = self.safe_request(test_url)
            if not attack_response: continue
            
            if self.confirm_vulnerability(attack_response, payload):
                score = self.calculate_vulnerability_score(context_info)
                vuln = {'parameter': param, 'payload': payload, 'context': context_info, 'score': score, 'type': 'reflected', 'evidence': self.get_exact_context(attack_response.text, payload)}
                self.confirmed_vulnerabilities.append(vuln)
                self.add_vulnerability(f"XSS Refletido confirmado em '{param}' (Score: {score})")
                return True
        return False

    def get_exact_context(self, html, text):
        """Pega o trecho exato do código onde a nossa string apareceu."""
        index = html.find(text)
        if index == -1: return ""
        start = max(0, index - 50)
        end = min(len(html), index + len(text) + 50)
        return html[start:end].strip()

    def scan(self):
        """Roda o scan de XSS."""
        print(f"    [+] Executando scan de XSS em: {self.target_url}")
        if not self.is_valid_url():
            self.add_warning("URL inválida")
            return self.results
            
        baseline_response = self.safe_request(self.target_url)
        if not baseline_response:
            return self.results
            
        parsed = urlparse(self.target_url)
        params = parse_qs(parsed.query)
        
        if not params:
            self.add_info("Nenhum parâmetro GET para testar.")
            return self.results

        test_string_base = "XSSSCAN" + hashlib.md5(self.target_url.encode()).hexdigest()[:4]
            
        for param, values in params.items():
            if values:
                test_value = f"{test_string_base}_{param}"
                test_params = params.copy()
                test_params[param] = [test_value]
                test_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(test_params, doseq=True), parsed.fragment))
                
                reflection_response = self.safe_request(test_url)
                if reflection_response and test_value in reflection_response.text:
                    context_info = self.analyze_reflection_context(reflection_response, test_value)
                    if context_info:
                        self.add_info(f"Parâmetro '{param}' reflete no contexto: {context_info.get('type')}")
                        self.test_parameter_xss(param, context_info)

        self.add_info(f"Scan de XSS concluído. Vulnerabilidades confirmadas: {len(self.confirmed_vulnerabilities)}")
        self.results['confirmed_vulnerabilities'] = self.confirmed_vulnerabilities
        return self.results
