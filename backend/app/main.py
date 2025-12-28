"""
Jenosize AI Content Generation Backend - FastAPI Application

Main application entry point for the Jenosize AI Content Generation API.
Configures FastAPI with CORS, middleware, routers, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time

from app.core.config import settings
from app.core.logging import logger
from app.routers import article_router, health_router
from app.services.qdrant_service import get_qdrant_service
from app.services.langchain_service import get_langchain_service
from app import __version__, __description__


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    Handles:
    - Service initialization on startup
    - Resource cleanup on shutdown
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Jenosize AI Content Generation Backend")
    logger.info(f"Version: {__version__}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"API Version: {settings.api_version}")
    logger.info("=" * 60)

    try:
        # Initialize Qdrant service
        logger.info("Initializing Qdrant service...")
        qdrant_service = get_qdrant_service()
        logger.info("Qdrant service initialized successfully")

        # Check if collection exists, initialize if needed
        try:
            stats = await qdrant_service.get_collection_stats()
            logger.info(
                f"Qdrant collection '{settings.qdrant_collection_name}' found: "
                f"{stats.get('points_count', 0)} articles"
            )
        except Exception as e:
            logger.warning(f"Qdrant collection not found or error: {str(e)}")
            logger.info("Collection will be initialized on first data import")

        # Initialize LangChain service
        logger.info("Initializing LangChain service...")
        langchain_service = get_langchain_service()
        logger.info(f"LangChain service initialized with model: {settings.llm_model}")

        # Verify Claude API connectivity
        claude_healthy, claude_msg = await langchain_service.health_check()
        if claude_healthy:
            logger.info(f"Claude API connection verified: {claude_msg}")
        else:
            logger.warning(f"Claude API check failed: {claude_msg}")

        logger.info("=" * 60)
        logger.info("Application startup complete - Ready to serve requests")
        logger.info(f"API documentation: http://{settings.backend_host}:{settings.backend_port}/docs")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down Jenosize AI Content Generation Backend")
    logger.info("=" * 60)


# Create FastAPI application
app = FastAPI(
    title="Jenosize AI Content Generation API",
    description=__description__,
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"/api/{settings.api_version}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests and responses.

    Logs:
    - Request method, path, client IP
    - Response status code, processing time
    """
    start_time = time.time()

    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)

    # Log response
    logger.info(
        f"Response: {response.status_code} for {request.method} {request.url.path} "
        f"in {process_time:.3f}s"
    )

    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed error messages.
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request parameters",
            "detail": exc.errors(),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions gracefully.
    """
    logger.error(
        f"Unhandled exception on {request.url.path}: {str(exc)}",
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.is_development else "Internal server error",
            "path": str(request.url.path),
        },
    )


# Include routers
app.include_router(health_router)
app.include_router(article_router)


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="API Root",
    description="Get API information and available endpoints",
)
async def root():
    """
    Root endpoint providing API information.

    Returns:
        API metadata and available endpoints
    """
    return {
        "name": "Jenosize AI Content Generation API",
        "version": __version__,
        "description": __description__,
        "environment": settings.environment,
        "api_version": settings.api_version,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "generate_article": "/api/v1/generate-article",
            "supported_options": "/api/v1/supported-options",
        },
        "status": "operational",
    }


# Development info endpoint (only in development)
if settings.is_development:
    @app.get(
        "/dev/info",
        tags=["development"],
        summary="Development Info",
        description="Get detailed configuration and service information (development only)",
    )
    async def dev_info():
        """
        Development endpoint for debugging and configuration verification.
        Only available in development environment.
        """
        return {
            "environment": settings.environment,
            "configuration": {
                "llm_model": settings.llm_model,
                "llm_temperature": settings.llm_temperature,
                "llm_max_tokens": settings.llm_max_tokens,
                "qdrant_host": settings.qdrant_host,
                "qdrant_port": settings.qdrant_port,
                "qdrant_collection": settings.qdrant_collection_name,
                "rag_top_k": settings.rag_top_k,
                "rag_similarity_threshold": settings.rag_similarity_threshold,
                "embedding_model": settings.embedding_model,
            },
            "features": {
                "rag_enabled": True,
                "embeddings_enabled": bool(settings.openai_api_key),
                "rate_limiting": settings.rate_limit_enabled,
                "debug_mode": settings.debug,
            },
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
