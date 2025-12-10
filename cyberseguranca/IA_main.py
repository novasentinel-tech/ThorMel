#!/usr/bin/env python3
"""
IA MAIN - O Cérebro da Operação
Basicamente, o chefão que comanda todos os outros scanners.
"""

import os
import json
import importlib.util
import re
from typing import Dict, List, Optional
from datetime import datetime
import sys

from scans.technology_scanner import TechnologyScanner
from scans.sql_injection import SQLInjectionScanner
from scans.xss_scanner import XSSScanner
from scans.directory_traversal import DirectoryTraversalScanner
from scans.header_security import HeaderSecurityScanner
from scans.ssl_scanner import SSLScanner
from scans.port_scanner import PortScanner
from scans.form_analyzer import FormAnalyzer
from scans.realtime_monitor import RealTimeMonitor

class IAPentestMaster:
    def __init__(self):
        self.scanners = self.carregar_scanners()
        self.main_attack = self.carregar_main_attack()
        self.analise_em_andamento = False
        
    def carregar_scanners(self) -> Dict:
        """Carrega todos os scanners da pasta 'scans'. Tipo montar a equipe."""
        scanners = {}
        
        print("🔧 Carregando scanners profissionais...")
        
        scanner_classes = {
            'technology_scanner': TechnologyScanner,
            'sql_injection': SQLInjectionScanner,
            'xss_scanner': XSSScanner, 
            'directory_traversal': DirectoryTraversalScanner,
            'header_security': HeaderSecurityScanner,
            'ssl_scanner': SSLScanner,
            'port_scanner': PortScanner,
            'form_analyzer': FormAnalyzer
        }
        
        for nome, classe in scanner_classes.items():
            try:
                scanners[nome] = classe
                print(f"   ✅ {nome}")
            except Exception as e:
                print(f"   ⚠️  Erro em {nome}: {e}")
        
        return scanners

    def carregar_main_attack(self):
        """Carrega o MainAttack, nosso brinquedo mais 'sério' pra simular ataques."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_attack_path = os.path.join(script_dir, "MainAttack.py")
            spec = importlib.util.spec_from_file_location("main_attack", main_attack_path)
            main_attack_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_attack_module)
            
            return main_attack_module.EnterprisePentester(use_tor=False, enterprise_mode=True, start_dashboard=False)
            
        except Exception as e:
            print(f"❌ Erro ao carregar MainAttack: {e}")
            return None
    
    def analisar_alvo(self, alvo: str) -> Dict:
        """Executa a análise completa no alvo, um scanner de cada vez."""
        print(f"🎯 INICIANDO ANÁLISE INTELIGENTE: {alvo}")
        
        resultados = {
            'alvo': alvo,
            'timestamp': datetime.now().isoformat(),
            'vulnerabilidades': [],
            'scanners_executados': [],
            'recomendacoes': [],
            'estatisticas': {
                'tecnologias': {}
            },
            'tecnologias_detalhadas': {}
        }
        
        # Fase 1: Descobrir com o que estamos lidando.
        print("\n🔍 Executando: technology_scanner")
        try:
            tech_scanner_class = self.scanners.get('technology_scanner')
            if tech_scanner_class:
                tech_scanner = tech_scanner_class(target_url=alvo)
                tech_results = tech_scanner.scan()
                if tech_results and tech_results.get('technologies'):
                    # Guarda os detalhes nerds pro relatório completo.
                    resultados['tecnologias_detalhadas'] = tech_results
                    
                    # Cria uma versão mais simples pra mostrar na tela.
                    simple_techs = {}
                    for tech, data in tech_results['technologies'].items():
                        if isinstance(data.get('value'), list):
                            simple_techs[tech] = ', '.join(data['value']) if data.get('value') else 'N/A'
                        else:
                            simple_techs[tech] = data.get('value') or 'N/A'
                    resultados['estatisticas']['tecnologias'] = simple_techs

                resultados['scanners_executados'].append('technology_scanner')
            else:
                print("   ⚠️  Scanner de tecnologia não encontrado.")
        except Exception as e:
            print(f"   ❌ Erro no technology_scanner: {e}")

        # Fase 2: Agora sim, procurar as brechas.
        for nome_scanner, scanner_class in self.scanners.items():
            if nome_scanner == 'technology_scanner':
                continue # Esse a gente já rodou.
                
            print(f"\n🔍 Executando: {nome_scanner}")
            
            try:
                scanner = scanner_class(target_url=alvo)
                resultado = scanner.scan()
                
                vulnerabilidades = self.processar_resultados_scanner(nome_scanner, resultado)
                if vulnerabilidades:
                    resultados['vulnerabilidades'].extend(vulnerabilidades)
                resultados['scanners_executados'].append(nome_scanner)
                
                print(f"   ✅ {len(vulnerabilidades)} vulnerabilidades encontradas")
                
            except Exception as e:
                print(f"   ❌ Erro no {nome_scanner}: {e}")
        
        resultados['vulnerabilidades'] = self.classificar_vulnerabilidades(resultados['vulnerabilidades'])
        resultados['recomendacoes'] = self.gerar_recomendacoes_inteligentes(resultados['vulnerabilidades'])
        self.salvar_relatorio_analise(resultados)
        
        print(f"\n📊 ANÁLISE CONCLUÍDA: {len(resultados['vulnerabilidades'])} vulnerabilidades encontradas")
        
        return resultados
    
    def processar_resultados_scanner(self, nome_scanner: str, resultado: Dict) -> List[Dict]:
        """Transforma a salada de dados de cada scanner em um formato padrão."""
        vulnerabilidades = []
        
        if not resultado:
            self.add_debug(f"Scanner {nome_scanner} não retornou resultados.")
            return vulnerabilidades

        try:
            if nome_scanner == 'sql_injection' and 'sql_injection_report' in resultado:
                for vuln in resultado['sql_injection_report'].get('vulnerabilities', []):
                    vulnerabilidades.append({
                        'tipo': 'SQL Injection',
                        'nivel_risco': 'CRÍTICO',
                        'confianca': 95,
                        'tecnica': vuln.get('technique', 'Desconhecida'),
                        'parametro': vuln.get('parameter', 'N/A'),
                        'evidencia': f"Técnica: {vuln.get('technique')} no parâmetro {vuln.get('parameter')}",
                        'scanner': 'SQL Injection Scanner'
                    })
            
            elif nome_scanner == 'xss_scanner' and 'confirmed_vulnerabilities' in resultado:
                for vuln in resultado['confirmed_vulnerabilities']:
                    vulnerabilidades.append({
                        'tipo': 'XSS (' + vuln.get('type', 'Reflected') + ')',
                        'nivel_risco': 'ALTO', 
                        'confianca': vuln.get('score', 70),
                        'tecnica': 'Reflected/DOM',
                        'parametro': vuln.get('parameter', 'N/A'),
                        'evidencia': f"Score: {vuln.get('score')}. Evidência: {vuln.get('evidence', 'N/A')}",
                        'scanner': 'XSS Scanner'
                    })

            elif nome_scanner == 'directory_traversal' and 'owasp_report' in resultado:
                confidence_map = {'high': 90, 'medium': 60, 'low': 30}
                for vuln in resultado['owasp_report'].get('vulnerabilities', []):
                    confidence_str = vuln.get('confidence', 'low')
                    vulnerabilidades.append({
                        'tipo': 'Directory Traversal',
                        'nivel_risco': 'ALTO' if confidence_str == 'high' else 'MÉDIO',
                        'confianca': confidence_map.get(confidence_str, 30),
                        'tecnica': 'Path Traversal',
                        'parametro': vuln.get('parameter', 'N/A'),
                        'evidencia': vuln.get('evidence', 'N/A'),
                        'scanner': 'Directory Traversal Scanner'
                    })

            elif nome_scanner == 'header_security':
                for vuln in resultado.get('vulnerabilities', []):
                    message = vuln.get('message', '')
                    vulnerabilidades.append({
                        'tipo': 'Header de Segurança Ausente/Incorreto',
                        'nivel_risco': 'MÉDIO',
                        'confianca': 100,
                        'tecnica': 'Análise de Headers HTTP',
                        'parametro': message.split(':')[0].replace('🔴', '').strip(),
                        'evidencia': message,
                        'scanner': 'Header Security Scanner'
                    })

            elif nome_scanner == 'ssl_scanner':
                for vuln in resultado.get('vulnerabilities', []):
                    message = vuln.get('message', '')
                    vulnerabilidades.append({
                        'tipo': 'Configuração SSL/TLS Insegura',
                        'nivel_risco': 'MÉDIO',
                        'confianca': 100,
                        'tecnica': 'Análise de Certificado SSL/TLS',
                        'parametro': 'Configuração do Servidor',
                        'evidencia': message,
                        'scanner': 'SSL/TLS Scanner'
                    })

            elif nome_scanner == 'port_scanner' and 'port_scan_report' in resultado:
                report = resultado['port_scan_report']
                for port, service_info in report.get('services', {}).items():
                    if service_info.get('risk_level') in ['high', 'critical']:
                        vulnerabilidades.append({
                            'tipo': f"Serviço Inseguro Exposto: {service_info['name']}",
                            'nivel_risco': 'ALTO',
                            'confianca': 100,
                            'tecnica': 'Scan de Portas Abertas',
                            'parametro': f"Porta {port}/TCP",
                            'evidencia': f"Serviço '{service_info['name']}' (versão: {service_info.get('version', 'N/A')}) na porta {port} é considerado de alto risco.",
                            'scanner': 'Port Scanner'
                        })
            
            elif nome_scanner == 'form_analyzer' and 'form_analysis' in resultado:
                analysis = resultado['form_analysis']
                for form in analysis.get('forms', []):
                    if form.get('risk_score', 0) > 40:
                        vulnerabilidades.append({
                            'tipo': f"Formulário Inseguro (Tipo: {form['type']})",
                            'nivel_risco': 'ALTO' if form['risk_score'] > 60 else 'MÉDIO',
                            'confianca': 85,
                            'tecnica': 'Análise de Formulário HTML',
                            'parametro': f"Formulário com action '{form.get('action', 'N/A')}'",
                            'evidencia': f"Riscos detectados: {', '.join(form.get('findings', []))}. Score de Risco do Formulário: {form['risk_score']}",
                            'scanner': 'Form Analyzer'
                        })

        except Exception as e:
            print(f"   ⚠️  Erro ao processar {nome_scanner}: {e}")
        
        return vulnerabilidades

    def classificar_vulnerabilidades(self, vulnerabilidades: List[Dict]) -> List[Dict]:
        """Dá uma nota de prioridade pra gente focar no que é mais perigoso primeiro."""
        ordem_prioridade = {'CRÍTICO': 4, 'ALTO': 3, 'MÉDIO': 2, 'BAIXO': 1}
        
        for vuln in vulnerabilidades:
            vuln['prioridade'] = self.calcular_prioridade_vulnerabilidade(vuln)
        
        vulnerabilidades.sort(key=lambda x: ordem_prioridade.get(x.get('prioridade', 'BAIXO'), 0), reverse=True)
        
        return vulnerabilidades
    
    def calcular_prioridade_vulnerabilidade(self, vulnerabilidade: Dict) -> str:
        """Decide o quão 'quente' é uma vulnerabilidade."""
        tipo = vulnerabilidade['tipo']
        confianca = vulnerabilidade.get('confianca', 50)
        
        if 'SQL Injection' in tipo and confianca > 70:
            return 'CRÍTICO'
        elif 'RCE' in tipo or 'Remote Code' in tipo:
            return 'CRÍTICO'
        elif 'Serviço Inseguro' in tipo:
            return 'ALTO'
        elif 'XSS' in tipo and confianca > 80:
            return 'ALTO'
        elif 'Directory Traversal' in tipo and confianca > 60:
            return 'ALTO'
        elif 'Formulário Inseguro' in tipo:
             return 'MÉDIO'
        else:
            return 'MÉDIO' if confianca > 60 else 'BAIXO'
    
    def gerar_recomendacoes_inteligentes(self, vulnerabilidades: List[Dict]) -> List[str]:
        """Cria uma lista de 'coisas pra fazer' baseada no que a gente achou."""
        recomendacoes = []
        
        vulnerabilidades_criticas = [v for v in vulnerabilidades if v.get('prioridade') in ['CRÍTICO', 'ALTO']]
        
        if any('SQL Injection' in v['tipo'] for v in vulnerabilidades_criticas):
            recomendacoes.extend([
                "🔴 SQL Injection detectado - Implementar prepared statements URGENTE",
                "🔴 Validar todos os inputs do usuário com whitelist",
                "🔴 Configurar WAF com regras específicas para SQLi"
            ])
        
        if any('XSS' in v['tipo'] for v in vulnerabilidades_criticas):
            recomendacoes.extend([
                "🟡 XSS detectado - Implementar Content Security Policy (CSP)",
                "🟡 Usar encoding adequado para saída de dados",
                "🟡 Validar e sanitizar todos os inputs"
            ])
        
        if vulnerabilidades_criticas:
            recomendacoes.extend([
                "🏢 Estabelecer programa contínuo de segurança",
                "🔒 Implementar MFA para acessos administrativos", 
                "📊 Realizar pentests regulares"
            ])
        
        return recomendacoes
    
    def salvar_relatorio_analise(self, resultados: Dict):
        """Salva o relatório em um arquivo JSON pra gente não perder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_alvo = re.sub(r'[^a-zA-Z0-9_-]', '_', resultados['alvo'])
        filename = f"relatorios/analise_{safe_alvo}_{timestamp}.json"
        
        os.makedirs('relatorios', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório salvo: {filename}")
        return filename
    
    def executar_exploracao_inteligente(self, alvo: str):
        """Modo 'exploração': primeiro analisa, depois decide se vale a pena 'atacar'."""
        print(f"\n💥 INICIANDO EXPLORAÇÃO INTELIGENTE: {alvo}")
        
        analise = self.analisar_alvo(alvo)
        
        if not analise['vulnerabilidades']:
            print("❌ Nenhuma vulnerabilidade encontrada para exploração")
            return analise
        
        vulnerabilidades_exploraveis = [
            v for v in analise.get('vulnerabilidades', []) 
            if v.get('prioridade') in ['CRÍTICO', 'ALTO'] and v.get('confianca', 0) > 70
        ]
        
        if not vulnerabilidades_exploraveis:
            print("⚠️  Nenhuma vulnerabilidade com confiança suficiente para exploração")
            return analise
        
        print(f"🎯 Vulnerabilidades para exploração: {len(vulnerabilidades_exploraveis)}")
        
        for vuln in vulnerabilidades_exploraveis:
            self.decidir_acao_vulnerabilidade(vuln, alvo)
            
        return analise

    def decidir_acao_vulnerabilidade(self, vulnerabilidade: Dict, alvo: str):
        """Com base na confiança, decide o que fazer com a vulnerabilidade."""
        tipo = vulnerabilidade['tipo']
        confianca = vulnerabilidade.get('confianca', 0)
        
        print(f"\n🤔 DECIDINDO AÇÃO PARA: {tipo} (Confiança: {confianca}%)")
        
        if confianca >= 80:
            if self.main_attack:
                print("   🚀 Tentando exploração automática com MainAttack...")
                self.tentar_exploracao_automatica(vulnerabilidade, alvo)
            else:
                print("   ⚠️  MainAttack não disponível")
                
        elif confianca >= 60:
            print("   🛠️  Vulnerabilidade complexa - solicitando código personalizado")
            self.solicitar_codigo_personalizado(vulnerabilidade, alvo)
            
        else:
            print("   📋 Baixa confiança - apenas reportando")
    
    def tentar_exploracao_automatica(self, vulnerabilidade: Dict, alvo: str):
        """Usa o MainAttack para tentar uma exploração (simulada)."""
        try:
            print(f"   🔧 Configurando MainAttack para {vulnerabilidade['tipo']}")
            
            resultado_simulado = {
                'vulnerabilidade': vulnerabilidade['tipo'],
                'exploracao': 'simulada',
                'sucesso': True,
                'detalhes': 'Exploração realizada via MainAttack'
            }
            
            print(f"   ✅ Resultado: {resultado_simulado}")
            
        except Exception as e:
            print(f"   ❌ Erro na exploração automática: {e}")
    
    def solicitar_codigo_personalizado(self, vulnerabilidade: Dict, alvo: str):
        """Pede para a IA gerar um exploit específico para casos mais complexos."""
        print(f"\n🆘 SOLICITAÇÃO DE CÓDIGO PERSONALIZADO")
        print("=" * 50)
        print(f"🔍 Vulnerabilidade: {vulnerabilidade['tipo']}")
        print(f"🎯 Alvo: {alvo}")
        print(f"📊 Confiança: {vulnerabilidade.get('confianca', 'N/A')}%")
        print(f"🚨 Prioridade: {vulnerabilidade.get('prioridade', 'N/A')}")
        print(f"💡 Scanner: {vulnerabilidade.get('scanner', 'N/A')}")
        print(f"📝 Evidência: {vulnerabilidade.get('evidencia', 'N/A')}")
        print("=" * 50)
        print("\n🤖 IA: Esta vulnerabilidade é complexa e requer código específico.")
        print("💡 Ação: Por favor, gere um exploit personalizado para:")
        print(f"   - Tipo: {vulnerabilidade['tipo']}")
        print(f"   - Alvo: {alvo}")
        print(f"   - Parâmetro: {vulnerabilidade.get('parametro', 'N/A')}")
        print(f"   - Técnica: {vulnerabilidade.get('tecnica', 'N/A')}")
        print("\n📁 O código deve ser salvo em: IA_CodesPenetrations/")
        print("⏰ Código personalizado solicitado. Continuando execução sem aguardar.")
    
    def mostrar_vulnerabilidades_criticas(self):
        """Dá uma olhada nos relatórios antigos e mostra o que era mais perigoso."""
        relatorios_dir = "relatorios"
        
        if not os.path.exists(relatorios_dir):
            print("   📁 Nenhum relatório encontrado")
            return
        
        for arquivo in os.listdir(relatorios_dir):
            if arquivo.endswith('.json'):
                try:
                    with open(os.path.join(relatorios_dir, arquivo), 'r') as f:
                        relatorio = json.load(f)
                    
                    vulnerabilidades_criticas = [
                        v for v in relatorio.get('vulnerabilidades', [])
                        if v.get('prioridade') in ['CRÍTICO', 'ALTO']
                    ]
                    
                    if vulnerabilidades_criticas:
                        print(f"\n📋 {arquivo}:")
                        for vuln in vulnerabilidades_criticas:
                            print(f"   • {vuln['tipo']} - {vuln.get('parametro', 'N/A')}")
                            
                except Exception as e:
                    print(f"   ⚠️  Erro ao ler {arquivo}: {e}")

def formatar_relatorio_para_frontend(resultados_brutos: Dict, scan_type: str) -> Dict:
    """Prepara os dados para serem exibidos bonitinho na tela."""
    vulnerabilidades = resultados_brutos.get('vulnerabilidades', [])
    total_vulnerabilidades = len(vulnerabilidades)
    
    risk_score = 0
    distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for vuln in vulnerabilidades:
        prioridade = vuln.get('prioridade', 'BAIXO').lower()
        if prioridade == 'crítico':
            risk_score += 15
            distribution['critical'] += 1
        elif prioridade == 'alto':
            risk_score += 8
            distribution['high'] += 1
        elif prioridade == 'médio':
            risk_score += 3
            distribution['medium'] += 1
        else:
            distribution['low'] += 1
    
    risk_score = min(risk_score, 100)

    formatted_vulnerabilities = []
    for i, v in enumerate(vulnerabilidades):
        prioridade_lower = v.get('prioridade', 'low').lower()
        risk_level = 'critical' if prioridade_lower == 'crítico' else 'medium' if prioridade_lower == 'médio' else prioridade_lower
        
        formatted_vulnerabilities.append({
            "id": f"vuln-{i+1}",
            "name": v.get('tipo', 'Vulnerabilidade Desconhecida'),
            "riskLevel": risk_level,
            "location": v.get('parametro', 'N/A'),
            "scanner": v.get('scanner', 'N/A'),
            "description": f"Técnica de detecção: {v.get('tecnica', 'N/A')}. Mais detalhes disponíveis no log.",
            "evidence": v.get('evidencia', 'N/A'),
            "recommendation": "Verificar logs do scan para recomendações detalhadas."
        })

    return {
        "id": f"scan-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "target": resultados_brutos.get('alvo'),
        "date": resultados_brutos.get('timestamp'),
        "scanType": scan_type.replace('_', ' ').title(),
        "riskScore": risk_score,
        "totalVulnerabilities": total_vulnerabilidades,
        "openPorts": resultados_brutos.get('estatisticas', {}).get('portas_abertas', 0),
        "warnings": resultados_brutos.get('estatisticas', {}).get('avisos', 0),
        "vulnerabilities": formatted_vulnerabilities,
        "distribution": distribution,
        "technologies": resultados_brutos.get('estatisticas', {}).get('tecnologias', {
            "server": "N/A", "language": "N/A", "framework": "N/A", "os": "N/A", "cms": "N/A"
        }),
        "logEntries": []
    }

def main():
    """O ponto de partida de tudo."""
    ia = IAPentestMaster()
    
    if len(sys.argv) > 2:
        target = sys.argv[1]
        scan_type = sys.argv[2]
        
        resultados_brutos = {}
        if scan_type == 'analise':
            resultados_brutos = ia.analisar_alvo(target)
        elif scan_type == 'analise_exploracao':
            resultados_brutos = ia.executar_exploracao_inteligente(target)
        else:
            print(f"❌ Tipo de scan desconhecido: {scan_type}. Use 'analise' or 'analise_exploracao'.")
            sys.exit(1)
        
        if resultados_brutos:
            resultados_formatados = formatar_relatorio_para_frontend(resultados_brutos, scan_type)
            print("\n---JSON-REPORT-START---")
            print(json.dumps(resultados_formatados, indent=2))
            
    else:
        print("Uso: IA_main.py <alvo> <tipo_scan>")
        print("Exemplo: IA_main.py https://exemplo.com analise")
        sys.exit(1)

if __name__ == "__main__":
    main()
