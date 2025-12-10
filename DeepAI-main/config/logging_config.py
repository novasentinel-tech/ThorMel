"""
Logging configuration for DeepAI system.
Implements structured logging with loguru.
"""

import sys
from pathlib import Path
from loguru import logger
from config.settings import settings

# Remove default handler
logger.remove()

# Console handler (structured)
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)

# File handler (detailed)
log_file = settings.logs_dir / "system.log"
logger.add(
    log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.log_level,
    rotation="100 MB",
    retention="7 days",
)

# Audit log (immutable, separate file)
audit_log_file = settings.logs_dir / "audit_log.jsonl"
logger.add(
    audit_log_file,
    format="{message}",
    level="INFO",
    serialize=True,
    rotation="200 MB",
    retention="30 days",
)


def get_logger(name: str) -> logger:
    """Get logger instance for a module."""
    return logger.bind(name=name)
