"""
Integrated Security Analysis Pipeline
Orchestrates entire flow: Collectors → Features → ML → RL → Explainability
"""

import numpy as np
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

from loguru import logger

# Import all components
from src.collectors.http_collector import HTTPHeadersCollector
from src.collectors.tls_collector import TLSCollector
from src.collectors.dns_collector import DNSCollector
from src.features.feature_extractor import FeatureExtractor
from src.models.supervised.lgbm_classifier import LightGBMClassifier
from src.models.reinforcement.ppo_agent import PPOAgent
from src.explainability.shap_explainer import ShapExplainer
from src.explainability.nlg_generator import NLGGenerator
from src.explainability.html_report_generator import HTMLReportGenerator
from src.explainability.explanation_quality import ExplanationQualityEvaluator


class SecurityLevel(str, Enum):
    """Security risk levels."""
    SEGURO = "seguro"
    AVISO = "aviso"
    VULNERÁVEL = "vulnerável"
    CRÍTICO = "crítico"


@dataclass
class AnalysisResult:
    """Complete analysis result for a domain."""
    domain: str
    collection_time: float
    feature_time: float
    prediction_time: float
    explanation_time: float
    total_time: float
    
    # ML Results
    ml_prediction: str
    ml_score: float
    ml_features: Dict[str, float]
    
    # RL Results
    rl_action: Optional[str] = None
    rl_confidence: Optional[float] = None
    
    # Explanations
    shap_explanation: Optional[Dict] = None
    nlg_explanation: Optional[Dict] = None
    quality_metrics: Optional[Dict] = None
    html_report_path: Optional[str] = None
    
    # Status
    collected_features: int = 0
    status: str = "success"
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'domain': self.domain,
            'timestamp': datetime.now().isoformat(),
            'times': {
                'collection': self.collection_time,
                'feature_engineering': self.feature_time,
                'ml_prediction': self.prediction_time,
                'explanation': self.explanation_time,
                'total': self.total_time,
            },
            'ml_results': {
                'prediction': self.ml_prediction,
                'confidence': float(self.ml_score),
                'top_features': dict(list(self.ml_features.items())[:10]),
            },
            'rl_results': {
                'action': self.rl_action,
                'confidence': float(self.rl_confidence) if self.rl_confidence else None,
            },
            'explanation': self.nlg_explanation,
            'quality': self.quality_metrics,
            'report': self.html_report_path,
            'status': self.status,
            'error': self.error,
        }


