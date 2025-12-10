"""
Model Evaluator for ML Classification
Comprehensive evaluation metrics and reporting
"""

import numpy as np
import logging
from typing import Dict, Tuple, Optional, Any
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    roc_curve, auc, precision_recall_curve
)
from sklearn.preprocessing import label_binarize
import json

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Comprehensive model evaluation with multiple metrics and reporting.
    """
    
    CLASS_NAMES = {
        0: 'secure',
        1: 'warning',
        2: 'vulnerable',
        3: 'critical'
    }
    
    def __init__(self):
        """Initialize evaluator."""
        self.metrics = {}
        self.predictions = None
        self.probabilities = None
        self.true_labels = None
        
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        sample_weight: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive model evaluation.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities (n_samples, n_classes)
            sample_weight: Sample weights for weighted metrics
            
        Returns:
            Dictionary with comprehensive metrics
        """
        self.true_labels = y_true
        self.predictions = y_pred
        self.probabilities = y_proba
        
        metrics = {}
        
        # Basic metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred, sample_weight=sample_weight)
        metrics['weighted_precision'] = precision_score(
            y_true, y_pred, average='weighted', sample_weight=sample_weight, zero_division=0
        )
        metrics['weighted_recall'] = recall_score(
            y_true, y_pred, average='weighted', sample_weight=sample_weight, zero_division=0
        )
        metrics['weighted_f1'] = f1_score(
            y_true, y_pred, average='weighted', sample_weight=sample_weight, zero_division=0
        )
        
        # Per-class metrics
        precision_per_class = precision_score(
            y_true, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0
        )
        recall_per_class = recall_score(
            y_true, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0
        )
        f1_per_class = f1_score(
            y_true, y_pred, average=None, labels=[0, 1, 2, 3], zero_division=0
        )
        
        metrics['per_class'] = {}
        for i in range(4):
            metrics['per_class'][self.CLASS_NAMES[i]] = {
                'precision': float(precision_per_class[i]),
                'recall': float(recall_per_class[i]),
                'f1': float(f1_per_class[i])
            }
        
        # Critical class recall (key metric: 95% target)
        critical_recall = recall_per_class[3]  # Class 3 = critical
        metrics['critical_recall'] = float(critical_recall)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3])
        metrics['confusion_matrix'] = cm.tolist()
        
        # Classification report
        report = classification_report(
            y_true, y_pred, 
            target_names=[self.CLASS_NAMES[i] for i in range(4)],
            digits=4, zero_division=0, output_dict=True
        )
        metrics['classification_report'] = report
        
        # ROC-AUC if probabilities provided
        if y_proba is not None:
            try:
                # One-vs-Rest for multiclass
                y_true_bin = label_binarize(y_true, classes=[0, 1, 2, 3])
                
                # Calculate ROC-AUC per class
                roc_auc_per_Class = {}
                for i in range(4):
                    try:
                        roc_auc = roc_auc_score(y_true_bin[:, i], y_proba[:, i])
                        roc_auc_per_class[self.CLASS_NAMES[i]] = float(roc_auc)
                    except ValueError:
                        roc_auc_per_class[self.CLASS_NAMES[i]] = np.nan
                
                metrics['roc_auc_per_class'] = roc_auc_per_class
                
                # Macro ROC-AUC
                metrics['roc_auc_macro'] = float(np.nanmean(list(roc_auc_per_class.values())))
            except Exception as e:
                logger.warning(f"ROC-AUC calculation failed: {e}")
                metrics['roc_auc_per_class'] = {}
                metrics['roc_auc_macro'] = np.nan
        
        self.metrics = metrics
        
        # Log detailed results
        self._log_metrics(metrics)
        
        return metrics
    
    def _log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log evaluation metrics."""
        logger.info("="*60)
        logger.info("MODEL EVALUATION RESULTS")
        logger.info("="*60)
        logger.info(f"Overall Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Weighted Precision: {metrics['weighted_precision']:.4f}")
        logger.info(f"Weighted Recall: {metrics['weighted_recall']:.4f}")
        logger.info(f"Weighted F1: {metrics['weighted_f1']:.4f}")
        logger.info(f"Critical Class Recall: {metrics['critical_recall']:.4f} (Target: 0.95)")
        logger.info("")
        logger.info("Per-Class Metrics:")
        for class_name, metrics_dict in metrics['per_class'].items():
            logger.info(f"  {class_name}:")
            logger.info(f"    Precision: {metrics_dict['precision']:.4f}")
            logger.info(f"    Recall: {metrics_dict['recall']:.4f}")
            logger.info(f"    F1: {metrics_dict['f1']:.4f}")
        logger.info("="*60)
    
    def get_metrics_summary(self) -> Dict[str, float]:
        """Get summary of key metrics."""
        if not self.metrics:
            logger.warning("No metrics computed yet. Call evaluate() first.")
            return {}
        
        return {
            'accuracy': self.metrics['accuracy'],
            'weighted_f1': self.metrics['weighted_f1'],
            'critical_recall': self.metrics['critical_recall'],
            'roc_auc_macro': self.metrics.get('roc_auc_macro', np.nan)
        }
    
    def get_class_metrics(self, class_name: str) -> Optional[Dict[str, float]]:
        """Get metrics for specific class."""
        if class_name not in self.metrics.get('per_class', {}):
            return None
        return self.metrics['per_class'][class_name]
    
    def check_targets_met(self) -> Dict[str, bool]:
        """
        Check if key performance targets are met.
        
        Targets:
        - Accuracy: 85%+
        - Critical Recall: 95%+
        - F1: 83%+
        
        Returns:
            Dictionary with target status
        """
        if not self.metrics:
            return {}
        
        targets = {
            'accuracy_85_percent': self.metrics['accuracy'] >= 0.85,
            'critical_recall_95_percent': self.metrics['critical_recall'] >= 0.95,
            'weighted_f1_83_percent': self.metrics['weighted_f1'] >= 0.83,
            'roc_auc_good': self.metrics.get('roc_auc_macro', 0) >= 0.80
        }
        
        logger.info("TARGET ACHIEVEMENT:")
        for target_name, is_met in targets.items():
            status = "✓ MET" if is_met else "✗ NOT MET"
            logger.info(f"  {target_name}: {status}")
        
        return targets
    
    def get_feature_importance_comparison(
        self,
        feature_importance_1: np.ndarray,
        feature_importance_2: np.ndarray,
        feature_names: Optional[list] = None,
        top_k: int = 20
    ) -> Dict[str, Any]:
        """
        Compare feature importances from two models.
        
        Args:
            feature_importance_1: Importance scores from model 1
            feature_importance_2: Importance scores from model 2
            feature_names: Feature names
            top_k: Number of top features to compare
            
        Returns:
            Comparison dictionary
        """
        if feature_names is None:
            feature_names = [f"Feature_{i}" for i in range(len(feature_importance_1))]
        
        # Get top k indices for model 1
        top_indices_1 = np.argsort(feature_importance_1)[-top_k:][::-1]
        top_indices_2 = np.argsort(feature_importance_2)[-top_k:][::-1]
        
        comparison = {
            'model_1_top_features': [
                {
                    'name': feature_names[idx],
                    'importance': float(feature_importance_1[idx])
                }
                for idx in top_indices_1
            ],
            'model_2_top_features': [
                {
                    'name': feature_names[idx],
                    'importance': float(feature_importance_2[idx])
                }
                for idx in top_indices_2
            ],
            'overlap': len(set(top_indices_1) & set(top_indices_2))
        }
        
        return comparison
    
    def save_metrics(self, filepath: str) -> None:
        """
        Save metrics to JSON file.
        
        Args:
            filepath: Output file path
        """
        # Convert numpy arrays/values to JSON-serializable format
        metrics_serializable = self._make_serializable(self.metrics)
        
        with open(filepath, 'w') as f:
            json.dump(metrics_serializable, f, indent=2)
        
        logger.info(f"Metrics saved to {filepath}")
    
    @staticmethod
    def _make_serializable(obj):
        """Convert numpy types to Python native types for JSON serialization."""
        if isinstance(obj, dict):
            return {k: ModelEvaluator._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [ModelEvaluator._make_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        else:
            return obj
