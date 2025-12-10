"""
Natural Language Generation Module
Generate human-readable explanations from SHAP values
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityRisk(Enum):
    """Security risk levels."""
    LOW = "Seguro"
    MEDIUM = "Aviso"
    HIGH = "Vulnerável"
    CRITICAL = "Crítico"


@dataclass
class ExplanationTemplate:
    """Template for generating explanations."""
    
    risk_level: SecurityRisk
    primary_factors: str
    secondary_factors: str
    recommendations: List[str]
    confidence_phrase: str
    

class NLGGenerator:
    """
    Natural Language Generation engine for explanations.
    
    Features:
    - Domain-specific templates
    - Risk level aware messaging
    - Confidence-calibrated language
    - Actionable recommendations
    """
    
    # Domain templates mapping
    DOMAIN_TEMPLATES = {
        'HTTP': {
            'factors': {
                'insecure_headers': 'ausência de headers de segurança',
                'missing_hsts': 'HSTS não configurado',
                'weak_ciphers': 'suporte a cifras fracas',
                'old_server': 'servidor web desatualizado',
                'xss_vulnerable': 'potencial vulnerabilidade XSS',
                'csrf_unprotected': 'falta de proteção CSRF'
            },
            'recommendations': {
                'insecure_headers': 'Implementar headers de segurança (Content-Security-Policy, X-Frame-Options)',
                'missing_hsts': 'Ativar HTTP Strict Transport Security (HSTS)',
                'weak_ciphers': 'Desabilitar suporte a cifras fracas (RC4, DES)',
                'old_server': 'Atualizar ou patchear o servidor web',
                'xss_vulnerable': 'Implementar input validation e output encoding',
                'csrf_unprotected': 'Implementar tokens CSRF e validação de origem'
            }
        },
        'TLS': {
            'factors': {
                'expired_cert': 'certificado expirado',
                'weak_key': 'chave criptográfica fraca',
                'self_signed': 'certificado auto-assinado',
                'old_tls': 'versão TLS desatualizada',
                'weak_signature': 'algoritmo de assinatura vulnerável',
                'missing_san': 'Subject Alternative Name ausente'
            },
            'recommendations': {
                'expired_cert': 'Renovar o certificado SSL/TLS',
                'weak_key': 'Usar chaves criptográficas de 2048 bits ou superiores',
                'self_signed': 'Obter certificado assinado por uma CA confiável',
                'old_tls': 'Atualizar para TLS 1.2 ou 1.3',
                'weak_signature': 'Usar SHA-256 ou algoritmos mais fortes',
                'missing_san': 'Adicionar domains relevantes ao SAN'
            }
        },
        'DNS': {
            'factors': {
                'no_dnssec': 'DNSSEC não configurado',
                'weak_ttl': 'TTL muito baixo',
                'dns_poisoning': 'vulnerável a DNS poisoning',
                'open_resolver': 'servidor DNS aberto',
                'slow_resolution': 'resolução DNS lenta',
                'no_spf': 'registro SPF ausente'
            },
            'recommendations': {
                'no_dnssec': 'Ativar DNSSEC para autenticação de DNS',
                'weak_ttl': 'Aumentar TTL para valores apropriados (3600-86400)',
                'dns_poisoning': 'Usar query authentication e response validation',
                'open_resolver': 'Restringir acesso ao servidor DNS',
                'slow_resolution': 'Otimizar infraestrutura DNS ou usar CDN',
                'no_spf': 'Configurar registro SPF para validação de email'
            }
        },
        'PORTS': {
            'factors': {
                'open_ports': 'portas abertas desnecessárias',
                'default_services': 'serviços padrão rodando',
                'weak_services': 'serviços vulneráveis ativo',
                'no_firewall': 'firewall não configurado',
                'rpc_exposed': 'RPC exposto',
                'telnet_enabled': 'Telnet habilitado'
            },
            'recommendations': {
                'open_ports': 'Configurar firewall para bloquear portas desnecessárias',
                'default_services': 'Desabilitar serviços padrão não utilizados',
                'weak_services': 'Desabilitar ou patchear serviços vulneráveis',
                'no_firewall': 'Implementar regras de firewall restritivas',
                'rpc_exposed': 'Não expor RPC na internet',
                'telnet_enabled': 'Usar SSH em vez de Telnet'
            }
        },
        'WHOIS': {
            'factors': {
                'privacy_exposed': 'informações de contato expostas',
                'stale_data': 'dados de registro desatualizados',
                'suspicious_registrant': 'registrante suspeito',
                'recent_change': 'registro alterado recentemente',
                'unlocked_domain': 'domínio não travado'
            },
            'recommendations': {
                'privacy_exposed': 'Usar serviço de privacy do registrador',
                'stale_data': 'Atualizar informações de registro',
                'suspicious_registrant': 'Verificar proprietário e autoridades',
                'recent_change': 'Investigar motivo da alteração',
                'unlocked_domain': 'Ativar lock de domínio no registrador'
            }
        },
        'TECH_STACK': {
            'factors': {
                'outdated_framework': 'framework desatualizado',
                'known_vulnerability': 'vulnerabilidade conhecida',
                'unsupported_version': 'versão não suportada',
                'deprecated_tech': 'tecnologia descontinuada',
                'weak_cms': 'CMS vulnerável',
                'plugin_risks': 'plugins/extensões suspeitas'
            },
            'recommendations': {
                'outdated_framework': 'Atualizar para versão LTS mais recente',
                'known_vulnerability': 'Aplicar patch de segurança urgentemente',
                'unsupported_version': 'Migrar para versão ativamente mantida',
                'deprecated_tech': 'Refatorar usando tecnologias modernas',
                'weak_cms': 'Considerar migração para CMS mais seguro',
                'plugin_risks': 'Auditar e remover plugins desnecessários'
            }
        }
    }
    
    # Risk level templates
    RISK_TEMPLATES = {
        'LOW': {
            'intro': 'Esta análise indica um nível **BAIXO** de risco de segurança.',
            'summary': 'O domínio demonstra boas práticas de segurança com apenas pequenas melhorias recomendadas.',
            'confidence': 'com alta confiança',
            'action': 'Monitoramento regular é recomendado'
        },
        'MEDIUM': {
            'intro': 'Esta análise indica um nível **MÉDIO** de risco de segurança.',
            'summary': 'Foram identificadas várias questões de segurança que deveriam ser endereçadas.',
            'confidence': 'com confiança moderada',
            'action': 'Ação remediativa é recomendada dentro de 30 dias'
        },
        'HIGH': {
            'intro': 'Esta análise indica um nível **ALTO** de risco de segurança.',
            'summary': 'Foram identificadas vulnerabilidades significativas que requerem atenção imediata.',
            'confidence': 'com alta confiança',
            'action': 'Ação remediativa urgente é recomendada (dentro de 7 dias)'
        },
        'CRITICAL': {
            'intro': 'Esta análise indica um nível **CRÍTICO** de risco de segurança.',
            'summary': 'Foram identificadas vulnerabilidades críticas com risco de exploração imediata.',
            'confidence': 'com muito alta confiança',
            'action': 'Ação remediativa imediata é CRÍTICA (dentro de 24 horas)'
        }
    }
    
    def __init__(self):
        """Initialize NLG generator."""
        logger.info("Initializing NLG generator...")
    
    def get_risk_level(self, prediction: str) -> SecurityRisk:
        """Map prediction to risk level."""
        if prediction.lower() == 'seguro':
            return SecurityRisk.LOW
        elif prediction.lower() == 'aviso':
            return SecurityRisk.MEDIUM
        elif prediction.lower() == 'vulnerável':
            return SecurityRisk.HIGH
        elif prediction.lower() == 'crítico':
            return SecurityRisk.CRITICAL
        else:
            return SecurityRisk.MEDIUM
    
    def generate_factor_explanation(
        self,
        domain_type: str,
        factor_names: List[str],
        factor_impacts: List[float],
        top_k: int = 5
    ) -> str:
        """
        Generate explanation for top contributing factors.
        
        Args:
            domain_type: Type of domain (HTTP, TLS, DNS, PORTS, WHOIS, TECH_STACK)
            factor_names: Names of factors
            factor_impacts: Impact values (SHAP values)
            top_k: Number of top factors to explain
            
        Returns:
            Natural language explanation
        """
        templates = self.DOMAIN_TEMPLATES.get(domain_type.upper(), {})
        factor_dict = templates.get('factors', {})
        
        # Convert to numpy array for safe operations
        import numpy as np
        factor_impacts_array = np.asarray(factor_impacts).flatten()
        
        # Limit factor_names to match the size of factor_impacts_array
        factor_names_list = list(factor_names[:len(factor_impacts_array)])
        
        # Get top factors
        try:
            top_indices = sorted(
                range(len(factor_impacts_array)),
                key=lambda i: abs(float(factor_impacts_array[i])),
                reverse=True
            )[:top_k]
        except (TypeError, ValueError) as e:
            logger.warning(f"Error sorting factors: {e}, returning empty explanation")
            return "Nenhum fator significativo identificado"
        
        explanations = []
        for idx in top_indices:
            if idx >= len(factor_names_list):
                continue
                
            factor_name = factor_names_list[idx]
            factor_impact = float(factor_impacts_array[idx])
            
            # Get human-readable factor name
            readable_name = factor_dict.get(factor_name, factor_name)
            
            # Determine direction
            direction = "aumentou" if factor_impact > 0 else "diminuiu"
            magnitude = abs(factor_impact)
            
            explanations.append(f"- {readable_name.capitalize()} {direction} o risco ({magnitude:.3f})")
        
        return "\n".join(explanations) if explanations else "Nenhum fator significativo identificado"
    
    def generate_recommendations(
        self,
        domain_type: str,
        factor_names: List[str],
        factor_impacts: List[float],
        top_k: int = 3
    ) -> List[str]:
        """
        Generate actionable recommendations.
        
        Args:
            domain_type: Type of domain
            factor_names: Names of factors
            factor_impacts: Impact values
            top_k: Number of top recommendations
            
        Returns:
            List of recommendation strings
        """
        templates = self.DOMAIN_TEMPLATES.get(domain_type.upper(), {})
        recommend_dict = templates.get('recommendations', {})
        
        # Convert to numpy array for safe operations
        import numpy as np
        factor_impacts_array = np.asarray(factor_impacts).flatten()
        
        # Limit factor_names to match size
        factor_names_list = list(factor_names[:len(factor_impacts_array)])
        
        # Get top factors
        try:
            top_indices = sorted(
                range(len(factor_impacts_array)),
                key=lambda i: abs(float(factor_impacts_array[i])),
                reverse=True
            )[:top_k]
        except (TypeError, ValueError) as e:
            logger.warning(f"Error sorting recommendations: {e}, returning empty list")
            return []
        
        recommendations = []
        for idx in top_indices:
            if idx >= len(factor_names_list):
                continue
                
            factor_name = factor_names_list[idx]
            
            # Get recommendation
            recommendation = recommend_dict.get(factor_name)
            if recommendation and recommendation not in recommendations:
                recommendations.append(recommendation)
        
        return recommendations
    
    def generate_full_explanation(
        self,
        domain: str,
        prediction: str,
        prediction_score: float,
        domain_type: str,
        factor_names: List[str],
        factor_impacts: List[float],
        base_value: float
    ) -> Dict[str, str]:
        """
        Generate complete explanation report.
        
        Args:
            domain: Domain being analyzed
            prediction: Predicted risk level
            prediction_score: Confidence score
            domain_type: Type of analysis domain
            factor_names: Factor names
            factor_impacts: SHAP values
            base_value: SHAP base value
            
        Returns:
            Dictionary with different explanation components
        """
        risk_level = self.get_risk_level(prediction)
        risk_key = risk_level.name
        
        # Get templates
        risk_template = self.RISK_TEMPLATES.get(risk_key, self.RISK_TEMPLATES['MEDIUM'])
        
        # Generate components
        intro = f"{risk_template['intro']}\n\n**Domínio:** {domain}"
        
        summary = risk_template['summary']
        
        explanation = self.generate_factor_explanation(
            domain_type,
            factor_names,
            factor_impacts,
            top_k=5
        )
        
        recommendations = self.generate_recommendations(
            domain_type,
            factor_names,
            factor_impacts,
            top_k=3
        )
        
        recommendations_text = "\n".join(
            f"{i+1}. {rec}" for i, rec in enumerate(recommendations)
        )
        
        # Confidence text
        confidence = f"Este resultado foi produzido {risk_template['confidence']} "
        confidence += f"(score: {prediction_score:.1%})"
        
        # Action text
        action = risk_template['action']
        
        return {
            'introduction': intro,
            'summary': summary,
            'explanation': explanation,
            'recommendations': recommendations_text if recommendations else 'Nenhuma recomendação específica',
            'confidence': confidence,
            'action_required': action,
            'risk_level': prediction
        }
    
    def generate_comparison(
        self,
        domain1_dict: Dict,
        domain2_dict: Dict
    ) -> str:
        """
        Generate comparison between two domain analyses.
        
        Args:
            domain1_dict: First explanation dictionary
            domain2_dict: Second explanation dictionary
            
        Returns:
            Comparison text
        """
        comparison = f"""
