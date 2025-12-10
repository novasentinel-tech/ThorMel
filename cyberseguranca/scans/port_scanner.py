"""
Scanner de Portas e Serviços v3.0
Esse aqui é o porteiro. Ele bate em cada porta pra ver qual está
aberta e tenta adivinhar o que tem lá dentro.
"""

import socket
import concurrent.futures
import asyncio
import aiohttp
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from scans.base_scanner import BaseScanner
from urllib.parse import urlparse
import re

class ScanType(Enum):
    TCP_CONNECT = "tcp_connect"
    TCP_SYN = "tcp_syn"
    UDP = "udp"
    FIN = "fin"
    XMAS = "xmas"
    NULL = "null"

class PortState(Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    OPEN_FILTERED = "open|filtered"
    UNFILTERED = "unfiltered"

class ServiceInfo:
    """Uma classe só pra guardar as infos do que a gente acha em cada porta."""
    def __init__(self):
        self.port = 0
        self.protocol = "tcp"
        self.service_name = "unknown"
        self.version = ""
        self.banner = ""
        self.risk_level = "low"
        self.vulnerabilities = []
        self.recommendations = []

class PortScanner(BaseScanner):
    """
    Scanner de portas com várias técnicas, pra ser rápido e discreto.
    """
    
    CRITICAL_PORTS = {
        'web_services': [80, 443, 8080, 8443, 8000, 3000, 5000],
        'remote_access': [22, 23, 3389, 5900, 5901],
        'databases': [1433, 1521, 3306, 5432, 27017, 6379],
        'file_services': [21, 445, 139, 2049],
    }
    
    SERVICE_VULNERABILITIES = {
        'ssh': {'weak_authentication': 'Risco alto se tiver senhas fracas'},
        'ftp': {'clear_text': 'Credenciais em texto puro, maior furada'},
        'telnet': {'clear_text': 'Tudo em texto puro, pior ainda'},
        'rdp': {'bluekeep': 'Vulnerabilidade crítica de RCE'},
        'smb': {'eternalblue': 'A famosa falha do WannaCry'}
    }
    
    def __init__(self, target_url: str, timeout: int = 3, max_workers: int = 50,
                 scan_type: ScanType = ScanType.TCP_CONNECT, stealth_mode: bool = True,
                 port_range: Tuple[int, int] = (1, 1000), detect_services: bool = True):
        super().__init__(target_url, timeout)
        
        self.max_workers = max_workers
        self.scan_type = scan_type
        self.stealth_mode = stealth_mode
        self.port_range = port_range
        self.detect_services = detect_services
        self.target_host = self.extract_hostname()
        
        self.open_ports = []
        self.service_info = {}
        self.scan_results = {}
        self.firewall_detected = False
        
        self.scan_delay = 0.1 if stealth_mode else 0.01
        self.max_retries = 2
        
    def extract_hostname(self) -> str:
        """Pega só o nome do site (ex: 'google.com') da URL completa."""
        parsed = urlparse(self.target_url)
        return parsed.hostname
    
    def get_ports_to_scan(self) -> List[int]:
        """Decide quais portas vamos 'bater'."""
        if self.port_range == (1, 1000):
            common_ports = set()
            for category, ports in self.CRITICAL_PORTS.items():
                common_ports.update(ports)
            common_ports.update(range(1, 1001))
            return sorted(common_ports)
        else:
            return list(range(self.port_range[0], self.port_range[1] + 1))
    
    def tcp_connect_scan(self, port: int) -> Tuple[PortState, Optional[str]]:
        """O jeito mais simples de checar uma porta: tenta conectar."""
        try:
            if self.stealth_mode:
                time.sleep(random.uniform(0.05, 0.2))
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((self.target_host, port))
                
                if result == 0:
                    banner = self.grab_banner(sock, port)
                    return (PortState.OPEN, banner)
                else:
                    return (PortState.CLOSED, None)
                    
        except socket.timeout:
            return (PortState.FILTERED, None)
        except socket.error as e:
            self.add_debug(f"Erro no scan da porta {port}: {e}")
            return (PortState.FILTERED, None)
    
    def grab_banner(self, sock: socket.socket, port: int) -> Optional[str]:
        """Se a porta tá aberta, a gente tenta 'ouvir' o que ela diz pra se apresentar."""
        try:
            sock.settimeout(2)
            if port == 22:
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                return banner.strip()
            elif port in [80, 443]:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                return banner.strip()
            else:
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                return banner.strip() if banner else None
                    
        except (socket.timeout, socket.error, UnicodeDecodeError):
            return None
        return None
    
    def identify_service(self, port: int, banner: Optional[str]) -> ServiceInfo:
        """Tenta adivinhar qual serviço tá rodando na porta."""
        service = ServiceInfo()
        service.port = port
        service.banner = banner or ""
        
        common_services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 80: 'http', 443: 'https', 3306: 'mysql', 5432: 'postgresql', 27017: 'mongodb'
        }
        service.service_name = common_services.get(port, 'unknown')
        
        if banner:
            service.version = self.extract_version_from_banner(banner, service.service_name)
        
        service.risk_level = self.assess_service_risk(service)
        service.recommendations = self.generate_service_recommendations(service)
        
        return service
    
    def extract_version_from_banner(self, banner: str, service_name: str) -> str:
        """Se o serviço se apresentou, a gente tenta pegar a versão dele."""
        version_patterns = {
            'ssh': r'SSH-[\d\.]+-([\w\d\.]+)', 'apache': r'Apache/([\d\.]+)', 'nginx': r'nginx/([\d\.]+)'
        }
        pattern = version_patterns.get(service_name)
        if pattern:
            match = re.search(pattern, banner, re.IGNORECASE)
            if match: return match.group(1)
        return ""
    
    def assess_service_risk(self, service: ServiceInfo) -> str:
        """Avalia o nível de perigo de um serviço estar aberto pra internet."""
        if service.service_name in ['telnet', 'ftp']: return "high"
        if service.service_name in ['ssh', 'rdp']: return "medium"
        return "low"
    
    def generate_service_recommendations(self, service: ServiceInfo) -> List[str]:
        """Dá umas dicas de como proteger o serviço que a gente achou."""
        recommendations = []
        if service.service_name == 'ftp': recommendations.append("Trocar FTP por SFTP ou FTPS.")
        elif service.service_name == 'telnet': recommendations.append("TROCAR POR SSH IMEDIATAMENTE.")
        elif service.service_name == 'ssh': recommendations.append("Usar autenticação por chaves, não senhas.")
        recommendations.append("Manter o software atualizado e monitorar os logs.")
        return recommendations
    
    def detect_firewall(self, scan_results: Dict[int, PortState]) -> bool:
        """Tenta adivinhar se tem um firewall no meio do caminho."""
        filtered_ports = [p for p, s in scan_results.items() if s == PortState.FILTERED]
        open_ports = [p for p, s in scan_results.items() if s == PortState.OPEN]
        if len(filtered_ports) > len(open_ports) * 2:
            return True
        return False
    
    def perform_parallel_scan(self) -> Dict[int, PortState]:
        """Usa várias 'threads' pra escanear as portas ao mesmo tempo e ser mais rápido."""
        ports_to_scan = self.get_ports_to_scan()
        results = {}
        
        self.add_info(f"Iniciando scan de {len(ports_to_scan)} portas em {self.target_host}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_port = {executor.submit(self.tcp_connect_scan, port): port for port in ports_to_scan}
            
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    state, banner = future.result()
                    results[port] = state
                    if state == PortState.OPEN:
                        self.open_ports.append(port)
                        self.add_info(f"Porta {port}/tcp ABERTA")
                        if self.detect_services:
                            self.service_info[port] = self.identify_service(port, banner)
                except Exception as e:
                    self.add_warning(f"Erro no scan da porta {port}: {e}")
        
        return results
    
    def generate_security_report(self) -> Dict:
        """Cria o relatório final do scan de portas."""
        report = {
            'target': self.target_host,
            'scan_timestamp': datetime.now().isoformat(),
            'results': {
                'total_ports_scanned': len(self.get_ports_to_scan()),
                'open_ports': len(self.open_ports),
                'firewall_detected': self.firewall_detected
            },
            'services': {},
            'recommendations': []
        }
        
        for port, service in self.service_info.items():
            report['services'][port] = {
                'name': service.service_name, 'version': service.version, 'risk_level': service.risk_level
            }
        
        if self.firewall_detected: report['recommendations'].append("Firewall detectado - revisar regras.")
        
        return report
    
    def scan(self):
        """Começa o scan de portas."""
        print(f"    [+] Iniciando scan de portas em: {self.target_host}")
        if not self.target_host:
            self.add_warning("Não foi possível extrair hostname da URL")
            return self.results
        
        start_time = time.time()
        
        try:
            scan_results = self.perform_parallel_scan()
            self.firewall_detected = self.detect_firewall(scan_results)
            
            scan_duration = time.time() - start_time
            self.add_info(f"⏱️ Scan concluído em {scan_duration:.2f} segundos")
            self.add_info(f"🔍 Portas abertas: {len(self.open_ports)}")
            
            if self.open_ports:
                high_risk = [f"{p}/{s.service_name}" for p, s in self.service_info.items() if s.risk_level == 'high']
                if high_risk: self.add_vulnerability(f"Serviços de alto risco: {', '.join(high_risk)}")
            
            self.results['port_scan_report'] = self.generate_security_report()
            
        except Exception as e:
            self.add_warning(f"Erro durante scan de portas: {str(e)}")
        
        return self.results
