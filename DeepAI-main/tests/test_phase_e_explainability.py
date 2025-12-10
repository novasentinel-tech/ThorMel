"""
Phase E: Explainability Tests
Comprehensive test suite for SHAP, NLG, HTML reports, and quality evaluation
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Add source to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from explainability.shap_explainer import ShapExplainer, ShapExplanation
from explainability.nlg_generator import NLGGenerator, SecurityRisk
from explainability.html_report_generator import HTMLReportGenerator
from explainability.explanation_quality import ExplanationQualityEvaluator, QualityMetrics

import lightgbm as lgb


# Create a real LightGBM model for testing
def create_test_model():
    """Create a real LightGBM model for testing."""
    np.random.seed(42)
    X_train = np.random.randn(100, 10)
    y_train = np.random.randint(0, 4, 100)
    
    train_data = lgb.Dataset(X_train, label=y_train)
    
    params = {
        'objective': 'multiclass',
        'num_class': 4,
        'num_leaves': 31,
        'learning_rate': 0.05,
        'verbose': -1,
        'seed': 42,
    }
    
    model = lgb.train(params, train_data, num_boost_round=10)
    return model


class TestShapExplainer:
    """Test SHAP explainer module."""
    
    def test_shap_explainer_initialization(self):
        """Test explainer initialization."""
        model = create_test_model()
        X_bg = np.random.randn(10, 10)
        feature_names = [f"feat_{i}" for i in range(10)]
        class_names = ["safe", "warning", "vulnerable", "critical"]
        
        explainer = ShapExplainer(
            model, X_bg, feature_names, class_names,
            model_type='lightgbm'
        )
        
        assert explainer.model is model
        assert len(explainer.feature_names) == 10
        assert len(explainer.class_names) == 4
    
    def test_shap_explanation_dataclass(self):
        """Test ShapExplanation dataclass."""
        shap_vals = np.random.randn(10)
        feature_names = [f"feat_{i}" for i in range(10)]
        feature_vals = np.random.randn(10)
        
        explanation = ShapExplanation(
            instance_idx=0,
            prediction="safe",
            prediction_score=0.95,
            base_value=0.5,
            shap_values=shap_vals,
            feature_names=feature_names,
            feature_values=feature_vals,
            top_positive_features=[],
            top_negative_features=[]
        )
        
        assert explanation.instance_idx == 0
        assert explanation.prediction == "safe"
        assert len(explanation.top_positive_features) >= 0
    
    def test_explain_instance(self):
        """Test single instance explanation."""
        model = create_test_model()
        X_bg = np.random.randn(10, 10)
        feature_names = [f"feat_{i}" for i in range(10)]
        class_names = ["safe", "warning", "vulnerable", "critical"]
        
        explainer = ShapExplainer(model, X_bg, feature_names, class_names)
        
        x = np.random.randn(10)
        explanation = explainer.explain_instance(x, instance_idx=0)
        
        assert isinstance(explanation, ShapExplanation)
        assert explanation.prediction in class_names
        assert len(explanation.shap_values) == 10
    
    def test_explain_dataset(self):
        """Test batch explanation."""
        model = create_test_model()
        X_bg = np.random.randn(10, 10)
        X_test = np.random.randn(5, 10)
        feature_names = [f"feat_{i}" for i in range(10)]
        class_names = ["safe", "warning", "vulnerable", "critical"]
        
        explainer = ShapExplainer(model, X_bg, feature_names, class_names)
        
        explanations = explainer.explain_dataset(X_test, max_instances=5)
        
        assert len(explanations) == 5
        assert all(isinstance(e, ShapExplanation) for e in explanations)
    
    def test_global_feature_importance(self):
        """Test global importance computation."""
        model = create_test_model()
        X_bg = np.random.randn(10, 10)
        X_test = np.random.randn(20, 10)
        feature_names = [f"feat_{i}" for i in range(10)]
        class_names = ["safe", "warning", "vulnerable", "critical"]
        
        explainer = ShapExplainer(model, X_bg, feature_names, class_names)
        
        importance = explainer.global_feature_importance(X_test)
        
        assert len(importance) == 10
        assert np.allclose(np.sum(importance), 1.0)  # Normalized
    
    def test_feature_importance_dict(self):
        """Test feature importance as dictionary."""
        model = create_test_model()
        X_bg = np.random.randn(10, 10)
        X_test = np.random.randn(10, 10)
        feature_names = [f"feat_{i}" for i in range(10)]
        class_names = ["safe", "warning", "vulnerable", "critical"]
        
        explainer = ShapExplainer(model, X_bg, feature_names, class_names)
        
        importance_dict = explainer.get_feature_importance_dict(X_test)
        
        assert isinstance(importance_dict, dict)
        assert len(importance_dict) == 10
        assert all(isinstance(v, float) for v in importance_dict.values())
    
    def test_get_top_features(self):
        """Test top features extraction."""
        model = create_test_model()
        X_bg = np.random.randn(10, 10)
        feature_names = [f"feat_{i}" for i in range(10)]
        class_names = ["safe", "warning", "vulnerable", "critical"]
        
        explainer = ShapExplainer(model, X_bg, feature_names, class_names)
        
        x = np.random.randn(10)
        explanation = explainer.explain_instance(x)
        top_features = explainer.get_top_features(explanation, top_k=5)
        
        assert len(top_features) <= 5
        assert all(len(t) == 3 for t in top_features)  # (name, shap_value, feature_value)


class TestNLGGenerator:
    """Test Natural Language Generation module."""
    
    def test_nlg_initialization(self):
        """Test NLG generator initialization."""
        gen = NLGGenerator()
        assert gen is not None
    
    def test_risk_level_mapping(self):
        """Test risk level mapping."""
        gen = NLGGenerator()
        
        assert gen.get_risk_level("seguro") == SecurityRisk.LOW
        assert gen.get_risk_level("aviso") == SecurityRisk.MEDIUM
        assert gen.get_risk_level("vulnerável") == SecurityRisk.HIGH
        assert gen.get_risk_level("crítico") == SecurityRisk.CRITICAL
    
    def test_factor_explanation(self):
        """Test factor explanation generation."""
        gen = NLGGenerator()
        
        factor_names = ["missing_hsts", "insecure_headers"]
        factor_impacts = [0.15, -0.08]
        
        explanation = gen.generate_factor_explanation(
            "HTTP", factor_names, factor_impacts, top_k=2
        )
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    def test_recommendations_generation(self):
        """Test recommendation generation."""
        gen = NLGGenerator()
        
        factor_names = ["missing_hsts", "weak_ciphers"]
        factor_impacts = [0.12, 0.08]
        
        recommendations = gen.generate_recommendations(
            "HTTP", factor_names, factor_impacts, top_k=2
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(r, str) for r in recommendations)
    
    def test_full_explanation_generation(self):
        """Test complete explanation."""
        gen = NLGGenerator()
        
        factor_names = ["missing_hsts", "insecure_headers"]
        factor_impacts = np.array([0.15, -0.08, 0.05, -0.03, 0.02])
        
        explanation = gen.generate_full_explanation(
            domain="example.com",
            prediction="aviso",
            prediction_score=0.75,
            domain_type="HTTP",
            factor_names=["h_0", "h_1", "h_2", "h_3", "h_4"],
            factor_impacts=factor_impacts,
            base_value=0.5
        )
        
        assert isinstance(explanation, dict)
        assert "introduction" in explanation
        assert "summary" in explanation
        assert "explanation" in explanation
        assert "recommendations" in explanation
        assert "confidence" in explanation
        assert "action_required" in explanation
        assert "risk_level" in explanation
    
    def test_summary_sentence(self):
        """Test summary sentence generation."""
        gen = NLGGenerator()
        
        summary = gen.get_summary_sentence("vulnerável", 0.92)
        
        assert isinstance(summary, str)
        assert "alto risco" in summary.lower()
        assert "92%" in summary


class TestHTMLReportGenerator:
    """Test HTML report generation."""
    
    def test_html_generator_initialization(self):
        """Test HTML generator initialization."""
        gen = HTMLReportGenerator()
        assert gen is not None
    
    def test_risk_class_mapping(self):
        """Test risk class CSS mapping."""
        gen = HTMLReportGenerator()
        
        assert gen._get_risk_class("seguro") == "low"
        assert gen._get_risk_class("aviso") == "medium"
        assert gen._get_risk_class("vulnerável") == "high"
        assert gen._get_risk_class("crítico") == "critical"
    
    def test_report_generation(self, tmp_path):
        """Test HTML report generation."""
        gen = HTMLReportGenerator()
        
        explanation_dict = {
            "introduction": "Test introduction",
            "summary": "Test summary",
            "explanation": "Test explanation",
            "recommendations": "1. Test recommendation",
            "confidence": "Test confidence",
            "action_required": "Test action",
            "risk_level": "aviso"
        }
        
        features_importance = {"feat_0": 0.3, "feat_1": 0.2}
        
        output_path = str(tmp_path / "report.html")
        html = gen.generate_report(
            domain="example.com",
            explanation_dict=explanation_dict,
            features_importance=features_importance,
            output_path=output_path
        )
        
        assert isinstance(html, str)
        assert "example.com" in html
        assert "<!DOCTYPE html>" in html
        assert Path(output_path).exists()
    
    def test_report_html_structure(self, tmp_path):
        """Test HTML structure is valid."""
        gen = HTMLReportGenerator()
        
        explanation_dict = {
            "introduction": "Test",
            "summary": "Test",
            "explanation": "Test",
            "recommendations": "Test",
            "confidence": "Test",
            "action_required": "Test",
            "risk_level": "crítico"
        }
        
        html = gen.generate_report(
            domain="test.com",
            explanation_dict=explanation_dict,
            features_importance={}
        )
        
        # Check key HTML elements
        assert "<html" in html
        assert "</html>" in html
        assert "<head>" in html
        assert "</head>" in html
        assert "<body>" in html
        assert "</body>" in html
        assert "risk-critical" in html
    
    def test_batch_report_generation(self, tmp_path):
        """Test batch report generation."""
        gen = HTMLReportGenerator()
        
        domains_data = [
            {
                "domain": "test1.com",
                "explanation": {"risk_level": "aviso"},
                "importance": {"feat_0": 0.5}
            },
            {
                "domain": "test2.com",
                "explanation": {"risk_level": "crítico"},
                "importance": {"feat_1": 0.6}
            }
        ]
        
        report_paths = gen.generate_batch_report(
            domains_data,
            output_dir=str(tmp_path)
        )
        
        assert len(report_paths) == 2
        assert all(Path(p).exists() for p in report_paths.values())


class TestExplanationQuality:
    """Test explanation quality evaluation."""
    
    def test_quality_metrics_creation(self):
        """Test QualityMetrics dataclass."""
        metrics = QualityMetrics(
            fidelity=0.9,
            stability=0.85,
            sparsity=0.8,
            completeness=0.9,
            comprehensibility=0.85,
            coverage=0.8,
            actionability=0.9
        )
        
        assert metrics.fidelity == 0.9
        assert metrics.overall_score is not None
        assert 0 <= metrics.overall_score <= 1
    
    def test_quality_evaluator_initialization(self):
        """Test evaluator initialization."""
        evaluator = ExplanationQualityEvaluator()
        assert evaluator is not None
    
    def test_fidelity_evaluation(self):
        """Test fidelity evaluation."""
        evaluator = ExplanationQualityEvaluator()
        
        shap_values = np.array([0.1, -0.05, 0.15, -0.03, 0.2])
        explanation_factors = ["feat_0", "feat_2", "feat_4"]
        
        fidelity = evaluator.evaluate_fidelity(
            "aviso", explanation_factors, shap_values
        )
        
        assert 0 <= fidelity <= 1
    
    def test_sparsity_evaluation(self):
        """Test sparsity evaluation."""
        evaluator = ExplanationQualityEvaluator()
        
        shap_values = np.array([0.5, 0.01, 0.02, 0.001, 0.1])
        
        sparsity = evaluator.evaluate_sparsity(shap_values, threshold=0.01)
        
        assert 0 <= sparsity <= 1
        # Sparsity should be reasonable for this sparse signal
        assert sparsity >= 0.3
    
    def test_completeness_evaluation(self):
        """Test completeness evaluation."""
        evaluator = ExplanationQualityEvaluator()
        
        explanation_domains = ["HTTP", "TLS", "DNS", "PORTS"]
        required_domains = ["HTTP", "TLS", "DNS"]
        
        completeness = evaluator.evaluate_completeness(
            explanation_domains, required_domains
        )
        
        assert completeness == 1.0  # All required domains covered
    
    def test_comprehensibility_evaluation(self):
        """Test comprehensibility evaluation."""
        evaluator = ExplanationQualityEvaluator()
        
        explanation_text = "This is a sample explanation with reasonable length"
        
        comprehensibility = evaluator.evaluate_comprehensibility(
            explanation_text, factor_count=7, recommendation_count=3
        )
        
        assert 0 <= comprehensibility <= 1
    
    def test_coverage_evaluation(self):
        """Test coverage evaluation."""
        evaluator = ExplanationQualityEvaluator()
        
        shap_values = np.array([0.2, 0.15, 0.1, 0.08, 0.05, 0.01, 0.01, 0.01])
        
        coverage = evaluator.evaluate_coverage(shap_values, top_k=5)
        
        assert 0 <= coverage <= 1
    
    def test_actionability_evaluation(self):
        """Test actionability evaluation."""
        evaluator = ExplanationQualityEvaluator()
        
        recommendations = [
            "Enable HSTS header",
            "Update TLS version",
            "Configure firewall"
        ]
        
        actionability = evaluator.evaluate_actionability(
            recommendations, has_specific_steps=True, has_timeline=True
        )
        
        assert 0 <= actionability <= 1
        assert actionability > 0.5
    
    def test_full_explanation_evaluation(self):
        """Test complete quality evaluation."""
        evaluator = ExplanationQualityEvaluator()
        
        shap_values = np.array([0.2, 0.15, 0.1, 0.08, 0.05, 0.01, 0.01, 0.01])
        explanation_text = "This is a comprehensive explanation"
        recommendations = ["Rec 1", "Rec 2", "Rec 3"]
        explanation_domains = ["HTTP", "TLS", "DNS"]
        
        metrics = evaluator.evaluate_explanation(
            prediction="aviso",
            shap_values=shap_values,
            explanation_text=explanation_text,
            recommendations=recommendations,
            explanation_domains=explanation_domains
        )
        
        assert isinstance(metrics, QualityMetrics)
        assert metrics.overall_score is not None
        assert 0 <= metrics.overall_score <= 1
    
    def test_quality_level_determination(self):
        """Test quality level determination."""
        evaluator = ExplanationQualityEvaluator()
        
        assert evaluator._get_quality_level(0.9) == "EXCELLENT"
        assert evaluator._get_quality_level(0.75) == "GOOD"
        assert evaluator._get_quality_level(0.6) == "ACCEPTABLE"
        assert evaluator._get_quality_level(0.2) == "POOR"
    
    def test_quality_report_generation(self):
        """Test quality report generation."""
        evaluator = ExplanationQualityEvaluator()
        
        metrics = QualityMetrics(
            fidelity=0.85,
            stability=0.8,
            sparsity=0.75,
            completeness=0.9,
            comprehensibility=0.85,
            coverage=0.8,
            actionability=0.9
        )
        
        report = evaluator.get_quality_report(metrics)
        
        assert isinstance(report, dict)
        assert "overall_quality" in report
        assert all(k in report for k in [
            'fidelity', 'stability', 'sparsity', 'completeness',
            'comprehensibility', 'coverage', 'actionability'
        ])


# Integration tests
class TestPhaseE_Integration:
    """Integration tests for Phase E."""
    
    def test_end_to_end_explanation_pipeline(self, tmp_path):
        """Test complete explanation pipeline."""
        # Setup
        model = create_test_model()
        X_bg = np.random.randn(10, 10)
        X_test = np.random.randn(5, 10)
        feature_names = [f"feat_{i}" for i in range(10)]
        class_names = ["safe", "warning", "vulnerable", "critical"]
        
        # SHAP explanation
        shap_explainer = ShapExplainer(model, X_bg, feature_names, class_names)
        explanation = shap_explainer.explain_instance(X_test[0])
        
        # NLG explanation
        nlg_gen = NLGGenerator()
        nlg_explanation = nlg_gen.generate_full_explanation(
            domain="example.com",
            prediction=explanation.prediction,
            prediction_score=explanation.prediction_score,
            domain_type="HTTP",
            factor_names=feature_names,
            factor_impacts=explanation.shap_values,
            base_value=explanation.base_value
        )
        
        # HTML report
        html_gen = HTMLReportGenerator()
        html_output = html_gen.generate_report(
            domain="example.com",
            explanation_dict=nlg_explanation,
            features_importance={fname: 0.1 for fname in feature_names},
            output_path=str(tmp_path / "report.html")
        )
        
        # Quality evaluation
        quality_eval = ExplanationQualityEvaluator()
        metrics = quality_eval.evaluate_explanation(
            prediction=explanation.prediction,
            shap_values=explanation.shap_values,
            explanation_text=nlg_explanation['explanation'],
            recommendations=nlg_explanation['recommendations'].split("\n"),
            explanation_domains=["HTTP"]
        )
        
        # Verify pipeline
        assert explanation is not None
        assert nlg_explanation is not None
        assert html_output is not None
        assert metrics.overall_score > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
