"""
Detetive de Tecnologia v2.0
Esse scanner fuça os headers, o HTML e até o DNS pra descobrir
com o que o site foi feito (PHP, React, WordPress, etc.).
"""

import re
import socket
import ssl
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import dns.resolver
from .base_scanner import BaseScanner
from collections import defaultdict

class TechnologyScanner(BaseScanner):
    def __init__(self, target_url, timeout=10):
        super().__init__(target_url, timeout)
        self.hostname = urlparse(target_url).hostname
        self.evidence = defaultdict(list)
        self.technologies = {
            'server': {'value': None, 'confidence': 0.0},
            'os': {'value': None, 'confidence': 0.0},
            'language': {'value': None, 'confidence': 0.0},
            'framework': {'value': None, 'confidence': 0.0},
            'cms': {'value': None, 'confidence': 0.0},
            'frontend': {'value': [], 'confidence': 0.0},
            'analytics': {'value': [], 'confidence': 0.0},
            'cloud_provider': {'value': None, 'confidence': 0.0},
            'waf': {'value': None, 'confidence': 0.0},
        }

    def _add_evidence(self, tech_type, value, confidence, source, details=""):
        """Anota uma pista que a gente encontrou."""
        self.evidence[tech_type].append({
            'value': value,
            'confidence': confidence,
            'source': source,
            'details': details
        })

    def analyze_headers(self, headers):
        """Dá uma olhada nos 'documentos' (cabeçalhos) do site."""
        server = headers.get('Server', '')
        if server:
            self._add_evidence('server', server, 0.9, 'Header: Server')
            if 'apache' in server.lower(): self._add_evidence('server', 'Apache', 0.9, 'Header: Server')
            elif 'nginx' in server.lower(): self._add_evidence('server', 'Nginx', 0.9, 'Header: Server')
            elif 'iis' in server.lower(): self._add_evidence('server', 'Microsoft-IIS', 0.9, 'Header: Server'); self._add_evidence('os', 'Windows', 0.8, 'Header: Server')
            elif 'cloudflare' in server.lower(): self._add_evidence('waf', 'Cloudflare', 1.0, 'Header: Server')

        powered_by = headers.get('X-Powered-By', '')
        if powered_by:
            if 'php' in powered_by.lower(): self._add_evidence('language', f"PHP/{powered_by.split('/')[-1]}", 1.0, 'Header: X-Powered-By')
            elif 'asp.net' in powered_by.lower(): self._add_evidence('framework', '.NET', 1.0, 'Header: X-Powered-By'); self._add_evidence('os', 'Windows', 0.9, 'Header: X-Powered-By')
            elif 'express' in powered_by.lower(): self._add_evidence('framework', 'Express', 1.0, 'Header: X-Powered-By'); self._add_evidence('language', 'Node.js', 1.0, 'Header: X-Powered-By')
            elif 'next.js' in powered_by.lower(): self._add_evidence('framework', 'Next.js', 1.0, 'Header: X-Powered-By')

        set_cookie = headers.get('Set-Cookie', '')
        if set_cookie:
            if 'PHPSESSID' in set_cookie: self._add_evidence('language', 'PHP', 0.6, 'Header: Set-Cookie')
            if 'JSESSIONID' in set_cookie: self._add_evidence('language', 'Java', 0.6, 'Header: Set-Cookie')
            if 'wp-' in set_cookie or 'wordpress_' in set_cookie: self._add_evidence('cms', 'WordPress', 0.9, 'Header: Set-Cookie')

        if 'CF-Ray' in headers: self._add_evidence('waf', 'Cloudflare', 1.0, 'Header: CF-Ray')
        if 'x-amz-cf-id' in headers: self._add_evidence('cloud_provider', 'AWS CloudFront', 1.0, 'Header: x-amz-cf-id')

    def analyze_html(self, content):
        """Lê o código-fonte da página procurando por 'digitais'."""
        soup = BeautifulSoup(content, 'html.parser')

        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            gen_content = generator['content'].lower()
            if 'wordpress' in gen_content: self._add_evidence('cms', 'WordPress', 1.0, 'HTML: Meta Generator')
            elif 'joomla' in gen_content: self._add_evidence('cms', 'Joomla', 1.0, 'HTML: Meta Generator')
            elif 'drupal' in gen_content: self._add_evidence('cms', 'Drupal', 1.0, 'HTML: Meta Generator')

        tags = soup.find_all(['script', 'link'])
        for tag in tags:
            src = tag.get('src') or tag.get('href', '')
            if not src: continue
            if '/_next/' in src: self._add_evidence('framework', 'Next.js', 1.0, 'HTML: Script/Link Tag')
            if '/wp-content/' in src: self._add_evidence('cms', 'WordPress', 1.0, 'HTML: Script/Link Tag')
            if 'react' in src: self._add_evidence('frontend', 'React', 0.7, 'HTML: Script Tag')

        if "google-analytics.com" in content or "gtag('config'" in content:
            self._add_evidence('analytics', 'Google Analytics', 1.0, 'HTML: Script Content')

    def analyze_dns(self):
        """Verifica o 'endereço' do site pra ver se ele mora na Amazon, Google, etc."""
        if not self.hostname: return
        try:
            resolver = dns.resolver.Resolver()
            for rdata in resolver.resolve(self.hostname, 'CNAME'):
                cname = rdata.target.to_text().lower()
                if 'amazonaws.com' in cname: self._add_evidence('cloud_provider', 'AWS', 0.9, 'DNS: CNAME Record')
                elif 'azure' in cname: self._add_evidence('cloud_provider', 'Azure', 0.9, 'DNS: CNAME Record')
                elif 'google' in cname: self._add_evidence('cloud_provider', 'Google Cloud', 0.9, 'DNS: CNAME Record')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            try:
                ip = socket.gethostbyname(self.hostname)
                rev_name = socket.gethostbyaddr(ip)[0].lower()
                if 'amazonaws.com' in rev_name: self._add_evidence('cloud_provider', 'AWS', 0.8, 'DNS: Reverse DNS')
                elif 'googleusercontent.com' in rev_name: self._add_evidence('cloud_provider', 'Google Cloud', 0.8, 'DNS: Reverse DNS')
            except (socket.herror, socket.gaierror):
                pass
        except Exception as e:
            self.add_debug(f"Falha na análise de DNS: {e}")

    def analyze_ssl(self):
        """Analisa o 'cadeado' (certificado SSL) do site."""
        if not self.hostname: return
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert = ssock.getpeercert()
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    issuer_org = issuer.get('organizationName', '').lower()
                    if 'cloudflare' in issuer_org: self._add_evidence('waf', 'Cloudflare', 0.8, 'SSL: Issuer')
                    if 'amazon' in issuer_org: self._add_evidence('cloud_provider', 'AWS', 0.8, 'SSL: Issuer')
        except Exception as e:
            self.add_debug(f"Falha na análise de SSL: {e}")

    def consolidate_results(self):
        """Junta todas as pistas e decide qual é a mais provável."""
        for tech_type, evidences in self.evidence.items():
            if not evidences: continue
            
            best_evidence = max(evidences, key=lambda x: x['confidence'])
            
            if tech_type in ['frontend', 'analytics']:
                unique_values = {e['value'] for e in evidences}
                self.technologies[tech_type]['value'] = list(unique_values)
                self.technologies[tech_type]['confidence'] = best_evidence['confidence']
            else:
                self.technologies[tech_type]['value'] = best_evidence['value']
                self.technologies[tech_type]['confidence'] = best_evidence['confidence']

        # Algumas adivinhações extras baseadas no que a gente já sabe
        if self.technologies['server']['value'] and 'iis' in self.technologies['server']['value'].lower():
            self._add_evidence('os', 'Windows', 0.9, 'Inferência a partir do servidor')
        if self.technologies['server']['value'] and ('apache' in self.technologies['server']['value'].lower() or 'nginx' in self.technologies['server']['value'].lower()):
             self._add_evidence('os', 'Linux (Provável)', 0.7, 'Inferência a partir do servidor')
        
        if self.evidence['os']:
            best_os_evidence = max(self.evidence['os'], key=lambda x: x['confidence'])
            self.technologies['os']['value'] = best_os_evidence['value']
            self.technologies['os']['confidence'] = best_os_evidence['confidence']

    def scan(self):
        """Executa o scan completo."""
        self.add_info(f"Executando detecção de tecnologias em: {self.target_url}")
        
        response = self.test_endpoint(self.target_url)
        if not response:
            self.add_warning("Não foi possível acessar a URL para análise de tecnologia.")
            return {'technologies': self.technologies, 'evidence': dict(self.evidence)}

        self.analyze_headers(response.headers)
        self.analyze_html(response.text)
        self.analyze_dns()
        self.analyze_ssl()
        
        self.consolidate_results()
        
        self.add_info(f"Tecnologias consolidadas: {self.technologies}")
        
        return {'technologies': self.technologies, 'evidence': dict(self.evidence)}
