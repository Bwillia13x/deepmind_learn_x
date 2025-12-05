"""Logging configuration."""

import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stderr,
    level="DEBUG" if settings.environment == "dev" else "INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Add file handler
logger.add(
    log_dir / "app.log",
    rotation="5 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

# Add metrics file (JSONL)
logger.add(
    log_dir / "metrics.jsonl",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    filter=lambda record: "metrics" in record["extra"],
    format="{message}",
    serialize=True,
)


def log_metric(name: str, **kwargs):
    """Log a metric in JSONL format."""
    logger.bind(metrics=True).info({"metric": name, **kwargs})
