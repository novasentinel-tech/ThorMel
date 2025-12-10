"""
SHAP Explainer Module
Generate instance-level explanations using SHAP TreeExplainer
"""

import numpy as np
import logging
from typing import Dict, Tuple, List, Optional, Any
from dataclasses import dataclass
import shap
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ShapExplanation:
    """SHAP explanation for a single instance."""
    
    instance_idx: int
    prediction: str
    prediction_score: float
    base_value: float
    shap_values: np.ndarray
    feature_names: List[str]
    feature_values: np.ndarray
    
    # Derived properties
    top_positive_features: List[Tuple[str, float]]
    top_negative_features: List[Tuple[str, float]]
    
    def __post_init__(self):
        """Compute derived properties."""
        # Handle multi-dimensional SHAP values
        shap_vals = self.shap_values
        if isinstance(shap_vals, (list, np.ndarray)):
            if len(np.array(shap_vals).shape) > 1:
                # Multi-dimensional - use first dimension
                shap_vals = np.array(shap_vals).flatten()
            else:
                shap_vals = np.asarray(shap_vals)
        else:
            shap_vals = np.asarray(shap_vals)
        
        # Ensure shap_vals and feature_names have compatible sizes
        if len(shap_vals) > len(self.feature_names):
            shap_vals = shap_vals[:len(self.feature_names)]
        
        # Get top contributing features
        sorted_indices = np.argsort(np.abs(shap_vals))[::-1]
        
        self.top_positive_features = [
            (self.feature_names[i], float(shap_vals[i]))
            for i in sorted_indices[:5]
            if i < len(self.feature_names) and float(shap_vals[i]) > 0
        ]
        
        self.top_negative_features = [
            (self.feature_names[i], float(shap_vals[i]))
            for i in sorted_indices[:5]
            if i < len(self.feature_names) and float(shap_vals[i]) < 0
        ]


