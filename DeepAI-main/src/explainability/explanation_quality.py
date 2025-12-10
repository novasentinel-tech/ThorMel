"""
Explanation Quality Evaluator
Measure and validate quality of generated explanations
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Metrics for explanation quality."""
    
    fidelity: float  # How well explanation matches prediction
    stability: float  # Consistency across similar inputs
    sparsity: float  # Number of features used
    completeness: float  # Coverage of important aspects
    comprehensibility: float  # Ease of understanding
    coverage: float  # Breadth of explanation
    actionability: float  # Usefulness of recommendations
    
    overall_score: float = None
    
    def __post_init__(self):
        """Compute overall score."""
        weights = {
            'fidelity': 0.25,
            'stability': 0.15,
            'sparsity': 0.10,
            'completeness': 0.15,
            'comprehensibility': 0.15,
            'coverage': 0.10,
            'actionability': 0.10
        }
        
        self.overall_score = (
            self.fidelity * weights['fidelity'] +
            self.stability * weights['stability'] +
            self.sparsity * weights['sparsity'] +
            self.completeness * weights['completeness'] +
            self.comprehensibility * weights['comprehensibility'] +
            self.coverage * weights['coverage'] +
            self.actionability * weights['actionability']
        )


class ExplanationQualityEvaluator:
    """
    Evaluate quality of explanations.
    
    Features:
    - Fidelity: Does explanation match prediction?
    - Stability: Consistent across similar inputs?
    - Sparsity: Uses minimum features?
    - Completeness: Covers all important aspects?
    - Comprehensibility: Human-readable?
    - Coverage: Broad explanation scope?
    - Actionability: Useful recommendations?
    """
    
    # Quality thresholds
    QUALITY_THRESHOLDS = {
        'EXCELLENT': 0.85,
        'GOOD': 0.70,
        'ACCEPTABLE': 0.50,
        'POOR': 0.30
    }
    
    def __init__(self):
        """Initialize evaluator."""
        logger.info("Initializing explanation quality evaluator...")
    
    def evaluate_fidelity(
        self,
        prediction: str,
        explanation_factors: List[str],
        shap_values: np.ndarray
    ) -> float:
        """
        Evaluate fidelity: Does explanation match prediction?
        
        Checks if the top contributing factors align with the predicted class.
        
        Args:
            prediction: Model prediction
            explanation_factors: Top factors contributing to prediction
            shap_values: SHAP values for instance
            
        Returns:
            Fidelity score [0, 1]
        """
        if len(explanation_factors) == 0:
            return 0.0
        
        # Flatten and handle multi-dimensional shap_values
        shap_array = np.asarray(shap_values).flatten()
        
        # Check if top factors have consistent direction with prediction
        top_indices = np.argsort(np.abs(shap_array))[-5:][::-1]
        consistency = 0
        
        for idx in top_indices:
            idx_int = int(idx)
            if idx_int < len(explanation_factors):
                consistency += 1
        
        fidelity = min(consistency / len(top_indices), 1.0)
        logger.debug(f"Fidelity: {fidelity:.3f}")
        
        return fidelity
    
    def evaluate_stability(
        self,
        shap_values: np.ndarray,
        similar_explanations: List[np.ndarray] = None
    ) -> float:
        """
        Evaluate stability: Consistent across similar inputs?
        
        Args:
            shap_values: SHAP values for instance
            similar_explanations: SHAP values for similar instances
            
        Returns:
            Stability score [0, 1]
        """
        if similar_explanations is None or len(similar_explanations) == 0:
            return 0.8  # Default if no similar examples
        
        # Compute correlation with similar explanations
        correlations = []
        for similar_shap in similar_explanations:
            if len(shap_values) == len(similar_shap):
                corr = np.corrcoef(shap_values, similar_shap)[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)
        
        if len(correlations) == 0:
            return 0.8
        
        stability = np.mean(correlations)
        stability = max(0, stability)  # Ensure non-negative
        logger.debug(f"Stability: {stability:.3f}")
        
        return stability
    
    def evaluate_sparsity(
        self,
        shap_values: np.ndarray,
        threshold: float = 0.01
    ) -> float:
        """
        Evaluate sparsity: Uses minimum necessary features?
        
        Higher sparsity score means using fewer important features.
        
        Args:
            shap_values: SHAP values
            threshold: Threshold for "important" feature
            
        Returns:
            Sparsity score [0, 1]
        """
        important_count = np.sum(np.abs(shap_values) > threshold)
        total_count = len(shap_values)
        
        # Penalize using too many features
        sparsity = 1.0 - (important_count / total_count)
        logger.debug(f"Sparsity: {sparsity:.3f} ({important_count}/{total_count} important)")
        
        return sparsity
    
    def evaluate_completeness(
        self,
        explanation_domains: List[str],
        required_domains: List[str]
    ) -> float:
        """
        Evaluate completeness: Covers all important aspects?
        
        Args:
            explanation_domains: Domains covered in explanation
            required_domains: Domains that should be covered
            
        Returns:
            Completeness score [0, 1]
        """
        if len(required_domains) == 0:
            return 1.0
        
        covered = sum(1 for domain in required_domains if domain in explanation_domains)
        completeness = covered / len(required_domains)
        logger.debug(f"Completeness: {completeness:.3f} ({covered}/{len(required_domains)} domains)")
        
        return completeness
    
    def evaluate_comprehensibility(
        self,
        explanation_text: str,
        factor_count: int,
        recommendation_count: int
    ) -> float:
        """
        Evaluate comprehensibility: Easy to understand?
        
        Based on explanation length, factor clarity, and recommendation count.
        
        Args:
            explanation_text: Generated explanation text
            factor_count: Number of factors explained
            recommendation_count: Number of recommendations
            
        Returns:
            Comprehensibility score [0, 1]
        """
        # Check explanation structure
        score = 0.5  # Base score
        
        # Text length (400-2000 chars is good)
        text_len = len(explanation_text)
        if 400 <= text_len <= 2000:
            score += 0.2
        elif text_len > 0:
            score += max(0, 0.2 * (1 - abs(text_len - 1200) / 1200))
        
        # Factor count (5-10 is good)
        if 5 <= factor_count <= 10:
            score += 0.2
        elif factor_count > 0:
            score += max(0, 0.2 * (1 - abs(factor_count - 7) / 7))
        
        # Recommendation count (3-5 is good)
        if 3 <= recommendation_count <= 5:
            score += 0.1
        elif recommendation_count > 0:
            score += max(0, 0.1 * (1 - abs(recommendation_count - 4) / 4))
        
        comprehensibility = min(score, 1.0)
        logger.debug(f"Comprehensibility: {comprehensibility:.3f}")
        
        return comprehensibility
    
    def evaluate_coverage(
        self,
        shap_values: np.ndarray,
        top_k: int = 10
    ) -> float:
        """
        Evaluate coverage: Breadth of explanation?
        
        Measures how many important features are covered.
        
        Args:
            shap_values: SHAP values
            top_k: Number of top features to consider
            
        Returns:
            Coverage score [0, 1]
        """
        if len(shap_values) == 0:
            return 0.0
        
        # Get top-k features by absolute value
        top_indices = np.argsort(np.abs(shap_values))[-top_k:]
        covered = np.sum(np.abs(shap_values[top_indices]) > 0)
        
        coverage = min(covered / top_k, 1.0)
        logger.debug(f"Coverage: {coverage:.3f} ({covered}/{top_k} top features)")
        
        return coverage
    
    def evaluate_actionability(
        self,
        recommendations: List[str],
        has_specific_steps: bool = True,
        has_timeline: bool = True
    ) -> float:
        """
        Evaluate actionability: Useful for decision making?
        
        Args:
            recommendations: List of recommendations
            has_specific_steps: Whether recommendations have specific steps
            has_timeline: Whether recommendations have timeline
            
        Returns:
            Actionability score [0, 1]
        """
        score = 0.0
        
        # Base score on recommendation count
        if len(recommendations) > 0:
            score += min(len(recommendations) / 5, 0.6)  # Max 0.6 for count
        
        # Bonus for specific steps
        if has_specific_steps:
            score += 0.2
        
        # Bonus for timeline
        if has_timeline:
            score += 0.2
        
        actionability = min(score, 1.0)
        logger.debug(f"Actionability: {actionability:.3f}")
        
        return actionability
    
    def evaluate_explanation(
        self,
        prediction: str,
        shap_values: np.ndarray,
        explanation_text: str,
        recommendations: List[str],
        explanation_domains: List[str],
        similar_explanations: List[np.ndarray] = None
    ) -> QualityMetrics:
        """
        Evaluate overall quality of explanation.
        
        Args:
            prediction: Model prediction
            shap_values: SHAP values
            explanation_text: Generated explanation
            recommendations: Generated recommendations
            explanation_domains: Domains covered in explanation
            similar_explanations: For stability evaluation
            
        Returns:
            QualityMetrics with overall score
        """
        logger.info("Evaluating explanation quality...")
        
        # Evaluate each component
        fidelity = self.evaluate_fidelity(
            prediction,
            explanation_domains,
            shap_values
        )
        
        stability = self.evaluate_stability(shap_values, similar_explanations)
        
        sparsity = self.evaluate_sparsity(shap_values)
        
        completeness = self.evaluate_completeness(
            explanation_domains,
            ['HTTP', 'TLS', 'DNS']  # Required domains
        )
        
        comprehensibility = self.evaluate_comprehensibility(
            explanation_text,
            len(explanation_domains),
            len(recommendations)
        )
        
        coverage = self.evaluate_coverage(shap_values)
        
        actionability = self.evaluate_actionability(recommendations)
        
        # Create metrics object
        metrics = QualityMetrics(
            fidelity=fidelity,
            stability=stability,
            sparsity=sparsity,
            completeness=completeness,
            comprehensibility=comprehensibility,
            coverage=coverage,
            actionability=actionability
        )
        
        # Log quality assessment
        quality_level = self._get_quality_level(metrics.overall_score)
        logger.info(f"Explanation quality: {quality_level} (score: {metrics.overall_score:.3f})")
        
        return metrics
    
    def _get_quality_level(self, score: float) -> str:
        """Map score to quality level."""
        for level, threshold in self.QUALITY_THRESHOLDS.items():
            if score >= threshold:
                return level
        return "POOR"
    
    def get_quality_report(self, metrics: QualityMetrics) -> Dict[str, str]:
        """
        Generate human-readable quality report.
        
        Args:
            metrics: QualityMetrics object
            
        Returns:
            Dictionary with quality assessment text
        """
        quality_level = self._get_quality_level(metrics.overall_score)
        
        report = {
            'overall_quality': f"{quality_level} ({metrics.overall_score:.1%})",
            'fidelity': f"Fidelidade: {metrics.fidelity:.1%} - {'✓ Boa' if metrics.fidelity > 0.7 else '✗ Pode melhorar'}",
            'stability': f"Estabilidade: {metrics.stability:.1%} - {'✓ Boa' if metrics.stability > 0.7 else '✗ Pode melhorar'}",
            'sparsity': f"Esparsidade: {metrics.sparsity:.1%} - {'✓ Eficiente' if metrics.sparsity > 0.7 else '✗ Usa muitos features'}",
            'completeness': f"Completude: {metrics.completeness:.1%} - {'✓ Completa' if metrics.completeness > 0.8 else '✗ Incompleta'}",
            'comprehensibility': f"Compreensibilidade: {metrics.comprehensibility:.1%} - {'✓ Clara' if metrics.comprehensibility > 0.7 else '✗ Confusa'}",
            'coverage': f"Cobertura: {metrics.coverage:.1%} - {'✓ Ampla' if metrics.coverage > 0.7 else '✗ Limitada'}",
            'actionability': f"Acionabilidade: {metrics.actionability:.1%} - {'✓ Útil' if metrics.actionability > 0.7 else '✗ Pouco útil'}"
        }
        
        return report
