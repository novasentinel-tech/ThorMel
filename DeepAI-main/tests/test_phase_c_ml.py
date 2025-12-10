"""
Test Suite for Phase C: ML Training
Comprehensive tests for dataset generation, training, and evaluation
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path

from src.data.dataset_generator import DatasetGenerator
from src.models.supervised.lgbm_trainer import LightGBMTrainer
from src.models.supervised.model_evaluator import ModelEvaluator


class TestDatasetGenerator:
    """Test dataset generation."""
    
    def test_dataset_generation_shape(self):
        """Test generated dataset has correct shape."""
        gen = DatasetGenerator(n_features=87)
        X, y = gen.generate_dataset(n_samples=1000)
        
        assert X.shape == (1000, 87), f"Expected shape (1000, 87), got {X.shape}"
        assert y.shape == (1000,), f"Expected shape (1000,), got {y.shape}"
    
    def test_dataset_generation_classes(self):
        """Test dataset has expected class distribution."""
        gen = DatasetGenerator(n_features=87)
        X, y = gen.generate_dataset(n_samples=1000)
        
        unique_classes = np.unique(y)
        assert set(unique_classes) == {0, 1, 2, 3}, f"Expected classes 0-3, got {unique_classes}"
    
    def test_dataset_feature_bounds(self):
        """Test features are in valid range."""
        gen = DatasetGenerator(n_features=87)
        X, y = gen.generate_dataset(n_samples=1000)
        
        assert np.all(X >= 0), "Features should be >= 0"
        assert np.all(X <= 1), "Features should be <= 1"
    
    def test_train_test_split(self):
        """Test train/test split."""
        gen = DatasetGenerator(n_features=87)
        X_train, X_test, y_train, y_test = gen.generate_train_test_split(
            n_samples=1000, test_size=0.2
        )
        
        assert X_train.shape[0] == 800
        assert X_test.shape[0] == 200
        assert len(y_train) == 800
        assert len(y_test) == 200
    
    def test_custom_class_distribution(self):
        """Test custom class distribution."""
        gen = DatasetGenerator(n_features=87)
        custom_dist = {0: 0.5, 1: 0.3, 2: 0.15, 3: 0.05}
        X, y = gen.generate_dataset(n_samples=1000, class_distribution=custom_dist)
        
        counts = np.bincount(y)
        # Allow 5% tolerance
        for cls, expected_prop in custom_dist.items():
            actual_prop = counts[cls] / len(y)
            assert abs(actual_prop - expected_prop) < 0.05, \
                f"Class {cls}: expected {expected_prop}, got {actual_prop}"
    
    def test_class_weights(self):
        """Test class weight calculation."""
        gen = DatasetGenerator(n_features=87)
        X, y = gen.generate_dataset(n_samples=1000)
        
        weights = gen.get_class_weights(y)
        assert len(weights) == 4, "Should have weights for 4 classes"
        assert all(w > 0 for w in weights.values()), "All weights should be positive"
    
    def test_dataset_statistics(self):
        """Test dataset statistics computation."""
        gen = DatasetGenerator(n_features=87)
        X, y = gen.generate_dataset(n_samples=1000)
        
        stats = gen.get_dataset_statistics(X, y)
        assert stats['n_samples'] == 1000
        assert stats['n_features'] == 87
        assert stats['n_classes'] == 4
        assert len(stats['feature_mean']) == 87
        assert len(stats['feature_std']) == 87
    
    def test_dataset_save_load(self):
        """Test dataset save/load."""
        gen = DatasetGenerator(n_features=87)
        X, y = gen.generate_dataset(n_samples=100)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_dataset.npz"
            gen.save_dataset(X, y, str(filepath))
            
            X_loaded, y_loaded = gen.load_dataset(str(filepath))
            
            np.testing.assert_array_equal(X, X_loaded)
            np.testing.assert_array_equal(y, y_loaded)


class TestLightGBMTrainer:
    """Test LightGBM training."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample training data."""
        gen = DatasetGenerator(n_features=87)
        X_train, X_test, y_train, y_test = gen.generate_train_test_split(
            n_samples=2000, test_size=0.2
        )
        return X_train, X_test, y_train, y_test
    
    def test_model_training(self, sample_data):
        """Test basic model training."""
        X_train, X_test, y_train, y_test = sample_data
        
        trainer = LightGBMTrainer()
        model, history = trainer.train(X_train, y_train, n_estimators=50)
        
        assert model is not None, "Model should be trained"
        assert 'n_samples_original' in history, "History should track training"
    
    def test_model_prediction(self, sample_data):
        """Test model predictions."""
        X_train, X_test, y_train, y_test = sample_data
        
        trainer = LightGBMTrainer()
        trainer.train(X_train, y_train, n_estimators=50)
        
        y_pred = trainer.predict(X_test)
        assert y_pred.shape == (X_test.shape[0],), "Predictions shape mismatch"
        assert set(np.unique(y_pred)) <= {0, 1, 2, 3}, "Predictions should be valid classes"
    
    def test_model_probability_predictions(self, sample_data):
        """Test probability predictions."""
        X_train, X_test, y_train, y_test = sample_data
        
        trainer = LightGBMTrainer()
        trainer.train(X_train, y_train, n_estimators=50)
        
        y_proba = trainer.predict(X_test, return_proba=True)
        assert y_proba.shape == (X_test.shape[0], 4), "Proba shape should be (n_samples, 4)"
        np.testing.assert_array_almost_equal(y_proba.sum(axis=1), np.ones(len(y_proba)))
    
    def test_feature_importance(self, sample_data):
        """Test feature importance extraction."""
        X_train, X_test, y_train, y_test = sample_data
        
        trainer = LightGBMTrainer()
        trainer.train(X_train, y_train, n_estimators=50)
        
        importance = trainer.get_feature_importance(top_k=20)
        
        assert 'top_k_features' in importance, "Should have top-k features"
        assert len(importance['top_k_features']) == 20, "Should return top-20"
        assert 'all_features_importance' in importance, "Should have all features"
    
    def test_model_save_load(self, sample_data):
        """Test model save/load."""
        X_train, X_test, y_train, y_test = sample_data
        
        trainer1 = LightGBMTrainer()
        trainer1.train(X_train, y_train, n_estimators=50)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_model.pkl"
            trainer1.save_model(str(filepath))
            
            trainer2 = LightGBMTrainer()
            trainer2.load_model(str(filepath))
            
            y_pred1 = trainer1.predict(X_test)
            y_pred2 = trainer2.predict(X_test)
            
            np.testing.assert_array_equal(y_pred1, y_pred2)


