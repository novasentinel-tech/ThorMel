"""
HTML Report Generation
Create professional HTML reports from explanations
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """
    Generate professional HTML reports with explanations.
    
    Features:
    - Responsive design
    - Dark/light themes
    - Interactive visualizations
    - PDF-friendly styling
    - Mobile-optimized
    """
    
    CSS_TEMPLATE = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin: 15px 0;
            font-size: 1.1em;
        }
        
        .risk-low {
            background: #4CAF50;
            color: white;
        }
        
        .risk-medium {
            background: #FF9800;
            color: white;
        }
        
        .risk-high {
            background: #f44336;
            color: white;
        }
        
        .risk-critical {
            background: #8B0000;
            color: white;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
            border-left: 4px solid #667eea;
            padding-left: 20px;
        }
        
        .section h2 {
            font-size: 1.8em;
            margin-bottom: 15px;
            color: #333;
        }
        
        .section h3 {
            font-size: 1.3em;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #555;
        }
        
        .score-bar {
            background: #e0e0e0;
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin: 15px 0;
        }
        
        .score-fill {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }
        
        .factor-list {
            list-style: none;
            margin: 15px 0;
        }
        
        .factor-list li {
            padding: 12px;
            margin: 8px 0;
            background: #f5f5f5;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }
        
        .recommendation {
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        
        .recommendation strong {
            color: #2e7d32;
        }
        
        .confidence-section {
            background: #f3e5f5;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #9c27b0;
        }
        
        .action-section {
            background: #fff3e0;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #ff9800;
            font-weight: 500;
        }
        
        .action-critical {
            background: #ffebee;
            border-left-color: #f44336;
        }
        
        .feature-importance {
            margin: 20px 0;
        }
        
        .feature-bar {
            display: flex;
            margin: 8px 0;
            align-items: center;
        }
        
        .feature-name {
            width: 200px;
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .feature-importance-bar {
            flex: 1;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            margin: 0 10px;
            overflow: hidden;
        }
        
        .feature-importance-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
        
        .feature-value {
            width: 50px;
            text-align: right;
            font-size: 0.9em;
            color: #666;
        }
        
        .footer {
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
            font-size: 0.9em;
            color: #666;
        }
        
        .metadata {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        
        .metadata-item {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 6px;
        }
        
        .metadata-label {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 0;
                border-radius: 0;
            }
            .header {
                padding: 20px;
            }
            .header h1 {
                font-size: 1.8em;
            }
            .metadata {
                grid-template-columns: 1fr;
            }
            .feature-name {
                width: 150px;
            }
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            .container {
                box-shadow: none;
                border-radius: 0;
            }
        }
    </style>
    """
    
    def __init__(self):
        """Initialize HTML report generator."""
        logger.info("Initializing HTML report generator...")
    
    def generate_report(
        self,
        domain: str,
        explanation_dict: Dict,
        features_importance: Dict[str, float],
        top_features: List[tuple] = None,
        metadata: Dict = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate complete HTML report.
        
        Args:
            domain: Domain being analyzed
            explanation_dict: Dictionary from NLG generator
            features_importance: Feature importance scores
            top_features: Top contributing features
            metadata: Additional metadata
            output_path: Path to save HTML file
            
        Returns:
            HTML string (also saves to file if output_path provided)
        """
        # Get risk level and corresponding styling
        risk_level = explanation_dict.get('risk_level', 'Aviso').lower()
        risk_badge_class = f"risk-{self._get_risk_class(risk_level)}"
        
        # Build HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Segurança - {domain}</title>
            {self.CSS_TEMPLATE}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Relatório de Análise de Segurança</h1>
                    <p>Análise de Risco para: <strong>{domain}</strong></p>
                    <span class="{risk_badge_class} risk-badge">{explanation_dict.get('risk_level', 'Aviso')}</span>
                </div>
                
                <div class="content">
        """
        
        # Introduction section
        html += f"""
                    <div class="section">
                        <h2>📋 Introdução</h2>
                        <p>{explanation_dict.get('introduction', 'N/A')}</p>
                    </div>
        """
        
        # Summary section
        html += f"""
                    <div class="section">
                        <h2>📊 Resumo Executivo</h2>
                        <p>{explanation_dict.get('summary', 'N/A')}</p>
                    </div>
        """
        
        # Key factors section
        html += f"""
                    <div class="section">
                        <h2>⚠️ Fatores Principais</h2>
                        <p>{explanation_dict.get('explanation', 'N/A')}</p>
                    </div>
        """
        
        # Feature importance section
        if features_importance:
            html += self._generate_importance_section(features_importance)
        
        # Recommendations section
        html += f"""
                    <div class="section">
                        <h2>💡 Recomendações</h2>
                        <div class="recommendation">
                            {explanation_dict.get('recommendations', 'Nenhuma recomendação').replace(chr(10), '<br>')}
                        </div>
                    </div>
        """
        
        # Confidence section
        html += f"""
                    <div class="confidence-section">
                        <strong>Confiança da Análise:</strong><br>
                        {explanation_dict.get('confidence', 'N/A')}
                    </div>
        """
        
        # Action required section
        action_class = "action-critical" if risk_level == 'crítico' else ""
        html += f"""
                    <div class="action-section {action_class}">
                        <strong>🎯 Ação Necessária:</strong><br>
                        {explanation_dict.get('action_required', 'N/A')}
                    </div>
        """
        
        # Metadata section
        if metadata:
            html += self._generate_metadata_section(metadata)
        
        # Footer
        html += f"""
                </div>
                
                <div class="footer">
                    <p>Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
                    <p>Sistema de Análise de Segurança DeepAI v1.0 | Fase E: Explainability</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save to file if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"HTML report saved to {output_path}")
        
        return html
    
    def _generate_importance_section(self, importance_dict: Dict[str, float]) -> str:
        """Generate feature importance visualization."""
        html = """
                    <div class="section">
                        <h2>📈 Importância das Características</h2>
                        <div class="feature-importance">
        """
        
        # Sort by importance
        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        max_importance = max([v for k, v in sorted_features]) if sorted_features else 1
        
        for feature_name, importance in sorted_features:
            percentage = (importance / max_importance) * 100 if max_importance > 0 else 0
            html += f"""
                            <div class="feature-bar">
                                <div class="feature-name">{feature_name}</div>
                                <div class="feature-importance-bar">
                                    <div class="feature-importance-fill" style="width: {percentage}%"></div>
                                </div>
                                <div class="feature-value">{importance:.3f}</div>
                            </div>
            """
        
        html += """
                        </div>
                    </div>
        """
        
        return html
    
    def _generate_metadata_section(self, metadata: Dict) -> str:
        """Generate metadata section."""
        html = """
                    <div class="section">
                        <h2>ℹ️ Informações Adicionais</h2>
                        <div class="metadata">
        """
        
        for key, value in metadata.items():
            html += f"""
                            <div class="metadata-item">
                                <div class="metadata-label">{key}</div>
                                <div>{value}</div>
                            </div>
            """
        
        html += """
                        </div>
                    </div>
        """
        
        return html
    
    def _get_risk_class(self, risk_level: str) -> str:
        """Map risk level to CSS class."""
        risk_map = {
            'seguro': 'low',
            'aviso': 'medium',
            'vulnerável': 'high',
            'crítico': 'critical'
        }
        return risk_map.get(risk_level.lower(), 'medium')
    
    def generate_batch_report(
        self,
        domains_data: List[Dict],
        output_dir: str = "reports"
    ) -> Dict[str, str]:
        """
        Generate reports for multiple domains.
        
        Args:
            domains_data: List of domain data dictionaries
            output_dir: Directory to save reports
            
        Returns:
            Dictionary mapping domain to report path
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        report_paths = {}
        
        for domain_data in domains_data:
            domain = domain_data.get('domain', 'unknown')
            output_path = f"{output_dir}/{domain.replace('.', '_')}_report.html"
            
            self.generate_report(
                domain=domain,
                explanation_dict=domain_data.get('explanation', {}),
                features_importance=domain_data.get('importance', {}),
                top_features=domain_data.get('top_features'),
                metadata={
                    'Domínio': domain,
                    'Data': datetime.now().strftime('%d/%m/%Y'),
                    'Horário': datetime.now().strftime('%H:%M:%S')
                },
                output_path=output_path
            )
            
            report_paths[domain] = output_path
        
        logger.info(f"Generated {len(report_paths)} HTML reports")
        return report_paths
