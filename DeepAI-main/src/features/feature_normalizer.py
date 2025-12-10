"""
Feature normalization module.
Implements Min-Max and StandardScaler normalization.
"""

from typing import Tuple, Optional
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from config.logging_config import get_logger

logger = get_logger(__name__)


class FeatureNormalizer:
    """Normalizes feature vectors for ML model input."""

    def __init__(self, method: str = "minmax"):
        """
        Initialize normalizer.

        Args:
            method: "minmax" or "standard"
        """
        self.method = method
        self.scaler = None
        self._is_fitted = False

    def fit(self, X: np.ndarray) -> "FeatureNormalizer":
        """
        Fit scaler to training data.

        Args:
            X: Training data (n_samples, n_features)

        Returns:
            Self for chaining
        """
        if self.method == "minmax":
            self.scaler = MinMaxScaler(feature_range=(0, 1))
        elif self.method == "standard":
            self.scaler = StandardScaler()
        else:
            raise ValueError(f"Unknown normalization method: {self.method}")

        self.scaler.fit(X)
        self._is_fitted = True
        logger.info(f"Fitted {self.method} scaler on {X.shape[0]} samples")
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform data using fitted scaler.

        Args:
            X: Data to transform

        Returns:
            Normalized data
        """
        if not self._is_fitted:
            raise RuntimeError("Scaler not fitted. Call fit() first.")

        return self.scaler.transform(X)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Fit and transform in one step.

        Args:
            X: Training data

        Returns:
            Normalized data
        """
        self.fit(X)
        return self.transform(X)

    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Reverse normalization.

        Args:
            X: Normalized data

        Returns:
            Original scale data
        """
        if not self._is_fitted:
            raise RuntimeError("Scaler not fitted.")

        return self.scaler.inverse_transform(X)

    def get_params(self) -> dict:
        """Get scaler parameters."""
        if self.method == "minmax":
            return {
                "method": "minmax",
                "feature_min": self.scaler.data_min_.tolist(),
                "feature_max": self.scaler.data_max_.tolist(),
            }
        elif self.method == "standard":
            return {
                "method": "standard",
                "mean": self.scaler.mean_.tolist(),
                "std": self.scaler.scale_.tolist(),
            }

    def __repr__(self) -> str:
        """String representation."""
        return f"FeatureNormalizer(method='{self.method}', fitted={self._is_fitted})"
