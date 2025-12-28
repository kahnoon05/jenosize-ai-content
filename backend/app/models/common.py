"""
Common Pydantic Models

Shared models used across the API for health checks, errors, and general responses.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status: 'healthy' or 'unhealthy'")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (development/production)")
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of dependent services (qdrant, langchain, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "v1",
                "environment": "development",
                "services": {
                    "qdrant": "connected",
                    "langchain": "initialized",
                    "claude_api": "available"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model for API errors."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    path: Optional[str] = Field(None, description="API path where error occurred")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input parameters",
                "detail": "Topic field is required and cannot be empty",
                "timestamp": "2024-01-15T10:30:00Z",
                "path": "/api/v1/generate-article"
            }
        }


class MessageResponse(BaseModel):
    """Generic message response model."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Article generated successfully",
                "success": True,
                "data": {"article_id": "abc123"},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
