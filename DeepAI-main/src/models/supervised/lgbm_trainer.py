"""
LightGBM Training Pipeline
Comprehensive ML training with hyperparameter tuning and SMOTE balancing
"""

import numpy as np
import logging
from typing import Dict, Tuple, Optional, Any, List
import pickle
from pathlib import Path

import lightgbm as lgb
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

from src.models.supervised.model_evaluator import ModelEvaluator

logger = logging.getLogger(__name__)


class LightGBMTrainer:
    """
    Complete LightGBM training pipeline with SMOTE balancing and hyperparameter tuning.
    
    Targets:
    - Accuracy: 85%+
    - Critical Recall: 95%+
    - F1 Score: 83%+
    """
    
    def __init__(self, random_state: int = 42, n_jobs: int = -1):
        """
        Initialize trainer.
        
        Args:
            random_state: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 = use all cores)
        """
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.model = None
        self.best_params = None
        self.scaler = StandardScaler()
        self.smote = SMOTE(random_state=random_state, k_neighbors=5)
        self.evaluator = ModelEvaluator()
        self.training_history = {}
        
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        **kwargs
    ) -> Tuple[lgb.LGBMClassifier, Dict[str, Any]]:
        """
        Train LightGBM model with SMOTE balancing.
        
        Args:
            X_train: Training features (n_samples, 87)
            y_train: Training labels
            **kwargs: Additional arguments for LGBMClassifier
            
        Returns:
            Trained model and training history
        """
        logger.info(f"Training LightGBM on {X_train.shape[0]} samples, {X_train.shape[1]} features")
        logger.info(f"Class distribution: {np.bincount(y_train)}")
        
        # Apply SMOTE for class balancing
        logger.info("Applying SMOTE for class balancing...")
        X_train_balanced, y_train_balanced = self.smote.fit_resample(X_train, y_train)
        logger.info(f"After SMOTE: {X_train_balanced.shape[0]} samples")
        logger.info(f"New class distribution: {np.bincount(y_train_balanced)}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train_balanced)
        
        # Create base model
        default_params = {
            'objective': 'multiclass',
            'num_class': 4,
            'num_leaves': 31,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'random_state': self.random_state,
            'verbose': -1,
            'n_jobs': self.n_jobs,
            'metric': 'multi_logloss'
        }
        
        # Update with user kwargs
        default_params.update(kwargs)
        
        # Initialize and train model
        self.model = lgb.LGBMClassifier(**default_params)
        
        logger.info("Training LightGBM model...")
        self.model.fit(X_train_scaled, y_train_balanced)
        
        logger.info("Model training completed")
        
        self.training_history['n_samples_original'] = X_train.shape[0]
        self.training_history['n_samples_balanced'] = X_train_balanced.shape[0]
        self.training_history['training_params'] = default_params
        
        return self.model, self.training_history
    
    def tune_hyperparameters(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        param_grid: Optional[Dict[str, List]] = None,
        cv: int = 5,
        scoring: str = 'f1_weighted'
    ) -> Dict[str, Any]:
        """
        Tune hyperparameters using GridSearchCV.
        
        Args:
            X_train: Training features
            y_train: Training labels
            param_grid: Parameter grid for GridSearchCV
            cv: Number of cross-validation folds
            scoring: Scoring metric
            
        Returns:
            Dictionary with tuning results
        """
        logger.info("Starting hyperparameter tuning...")
        
        # Apply SMOTE
        X_train_balanced, y_train_balanced = self.smote.fit_resample(X_train, y_train)
        X_train_scaled = self.scaler.fit_transform(X_train_balanced)
        
        # Default parameter grid
        if param_grid is None:
            param_grid = {
                'num_leaves': [20, 31, 50],
                'learning_rate': [0.05, 0.1, 0.2],
                'n_estimators': [100, 200, 300],
                'max_depth': [5, 7, 10],
                'min_child_samples': [10, 20, 30]
            }
        
        logger.info(f"Parameter grid: {param_grid}")
        
        # Create base model
        base_model = lgb.LGBMClassifier(
            objective='multiclass',
            num_class=4,
            random_state=self.random_state,
            verbose=-1,
            n_jobs=self.n_jobs
        )
        
        # GridSearchCV
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=StratifiedKFold(n_splits=cv, shuffle=True, random_state=self.random_state),
            scoring=scoring,
            n_jobs=self.n_jobs,
            verbose=1
        )
        
        logger.info(f"Running {cv}-fold cross-validation...")
        grid_search.fit(X_train_scaled, y_train_balanced)
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV score ({scoring}): {grid_search.best_score_:.4f}")
        
        self.best_params = grid_search.best_params_
        self.model = grid_search.best_estimator_
        
        self.training_history['grid_search_results'] = {
            'best_params': self.best_params,
            'best_score': float(grid_search.best_score_),
            'scoring_metric': scoring,
            'cv_folds': cv,
            'all_results': [
                {
                    'params': result['params'],
                    'mean_test_score': float(result['mean_test_score']),
                    'std_test_score': float(result['std_test_score'])
                }
                for result in grid_search.cv_results_['params']  # Limited for memory
            ][:10]  # Only top 10 results
        }
        
        return self.training_history['grid_search_results']
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluate model on test set.
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        logger.info(f"Evaluating model on {X_test.shape[0]} test samples...")
        
        # Scale features
        X_test_scaled = self.scaler.transform(X_test)
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        y_proba = self.model.predict_proba(X_test_scaled)
        
        # Evaluate
        metrics = self.evaluator.evaluate(y_test, y_pred, y_proba)
        
        # Check targets
        targets_met = self.evaluator.check_targets_met()
        
        self.training_history['evaluation_metrics'] = metrics
        self.training_history['targets_met'] = targets_met
        
        return {
            'metrics': metrics,
            'targets_met': targets_met
        }
    
    def get_feature_importance(
        self,
        top_k: int = 20,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract feature importance from trained model.
        
        Args:
            top_k: Number of top features to return
            feature_names: Feature names for readability
            
        Returns:
            Feature importance dictionary
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        logger.info("Extracting feature importance...")
        
        # Get importance
        importance = self.model.feature_importances_
        
        # Get top k
        top_indices = np.argsort(importance)[-top_k:][::-1]
        
        if feature_names is None:
            feature_names = [f"Feature_{i}" for i in range(len(importance))]
        
        feature_importance_dict = {
            'all_features_importance': {
                feature_names[i]: float(importance[i])
                for i in range(len(importance))
            },
            'top_k_features': [
                {
                    'rank': i + 1,
                    'name': feature_names[idx],
                    'importance': float(importance[idx]),
                    'importance_relative': float(importance[idx] / importance.sum())
                }
                for i, idx in enumerate(top_indices)
            ]
        }
        
        logger.info("Top 10 features:")
        for item in feature_importance_dict['top_k_features'][:10]:
            logger.info(f"  {item['rank']}. {item['name']}: {item['importance']:.4f}")
        
        self.training_history['feature_importance'] = feature_importance_dict
        
        return feature_importance_dict
    
    def cross_validate(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        cv: int = 5,
        scoring: str = 'f1_weighted'
    ) -> Dict[str, float]:
        """
        Perform cross-validation.
        
        Args:
            X_train: Training features
            y_train: Training labels
            cv: Number of folds
            scoring: Scoring metric
            
        Returns:
            Cross-validation scores
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        logger.info(f"Running {cv}-fold cross-validation...")
        
        # Apply SMOTE
        X_balanced, y_balanced = self.smote.fit_resample(X_train, y_train)
        X_scaled = self.scaler.fit_transform(X_balanced)
        
        # Cross-validate
        scores = cross_val_score(
            self.model, X_scaled, y_balanced,
            cv=StratifiedKFold(n_splits=cv, shuffle=True, random_state=self.random_state),
            scoring=scoring,
            n_jobs=self.n_jobs
        )
        
        logger.info(f"CV scores: {scores}")
        logger.info(f"Mean CV score: {scores.mean():.4f} (+/- {scores.std():.4f})")
        
        cv_results = {
            'fold_scores': scores.tolist(),
            'mean_score': float(scores.mean()),
            'std_score': float(scores.std()),
            'scoring_metric': scoring
        }
        
        self.training_history['cross_validation'] = cv_results
        
        return cv_results
    
    def save_model(self, filepath: str) -> None:
        """
        Save trained model.
        
        Args:
            filepath: Output file path
        """
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'best_params': self.best_params,
                'training_history': self.training_history
            }, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load trained model.
        
        Args:
            filepath: Input file path
        """
        with open(filepath, 'rb') as f:
            checkpoint = pickle.load(f)
        
        self.model = checkpoint['model']
        self.scaler = checkpoint['scaler']
        self.best_params = checkpoint.get('best_params')
        self.training_history = checkpoint.get('training_history', {})
        
        logger.info(f"Model loaded from {filepath}")
    
    def predict(
        self,
        X: np.ndarray,
        return_proba: bool = False
    ) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features
            return_proba: Return prediction probabilities
            
        Returns:
            Predictions or probabilities
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X_scaled = self.scaler.transform(X)
        
        if return_proba:
            return self.model.predict_proba(X_scaled)
        else:
            return self.model.predict(X_scaled)
    
    def get_training_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive training summary.
        
        Returns:
            Training summary dictionary
        """
        return {
            'model_type': 'LightGBM Multiclass Classifier',
            'n_classes': 4,
            'class_names': ['secure', 'warning', 'vulnerable', 'critical'],
            'training_history': self.training_history,
            'best_parameters': self.best_params
        }
    
    def save_summary(self, filepath: str) -> None:
        """Save training summary to file."""
        import json
        
        summary = self.get_training_summary()
        
        # Make serializable
        def make_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            else:
                return obj
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(make_serializable(summary), f, indent=2)
        
        logger.info(f"Training summary saved to {filepath}")