class TestModelEvaluator:
    """Test model evaluation."""
    
    @pytest.fixture
    def eval_data(self):
        """Generate evaluation data."""
        gen = DatasetGenerator(n_features=87)
        X_train, X_test, y_train, y_test = gen.generate_train_test_split(n_samples=1000)
        
        trainer = LightGBMTrainer()
        trainer.train(X_train, y_train, n_estimators=30)
        
        y_pred = trainer.predict(X_test)
        y_proba = trainer.predict(X_test, return_proba=True)
        
        return y_test, y_pred, y_proba
    
    def test_evaluation_metrics(self, eval_data):
        """Test comprehensive evaluation metrics."""
        y_test, y_pred, y_proba = eval_data
        
        evaluator = ModelEvaluator()
        metrics = evaluator.evaluate(y_test, y_pred, y_proba)
        
        assert 'accuracy' in metrics, "Should compute accuracy"
        assert 'weighted_f1' in metrics, "Should compute F1"
        assert 'critical_recall' in metrics, "Should compute critical recall"
        assert metrics['accuracy'] >= 0.0 and metrics['accuracy'] <= 1.0
        assert metrics['weighted_f1'] >= 0.0 and metrics['weighted_f1'] <= 1.0
    
    def test_per_class_metrics(self, eval_data):
        """Test per-class metrics."""
        y_test, y_pred, y_proba = eval_data
        
        evaluator = ModelEvaluator()
        metrics = evaluator.evaluate(y_test, y_pred, y_proba)
        
        assert 'per_class' in metrics, "Should have per-class metrics"
        assert len(metrics['per_class']) == 4, "Should have 4 classes"
        
        for class_name in ['secure', 'warning', 'vulnerable', 'critical']:
            assert class_name in metrics['per_class']
            class_metrics = metrics['per_class'][class_name]
            assert 'precision' in class_metrics
            assert 'recall' in class_metrics
            assert 'f1' in class_metrics
    
    def test_confusion_matrix(self, eval_data):
        """Test confusion matrix."""
        y_test, y_pred, y_proba = eval_data
        
        evaluator = ModelEvaluator()
        metrics = evaluator.evaluate(y_test, y_pred, y_proba)
        
        cm = np.array(metrics['confusion_matrix'])
        assert cm.shape == (4, 4), "Confusion matrix should be 4x4"
        assert cm.sum() == len(y_test), "Sum should equal number of samples"
    
    def test_target_achievement(self, eval_data):
        """Test target achievement check."""
        y_test, y_pred, y_proba = eval_data
        
        evaluator = ModelEvaluator()
        evaluator.evaluate(y_test, y_pred, y_proba)
        
        targets = evaluator.check_targets_met()
        
        assert isinstance(targets, dict)
        assert 'accuracy_85_percent' in targets
        assert 'critical_recall_95_percent' in targets
        assert 'weighted_f1_83_percent' in targets


class TestIntegrationPhaseC:
    """Integration tests for complete Phase C pipeline."""
    
    def test_complete_training_pipeline(self):
        """Test complete training pipeline."""
        # Generate dataset
        gen = DatasetGenerator(n_features=87)
        X_train, X_test, y_train, y_test = gen.generate_train_test_split(
            n_samples=2000, test_size=0.2
        )
        
        # Train model
        trainer = LightGBMTrainer()
        trainer.train(X_train, y_train, n_estimators=50)
        
        # Evaluate
        results = trainer.evaluate(X_test, y_test)
        metrics = results['metrics']
        
        assert metrics['accuracy'] > 0, "Should have positive accuracy"
        assert metrics['weighted_f1'] > 0, "Should have positive F1"
        
        logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Weighted F1: {metrics['weighted_f1']:.4f}")
        logger.info(f"Critical Recall: {metrics['critical_recall']:.4f}")
    
    def test_training_with_feature_names(self):
        """Test training with feature names."""
        gen = DatasetGenerator(n_features=87)
        X_train, X_test, y_train, y_test = gen.generate_train_test_split(
            n_samples=1000, test_size=0.2
        )
        
        trainer = LightGBMTrainer()
        trainer.train(X_train, y_train, n_estimators=30)
        
        # Get feature importance with names
        feature_names = [f"Feature_{i}" for i in range(87)]
        importance = trainer.get_feature_importance(top_k=10, feature_names=feature_names)
        
        assert len(importance['top_k_features']) == 10
        for item in importance['top_k_features']:
            assert 'name' in item
            assert 'importance' in item


# Logging helper
import logging
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
