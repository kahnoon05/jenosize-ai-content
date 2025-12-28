"""
Core Package

Contains core application components including configuration, logging, and security.
"""

from app.core.config import settings
from app.core.logging import logger

__all__ = [
    "settings",
    "logger",
]
