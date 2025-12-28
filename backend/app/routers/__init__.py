"""
API Routers Package

Contains all FastAPI route handlers for the Jenosize AI Content Generation API.
"""

from app.routers.article import router as article_router
from app.routers.health import router as health_router

__all__ = [
    "article_router",
    "health_router",
]
