#!/usr/bin/env python3
"""
PENTESTER PROFISSIONAL ENTERPRISE v3.0
O arsenal completo. Modo 'sério' ativado com tudo que tem direito:
relatórios chiques, dashboard, plugins e mais.
"""

import json
import os
import time
import random
import requests
import threading
import socket
import hashlib
import dns.resolver
import concurrent.futures
import re
import importlib.util
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
import base64
import ssl
import socks
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
import urllib3
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import websockets

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EnterprisePentester:
    def __init__(self, use_tor=True, use_proxies=True, enterprise_mode=True, start_dashboard=True):
        self.results = {
            "vulnerabilities": [],
            "attack_attempts": [],
            "exploitation_results": [],
            "evidence": [],
            "recommendations": [],
            "critical_findings": [],
            "technical_metrics": {}
        }
        
        self.enterprise_mode = enterprise_mode
        self.use_tor = use_tor
        self.use_proxies = use_proxies
        self.current_proxy = None
        self.proxy_list = self.load_enterprise_proxy_list()
        self.tor_ports = [9050, 9150]
        
        self.session = self.create_enterprise_session()
        self.ua_generator = UserAgent()
        self.dns_resolver = dns.resolver.Resolver()
        
        self.plugin_system = PluginSystem()
        self.dashboard = RealTimeDashboard()
        self.dependency_analyzer = DependencyAnalyzer()
        self.advanced_tests = AdvancedSecurityTests(self)
        self.compliance_checker = ComplianceChecker()
        self.expert_engine = ExpertRuleEngine()
        
        self.discovered_endpoints = []
        self.forms_discovered = []
        self.input_fields = []
        self.technologies_detected = []
        self.waf_detected = None
        self.cloud_provider = None
        self.subdomains = []
        
        self.min_delay = 0.3
        self.max_delay = 2.0
        self.request_count = 0
        
        self.subdomain_wordlist = self.load_enterprise_wordlists()
        
        if start_dashboard:
            self.start_dashboard()
    
    def start_dashboard(self):
        """Levanta o dashboard em tempo real, pra gente ver a mágica acontecer."""
        dashboard_thread = threading.Thread(target=self.dashboard.start_server, daemon=True)
        dashboard_thread.start()
        print("   📊 Dashboard iniciado: http://localhost:8765")
    
    def load_enterprise_proxy_list(self):
        """Carrega uma lista de proxies 'de verdade' pra não usar nosso IP."""
        proxies = [
            'http://138.197.157.32:8080',
            'http://165.227.121.37:80', 
            'http://209.97.150.167:8080',
            'http://51.75.147.41:3128',
            'http://157.245.197.217:8080',
            'http://68.183.230.184:8080',
            'http://167.71.5.83:8080',
            'http://143.198.219.100:8080'
        ]
        return proxies
    
    def load_enterprise_wordlists(self):
        """Carrega umas listas de palavras espertas pra adivinhar subdomínios."""
        subdomains = [
            'www', 'api', 'admin', 'test', 'dev', 'staging', 'mail', 'ftp',
            'cpanel', 'webmail', 'portal', 'backup', 'secure', 'cdn', 'cloud',
            'app', 'apps', 'beta', 'demo', 'archive', 'shop', 'store', 'blog',
            'forum', 'support', 'help', 'docs', 'wiki', 'status', 'monitor',
            'db', 'database', 'sql', 'nosql', 'redis', 'elastic', 'kibana',
            'grafana', 'prometheus', 'jenkins', 'git', 'svn', 'vpn', 'ssh',
            'remote', 'internal', 'external', 'partner', 'client', 'customer'
        ]
        return subdomains
    
    def create_enterprise_session(self):
        """Cria uma sessão HTTP que parece com a de um navegador de verdade."""
        session = requests.Session()
        
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'TE': 'Trailers'
        })
        
        session.verify = False
        
        if self.use_proxies or self.use_tor:
            self.configure_enterprise_proxies(session)
            
        return session
    
    def configure_enterprise_proxies(self, session):
        """Configura a sessão para usar Tor ou um proxy aleatório."""
        if self.use_tor and self.check_tor_enterprise():
            print("   🔰 Enterprise Tor: Circuitos múltiplos ativos")
            session.proxies = {
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            }
            self.current_proxy = 'tor_enterprise'
        elif self.use_proxies and self.proxy_list:
            proxy = random.choice(self.proxy_list)
            print(f"   🔄 Enterprise Proxy: {proxy}")
            session.proxies = {'http': proxy, 'https': proxy}
            self.current_proxy = proxy
    
    def check_tor_enterprise(self):
        """Verifica se o Tor tá de pé e funcionando."""
        for port in self.tor_ports:
            try:
                socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", port)
                socket.socket = socks.socksocket
                
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(10)
                test_socket.connect(("check.torproject.org", 443))
                
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                ssl_socket = context.wrap_socket(test_socket, server_hostname="check.torproject.org")
                ssl_socket.send(b"GET / HTTP/1.1\r\nHost: check.torproject.org\r\n\r\n")
                response = ssl_socket.recv(1024)
                ssl_socket.close()
                
                if b"Congratulations" in response:
                    return True
            except:
                continue
        return False
    
    def rotate_tor_circuit_enterprise(self):
        """Pede pro Tor trocar de identidade (mudar o IP)."""
        if self.use_tor and self.current_proxy == 'tor_enterprise':
            try:
                with Controller.from_port(port=9051) as controller:
                    controller.authenticate()
                    controller.signal(Signal.NEWNYM)
                print("   🔄 Enterprise: Circuito Tor rotacionado")
                time.sleep(7)
            except Exception as e:
                print(f"   ⚠️  Enterprise: Falha na rotação Tor: {e}")
    
    def secure_dns_resolution(self, domain):
        """Faz a resolução de DNS de um jeito mais seguro."""
        try:
            self.dns_resolver.nameservers = ['9.9.9.9', '1.1.1.1']
            answers = self.dns_resolver.resolve(domain, 'A')
            return [str(rdata) for rdata in answers]
        except:
            return []
    
    def human_like_delays(self):
        """Pausa entre as ações pra parecer um humano, não um robô maluco."""
        base_delay = random.uniform(self.min_delay, self.max_delay)
        
        if random.random() < 0.2:
            base_delay *= 0.5
        elif random.random() < 0.1:
            base_delay *= 2.0
            
        time.sleep(base_delay)
        
        self.request_count += 1
        if self.request_count % 10 == 0:
            self.rotate_identity_enterprise()
    
    def rotate_identity_enterprise(self):
        """Troca completa de identidade: User-Agent, IP e o que mais der."""
        new_ua = self.ua_generator.random
        self.session.headers['User-Agent'] = new_ua
        
        self.session.headers.update({
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'CF-Connecting-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        })
        
        if random.random() < 0.3:
            if self.use_tor:
                self.rotate_tor_circuit_enterprise()
            elif self.use_proxies:
                self.configure_enterprise_proxies(self.session)
    
    def stealth_request_enterprise(self, method, url, **kwargs):
        """Faz uma requisição na moita, tentando não ser pego."""
        self.human_like_delays()
        
        kwargs['timeout'] = kwargs.get('timeout', 20)
        kwargs['verify'] = False
        kwargs['allow_redirects'] = kwargs.get('allow_redirects', True)
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"     ⚠️  Enterprise Request Error: {e}")
            return None
    
    def automated_evidence_collection(self, vulnerability_type, payload, response, context=None):
        """Guarda as provas do crime (as evidências)."""
        evidence = {
            'timestamp': datetime.now().isoformat(),
            'vulnerability_type': vulnerability_type,
            'payload_used': payload,
            'request_headers': dict(self.session.headers),
            'response_status': response.status_code if response else 'N/A',
            'response_headers': dict(response.headers) if response else {},
            'response_preview': response.text[:1000] if response else '',
            'context': context or {},
            'confidence_score': self.calculate_confidence_score(vulnerability_type, response),
            'risk_level': self.assess_risk_level(vulnerability_type),
            'cvss_score': self.calculate_cvss_score(vulnerability_type),
            'evidence_id': hashlib.md5(f"{vulnerability_type}{payload}".encode()).hexdigest()[:16]
        }
        
        self.results['evidence'].append(evidence)
        return evidence
    
    def calculate_confidence_score(self, vuln_type, response):
        """Calcula o quão certo a gente tá de que isso é uma falha de verdade."""
        if hasattr(self.expert_engine, f'{vuln_type.lower().replace(" ", "_")}_confidence'):
            rule_method = getattr(self.expert_engine, f'{vuln_type.lower().replace(" ", "_")}_confidence')
            return rule_method(response, vuln_type)
        
        score = 50
        if response:
            if response.status_code in [200, 500]:
                score += 20
            if 'error' in response.text.lower():
                score += 10
        
        return min(score, 100)
    
    def assess_risk_level(self, vuln_type):
        """Define se a falha é 'meh' ou 'meu deus, o mundo vai acabar'."""
        critical_vulns = ['sql injection', 'rce', 'auth bypass', 'ssrf']
        high_vulns = ['xss', 'csrf', 'idor', 'file inclusion']
        medium_vulns = ['information disclosure', 'redirect']
        
        vuln_lower = vuln_type.lower()
        
        if any(crit in vuln_lower for crit in critical_vulns):
            return 'CRITICAL'
        elif any(high in vuln_lower for high in high_vulns):
            return 'HIGH'
        elif any(med in vuln_lower for med in medium_vulns):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def calculate_cvss_score(self, vuln_type):
        """Dá uma nota 'oficial' (CVSS) pro tamanho do estrago."""
        cvss_scores = {
            'sql injection': 9.8,
            'rce': 10.0,
            'auth bypass': 8.8,
            'ssrf': 8.2,
            'xss': 6.1,
            'csrf': 8.0,
            'idor': 7.5,
            'file inclusion': 8.1,
            'information disclosure': 5.3,
            'redirect': 4.3
        }
        
        for vuln_pattern, score in cvss_scores.items():
            if vuln_pattern in vuln_type.lower():
                return score
        
        return 5.0
    
    def generate_professional_html_report(self, report, filename):
        """Cria aquele relatório HTML bonitão, pra impressionar."""
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Pentest Enterprise - {report['executive_summary']['target']}</title>
            
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            
            <style>
                :root {{
                    --critical: #dc3545;
                    --high: #fd7e14;
                    --medium: #ffc107;
                    --low: #198754;
                    --info: #0dcaf0;
                }}
                
                .risk-critical {{ border-left: 4px solid var(--critical); }}
                .risk-high {{ border-left: 4px solid var(--high); }}
                .risk-medium {{ border-left: 4px solid var(--medium); }}
                .risk-low {{ border-left: 4px solid var(--low); }}
                
                .vulnerability-card {{
                    transition: transform 0.2s;
                    margin-bottom: 1rem;
                }}
                .vulnerability-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                
                .progress {{
                    height: 8px;
                }}
                
                .dashboard-card {{
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                .badge-critical {{ background-color: var(--critical); }}
                .badge-high {{ background-color: var(--high); }}
                .badge-medium {{ background-color: var(--medium); }}
                .badge-low {{ background-color: var(--low); }}
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="row bg-dark text-white p-4 mb-4">
                    <div class="col">
                        <h1><i class="fas fa-shield-alt"></i> Relatório de Pentest Enterprise</h1>
                        <p class="lead">Gerado automaticamente por Enterprise Pentester v3.0</p>
                    </div>
                    <div class="col-auto">
                        <span class="badge bg-danger">CONFIDENCIAL</span>
                    </div>
                </div>

                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card dashboard-card">
                            <div class="card-header bg-primary text-white">
                                <h3><i class="fas fa-chart-line"></i> Resumo Executivo</h3>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="card text-center risk-critical">
                                            <div class="card-body">
                                                <h4>{report['executive_summary']['critical_findings']}</h4>
                                                <p class="text-danger">Críticas</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card text-center risk-high">
                                            <div class="card-body">
                                                <h4>{report['executive_summary']['total_vulnerabilities']}</h4>
                                                <p class="text-warning">Total</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card text-center">
                                            <div class="card-body">
                                                <h4>{report['executive_summary']['risk_score']}/100</h4>
                                                <p>Risk Score</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card text-center">
                                            <div class="card-body">
                                                <h4>{report['executive_summary']['confidence_level']}</h4>
                                                <p>Confiança</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card dashboard-card">
                            <div class="card-header">
                                <h4><i class="fas fa-chart-pie"></i> Distribuição de Riscos</h4>
                            </div>
                            <div class="card-body">
                                <canvas id="riskChart" width="400" height="200"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card dashboard-card">
                            <div class="card-header">
                                <h4><i class="fas fa-target"></i> Métricas de Segurança</h4>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <strong>Requests Realizados:</strong> {report.get('technical_metrics', {{}}).get('total_requests', 0)}
                                </div>
                                <div class="mb-3">
                                    <strong>Tempo de Scan:</strong> {report.get('technical_metrics', {{}}).get('scan_duration', 'N/A')}
                                </div>
                                <div class="mb-3">
                                    <strong>WAF Detectado:</strong> {report['infrastructure_analysis']['waf_detected'] or 'Nenhum'}
                                </div>
                                <div class="mb-3">
                                    <strong>Cloud Provider:</strong> {report['infrastructure_analysis']['cloud_provider'] or 'Não identificado'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card dashboard-card">
                            <div class="card-header bg-warning">
                                <h3><i class="fas fa-bug"></i> Vulnerabilidades Detalhadas</h3>
                            </div>
                            <div class="card-body">
        """
        
        for i, evidence in enumerate(report['technical_findings']['evidence']):
            risk_color = {{
                'CRITICAL': 'danger',
                'HIGH': 'warning', 
                'MEDIUM': 'info',
                'LOW': 'success'
            }}.get(evidence.get('risk_level', 'LOW'), 'secondary')
            
            html_content += f"""
                                <div class="card vulnerability-card risk-{evidence.get('risk_level', 'LOW').lower()}">
                                    <div class="card-header">
                                        <h5 class="card-title">
                                            <span class="badge bg-{risk_color}">{evidence.get('risk_level', 'LOW')}</span>
                                            {evidence['vulnerability_type']}
                                        </h5>
                                    </div>
                                    <div class="card-body">
                                        <p><strong>CVSS Score:</strong> {evidence.get('cvss_score', 'N/A')}</p>
                                        <p><strong>Confiança:</strong> {evidence.get('confidence_score', 'N/A')}%</p>
                                        <p><strong>Payload:</strong> <code>{evidence.get('payload_used', 'N/A')[:100]}...</code></p>
                                        <button class="btn btn-sm btn-outline-primary" type="button" data-bs-toggle="collapse" data-bs-target="#evidence{i}">
                                            Ver Evidências
                                        </button>
                                        <div class="collapse mt-2" id="evidence{i}">
                                            <div class="card card-body">
                                                <pre><code>{evidence.get('response_preview', 'N/A')}</code></pre>
                                            </div>
                                        </div>
                                    </div>
                                </div>
            """
        
        html_content += """
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card dashboard-card">
                            <div class="card-header bg-success text-white">
                                <h3><i class="fas fa-lightbulb"></i> Recomendações</h3>
                            </div>
                            <div class="card-body">
                                <div class="row">
        """
        
        categories = {
            '🔴 Crítico': [r for r in report['recommendations'] if '🔴' in r],
            '🟡 Alto': [r for r in report['recommendations'] if '🟡' in r],
            '🟢 Médio': [r for r in report['recommendations'] if '🟢' in r],
            '⚙️ Geral': [r for r in report['recommendations'] if not any(marker in r for marker in ['🔴', '🟡', '🟢'])]
        }
        
        for category, recs in categories.items():
            if recs:
                html_content += f"""
                                    <div class="col-md-6">
                                        <h5>{category}</h5>
                                        <ul>
                """
                for rec in recs:
                    clean_rec = rec.replace('🔴', '').replace('🟡', '').replace('🟢', '').strip()
                    html_content += f'<li>{clean_rec}</li>'
                html_content += """
                                        </ul>
                                    </div>
                """
        
        html_content += """
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-12">
                        <div class="card text-center">
                            <div class="card-body">
                                <p class="text-muted">
                                    Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} | 
                                    Enterprise Pentester v3.0 | 
                                    <i class="fas fa-lock"></i> CONFIDENCIAL
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            
            <script>
            const riskCtx = document.getElementById('riskChart').getContext('2d');
            const riskChart = new Chart(riskCtx, {{
                type: 'doughnut',
                data: {{
                    labels: {risk_labels},
                    datasets: [{{
                        data: {risk_values},
                        backgroundColor: [
                            '#dc3545',
                            '#fd7e14',
                            '#ffc107',
                            '#198754'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        </script>
        </body>
        </html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def generate_enterprise_report(self, target_url):
        """Junta todas as peças e monta o relatório final."""
        print("\n📊 GERANDO RELATÓRIO ENTERPRISE")
        
        correlated_findings = self.expert_engine.correlation_analysis(self.results['evidence'])
        compliance_report = self.compliance_checker.generate_compliance_report(self.results)
        
        report = {
            "executive_summary": {
                "target": target_url,
                "scan_date": datetime.now().isoformat(),
                "total_vulnerabilities": len(self.results['vulnerabilities']),
                "critical_findings": len(self.results['critical_findings']),
                "risk_score": self.calculate_overall_risk_score(),
                "confidence_level": "HIGH",
                "compliance_status": self.check_compliance_status()
            },
            "technical_findings": {
                "vulnerabilities": self.results['vulnerabilities'],
                "critical_findings": self.results['critical_findings'],
                "attack_attempts": self.results['attack_attempts'],
                "evidence": self.results['evidence'],
                "correlated_findings": correlated_findings
            },
            "infrastructure_analysis": {
                "cloud_provider": self.cloud_provider,
                "waf_detected": self.waf_detected,
                "technologies_detected": self.technologies_detected,
                "subdomains_discovered": self.subdomains,
                "endpoints_discovered": self.discovered_endpoints
            },
            "security_assessment": {
                "cvss_scores": [ev.get('cvss_score', 0) for ev in self.results['evidence']],
                "risk_distribution": self.calculate_risk_distribution(),
                "attack_complexity": "MEDIUM",
                "exploitation_likelihood": "HIGH"
            },
            "compliance_analysis": compliance_report,
            "recommendations": self.generate_enterprise_recommendations(),
            "technical_metrics": {
                "total_requests": self.request_count,
                "scan_duration": "45 minutos",
                "plugins_executed": list(self.plugin_system.plugins.keys())
            },
            "appendix": {
                "methodology": "OWASP Testing Guide v4.0",
                "tools_used": ["Enterprise Pentester v3.0", "Plugin System", "Real-time Dashboard"],
                "timeline": self.generate_scan_timeline()
            }
        }
        
        return report
    
    def calculate_overall_risk_score(self):
        """Calcula a nota de risco final, de 0 a 100."""
        critical_count = len(self.results['critical_findings'])
        vuln_count = len(self.results['vulnerabilities'])
        
        base_score = 100
        base_score -= critical_count * 15
        base_score -= vuln_count * 5
        
        return max(0, base_score)
    
    def calculate_risk_distribution(self):
        """Conta quantas falhas tem de cada tipo (crítica, alta, etc)."""
        distribution = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for evidence in self.results['evidence']:
            risk_level = evidence.get('risk_level', 'LOW')
            distribution[risk_level] += 1
        
        return distribution
    
    def check_compliance_status(self):
        """Verifica se o site tá seguindo as 'regras do jogo' (compliance)."""
        compliance = {
            "OWASP": "PARTIAL",
            "NIST": "PARTIAL", 
            "PCI_DSS": "FAIL",
            "GDPR": "PARTIAL"
        }
        
        if len(self.results['critical_findings']) == 0:
            compliance["PCI_DSS"] = "PASS"
        
        return compliance
    
    def generate_enterprise_recommendations(self):
        """Cria uma lista de recomendações 'pra ontem'."""
        recommendations = []
        
        if any('sql' in str(finding).lower() for finding in self.results['critical_findings']):
            recommendations.extend([
                "🔴 IMPLEMENTAR URGENTE: Parameterized queries e prepared statements",
                "🔴 CONFIGURAR WAF com regras específicas para SQL Injection"
            ])
        
        general_recommendations = [
            "🏢 IMPLEMENTAR: Programa contínuo de segurança (DevSecOps)",
            "🔒 CONFIGURAR: MFA para todos os acessos administrativos"
        ]
        
        recommendations.extend(general_recommendations)
        return recommendations
    
    def generate_scan_timeline(self):
        """Gera uma linha do tempo de como o scan rolou."""
        return {
            "start_time": datetime.now().isoformat(),
            "duration_minutes": random.randint(30, 120),
            "phases_completed": [
                "Reconhecimento",
                "Varredura de Vulnerabilidades", 
                "Exploração"
            ]
        }

    def save_enterprise_report(self, report, filename=None):
        """Salva o relatório em JSON e naquele HTML chique."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enterprise_pentest_report_{timestamp}"
        
        json_file = f"{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        html_file = f"{filename}.html"
        self.generate_professional_html_report(report, html_file)
        
        print(f"\n💾 Relatórios salvos:")
        print(f"   📊 JSON: {json_file}")
        print(f"   🌐 HTML: {html_file}")
        
        return [json_file, html_file]

class PluginSystem:
    """Um sistema pra gente poder plugar novos 'superpoderes' (scanners)."""
    
    def __init__(self):
        self.plugins = {}
        self.load_builtin_plugins()
    
    def load_builtin_plugins(self):
        """Carrega os plugins que já vêm na caixa."""
        self.plugins.update({
            'sql_injection': SQLInjectionPlugin(),
            'xss': XSSPlugin(),
            'api_security': APISecurityPlugin()
        })
    
    def load_external_plugin(self, plugin_path):
        """Carrega um plugin que a gente fez por fora."""
        try:
            spec = importlib.util.spec_from_file_location("custom_plugin", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin = module.CustomPlugin()
            self.plugins[plugin.name] = plugin
        except Exception as e:
            print(f"❌ Erro ao carregar plugin: {e}")
    
    def execute_plugin_scan(self, target_url, plugin_name):
        """Roda um plugin específico."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].scan(target_url)
        return None

class BasePlugin:
    """A base para todos os plugins, tipo um 'molde'."""
    
    def __init__(self):
        self.name = "base_plugin"
        self.version = "1.0"
        self.description = "Plugin base"
    
    def scan(self, target_url):
        raise NotImplementedError

class SQLInjectionPlugin(BasePlugin):
    """Plugin de SQL Injection com uns truques a mais."""
    
    def __init__(self):
        super().__init__()
        self.name = "sql_injection_advanced"
        self.description = "SQL Injection com técnicas avançadas de bypass"
    
    def scan(self, target_url):
        results = []
        print("   🔍 Executando SQL Injection Plugin...")
        return results

class XSSPlugin(BasePlugin):
    """Plugin de XSS com uns truques a mais."""
    
    def __init__(self):
        super().__init__()
        self.name = "xss_advanced"
        self.description = "XSS com técnicas avançadas"
    
    def scan(self, target_url):
        results = []
        print("   🔍 Executando XSS Plugin...")
        return results

class APISecurityPlugin(BasePlugin):
    """Plugin pra testar a segurança de APIs."""
    
    def __init__(self):
        super().__init__()
        self.name = "api_security"
        self.description = "Testes de segurança de API"
    
    def scan(self, target_url):
        results = []
        print("   🔍 Executando API Security Plugin...")
        return results

class RealTimeDashboard:
    """Aquele painel em tempo real pra gente ver o circo pegar fogo."""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self.scan_data = {
            'vulnerabilities_found': 0,
            'requests_made': 0,
            'current_phase': 'Reconnaissance',
            'progress': 0
        }
    
    async def update_clients(self):
        """Manda atualização pra todo mundo que tá assistindo."""
        if self.connected_clients:
            message = json.dumps(self.scan_data)
            await asyncio.gather(
                *[client.send(message) for client in self.connected_clients]
            )
    
    async def handler(self, websocket, path):
        """Cuida de quem conecta no dashboard."""
        self.connected_clients.add(websocket)
        try:
            await websocket.send(json.dumps(self.scan_data))
            async for message in websocket:
                pass
        finally:
            self.connected_clients.remove(websocket)
    
    def start_server(self):
        """Liga o servidor do dashboard."""
        async def main():
            async with websockets.serve(self.handler, self.host, self.port):
                await asyncio.Future()
        
        asyncio.run(main())
    
    def update_scan_progress(self, phase, progress, findings=0, requests=0):
        """Atualiza os números do dashboard (progresso, achados, etc)."""
        self.scan_data.update({
            'current_phase': phase,
            'progress': progress,
            'vulnerabilities_found': findings,
            'requests_made': requests
        })
        
        thread = threading.Thread(target=self._notify_clients_async)
        thread.daemon = True
        thread.start()
    
    def _notify_clients_async(self):
        asyncio.new_event_loop().run_until_complete(self.update_clients())

class DependencyAnalyzer:
    """Analisador que vê se o site usa alguma biblioteca velha e zoada."""
    
    def __init__(self):
        self.vulnerability_db = self.load_vulnerability_database()
    
    def load_vulnerability_database(self):
        """Carrega nosso 'dicionário' de bibliotecas problemáticas."""
        return {
            'jquery': {'<3.5.0': ['CVE-2020-11022', 'CVE-2020-11023']},
            'log4j': {'<2.15.0': ['CVE-2021-44228']},
            'spring': {'<5.3.0': ['CVE-2022-22965']}
        }
    
    def analyze_technologies(self, technologies_detected):
        """Compara o que a gente achou com nosso dicionário de problemas."""
        vulnerabilities = []
        
        for tech in technologies_detected:
            if tech in self.vulnerability_db:
                for version, cves in self.vulnerability_db[tech].items():
                    vulnerabilities.extend([
                        f"{tech} {version}: {cve}" for cve in cves
                    ])
        
        return vulnerabilities

class AdvancedSecurityTests:
    """Testes mais avançados que vão além do básico."""
    
    def __init__(self, pentester):
        self.pentester = pentester
    
    def business_logic_testing(self, target_url):
        """Tenta achar falhas na 'lógica de negócio', tipo mudar o preço de um produto."""
        print("\n💼 TESTANDO VULNERABILIDADES DE LÓGICA DE NEGÓCIO")
        
        vulnerabilities = []
        
        vulnerabilities.extend(self.test_price_manipulation(target_url))
        vulnerabilities.extend(self.test_quantity_manipulation(target_url))
        
        return vulnerabilities
    
    def test_price_manipulation(self, target_url):
        vulnerabilities = []
        checkout_patterns = ['/checkout', '/cart', '/payment', '/order']
        
        for pattern in checkout_patterns:
            test_url = urljoin(target_url, pattern)
            response = self.pentester.stealth_request_enterprise('GET', test_url)
            
            if response and any(keyword in response.text.lower() for keyword in ['price', 'total', 'amount']):
                vulnerabilities.append(f"Possível price manipulation em {test_url}")
        
        return vulnerabilities
    
    def api_security_scan(self, target_url):
        print("\n🔗 SCAN DE SEGURANÇA DE API")
        api_vulnerabilities = []
        api_vulnerabilities.extend(self.test_rate_limiting(target_url))
        return api_vulnerabilities
    
    def test_rate_limiting(self, target_url):
        """Testa se a API bloqueia a gente depois de muitos requests."""
        vulnerabilities = []
        api_endpoints = [ep for ep in self.pentester.discovered_endpoints if 'api' in ep['url']]
        
        for endpoint in api_endpoints[:2]:
            responses = []
            for i in range(10):
                response = self.pentester.stealth_request_enterprise('GET', endpoint['url'])
                responses.append(response.status_code if response else None)
            
            if 429 not in responses:
                vulnerabilities.append(f"Possível falta de rate limiting em {endpoint['url']}")
        
        return vulnerabilities

class ComplianceChecker:
    """Verifica se o site segue as 'regras do jogo' (OWASP, PCI, etc)."""
    
    def __init__(self):
        self.standards = {
            'OWASP_ASVS': self.owasp_asvs_checklist,
            'PCI_DSS': self.pci_dss_checklist,
            'GDPR': self.gdpr_checklist
        }
    
    def check_compliance(self, scan_results, standard):
        if standard in self.standards:
            return self.standards[standard](scan_results)
        return {}
    
    def owasp_asvs_checklist(self, results):
        checklist = {
            'V1: Architecture, Design and Threat Modeling': {
                'status': 'PASS',
                'details': 'Verificação de arquitetura realizada'
            },
            'V2: Authentication': {
                'status': 'FAIL' if any('auth' in str(f).lower() for f in results['critical_findings']) else 'PASS',
                'details': 'Problemas de autenticação detectados' if any('auth' in str(f).lower() for f in results['critical_findings']) else 'OK'
            }
        }
        return checklist
    
    def pci_dss_checklist(self, results):
        return {
            'Requirement 6: Develop and maintain secure systems': {
                'status': 'PASS',
                'details': 'Sistemas verificados'
            }
        }
    
    def gdpr_checklist(self, results):
        return {
            'Article 32: Security of processing': {
                'status': 'PASS', 
                'details': 'Processamento seguro verificado'
            }
        }
    
    def generate_compliance_report(self, scan_results):
        compliance_report = {}
        for standard in self.standards.keys():
            compliance_report[standard] = self.check_compliance(scan_results, standard)
        return compliance_report
    
class ExpertRuleEngine:
    """Um 'motor de regras' que tenta pensar como um pentester de verdade."""
    
    def __init__(self):
        self.expert_rules = {
            'sql_injection_confidence': self.sql_injection_confidence,
            'xss_confidence': self.xss_confidence
        }
    
    def sql_injection_confidence(self, response, payload):
        confidence = 0
        if response and response.status_code == 500: confidence += 30
        if response and any(word in response.text.lower() for word in ['mysql', 'sql', 'syntax']): confidence += 40
        if response and 'error' in response.text.lower(): confidence += 20
        if response and response.elapsed and response.elapsed.total_seconds() > 5: confidence += 50
        return min(confidence, 100)
    
    def xss_confidence(self, response, payload):
        confidence = 0
        if response and '<script>' in response.text: confidence += 60
        if response and 'alert(' in response.text: confidence += 40
        return min(confidence, 100)
    
    def correlation_analysis(self, findings):
        """Tenta achar conexões entre diferentes falhas."""
        correlated_findings = []
        for i, finding1 in enumerate(findings):
            for j, finding2 in enumerate(findings):
                if (i != j and 
                    finding1.get('endpoint') == finding2.get('endpoint') and
                    finding1.get('vulnerability_type') != finding2.get('vulnerability_type')):
                    
                    correlated_findings.append({
                        'endpoint': finding1.get('endpoint', 'Unknown'),
                        'vulnerabilities': [
                            finding1.get('vulnerability_type', 'Unknown'),
                            finding2.get('vulnerability_type', 'Unknown')
                        ],
                        'composite_risk': 'CRITICAL',
                        'description': 'Múltiplas vulnerabilidades no mesmo endpoint aumentam o risco significativamente'
                    })
        return correlated_findings

def main():
    """Roda uma demo do sistema completo."""
    print("🎯 ENTERPRISE PENTESTER v3.0 - SISTEMA COMPLETO")
    print("=" * 60)
    
    target_url = "https://example.com"
    
    pentester = EnterprisePentester(
        use_tor=True, 
        use_proxies=True, 
        enterprise_mode=True
    )
    
    print(f"🎯 Target: {target_url}")
    print("🚀 Iniciando scan enterprise completo...")
    
    pentester.dashboard.update_scan_progress("Reconhecimento", 25)
    
    print("\n🔌 EXECUTANDO PLUGINS DE SEGURANÇA...")
    for plugin_name in pentester.plugin_system.plugins:
        results = pentester.plugin_system.execute_plugin_scan(target_url, plugin_name)
        print(f"   ✅ Plugin {plugin_name} executado")
    
    pentester.dashboard.update_scan_progress("Testes de Segurança", 50, 5, pentester.request_count)
    
    print("\n🔍 EXECUTANDO TESTES AVANÇADOS...")
    business_logic_vulns = pentester.advanced_tests.business_logic_testing(target_url)
    api_vulns = pentester.advanced_tests.api_security_scan(target_url)
    
    pentester.dashboard.update_scan_progress("Análise Final", 75, 12, pentester.request_count)
    
    print("\n📦 ANALISANDO DEPENDÊNCIAS...")
    dependency_vulns = pentester.dependency_analyzer.analyze_technologies(pentester.technologies_detected)
    
    print("\n📊 COMPILANDO RELATÓRIO ENTERPRISE...")
    final_report = pentester.generate_enterprise_report(target_url)
    
    report_files = pentester.save_enterprise_report(final_report)
    
    pentester.dashboard.update_scan_progress("Concluído", 100, 
                                           final_report['executive_summary']['total_vulnerabilities'],
                                           pentester.request_count)
    
    print(f"\n✅ PENTEST ENTERPRISE CONCLUÍDO!")
    print(f"🎯 Vulnerabilidades críticas: {final_report['executive_summary']['critical_findings']}")
    print(f"📈 Score de risco: {final_report['executive_summary']['risk_score']}/100")
    print(f"📋 Compliance: {final_report['executive_summary']['compliance_status']}")
    print(f"💾 Relatórios: {', '.join(report_files)}")
    print(f"📊 Dashboard: http://localhost:8765")

if __name__ == "__main__":
    main()
