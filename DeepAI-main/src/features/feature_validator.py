"""
Feature validation module.
Validates feature data quality and consistency.
"""

from typing import Dict, List, Tuple, Any
import numpy as np
from scipy import stats

from config.logging_config import get_logger

logger = get_logger(__name__)


class FeatureValidator:
    """Validates feature vectors for data quality issues."""

    ALLOWED_WARNINGS = {
        "nan_values",
        "inf_values",
        "extreme_outliers",
        "feature_missing",
        "feature_zero_variance",
    }

    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator.

        Args:
            strict_mode: If True, raise exceptions on warnings
        """
        self.strict_mode = strict_mode
        self.warnings = []
        self.feature_ranges = {}

    def validate(self, features: np.ndarray, feature_names: List[str] = None) -> bool:
        """
        Validate feature vector.

        Args:
            features: Feature vector to validate
            feature_names: Optional names for features

        Returns:
            True if valid, False otherwise
        """
        self.warnings = []

        # Check shape
        if features.ndim != 1:
            msg = f"Features must be 1D array, got shape {features.shape}"
            if self.strict_mode:
                raise ValueError(msg)
            self.warnings.append(msg)
            return False

        # Expected 87 features
        if len(features) != 87:
            msg = f"Expected 87 features, got {len(features)}"
            if self.strict_mode:
                raise ValueError(msg)
            self.warnings.append(msg)
            return False

        # Check for NaN values
        nan_count = np.isnan(features).sum()
        if nan_count > 0:
            msg = f"Found {nan_count} NaN values"
            if self.strict_mode:
                raise ValueError(msg)
            self.warnings.append(msg)

        # Check for infinite values
        inf_count = np.isinf(features).sum()
        if inf_count > 0:
            msg = f"Found {inf_count} infinite values"
            if self.strict_mode:
                raise ValueError(msg)
            self.warnings.append(msg)

        # Check value ranges (0-1 for most normalized features)
        invalid_range = np.sum((features < 0) | (features > 100))
        if invalid_range > 0:
            msg = f"Found {invalid_range} values outside expected range"
            logger.warning(msg)

        # Check for all zeros
        if np.allclose(features, 0):
            msg = "All feature values are zero"
            if self.strict_mode:
                raise ValueError(msg)
            self.warnings.append(msg)

        # Check for constant features (zero variance)
        if np.var(features) < 1e-6:
            msg = "Features have near-zero variance"
            logger.warning(msg)

        return len(self.warnings) == 0

    def validate_batch(self, features_batch: np.ndarray) -> Dict[int, List[str]]:
        """
        Validate batch of feature vectors.

        Args:
            features_batch: Array of shape (n_samples, n_features)

        Returns:
            Dictionary mapping sample index to warnings
        """
        issues = {}

        for i, sample in enumerate(features_batch):
            self.validate(sample)
            if self.warnings:
                issues[i] = self.warnings.copy()

        return issues

    def get_warnings(self) -> List[str]:
        """Get list of validation warnings."""
        return self.warnings.copy()

    def check_consistency(self, features_list: List[np.ndarray]) -> bool:
        """
        Check consistency across multiple feature vectors.

        Args:
            features_list: List of feature vectors

        Returns:
            True if consistent
        """
        if not features_list:
            return True

        # Check all have same length
        lengths = [len(f) for f in features_list]
        if len(set(lengths)) > 1:
            logger.warning(f"Inconsistent feature lengths: {set(lengths)}")
            return False

        # Check data types
        dtypes = [f.dtype for f in features_list]
        if len(set(str(dt) for dt in dtypes)) > 1:
            logger.warning(f"Inconsistent data types: {set(dtypes)}")

        return True

    def detect_outliers(self, features: np.ndarray, threshold: float = 3.0) -> Dict[int, float]:
        """
        Detect outliers using Z-score.

        Args:
            features: Feature vector
            threshold: Z-score threshold (default 3.0 = 99.7% confidence)

        Returns:
            Dictionary of outlier indices and scores
        """
        outliers = {}

        # Convert to 2D for analysis
        if features.ndim == 1:
            features_2d = features.reshape(1, -1)
        else:
            features_2d = features

        # Z-score normalization
        z_scores = np.abs(stats.zscore(features_2d, axis=1))

        for i, scores in enumerate(z_scores):
            outlier_indices = np.where(scores > threshold)[0]
            for idx in outlier_indices:
                outliers[idx] = float(scores[idx])

        return outliers

    def detect_anomalies(self, features: np.ndarray, method: str = "isolation_forest") -> Dict[str, Any]:
        """
        Detect anomalies using specified method.

        Args:
            features: Feature vector or batch
            method: Detection method

        Returns:
            Dictionary with anomaly results
        """
        results = {"method": method, "is_anomaly": False, "score": 0.0}

        if method == "isolation_forest":
            try:
                from sklearn.ensemble import IsolationForest

                # Handle both single sample and batch
                if features.ndim == 1:
                    features_2d = features.reshape(1, -1)
                else:
                    features_2d = features

                model = IsolationForest(contamination=0.1, random_state=42)
                predictions = model.fit_predict(features_2d)
                scores = model.score_samples(features_2d)

                results["is_anomaly"] = (predictions == -1)[0] if predictions.ndim > 0 else predictions == -1
                results["score"] = float(scores[0]) if scores.ndim > 0 else float(scores)

            except Exception as e:
                logger.error(f"Anomaly detection failed: {e}")

        elif method == "zscore":
            if features.ndim == 1:
                z_scores = np.abs(stats.zscore(features))
                anomaly_count = np.sum(z_scores > 3.0)
                results["is_anomaly"] = anomaly_count > 0
                results["score"] = float(np.mean(z_scores))

        return results

    def get_feature_statistics(self, features: np.ndarray) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for features.

        Args:
            features: Feature vector or batch

        Returns:
            Dictionary with statistics per feature
        """
        if features.ndim == 1:
            features = features.reshape(1, -1)

        stats_dict = {}

        for i in range(features.shape[1]):
            col = features[:, i]
            stats_dict[f"feature_{i}"] = {
                "mean": float(np.mean(col)),
                "std": float(np.std(col)),
                "min": float(np.min(col)),
                "max": float(np.max(col)),
                "median": float(np.median(col)),
                "q25": float(np.percentile(col, 25)),
                "q75": float(np.percentile(col, 75)),
            }

        return stats_dict

    def __repr__(self) -> str:
        """String representation."""
        return f"FeatureValidator(strict_mode={self.strict_mode}, warnings={len(self.warnings)})"
