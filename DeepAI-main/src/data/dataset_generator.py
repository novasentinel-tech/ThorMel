"""
Dataset Generator for ML Training
Generates synthetic training datasets with realistic feature distributions
"""

import numpy as np
import logging
from typing import Tuple, Dict, Optional
from sklearn.datasets import make_classification
from pathlib import Path

logger = logging.getLogger(__name__)


class DatasetGenerator:
    """
    Generate synthetic training datasets for ML model development.
    
    Creates realistic feature distributions mimicking actual security characteristics
    with 4 target classes: secure, warning, vulnerable, critical
    """
    
    # Feature categories from Phase B
    FEATURE_CATEGORIES = {
        'HTTP': (0, 15),      # Features 0-14
        'TLS': (15, 33),      # Features 15-32
        'DNS': (33, 45),      # Features 33-44
        'WHOIS': (45, 55),    # Features 45-54
        'PORTS': (55, 70),    # Features 55-69
        'TECH': (70, 87)      # Features 70-86
    }
    
    # Target classes
    CLASS_NAMES = {
        0: 'secure',
        1: 'warning',
        2: 'vulnerable',
        3: 'critical'
    }
    
    def __init__(self, n_features: int = 87, random_state: int = 42):
        """
        Initialize dataset generator.
        
        Args:
            n_features: Number of features (default: 87)
            random_state: Random seed for reproducibility
        """
        self.n_features = n_features
        self.random_state = random_state
        np.random.seed(random_state)
        
    def generate_dataset(
        self,
        n_samples: int = 10000,
        class_distribution: Optional[Dict[int, float]] = None,
        feature_noise: float = 0.1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training dataset.
        
        Args:
            n_samples: Total number of samples to generate
            class_distribution: Class distribution dict {class: proportion}
                Default: {0: 0.40, 1: 0.25, 2: 0.20, 3: 0.15}
            feature_noise: Gaussian noise std for feature values
            
        Returns:
            X: Feature array (n_samples, 87)
            y: Target labels (n_samples,)
        """
        if class_distribution is None:
            class_distribution = {0: 0.40, 1: 0.25, 2: 0.20, 3: 0.15}
        
        logger.info(f"Generating {n_samples} samples with distribution {class_distribution}")
        
        # Initialize feature and label arrays
        X = np.zeros((n_samples, self.n_features), dtype=np.float32)
        y = np.zeros(n_samples, dtype=np.int32)
        
        sample_idx = 0
        
        # Generate samples per class
        for class_label, proportion in class_distribution.items():
            n_class_samples = int(n_samples * proportion)
            
            # Generate base features for this class
            class_features = self._generate_class_features(
                n_class_samples,
                class_label,
                feature_noise
            )
            
            # Assign to X and y
            X[sample_idx:sample_idx + n_class_samples] = class_features
            y[sample_idx:sample_idx + n_class_samples] = class_label
            
            logger.debug(f"Class {class_label} ({self.CLASS_NAMES[class_label]}): "
                        f"{n_class_samples} samples")
            
            sample_idx += n_class_samples
        
        # Shuffle dataset
        shuffle_idx = np.random.permutation(n_samples)
        X = X[shuffle_idx]
        y = y[shuffle_idx]
        
        logger.info(f"Dataset generated: X.shape={X.shape}, y.shape={y.shape}")
        logger.info(f"Class distribution: {np.bincount(y)}")
        
        return X, y
    
    def _generate_class_features(
        self,
        n_samples: int,
        class_label: int,
        noise: float
    ) -> np.ndarray:
        """
        Generate features for a specific security class.
        
        Args:
            n_samples: Number of samples to generate
            class_label: Target class (0-3)
            noise: Noise standard deviation
            
        Returns:
            Feature array (n_samples, 87)
        """
        features = np.random.uniform(0, 1, (n_samples, self.n_features)).astype(np.float32)
        
        # Adjust feature distributions based on class
        if class_label == 0:  # SECURE
            # High security features
            features[:, 3:15] = np.random.uniform(0.8, 1.0, (n_samples, 12))  # HTTP security
            features[:, 15:33] = np.random.uniform(0.8, 1.0, (n_samples, 18))  # TLS security
            features[:, 33:45] = np.random.uniform(0.7, 1.0, (n_samples, 12))  # DNS security
            features[:, 45:55] = np.random.uniform(0.8, 1.0, (n_samples, 10))  # WHOIS trust
            features[:, 55:70] = np.random.uniform(0.0, 0.3, (n_samples, 15))  # Low ports exposure
            features[:, 70:87] = np.random.uniform(0.8, 1.0, (n_samples, 17))  # Tech security
            
        elif class_label == 1:  # WARNING
            # Mixed security features
            features[:, 3:15] = np.random.uniform(0.5, 0.8, (n_samples, 12))  # HTTP medium
            features[:, 15:33] = np.random.uniform(0.6, 0.9, (n_samples, 18))  # TLS medium-good
            features[:, 33:45] = np.random.uniform(0.4, 0.7, (n_samples, 12))  # DNS medium
            features[:, 45:55] = np.random.uniform(0.5, 0.8, (n_samples, 10))  # WHOIS medium
            features[:, 55:70] = np.random.uniform(0.3, 0.6, (n_samples, 15))  # Medium ports
            features[:, 70:87] = np.random.uniform(0.5, 0.8, (n_samples, 17))  # Tech medium
            
        elif class_label == 2:  # VULNERABLE
            # Weak security features
            features[:, 3:15] = np.random.uniform(0.2, 0.5, (n_samples, 12))  # HTTP weak
            features[:, 15:33] = np.random.uniform(0.1, 0.5, (n_samples, 18))  # TLS weak
            features[:, 33:45] = np.random.uniform(0.1, 0.4, (n_samples, 12))  # DNS weak
            features[:, 45:55] = np.random.uniform(0.2, 0.5, (n_samples, 10))  # WHOIS risky
            features[:, 55:70] = np.random.uniform(0.5, 0.8, (n_samples, 15))  # Many ports open
            features[:, 70:87] = np.random.uniform(0.1, 0.4, (n_samples, 17))  # Tech vulnerable
            
        else:  # CRITICAL (class_label == 3)
            # Very weak security features
            features[:, 3:15] = np.random.uniform(0.0, 0.2, (n_samples, 12))  # HTTP critical
            features[:, 15:33] = np.random.uniform(0.0, 0.2, (n_samples, 18))  # TLS critical
            features[:, 33:45] = np.random.uniform(0.0, 0.2, (n_samples, 12))  # DNS critical
            features[:, 45:55] = np.random.uniform(0.0, 0.2, (n_samples, 10))  # WHOIS critical
            features[:, 55:70] = np.random.uniform(0.8, 1.0, (n_samples, 15))  # Many ports exposed
            features[:, 70:87] = np.random.uniform(0.0, 0.2, (n_samples, 17))  # Tech critical
        
        # Add noise
        noise_array = np.random.normal(0, noise, features.shape).astype(np.float32)
        features = np.clip(features + noise_array, 0, 1).astype(np.float32)
        
        return features
    
    def generate_train_test_split(
        self,
        n_samples: int = 10000,
        test_size: float = 0.2,
        class_distribution: Optional[Dict[int, float]] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate complete train/test dataset split.
        
        Args:
            n_samples: Total samples
            test_size: Proportion for test set
            class_distribution: Class distribution dict
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        X, y = self.generate_dataset(n_samples, class_distribution)
        
        # Train/test split
        split_idx = int(n_samples * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        logger.info(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test
    
    def save_dataset(
        self,
        X: np.ndarray,
        y: np.ndarray,
        filepath: str
    ) -> None:
        """
        Save dataset to NPZ file.
        
        Args:
            X: Feature array
            y: Label array
            filepath: Output file path
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(filepath, X=X, y=y)
        logger.info(f"Dataset saved to {filepath}")
    
    def load_dataset(self, filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load dataset from NPZ file.
        
        Args:
            filepath: Input file path
            
        Returns:
            X, y arrays
        """
        data = np.load(filepath)
        logger.info(f"Dataset loaded from {filepath}")
        return data['X'], data['y']
    
    def get_class_weights(self, y: np.ndarray) -> Dict[int, float]:
        """
        Calculate class weights for imbalanced dataset.
        
        Args:
            y: Label array
            
        Returns:
            Dictionary of class weights
        """
        unique, counts = np.unique(y, return_counts=True)
        total = len(y)
        weights = {}
        
        for class_label, count in zip(unique, counts):
            # Weight inversely proportional to class frequency
            weights[class_label] = total / (len(unique) * count)
        
        logger.info(f"Class weights: {weights}")
        return weights
    
    def get_dataset_statistics(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Get comprehensive dataset statistics.
        
        Args:
            X: Feature array
            y: Label array
            
        Returns:
            Dictionary with dataset statistics
        """
        unique, counts = np.unique(y, return_counts=True)
        
        stats = {
            'n_samples': X.shape[0],
            'n_features': X.shape[1],
            'n_classes': len(unique),
            'class_distribution': {
                self.CLASS_NAMES[int(c)]: int(cnt) 
                for c, cnt in zip(unique, counts)
            },
            'feature_mean': X.mean(axis=0).tolist(),
            'feature_std': X.std(axis=0).tolist(),
            'feature_min': X.min(axis=0).tolist(),
            'feature_max': X.max(axis=0).tolist(),
        }
        
        logger.info(f"Dataset statistics: {stats}")
        return stats
