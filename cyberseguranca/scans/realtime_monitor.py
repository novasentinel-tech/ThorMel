"""
O Espião
Esse carinha fica de olho no site e avisa se algo mudar.
Útil pra saber se o site foi modificado por alguém.
"""

import time
import schedule
from datetime import datetime
from scans.base_scanner import BaseScanner
from scans.header_security import HeaderSecurityScanner
import hashlib

class RealTimeMonitor(BaseScanner):
    def __init__(self, target_url, check_interval=300, timeout=10):
        super().__init__(target_url, timeout)
        self.check_interval = check_interval
        self.previous_hash = None
    
    def get_content_hash(self):
        """Pega o 'DNA' (hash) da página pra gente poder comparar depois."""
        response = self.test_endpoint(self.target_url)
        if response:
            content = response.text
            return hashlib.md5(content.encode()).hexdigest()
        return None
    
    def monitor_changes(self):
        """Verifica se o 'DNA' da página mudou desde a última vez que a gente olhou."""
        current_hash = self.get_content_hash()
        
        if current_hash and self.previous_hash and current_hash != self.previous_hash:
            print(f"[{datetime.now()}] ⚠️  ALTERAÇÃO DETECTADA NO SITE!")
            self.add_warning("Alteração no conteúdo do site detectada")
        
        self.previous_hash = current_hash
    
    def periodic_scan(self):
        """De tempos em tempos, roda um scan mais completo pra ver se tá tudo em ordem."""
        print(f"[{datetime.now()}] Executando scan periódico...")
        
        header_scanner = HeaderSecurityScanner(self.target_url, self.timeout)
        header_results = header_scanner.scan()
        
        for warning in header_results.get('warnings', []):
            print(f"    ⚠️  {warning}")
    
    def start_monitoring(self):
        """Inicia o modo 'espião'."""
        print(f"[+] Iniciando monitoramento em tempo real de: {self.target_url}")
        print(f"[+] Verificando a cada {self.check_interval} segundos")
        
        self.previous_hash = self.get_content_hash()
        print("[+] Hash inicial calculado")
        
        schedule.every(self.check_interval).seconds.do(self.monitor_changes)
        schedule.every(3600).seconds.do(self.periodic_scan)
        
        print("[+] Monitoramento ativo. Pressione Ctrl+C para parar.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] Monitoramento interrompido pelo usuário")
    
    def scan(self):
        """O 'scan' desse módulo é na verdade iniciar o monitoramento."""
        self.start_monitoring()
        return self.results