class IntegratedPipeline:
    """
    Complete security analysis pipeline.
    
    Workflow:
    1. Data Collection (HTTP, TLS, DNS)
    2. Feature Engineering (87 features)
    3. ML Prediction (LightGBM)
    4. RL Action Selection (PPO)
    5. Explainability (SHAP + NLG + HTML)
    6. Quality Evaluation
    """
    
    def __init__(
        self,
        ml_model_path: Optional[Path] = None,
        rl_model_path: Optional[Path] = None,
        shap_background_size: int = 100
    ):
        """
        Initialize integrated pipeline.
        
        Args:
            ml_model_path: Path to LightGBM model
            rl_model_path: Path to PPO model
            shap_background_size: Size of background dataset for SHAP
        """
        logger.info("Initializing integrated pipeline...")
        
        # Initialize collectors
        self.http_collector = HTTPHeadersCollector()
        self.tls_collector = TLSCollector()
        self.dns_collector = DNSCollector()
        
        # Initialize feature extractor
        self.feature_extractor = FeatureExtractor()
        
        # Initialize models
        self.ml_model = None
        self.rl_agent = None
        
        if ml_model_path and ml_model_path.exists():
            self.ml_model = LightGBMClassifier()
            self.ml_model.load(ml_model_path)
            logger.info(f"Loaded ML model from {ml_model_path}")
        
        if rl_model_path and rl_model_path.exists():
            self.rl_agent = PPOAgent()
            self.rl_agent.load(rl_model_path)
            logger.info(f"Loaded RL agent from {rl_model_path}")
        
        # Initialize explainability components
        self.shap_explainer = None
        self.nlg_generator = NLGGenerator()
        self.html_generator = HTMLReportGenerator()
        self.quality_evaluator = ExplanationQualityEvaluator()
        
        # SHAP background data (create synthetic if no model available)
        if self.ml_model:
            np.random.seed(42)
            self.shap_background = np.random.randn(shap_background_size, 87)
            feature_names = [f"feature_{i}" for i in range(87)]
            class_names = ["seguro", "aviso", "vulnerável", "crítico"]
            
            try:
                self.shap_explainer = ShapExplainer(
                    self.ml_model.model,
                    self.shap_background,
                    feature_names,
                    class_names
                )
                logger.info("SHAP explainer initialized")
            except Exception as e:
                logger.warning(f"Could not initialize SHAP explainer: {e}")
                self.shap_explainer = None
        
        logger.info("Pipeline initialized successfully")
    
    def collect_data(self, domain: str) -> Dict[str, any]:
        """
        Collect security data from domain.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Dictionary with collected data
        """
        t0 = time.time()
        collected_data = {}
        
        try:
            # HTTP collection
            http_data = self.http_collector.collect(domain)
            collected_data['http'] = http_data
            
            # TLS collection
            tls_data = self.tls_collector.collect(domain)
            collected_data['tls'] = tls_data
            
            # DNS collection
            dns_data = self.dns_collector.collect(domain)
            collected_data['dns'] = dns_data
            
            collection_time = time.time() - t0
            logger.info(f"Data collection completed for {domain} ({collection_time:.3f}s)")
            
            return collected_data
            
        except Exception as e:
            logger.error(f"Data collection failed for {domain}: {e}")
            raise
    
    def extract_features(self, collected_data: Dict) -> Tuple[np.ndarray, Dict]:
        """
        Extract features from collected data.
        
        Args:
            collected_data: Data from collectors
            
        Returns:
            Tuple of (feature_vector, feature_dict)
        """
        t0 = time.time()
        
        try:
            # Restructure data for FeatureExtractor expectations
            structured_data = {
                "collectors": collected_data
            }
            
            # Extract features (returns tuple: (vector, dict))
            feature_vector, feature_dict = self.feature_extractor.extract_features(structured_data)
            
            extraction_time = time.time() - t0
            logger.info(f"Feature extraction completed ({extraction_time:.3f}s, {len(feature_dict)} features)")
            
            return feature_vector, feature_dict
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise
    
    def predict_ml(self, feature_vector: np.ndarray) -> Tuple[str, float, Dict]:
        """
        Get ML model prediction.
        
        Args:
            feature_vector: 87-dimensional feature vector
            
        Returns:
            Tuple of (prediction, score, feature_importance)
        """
        t0 = time.time()
        
        if not self.ml_model:
            logger.warning("ML model not available, returning default prediction")
            return "aviso", 0.5, {}
        
        try:
            # Get prediction
            prediction, score = self.ml_model.predict(feature_vector)
            
            # Get feature importance
            try:
                importance = self.ml_model.feature_importance()
                feature_importance = dict(zip([f"f{i}" for i in range(len(importance))], importance))
            except:
                feature_importance = {}
            
            prediction_time = time.time() - t0
            logger.info(f"ML prediction completed ({prediction_time:.3f}s): {prediction} ({score:.3f})")
            
            return prediction, score, feature_importance
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return "aviso", 0.5, {}
    
    def select_rl_action(self, feature_vector: np.ndarray) -> Tuple[Optional[str], Optional[float]]:
        """
        Get RL agent action.
        
        Args:
            feature_vector: 87-dimensional feature vector
            
        Returns:
            Tuple of (action, confidence)
        """
        if not self.rl_agent:
            logger.warning("RL agent not available")
            return None, None
        
        try:
            action, confidence = self.rl_agent.select_action(feature_vector)
            logger.info(f"RL action selected: {action} ({confidence:.3f})")
            return action, confidence
        except Exception as e:
            logger.warning(f"RL action selection failed: {e}")
            return None, None
    
    def generate_explanations(
        self,
        domain: str,
        ml_prediction: str,
        ml_score: float,
        feature_vector: np.ndarray
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """
        Generate SHAP and NLG explanations.
        
        Args:
            domain: Domain name
            ml_prediction: ML model prediction
            ml_score: ML confidence score
            feature_vector: Feature vector
            
        Returns:
            Tuple of (shap_explanation, nlg_explanation, quality_metrics)
        """
        t0 = time.time()
        
        try:
            # SHAP explanation
            shap_dict = None
            if self.shap_explainer:
                try:
                    explanation = self.shap_explainer.explain_instance(feature_vector)
                    shap_dict = {
                        'top_positive': explanation.top_positive_features[:5],
                        'top_negative': explanation.top_negative_features[:5],
                        'base_value': float(explanation.base_value),
                    }
                except Exception as e:
                    logger.warning(f"SHAP explanation failed: {e}")
            
            # NLG explanation
            nlg_dict = self.nlg_generator.generate_full_explanation(
                domain=domain,
                prediction=ml_prediction,
                prediction_score=ml_score,
                domain_type="HTTP",
                factor_names=[f"f{i}" for i in range(87)],
                factor_impacts=feature_vector,
                base_value=0.5
            )
            
            # Quality evaluation
            quality_dict = None
            try:
                metrics = self.quality_evaluator.evaluate_explanation(
                    prediction=ml_prediction,
                    shap_values=feature_vector,
                    explanation_text=nlg_dict['explanation'],
                    recommendations=nlg_dict['recommendations'].split('\n'),
                    explanation_domains=["HTTP"]
                )
                
                quality_dict = {
                    'fidelity': float(metrics.fidelity),
                    'stability': float(metrics.stability),
                    'sparsity': float(metrics.sparsity),
                    'completeness': float(metrics.completeness),
                    'comprehensibility': float(metrics.comprehensibility),
                    'coverage': float(metrics.coverage),
                    'actionability': float(metrics.actionability),
                    'overall_score': float(metrics.overall_score),
                }
            except Exception as e:
                logger.warning(f"Quality evaluation failed: {e}")
            
            explanation_time = time.time() - t0
            logger.info(f"Explanations generated ({explanation_time:.3f}s)")
            
            return shap_dict, nlg_dict, quality_dict
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return None, None, None
    
    def generate_html_report(
        self,
        domain: str,
        nlg_explanation: Dict,
        feature_dict: Dict,
        output_dir: Optional[Path] = None
    ) -> Optional[str]:
        """
        Generate HTML report.
        
        Args:
            domain: Domain name
            nlg_explanation: NLG explanation dictionary
            feature_dict: Feature importance dictionary
            output_dir: Output directory for reports
            
        Returns:
            Path to generated report
        """
        try:
            if not output_dir:
                output_dir = Path("data/reports")
            
            output_dir.mkdir(parents=True, exist_ok=True)
            report_path = output_dir / f"{domain.replace('.', '_')}_report.html"
            
            html = self.html_generator.generate_report(
                domain=domain,
                explanation_dict=nlg_explanation,
                features_importance=feature_dict,
                output_path=str(report_path)
            )
            
            logger.info(f"HTML report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.warning(f"HTML report generation failed: {e}")
            return None
    
    def analyze_domain(
        self,
        domain: str,
        generate_report: bool = True,
        report_dir: Optional[Path] = None
    ) -> AnalysisResult:
        """
        Complete analysis pipeline for a domain.
        
        Args:
            domain: Domain to analyze
            generate_report: Whether to generate HTML report
            report_dir: Directory for reports
            
        Returns:
            AnalysisResult object
        """
        total_start = time.time()
        result = AnalysisResult(
            domain=domain,
            collection_time=0,
            feature_time=0,
            prediction_time=0,
            explanation_time=0,
            total_time=0,
            ml_prediction="",
            ml_score=0.0,
            ml_features={}
        )
        
        try:
            # Step 1: Data Collection
            t0 = time.time()
            collected_data = self.collect_data(domain)
            result.collection_time = time.time() - t0
            
            # Step 2: Feature Engineering
            t0 = time.time()
            feature_vector, feature_dict = self.extract_features(collected_data)
            result.feature_time = time.time() - t0
            result.collected_features = len(feature_dict)
            result.ml_features = feature_dict
            
            # Step 3: ML Prediction
            t0 = time.time()
            ml_pred, ml_score, importance = self.predict_ml(feature_vector)
            result.prediction_time = time.time() - t0
            result.ml_prediction = ml_pred
            result.ml_score = float(ml_score)
            
            # Step 4: RL Action Selection
            rl_action, rl_conf = self.select_rl_action(feature_vector)
            result.rl_action = rl_action
            result.rl_confidence = rl_conf
            
            # Step 5: Explanations
            t0 = time.time()
            shap_exp, nlg_exp, quality = self.generate_explanations(
                domain, ml_pred, ml_score, feature_vector
            )
            result.explanation_time = time.time() - t0
            result.shap_explanation = shap_exp
            result.nlg_explanation = nlg_exp
            result.quality_metrics = quality
            
            # Step 6: HTML Report (optional)
            if generate_report and nlg_exp:
                report_path = self.generate_html_report(
                    domain, nlg_exp, feature_dict, report_dir
                )
                result.html_report_path = report_path
            
            result.total_time = time.time() - total_start
            result.status = "success"
            
            logger.info(f"✓ Analysis completed for {domain} ({result.total_time:.3f}s)")
            
        except Exception as e:
            result.status = "error"
            result.error = str(e)
            logger.error(f"✗ Analysis failed for {domain}: {e}")
        
        return result
    
    def analyze_batch(
        self,
        domains: List[str],
        generate_reports: bool = True,
        report_dir: Optional[Path] = None
    ) -> List[AnalysisResult]:
        """
        Analyze multiple domains.
        
        Args:
            domains: List of domains
            generate_reports: Whether to generate reports
            report_dir: Directory for reports
            
        Returns:
            List of AnalysisResult objects
        """
        logger.info(f"Starting batch analysis of {len(domains)} domains...")
        
        results = []
        for i, domain in enumerate(domains, 1):
            logger.info(f"[{i}/{len(domains)}] Analyzing {domain}...")
            result = self.analyze_domain(domain, generate_reports, report_dir)
            results.append(result)
        
        # Summary statistics
        successful = sum(1 for r in results if r.status == "success")
        total_time = sum(r.total_time for r in results)
        avg_time = total_time / len(results) if results else 0
        
        logger.info(f"\n✓ Batch analysis completed:")
        logger.info(f"  - Successful: {successful}/{len(domains)}")
        logger.info(f"  - Total time: {total_time:.2f}s")
        logger.info(f"  - Average time: {avg_time:.2f}s/domain")
        
        return results


if __name__ == '__main__':
    # Example usage
    pipeline = IntegratedPipeline()
    
    test_domains = [
        "example.com",
        "google.com",
        "github.com",
    ]
    
    results = pipeline.analyze_batch(test_domains)
    
    # Export results
    for result in results:
        result_dict = result.to_dict()
        print(json.dumps(result_dict, indent=2))