## Comparação de Análise

**Domínio 1:** {domain1_dict['introduction']}
- Risco: {domain1_dict['risk_level']}

**Domínio 2:** {domain2_dict['introduction']}
- Risco: {domain2_dict['risk_level']}

A diferença principal é que:
- Domínio 1 tem {domain1_dict['confidence']}
- Domínio 2 tem {domain2_dict['confidence']}
        """
        
        return comparison.strip()
    
    def get_summary_sentence(self, prediction: str, prediction_score: float) -> str:
        """
        Get one-sentence summary.
        
        Args:
            prediction: Risk level prediction
            prediction_score: Confidence score
            
        Returns:
            Single sentence summary
        """
        risk_level = self.get_risk_level(prediction)
        
        if risk_level == SecurityRisk.LOW:
            return f"Este domínio apresenta baixo risco de segurança ({prediction_score:.0%} de confiança)"
        elif risk_level == SecurityRisk.MEDIUM:
            return f"Este domínio apresenta risco moderado de segurança ({prediction_score:.0%} de confiança)"
        elif risk_level == SecurityRisk.HIGH:
            return f"Este domínio apresenta alto risco de segurança ({prediction_score:.0%} de confiança)"
        else:  # CRITICAL
            return f"Este domínio apresenta risco crítico de segurança ({prediction_score:.0%} de confiança)"
