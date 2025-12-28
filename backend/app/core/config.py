"""
Application Configuration Module

Manages all configuration settings for the Jenosize AI Content Generation Backend.
Uses Pydantic Settings for type-safe configuration management with environment variable support.
"""

from typing import List, Optional
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    Type validation and conversion is handled automatically by Pydantic.
    """

    # ============================================
    # Application Settings
    # ============================================
    environment: str = Field(default="development", description="Application environment")
    app_name: str = Field(default="Jenosize AI Content Generator", description="Application name")
    api_version: str = Field(default="v1", description="API version")
    debug: bool = Field(default=False, description="Debug mode")

    # ============================================
    # API Keys (At least one required)
    # ============================================
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key for Claude models (optional)")

    # ============================================
    # Qdrant Vector Database Settings
    # ============================================
    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant REST API port")
    qdrant_grpc_port: int = Field(default=6334, description="Qdrant gRPC port")
    qdrant_collection_name: str = Field(
        default="jenosize_articles",
        description="Qdrant collection name for article embeddings"
    )
    qdrant_use_grpc: bool = Field(default=False, description="Use gRPC for Qdrant connection")

    # Qdrant Cloud Support
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant Cloud API key")
    qdrant_use_https: bool = Field(default=False, description="Use HTTPS for Qdrant (required for Qdrant Cloud)")

    # ============================================
    # Backend API Settings
    # ============================================
    backend_host: str = Field(default="0.0.0.0", description="Backend host")
    backend_port: int = Field(default=8000, description="Backend port")
    cors_origins: str = Field(
        default="*",
        description="Allowed CORS origins (comma-separated or *)"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # ============================================
    # LangChain & LLM Settings
    # ============================================
    llm_model: str = Field(
        default="claude-sonnet-4-5-20250929",
        description="LLM model to use for content generation"
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="LLM temperature for generation"
    )
    llm_max_tokens: int = Field(
        default=4096,
        ge=100,
        le=8192,
        description="Maximum tokens for LLM generation"
    )

    # ============================================
    # RAG Configuration
    # ============================================
    rag_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of similar articles to retrieve for RAG"
    )
    rag_similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for RAG retrieval"
    )

    # ============================================
    # Embedding Settings
    # ============================================
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model for vector embeddings (local, no API key needed)"
    )
    embedding_dimensions: int = Field(
        default=384,
        description="Embedding vector dimensions (384 for all-MiniLM-L6-v2)"
    )

    # ============================================
    # Content Generation Settings
    # ============================================
    default_article_length: int = Field(
        default=2000,
        ge=500,
        le=5000,
        description="Default target article length in words"
    )
    min_article_length: int = Field(
        default=800,
        ge=300,
        le=2000,
        description="Minimum article length"
    )
    max_article_length: int = Field(
        default=4000,
        ge=1000,
        le=10000,
        description="Maximum article length"
    )

    # SEO Settings
    generate_meta_description: bool = Field(
        default=True,
        description="Automatically generate meta descriptions"
    )
    generate_keywords: bool = Field(
        default=True,
        description="Automatically extract keywords"
    )
    max_keywords: int = Field(
        default=10,
        ge=3,
        le=20,
        description="Maximum number of keywords to generate"
    )

    # ============================================
    # Logging & Monitoring
    # ============================================
    log_level: str = Field(default="INFO", description="Logging level")
    enable_debug_logs: bool = Field(default=False, description="Enable debug logs")

    # ============================================
    # Rate Limiting
    # ============================================
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Max requests per period")
    rate_limit_period: int = Field(default=3600, description="Rate limit period in seconds")

    # ============================================
    # Storage & Paths
    # ============================================
    storage_path: str = Field(default="./data/generated", description="Storage path for generated articles")
    sample_data_path: str = Field(default="./data/samples", description="Path to sample articles")

    # ============================================
    # Pydantic Settings Configuration
    # ============================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from environment
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is one of the allowed values."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v_upper

    @property
    def qdrant_url(self) -> str:
        """Get Qdrant URL for REST API connection."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once and reused across the application.
    This improves performance and ensures consistency.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()
