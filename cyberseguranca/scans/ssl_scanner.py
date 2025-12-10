"""
Scanner de SSL/TLS
Basicamente, a gente checa o 'cadeado' do site pra ver se ele é
de verdade ou se é só de enfeite.
"""

import socket
import ssl
from scans.base_scanner import BaseScanner
from urllib.parse import urlparse
from datetime import datetime

class SSLScanner(BaseScanner):
    def __init__(self, target_url, timeout=10):
        super().__init__(target_url, timeout)
    
    def check_certificate(self, hostname):
        """Verifica o certificado SSL."""
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    self.add_info(f"Protocolo: {ssock.version()}")
                    
                    expire_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expire = (expire_date - datetime.now()).days
                    
                    if days_until_expire < 30:
                        self.add_warning(f"Certificado expira em {days_until_expire} dias")
                    else:
                        self.add_info(f"Certificado válido por {days_until_expire} dias")
                    
                    return True
                    
        except ssl.SSLError as e:
            self.add_vulnerability(f"Problema com SSL: {str(e)}")
        except Exception as e:
            self.add_warning(f"Erro ao verificar SSL: {str(e)}")
        
        return False
    
    def scan(self):
        """Executa a verificação."""
        print(f"    [+] Verificando SSL/TLS em: {self.target_url}")
        
        parsed = urlparse(self.target_url)
        hostname = parsed.netloc
        
        if not hostname:
            self.add_warning("Não foi possível extrair hostname da URL")
            return self.results
        
        self.check_certificate(hostname)
        
        return self.results
