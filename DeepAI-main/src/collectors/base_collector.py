"""
Base collector class for all data collection modules.
Implements common patterns for passive data gathering.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from config.logging_config import get_logger

logger = get_logger(__name__)


class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.
    Ensures consistent interface for passive information gathering.
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize collector.

        Args:
            timeout: Operation timeout in seconds
        """
        self.timeout = timeout
        self.name = self.__class__.__name__

    @abstractmethod
    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect data from target.

        Args:
            target: Target domain or IP
            **kwargs: Additional arguments

        Returns:
            Dictionary of collected data
        """
        pass

    def __call__(self, target: str, **kwargs) -> Dict[str, Any]:
        """Collectors are callable."""
        return self.collect(target, **kwargs)

    def _log_collection_start(self, target: str):
        """Log collection start."""
        logger.debug(f"{self.name} starting collection for {target}")

    def _log_collection_end(self, target: str, success: bool = True):
        """Log collection end."""
        status = "completed" if success else "failed"
        logger.debug(f"{self.name} {status} for {target}")
