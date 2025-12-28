"""
Logging Configuration Module

Configures structured logging for the Jenosize AI Content Generation Backend using Loguru.
Provides consistent logging format, log levels, and integration with FastAPI.
"""

import sys
from pathlib import Path
from loguru import logger

from app.core.config import settings


def configure_logging():
    """
    Configure Loguru logger with appropriate settings for the application.

    Sets up:
    - Console logging with colored output
    - File logging with rotation
    - JSON structured logging for production
    - Log levels based on environment
    """
    # Remove default handler
    logger.remove()

    # Determine log level
    log_level = settings.log_level if hasattr(settings, "log_level") else "INFO"

    # Console handler with colors (development)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=settings.is_development if hasattr(settings, "is_development") else True,
    )

    # File handler with rotation
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)

    logger.add(
        log_path / "app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        backtrace=True,
        diagnose=True,
    )

    # Error file handler (errors only)
    logger.add(
        log_path / "error_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",  # Keep error logs longer
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        backtrace=True,
        diagnose=True,
    )

    logger.info(f"Logging configured with level: {log_level}")


# Configure logging on module import
configure_logging()

# Export configured logger
__all__ = ["logger"]
