"""
Phase F: Integration & Testing
Comprehensive test suite for end-to-end pipeline, performance, load, and security
"""

import pytest
import numpy as np
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Add source to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from pipeline.integrated_pipeline import IntegratedPipeline, AnalysisResult, SecurityLevel
from models.supervised.lgbm_classifier import LightGBMClassifier
from models.reinforcement.ppo_agent import PPOAgent
from explainability.shap_explainer import ShapExplainer


class TestPipelineIntegration:
    """Test complete pipeline integration."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = IntegratedPipeline()
        
        assert pipeline.http_collector is not None
        assert pipeline.tls_collector is not None
        assert pipeline.dns_collector is not None
        assert pipeline.feature_extractor is not None
        assert pipeline.nlg_generator is not None
        assert pipeline.html_generator is not None
    
    def test_single_domain_analysis(self):
        """Test analysis of single domain."""
        pipeline = IntegratedPipeline()
        
        result = pipeline.analyze_domain("example.com", generate_report=False)
        
        assert result.domain == "example.com"
        assert result.status in ["success", "error"]
        assert result.total_time > 0
        assert result.collection_time >= 0
        assert result.feature_time >= 0
    
    def test_result_to_dict(self):
        """Test result serialization."""
        result = AnalysisResult(
            domain="test.com",
            collection_time=0.1,
            feature_time=0.2,
            prediction_time=0.1,
            explanation_time=0.15,
            total_time=0.55,
            ml_prediction="aviso",
            ml_score=0.75,
            ml_features={"f0": 0.5, "f1": 0.3},
            status="success"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['domain'] == "test.com"
        assert result_dict['ml_results']['prediction'] == "aviso"
        assert 'timestamp' in result_dict
    
    def test_batch_analysis(self):
        """Test batch domain analysis."""
        pipeline = IntegratedPipeline()
        
        domains = ["example.com", "test.com", "sample.com"]
        results = pipeline.analyze_batch(domains, generate_reports=False)
        
        assert len(results) == 3
        assert all(isinstance(r, AnalysisResult) for r in results)
    
    def test_feature_vector_shape(self):
        """Test feature vector dimensions."""
        pipeline = IntegratedPipeline()
        
        result = pipeline.analyze_domain("example.com", generate_report=False)
        
        if result.status == "success":
            assert result.collected_features >= 0


class TestEndToEndPipeline:
    """Test complete end-to-end workflows."""
    
    def test_data_collection_to_features(self):
        """Test collection through feature extraction."""
        pipeline = IntegratedPipeline()
        
        # Collect
        collected = pipeline.collect_data("example.com")
        assert isinstance(collected, dict)
        
        # Extract features
        features, feature_dict = pipeline.extract_features(collected)
        assert features is not None
        assert isinstance(feature_dict, dict)
    
    def test_ml_prediction_workflow(self):
        """Test ML prediction workflow."""
        pipeline = IntegratedPipeline()
        
        # Create sample feature vector
        feature_vector = np.random.randn(87)
        
        # Predict
        prediction, score, importance = pipeline.predict_ml(feature_vector)
        
        assert isinstance(prediction, str)
        assert 0 <= score <= 1
        assert isinstance(importance, dict)
    
    def test_rl_action_workflow(self):
        """Test RL action selection workflow."""
        pipeline = IntegratedPipeline()
        
        feature_vector = np.random.randn(87)
        action, confidence = pipeline.select_rl_action(feature_vector)
        
        # RL might not be available
        if action is not None:
            assert isinstance(action, str)
            assert 0 <= confidence <= 1
    
    def test_explanation_workflow(self):
        """Test explanation generation workflow."""
        pipeline = IntegratedPipeline()
        
        feature_vector = np.random.randn(87)
        
        shap_exp, nlg_exp, quality = pipeline.generate_explanations(
            "example.com",
            "aviso",
            0.75,
            feature_vector
        )
        
        # NLG should always work
        assert nlg_exp is not None
        assert 'introduction' in nlg_exp
        assert 'recommendations' in nlg_exp
    
    def test_html_report_generation(self):
        """Test HTML report generation."""
        pipeline = IntegratedPipeline()
        
        nlg_exp = {
            'introduction': 'Test',
            'summary': 'Test',
            'explanation': 'Test',
            'recommendations': 'Test',
            'confidence': 'Test',
            'action_required': 'Test',
            'risk_level': 'aviso'
        }
        
        feature_dict = {f"f{i}": 0.1 for i in range(10)}
        
        report_path = pipeline.generate_html_report(
            "test.com",
            nlg_exp,
            feature_dict,
            Path("/tmp")
        )
        
        if report_path:
            assert Path(report_path).exists()


class TestPerformanceBenchmarking:
    """Test performance characteristics."""
    
    def test_single_analysis_performance(self):
        """Test performance of single domain analysis."""
        pipeline = IntegratedPipeline()
        
        t0 = time.time()
        result = pipeline.analyze_domain("example.com", generate_report=False)
        elapsed = time.time() - t0
        
        # Should complete in reasonable time
        assert elapsed < 60  # Under 60 seconds
        assert result.total_time > 0
    
    def test_batch_performance(self):
        """Test batch analysis performance."""
        pipeline = IntegratedPipeline()
        
        domains = [f"test{i}.com" for i in range(5)]
        
        t0 = time.time()
        results = pipeline.analyze_batch(domains, generate_reports=False)
        elapsed = time.time() - t0
        
        assert len(results) == 5
        assert elapsed > 0
        
        # Calculate average time per domain
        avg_time = elapsed / len(domains)
        assert avg_time < 60  # Should average under 60s per domain
    
    def test_feature_extraction_performance(self):
        """Test feature extraction performance."""
        pipeline = IntegratedPipeline()
        
        collected = pipeline.collect_data("example.com")
        
        t0 = time.time()
        features, feature_dict = pipeline.extract_features(collected)
        elapsed = time.time() - t0
        
        # Feature extraction should be fast
        assert elapsed < 5  # Under 5 seconds
    
    def test_ml_prediction_performance(self):
        """Test ML prediction latency."""
        pipeline = IntegratedPipeline()
        
        feature_vector = np.random.randn(87)
        
        t0 = time.time()
        prediction, score, _ = pipeline.predict_ml(feature_vector)
        elapsed = time.time() - t0
        
        # ML prediction should be very fast
        assert elapsed < 1  # Under 1 second (typically < 100ms)


class TestLoadAndStress:
    """Test system under load."""
    
    def test_concurrent_domain_analysis(self):
        """Test concurrent analysis of multiple domains."""
        pipeline = IntegratedPipeline()
        
        domains = [f"test{i}.com" for i in range(3)]
        
        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(pipeline.analyze_domain, domain, False)
                for domain in domains
            ]
            results = [f.result() for f in as_completed(futures)]
        
        assert len(results) == 3
        assert all(isinstance(r, AnalysisResult) for r in results)
    
    def test_memory_efficiency(self):
        """Test memory usage during batch operations."""
        pipeline = IntegratedPipeline()
        
        # Process multiple domains
        domains = [f"test{i}.com" for i in range(5)]
        results = pipeline.analyze_batch(domains, generate_reports=False)
        
        assert len(results) == 5
        # Should not raise memory errors
    
    def test_rapid_sequential_analysis(self):
        """Test rapid sequential domain analysis."""
        pipeline = IntegratedPipeline()
        
        t0 = time.time()
        for i in range(5):
            result = pipeline.analyze_domain(f"test{i}.com", generate_report=False)
            assert result is not None
        elapsed = time.time() - t0
        
        assert elapsed > 0


class TestSecurityAndSafety:
    """Test security aspects of pipeline."""
    
    def test_invalid_domain_handling(self):
        """Test handling of invalid domains."""
        pipeline = IntegratedPipeline()
        
        result = pipeline.analyze_domain("invalid..domain!!!.com", generate_report=False)
        
        # Should handle gracefully
        assert result is not None
        assert result.domain == "invalid..domain!!!.com"
    
    def test_timeout_handling(self):
        """Test handling of collection timeouts."""
        pipeline = IntegratedPipeline()
        
        # Test with domain that might timeout
        result = pipeline.analyze_domain(
            "nonexistent-domain-12345.com",
            generate_report=False
        )
        
        # Should complete (either success or error)
        assert result is not None
        assert result.total_time > 0
    
    def test_error_recovery(self):
        """Test pipeline error recovery."""
        pipeline = IntegratedPipeline()
        
        # Analyze multiple domains, some might fail
        domains = ["example.com", "invalid..", "test.com"]
        results = pipeline.analyze_batch(domains, generate_reports=False)
        
        assert len(results) == len(domains)
        # Should handle mixed success/failure
    
    def test_result_data_validation(self):
        """Test result data is valid."""
        pipeline = IntegratedPipeline()
        
        result = pipeline.analyze_domain("example.com", generate_report=False)
        result_dict = result.to_dict()
        
        # Validate structure
        assert 'times' in result_dict
        assert 'ml_results' in result_dict
        assert 'status' in result_dict
        
        # Timestamps should be valid
        assert 'timestamp' in result_dict


class TestPipelineIntegration_ComponentsBehavior:
    """Test behavior of integrated components."""
    
    def test_feature_consistency(self):
        """Test feature extraction consistency."""
        pipeline = IntegratedPipeline()
        
        collected = pipeline.collect_data("example.com")
        features1, dict1 = pipeline.extract_features(collected)
        
        # Same data should produce same features
        features2, dict2 = pipeline.extract_features(collected)
        
        assert len(dict1) == len(dict2)
    
    def test_prediction_stability(self):
        """Test ML prediction stability."""
        pipeline = IntegratedPipeline()
        
        feature_vector = np.random.RandomState(42).randn(87)
        
        pred1, score1, _ = pipeline.predict_ml(feature_vector)
        pred2, score2, _ = pipeline.predict_ml(feature_vector)
        
        # Same input should give same output
        assert pred1 == pred2
        assert abs(score1 - score2) < 1e-6
    
    def test_explanation_completeness(self):
        """Test all explanation components are included."""
        pipeline = IntegratedPipeline()
        
        result = pipeline.analyze_domain("example.com", generate_report=False)
        
        if result.status == "success":
            assert result.ml_prediction is not None
            assert result.ml_score is not None
            if result.nlg_explanation:
                assert 'introduction' in result.nlg_explanation
                assert 'recommendations' in result.nlg_explanation


class TestPipelineOutputFormats:
    """Test output format correctness."""
    
    def test_result_dict_json_serializable(self):
        """Test that result can be serialized to JSON."""
        result = AnalysisResult(
            domain="test.com",
            collection_time=0.1,
            feature_time=0.2,
            prediction_time=0.1,
            explanation_time=0.15,
            total_time=0.55,
            ml_prediction="aviso",
            ml_score=0.75,
            ml_features={"f0": 0.5},
        )
        
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)
        
        assert isinstance(json_str, str)
        loaded = json.loads(json_str)
        assert loaded['domain'] == "test.com"
    
    def test_batch_results_export(self):
        """Test batch results can be exported."""
        results = [
            AnalysisResult(
                domain=f"test{i}.com",
                collection_time=0.1,
                feature_time=0.1,
                prediction_time=0.1,
                explanation_time=0.1,
                total_time=0.4,
                ml_prediction="aviso",
                ml_score=0.7,
                ml_features={},
            )
            for i in range(3)
        ]
        
        # Export all results
        export = [r.to_dict() for r in results]
        
        assert len(export) == 3
        json_str = json.dumps(export)
        assert isinstance(json_str, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
