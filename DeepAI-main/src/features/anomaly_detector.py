"""
Anomaly detection module for features.
Detects unusual patterns in feature vectors.
"""

from typing import Dict, List, Tuple, Any
import numpy as np
from scipy import stats
from scipy.spatial.distance import mahalanobis

from config.logging_config import get_logger

logger = get_logger(__name__)


class AnomalyDetector:
    """Detects anomalies in feature vectors."""

    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector.

        Args:
            contamination: Expected proportion of anomalies (0-1)
        """
        self.contamination = contamination
        self.thresholds = {}
        self.reference_stats = None

    def fit(self, X: np.ndarray) -> "AnomalyDetector":
        """
        Fit detector on training data.

        Args:
            X: Training data (n_samples, n_features)

        Returns:
            Self for chaining
        """
        # Calculate reference statistics
        self.reference_stats = {
            "mean": np.mean(X, axis=0),
            "std": np.std(X, axis=0),
            "median": np.median(X, axis=0),
            "q1": np.percentile(X, 25, axis=0),
            "q3": np.percentile(X, 75, axis=0),
        }

        # Calculate IQR-based thresholds
        iqr = self.reference_stats["q3"] - self.reference_stats["q1"]
        self.thresholds = {
            "lower": self.reference_stats["q1"] - 1.5 * iqr,
            "upper": self.reference_stats["q3"] + 1.5 * iqr,
        }

        logger.info("Anomaly detector fitted on training data")
        return self

    def detect_zscore(self, X: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """
        Detect anomalies using Z-score method.

        Args:
            X: Data to check
            threshold: Z-score threshold

        Returns:
            Boolean array (True = anomaly)
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        z_scores = np.abs(stats.zscore(X, axis=0))
        return np.sum(z_scores > threshold, axis=1) > 0

    def detect_iqr(self, X: np.ndarray) -> np.ndarray:
        """
        Detect anomalies using IQR (Interquartile Range).

        Args:
            X: Data to check

        Returns:
            Boolean array (True = anomaly)
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        if self.thresholds is None:
            raise RuntimeError("Detector not fitted. Call fit() first.")

        lower = X < self.thresholds["lower"]
        upper = X > self.thresholds["upper"]
        return np.sum(lower | upper, axis=1) > 0

    def detect_isolation_forest(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies using Isolation Forest.

        Args:
            X: Data to check

        Returns:
            Tuple of (anomaly_flags, anomaly_scores)
        """
        try:
            from sklearn.ensemble import IsolationForest

            if X.ndim == 1:
                X = X.reshape(1, -1)

            model = IsolationForest(
                contamination=self.contamination,
                random_state=42
            )
            predictions = model.fit_predict(X)
            scores = model.score_samples(X)

            return predictions == -1, scores

        except ImportError:
            logger.warning("sklearn not available for IsolationForest")
            return np.zeros(len(X), dtype=bool), np.zeros(len(X))

    def detect_lof(self, X: np.ndarray, n_neighbors: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies using Local Outlier Factor.

        Args:
            X: Data to check
            n_neighbors: Number of neighbors for LOF

        Returns:
            Tuple of (anomaly_flags, anomaly_scores)
        """
        try:
            from sklearn.neighbors import LocalOutlierFactor

            if X.ndim == 1:
                X = X.reshape(1, -1)

            model = LocalOutlierFactor(n_neighbors=n_neighbors)
            predictions = model.fit_predict(X)
            scores = model.negative_outlier_factor_

            return predictions == -1, -scores

        except ImportError:
            logger.warning("sklearn not available for LocalOutlierFactor")
            return np.zeros(len(X), dtype=bool), np.zeros(len(X))

    def detect_mahalanobis(self, X: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """
        Detect anomalies using Mahalanobis distance.

        Args:
            X: Data to check
            threshold: Distance threshold

        Returns:
            Boolean array (True = anomaly)
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        if self.reference_stats is None:
            raise RuntimeError("Detector not fitted. Call fit() first.")

        mean = self.reference_stats["mean"]
        cov = np.cov(X.T)

        # Regularize covariance matrix if singular
        try:
            cov_inv = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            cov += np.eye(cov.shape[0]) * 1e-6
            cov_inv = np.linalg.inv(cov)

        distances = []
        for sample in X:
            try:
                dist = mahalanobis(sample, mean, cov_inv)
                distances.append(dist)
            except Exception:
                distances.append(0.0)

        return np.array(distances) > threshold

    def detect_ensemble(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Ensemble anomaly detection using multiple methods.

        Args:
            X: Data to check

        Returns:
            Dictionary with results from all methods
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        results = {
            "sample_count": X.shape[0],
            "methods": {},
            "consensus_anomalies": 0,
        }

        # Z-score method
        try:
            zscore_anomalies = self.detect_zscore(X)
            results["methods"]["zscore"] = {
                "anomalies": np.sum(zscore_anomalies),
                "confidence": np.mean(zscore_anomalies)
            }
        except Exception as e:
            logger.warning(f"Z-score detection failed: {e}")

        # IQR method
        try:
            iqr_anomalies = self.detect_iqr(X)
            results["methods"]["iqr"] = {
                "anomalies": np.sum(iqr_anomalies),
                "confidence": np.mean(iqr_anomalies)
            }
        except Exception as e:
            logger.warning(f"IQR detection failed: {e}")

        # Isolation Forest
        try:
            if_anomalies, if_scores = self.detect_isolation_forest(X)
            results["methods"]["isolation_forest"] = {
                "anomalies": np.sum(if_anomalies),
                "mean_score": float(np.mean(if_scores))
            }
        except Exception as e:
            logger.warning(f"IsolationForest detection failed: {e}")

        # Consensus score
        method_count = len(results["methods"])
        if method_count > 0:
            results["consensus_anomalies"] = sum(
                m.get("anomalies", 0) for m in results["methods"].values()
            ) / method_count

        return results

    def get_anomaly_report(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Generate comprehensive anomaly report.

        Args:
            X: Data to check

        Returns:
            Detailed anomaly report
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        report = {
            "total_samples": X.shape[0],
            "total_features": X.shape[1],
            "analysis": self.detect_ensemble(X),
        }

        # Feature-level statistics
        feature_stats = {}
        for i in range(X.shape[1]):
            col = X[:, i]
            feature_stats[f"feature_{i}"] = {
                "mean": float(np.mean(col)),
                "std": float(np.std(col)),
                "min": float(np.min(col)),
                "max": float(np.max(col)),
                "non_zero": int(np.sum(col != 0)),
            }

        report["feature_statistics"] = feature_stats

        return report

    def __repr__(self) -> str:
        """String representation."""
        fitted = self.reference_stats is not None
        return f"AnomalyDetector(contamination={self.contamination}, fitted={fitted})"
