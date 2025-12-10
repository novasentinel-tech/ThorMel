"""
Isso aqui é só pra facilitar a vida. Em vez de importar cada scanner
um por um, a gente junta tudo aqui e importa de uma vez só.
"""

from .base_scanner import BaseScanner
from .sql_injection import SQLInjectionScanner
from .xss_scanner import XSSScanner
from .directory_traversal import DirectoryTraversalScanner
from .header_security import HeaderSecurityScanner
from .ssl_scanner import SSLScanner
from .port_scanner import PortScanner
from .form_analyzer import FormAnalyzer
from .realtime_monitor import RealTimeMonitor
from .technology_scanner import TechnologyScanner

__all__ = [
    'BaseScanner',
    'TechnologyScanner',
    'SQLInjectionScanner',
    'XSSScanner',
    'DirectoryTraversalScanner',
    'HeaderSecurityScanner',
    'SSLScanner',
    'PortScanner',
    'FormAnalyzer',
    'RealTimeMonitor'
]