class ShapExplainer:
    """
    SHAP TreeExplainer for model-agnostic explanations.
    
    Features:
    - TreeExplainer for fast SHAP computation
    - Instance-level feature importance
    - Global feature importance aggregation
    - Explanation persistence
    """
    
    def __init__(
        self,
        model: Any,
        X_background: np.ndarray,
        feature_names: List[str],
        class_names: List[str],
        model_type: str = 'lightgbm'
    ):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model (LightGBM, XGBoost, etc.)
            X_background: Background dataset for SHAP computation
            feature_names: List of feature names
            class_names: List of class names (prediction labels)
            model_type: Type of model ('lightgbm', 'xgboost', 'sklearn')
        """
        self.model = model
        self.X_background = X_background
        self.feature_names = feature_names
        self.class_names = class_names
        self.model_type = model_type
        
        logger.info(f"Initializing SHAP {model_type} explainer...")
        logger.info(f"Background dataset shape: {X_background.shape}")
        logger.info(f"Features: {len(feature_names)}")
        logger.info(f"Classes: {len(class_names)}")
        
        # Initialize explainer based on model type
        if model_type.lower() == 'lightgbm':
            self.explainer = shap.TreeExplainer(model)
        elif model_type.lower() == 'xgboost':
            self.explainer = shap.TreeExplainer(model)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        logger.info("SHAP explainer initialized successfully")
        
        # Caching
        self._shap_values_cache = {}
        self._global_importance_cache = None
    
    def explain_instance(self, x: np.ndarray, instance_idx: int = 0) -> ShapExplanation:
        """
        Generate SHAP explanation for single instance.
        
        Args:
            x: Feature vector (1D array)
            instance_idx: Index of this instance (for tracking)
            
        Returns:
            ShapExplanation object
        """
        # Ensure 2D shape for model
        if x.ndim == 1:
            x = x.reshape(1, -1)
        
        # Get prediction
        logits = self.model.predict(x)[0]
        prediction_idx = np.argmax(logits)
        prediction = self.class_names[prediction_idx]
        prediction_score = float(logits[prediction_idx])
        
        # Compute SHAP values (returns per-class values)
        shap_values = self.explainer.shap_values(x)
        
        # For multi-class: get SHAP values for predicted class
        if isinstance(shap_values, list):
            # Multi-output: list of arrays per class
            shap_values_pred = shap_values[prediction_idx][0]
        else:
            # Binary: single array
            shap_values_pred = shap_values[0]
        
        # Base value
        base_value = self.explainer.expected_value
        if isinstance(base_value, (list, np.ndarray)):
            base_value = base_value[prediction_idx]
        
        # Create explanation
        explanation = ShapExplanation(
            instance_idx=instance_idx,
            prediction=prediction,
            prediction_score=prediction_score,
            base_value=float(base_value),
            shap_values=shap_values_pred,
            feature_names=self.feature_names,
            feature_values=x[0],
            top_positive_features=[],
            top_negative_features=[]
        )
        
        logger.debug(
            f"Generated explanation for instance {instance_idx}: "
            f"prediction={prediction}, score={prediction_score:.4f}"
        )
        
        return explanation
    
    def explain_dataset(
        self,
        X: np.ndarray,
        batch_size: int = 100,
        max_instances: Optional[int] = None
    ) -> List[ShapExplanation]:
        """
        Generate SHAP explanations for dataset.
        
        Args:
            X: Feature matrix
            batch_size: Batch size for SHAP computation
            max_instances: Maximum instances to explain (for memory)
            
        Returns:
            List of ShapExplanation objects
        """
        n_instances = min(len(X), max_instances) if max_instances else len(X)
        logger.info(f"Explaining {n_instances} instances...")
        
        explanations = []
        
        for i in range(n_instances):
            explanation = self.explain_instance(X[i], instance_idx=i)
            explanations.append(explanation)
            
            if (i + 1) % 100 == 0:
                logger.info(f"Explained {i + 1}/{n_instances} instances")
        
        logger.info(f"Generated {len(explanations)} explanations")
        return explanations
    
    def global_feature_importance(
        self,
        X: np.ndarray,
        method: str = 'mean_abs'
    ) -> np.ndarray:
        """
        Compute global feature importance from SHAP values.
        
        Args:
            X: Feature matrix
            method: 'mean_abs' (default), 'variance', 'mean'
            
        Returns:
            Feature importance array
        """
        logger.info(f"Computing global feature importance using {method}...")
        
        # Compute SHAP values for dataset
        shap_values = self.explainer.shap_values(X)
        
        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            # List of arrays for each class: [array(n_samples, n_features), ...]
            stacked_values = np.abs(np.array(shap_values))  # (n_classes, n_samples, n_features)
            shap_values = np.mean(stacked_values, axis=0)  # (n_samples, n_features)
        elif isinstance(shap_values, np.ndarray):
            shap_values = np.abs(shap_values)
            
            # Handle multi-class format: (n_samples, n_features, n_classes)
            if shap_values.ndim == 3:
                # Average across classes
                shap_values = np.mean(shap_values, axis=2)  # (n_samples, n_features)
            elif shap_values.ndim == 1:
                shap_values = shap_values.reshape(1, -1)  # (1, n_features)
        
        # Ensure we have (n_samples, n_features) shape
        if shap_values.ndim != 2:
            shap_values = np.atleast_2d(shap_values)
        
        # Compute importance per feature
        if method == 'mean_abs':
            importance = np.mean(np.abs(shap_values), axis=0)
        elif method == 'variance':
            importance = np.var(np.abs(shap_values), axis=0)
        elif method == 'mean':
            importance = np.mean(shap_values, axis=0)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Ensure 1D
        importance = np.asarray(importance).flatten()
        
        # Normalize to [0, 1]
        importance = importance / (np.sum(importance) + 1e-10)
        
        # Log top features
        try:
            importance_list = list(zip(self.feature_names, importance.tolist() if hasattr(importance, 'tolist') else importance))
            top_features = sorted(importance_list, key=lambda x: float(x[1]), reverse=True)[:5]
            logger.info(f"Top 5 important features: {top_features}")
        except Exception as e:
            logger.warning(f"Could not log top features: {e}")
        
        self._global_importance_cache = importance
        return importance
    
    def get_feature_importance_dict(self, X: np.ndarray) -> Dict[str, float]:
        """
        Get feature importance as dictionary.
        
        Args:
            X: Feature matrix for importance computation
            
        Returns:
            Dictionary of feature_name -> importance
        """
        importance = self.global_feature_importance(X)
        return {
            name: float(imp)
            for name, imp in zip(self.feature_names, importance)
        }
    
    def explain_class_difference(
        self,
        x: np.ndarray,
        class1_idx: int,
        class2_idx: int
    ) -> Dict[str, float]:
        """
        Explain difference in predictions between two classes.
        
        Args:
            x: Feature vector
            class1_idx: Index of first class
            class2_idx: Index of second class
            
        Returns:
            Dictionary of feature -> SHAP value difference
        """
        if x.ndim == 1:
            x = x.reshape(1, -1)
        
        shap_values = self.explainer.shap_values(x)
        
        if isinstance(shap_values, list):
            diff = shap_values[class1_idx][0] - shap_values[class2_idx][0]
        else:
            diff = shap_values[0]
        
        return {
            name: float(val)
            for name, val in zip(self.feature_names, diff)
        }
    
    def save(self, filepath: str) -> None:
        """Save explainer to disk."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'explainer': self.explainer,
            'X_background': self.X_background,
            'feature_names': self.feature_names,
            'class_names': self.class_names,
            'model_type': self.model_type,
            'model': self.model
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Explainer saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'ShapExplainer':
        """Load explainer from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        explainer_obj = cls.__new__(cls)
        explainer_obj.explainer = data['explainer']
        explainer_obj.X_background = data['X_background']
        explainer_obj.feature_names = data['feature_names']
        explainer_obj.class_names = data['class_names']
        explainer_obj.model_type = data['model_type']
        explainer_obj.model = data['model']
        explainer_obj._shap_values_cache = {}
        explainer_obj._global_importance_cache = None
        
        logger.info(f"Explainer loaded from {filepath}")
        return explainer_obj
    
    def get_top_features(
        self,
        explanation: ShapExplanation,
        top_k: int = 10
    ) -> List[Tuple[str, float, float]]:
        """
        Get top contributing features for explanation.
        
        Args:
            explanation: ShapExplanation object
            top_k: Number of top features
            
        Returns:
            List of (feature_name, shap_value, feature_value) tuples
        """
        shap_vals = np.asarray(explanation.shap_values).flatten()
        feature_importance = np.abs(shap_vals)
        
        # Ensure we don't request more features than available
        k = min(top_k, len(shap_vals))
        top_indices = np.argsort(feature_importance)[-k:][::-1]
        
        result = []
        for idx in top_indices:
            idx_int = int(idx)
            if idx_int < len(explanation.feature_names):
                result.append((
                    explanation.feature_names[idx_int],
                    float(shap_vals[idx_int]),
                    float(explanation.feature_values[idx_int])
                ))
        
        return result
