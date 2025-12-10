"""
Configuration and settings module for DeepAI system.
Loads from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Base directories
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = DATA_DIR / "logs"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    repo_root: Path = REPO_ROOT
    data_dir: Path = DATA_DIR
    models_dir: Path = MODELS_DIR
    logs_dir: Path = LOGS_DIR

    # Security & Rate Limiting
    max_scan_timeout: int = int(os.getenv("MAX_SCAN_TIMEOUT", 60))
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", 5))
    rate_limit_per_hour: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", 50))
    rate_limit_per_day: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_DAY", 200))
    rate_limit_target_per_hour: int = int(os.getenv("RATE_LIMIT_TARGET_PER_HOUR", 1))

    # Academic Mode (MANDATORY)
    academic_mode: bool = os.getenv("ACADEMIC_MODE", "true").lower() == "true"
    enforce_rate_limits: bool = os.getenv("ENFORCE_RATE_LIMITS", "true").lower() == "true"
    log_audit_events: bool = os.getenv("LOG_AUDIT_EVENTS", "true").lower() == "true"

    # Model Paths
    ml_model_path: Optional[str] = os.getenv("ML_MODEL_PATH", str(MODELS_DIR / "latest"))
    rl_model_path: Optional[str] = os.getenv("RL_MODEL_PATH", str(MODELS_DIR / "rl_latest"))
    shap_explainer_path: Optional[str] = os.getenv(
        "SHAP_EXPLAINER_PATH", str(MODELS_DIR / "shap_explainer.pkl")
    )

    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))
    api_workers: int = int(os.getenv("API_WORKERS", 4))

    # Feature Flags
    enable_deep_scan: bool = os.getenv("ENABLE_DEEP_SCAN", "false").lower() == "true"
    enable_active_analysis: bool = os.getenv("ENABLE_ACTIVE_ANALYSIS", "false").lower() == "true"

    class Config:
        env_file = REPO_ROOT / ".env"
        case_sensitive = False

    def ensure_directories_exist(self):
        """Create required directories if they don't exist."""
        for directory in [self.data_dir, self.models_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def validate_academic_mode(self):
        """Validate that academic mode is enforced."""
        if not self.academic_mode:
            raise RuntimeError(
                "CRITICAL: Academic mode must be enabled. "
                "System operates ONLY in passive observation mode."
            )


# Global settings instance
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories_exist()

# Enforce academic mode on import
settings.validate_academic_mode()
