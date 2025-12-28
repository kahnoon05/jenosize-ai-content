"""
Health Check Router

Provides health check endpoints for monitoring service status and dependencies.
"""

from fastapi import APIRouter, status
from typing import Dict, Any

from app.models.common import HealthResponse
from app.services.content_generator import get_content_generator
from app.core.config import settings
from app.core.logging import logger
from app import __version__

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the API and its dependencies",
)
async def health_check() -> HealthResponse:
    """
    Perform health check on the API and all dependent services.

    Returns:
        HealthResponse with status of all services
    """
    try:
        # Get content generator service
        content_gen = get_content_generator()

        # Check all services
        health_status = await content_gen.health_check()

        # Build service status dict
        services_status = {}
        for service_name, service_info in health_status.get("services", {}).items():
            services_status[service_name] = service_info["status"]

        # Determine overall status
        overall_status = health_status.get("overall_status", "unknown")
        status_text = "healthy" if overall_status == "healthy" else "degraded"

        logger.info(f"Health check completed: {status_text}")

        return HealthResponse(
            status=status_text,
            version=settings.api_version,
            environment=settings.environment,
            services=services_status,
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version=settings.api_version,
            environment=settings.environment,
            services={"error": str(e)},
        )


@router.get(
    "/health/detailed",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Detailed Health Check",
    description="Get detailed health information including service messages",
)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Get detailed health information for debugging and monitoring.

    Returns:
        Detailed health status with messages from each service
    """
    try:
        content_gen = get_content_generator()
        health_status = await content_gen.health_check()

        return {
            "status": health_status.get("overall_status", "unknown"),
            "version": __version__,
            "api_version": settings.api_version,
            "environment": settings.environment,
            "services": health_status.get("services", {}),
            "configuration": {
                "llm_model": settings.llm_model,
                "rag_enabled": True,
                "rag_top_k": settings.rag_top_k,
                "collection_name": settings.qdrant_collection_name,
            },
        }

    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
