"""
A BASE DE TUDO - O Scanner Original (v3.0)
Todo scanner novo que a gente cria tem que 'aprender' com esse aqui.
Ele já sabe como se comportar na internet: ser educado (rate limit),
ter um disfarce (user-agent) e não desistir fácil (retries).
"""

import requests
from urllib.parse import urlparse
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
from dataclasses import dataclass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import json

@dataclass
class ScanMetrics:
    """Uma classe só pra gente guardar os números do scan."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    average_response_time: float = 0.0
    memory_usage_mb: float = 0.0

class BaseScanner:
    """
    O 'molde' de todos os nossos scanners.
    """
    
    # Nossos disfarces. Uma lista de User-Agents pra gente não parecer um robô.
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Security-Scanner/3.0 (Compatible; Security Audit)"
    ]
    
    def __init__(self, target_url: str, timeout: int = 10, max_redirects: int = 5,
                 rate_limit_delay: float = 0.5, max_retries: int = 3,
                 verify_ssl: bool = True, debug: bool = False):
        
        self.target_url = target_url
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.debug = debug
        
        self.last_request_time = 0
        self.request_count = 0
        self.session = None
        self.results = {
            'vulnerabilities': [],
            'warnings': [],
            'info': [],
            'debug': [] if debug else None
        }
        
        self.metrics = ScanMetrics()
        self.scan_start_time = None
        self.shared_state = {}
        
        self.setup_logging()
        self._initialize_session()
    
    def setup_logging(self):
        """Configura os logs pra gente saber o que tá rolando por debaixo dos panos."""
        self.logger = logging.getLogger(f'scanner.{self.__class__.__name__}')
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
    
    def _initialize_session(self):
        """Prepara nossa 'mochila' pra fazer as requisições (a sessão HTTP)."""
        self.session = requests.Session()
    
        self.session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Se algo der errado, ele tenta de novo sozinho. Esperto, né?
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.verify = self.verify_ssl
        self.session.max_redirects = self.max_redirects
        
        self.logger.info(f"Sessão inicializada para {self.target_url}")
    
    def get_random_user_agent(self) -> str:
        """Pega um disfarce aleatório da nossa lista."""
        return random.choice(self.USER_AGENTS)
    
    def rotate_user_agent(self):
        """Troca de disfarce no meio do caminho."""
        new_agent = self.get_random_user_agent()
        self.session.headers['User-Agent'] = new_agent
        self.logger.debug(f"User-Agent rotacionado para: {new_agent[:50]}...")
    
    def enforce_rate_limit(self):
        """Respira um pouco entre uma requisição e outra pra não ser chato."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
            self.logger.debug(f"Rate limiting aplicado: dormiu {sleep_time:.2f}s")
        
        self.last_request_time = time.time()
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """O coração do scanner: faz a requisição de verdade, com cuidado."""
        self.enforce_rate_limit()
        
        request_kwargs = {
            'timeout': self.timeout,
            'allow_redirects': True,
            'verify': self.verify_ssl
        }
        request_kwargs.update(kwargs)
        
        if self.request_count % 5 == 0:
            self.rotate_user_agent()
        
        start_time = time.time()
        
        try:
            response = self.session.request(method.upper(), url, **request_kwargs)
            self.request_count += 1
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            
            response_time = time.time() - start_time
            self.metrics.total_duration += response_time
            self.metrics.average_response_time = (
                self.metrics.total_duration / self.metrics.total_requests
            )
            
            if 'Retry-After' in response.headers:
                retry_after = int(response.headers['Retry-After'])
                self.logger.warning(f"Rate limit detectado, aguardando {retry_after}s")
                time.sleep(retry_after)
            
            self.logger.debug(f"Request {method} {url} - Status: {response.status_code} - Time: {response_time:.2f}s")
            
            return response
            
        except requests.exceptions.Timeout:
            self.metrics.failed_requests += 1
            self.logger.error(f"Timeout na requisição para {url}")
            return None
            
        except requests.exceptions.ConnectionError as e:
            self.metrics.failed_requests += 1
            self.logger.error(f"Erro de conexão para {url}: {e}")
            return None
            
        except requests.exceptions.HTTPError as e:
            self.metrics.failed_requests += 1
            self.logger.error(f"Erro HTTP para {url}: {e}")
            return None
            
        except requests.exceptions.RequestException as e:
            self.metrics.failed_requests += 1
            self.logger.error(f"Erro na requisição para {url}: {e}")
            return None
        
        except Exception as e:
            self.metrics.failed_requests += 1
            self.logger.error(f"Erro inesperado na requisição para {url}: {e}")
            return None
    
    def test_endpoint(self, url: str, method: str = 'GET', data: Optional[Dict] = None,
                     json_data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[requests.Response]:
        """Testa um endpoint específico, com um pouco mais de validação."""
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        kwargs = {
            'headers': request_headers,
            'allow_redirects': False
        }
        
        if data:
            kwargs['data'] = data
        if json_data:
            kwargs['json'] = json_data
        
        response = self.make_request(url, method, **kwargs)
        
        if response and self.validate_response(response):
            return response
        
        return None
    
    def validate_response(self, response: requests.Response) -> bool:
        """Checa se a resposta do site faz sentido ou se é lixo."""
        if response.status_code >= 500:
            self.logger.warning(f"Status code de erro do servidor: {response.status_code}")
            return False
        
        content_type = response.headers.get('content-type', '').lower()
        if 'application/octet-stream' in content_type and len(response.content) > 1024 * 1024:
            self.logger.warning("Resposta muito grande e tipo binário - ignorando")
            return False
        
        if self.is_generic_error_page(response):
            self.logger.debug("Página de erro genérica detectada")
            return False
        
        if response.is_redirect and self.is_suspicious_redirect(response):
            self.logger.warning(f"Redirecionamento suspeito para: {response.headers.get('location')}")
            return False
        
        return True
    
    def is_generic_error_page(self, response: requests.Response) -> bool:
        """Tenta adivinhar se a página é só uma tela de erro sem graça."""
        error_indicators = [
            'error occurred',
            'page not found',
            'internal server error',
            'website is under maintenance',
            'service unavailable'
        ]
        
        content_lower = response.text.lower()
        return any(indicator in content_lower for indicator in error_indicators)
    
    def is_suspicious_redirect(self, response: requests.Response) -> bool:
        """Vê se o site tá tentando nos mandar pra um lugar estranho."""
        if not response.is_redirect:
            return False
        
        location = response.headers.get('location', '')
        
        target_domain = urlparse(self.target_url).netloc
        redirect_domain = urlparse(location).netloc
        
        if redirect_domain and redirect_domain != target_domain:
            trusted_domains = ['accounts.google.com', 'login.microsoftonline.com', 'facebook.com']
            if not any(trusted in redirect_domain for trusted in trusted_domains):
                return True
        
        if location.startswith('http:') and self.target_url.startswith('https:'):
            return True
        
        return False
    
    def is_valid_url(self) -> bool:
        """Checa se a URL que nos deram é de verdade."""
        try:
            result = urlparse(self.target_url)
            if not all([result.scheme, result.netloc]):
                return False
            
            if self.is_restricted_host(result.netloc):
                self.logger.warning(f"Host restrito detectado: {result.netloc}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar URL: {e}")
            return False
    
    def is_restricted_host(self, hostname: str) -> bool:
        """Não vamos nos auto-atacar, né? Verifica se o alvo não é a nossa própria máquina."""
        restricted_hosts = [
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '::1',
            '169.254.169.254',
            'metadata.google.internal'
        ]
        
        return hostname in restricted_hosts or hostname.endswith('.internal')
    
    def add_vulnerability(self, message: str, evidence: Optional[Dict] = None):
        """ACHEI ALGO! Adiciona uma vulnerabilidade na nossa lista de achados."""
        vulnerability = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'scanner': self.__class__.__name__,
            'evidence': evidence or {}
        }
        self.results['vulnerabilities'].append(vulnerability)
        self.logger.warning(f"VULNERABILIDADE: {message}")
    
    def add_warning(self, message: str):
        """Opa, isso é suspeito. Adiciona um aviso."""
        self.results['warnings'].append({
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'scanner': self.__class__.__name__
        })
        self.logger.warning(f"AVISO: {message}")
    
    def add_info(self, message: str):
        """Só uma informação útil pra gente saber o que rolou."""
        self.results['info'].append({
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'scanner': self.__class__.__name__
        })
        self.logger.info(f"INFO: {message}")
    
    def add_debug(self, message: str):
        """Informação super detalhada que só aparece se a gente estiver no modo 'nerd' (debug)."""
        if self.debug and self.results.get('debug') is not None:
            self.results['debug'].append({
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'scanner': self.__class__.__name__
            })
            self.logger.debug(f"DEBUG: {message}")
    
    def get_metrics_report(self) -> Dict[str, Any]:
        """Mostra os números do scan: quantos requests, quanto tempo, etc."""
        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'success_rate': (self.metrics.successful_requests / self.metrics.total_requests * 100) if self.metrics.total_requests > 0 else 0,
            'total_duration_seconds': self.metrics.total_duration,
            'average_response_time_seconds': self.metrics.average_response_time,
            'requests_per_second': self.metrics.total_requests / self.metrics.total_duration if self.metrics.total_duration > 0 else 0,
            'scan_start_time': self.scan_start_time.isoformat() if self.scan_start_time else None,
            'scan_duration_seconds': (datetime.now() - self.scan_start_time).total_seconds() if self.scan_start_time else 0
        }
    
    def save_scan_report(self, filename: str):
        """Salva tudo que a gente descobriu num arquivo JSON."""
        report = {
            'scan_metadata': {
                'target': self.target_url,
                'scanner': self.__class__.__name__,
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.scan_start_time).total_seconds() if self.scan_start_time else 0
            },
            'results': self.results,
            'metrics': self.get_metrics_report(),
            'configuration': {
                'timeout': self.timeout,
                'max_redirects': self.max_redirects,
                'rate_limit_delay': self.rate_limit_delay,
                'max_retries': self.max_retries,
                'verify_ssl': self.verify_ssl
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Relatório salvo em: {filename}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório: {e}")
    
    def start_scan(self):
        """Aperta o 'play' no scan."""
        self.scan_start_time = datetime.now()
        self.logger.info(f"Iniciando scan em: {self.target_url}")
        self.add_info(f"Scan iniciado em {self.scan_start_time.isoformat()}")
    
    def end_scan(self):
        """Acabou! Hora de registrar os resultados finais."""
        end_time = datetime.now()
        duration = (end_time - self.scan_start_time).total_seconds() if self.scan_start_time else 0
        
        self.add_info(f"Scan finalizado em {end_time.isoformat()}")
        self.add_info(f"Duração total: {duration:.2f} segundos")
        self.add_info(f"Total de requisições: {self.metrics.total_requests}")
        self.add_info(f"Taxa de sucesso: {self.get_metrics_report()['success_rate']:.1f}%")
        
        self.logger.info(f"Scan finalizado - Duração: {duration:.2f}s - Requests: {self.metrics.total_requests}")
    
    def cleanup(self):
        """Arruma a bagunça depois que o scan termina."""
        if self.session:
            self.session.close()
            self.logger.debug("Sessão HTTP fechada")
        
        self.shared_state.clear()
        
        self.logger.info("Cleanup realizado com sucesso")
    
    def scan(self):
        """Cada scanner tem que ter o seu próprio jeito de 'escanear'."""
        raise NotImplementedError("Método scan deve ser implementado pela classe filha")
    
    def __enter__(self):
        self.start_scan()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_scan()
        self.cleanup()
    
    def __del__(self):
        self.cleanup()
