"""
Cloud Deployment Configuration Updates

Add these fields to your Settings class in config.py
for cloud deployment support (Qdrant Cloud, Railway, etc.)
"""

# Add these imports to your config.py if not already present:
# from typing import Optional

# Add these fields to the Settings class:

# ============================================
# Qdrant Cloud Configuration (Add to config.py)
# ============================================

qdrant_api_key: Optional[str] = Field(
    default=None,
    description="Qdrant Cloud API key for authentication"
)

qdrant_use_https: bool = Field(
    default=False,
    description="Use HTTPS for Qdrant connection (required for Qdrant Cloud)"
)

# ============================================
# Railway/Cloud Platform Configuration
# ============================================

port: int = Field(
    default=8000,
    description="Server port (Railway sets PORT environment variable)"
)

# Update the existing qdrant_url property to support cloud:
@property
def qdrant_url(self) -> str:
    """Get Qdrant URL for connection."""
    protocol = "https" if self.qdrant_use_https else "http"
    return f"{protocol}://{self.qdrant_host}:{self.qdrant_port}"


# ============================================
# Complete Example Settings Class
# ============================================
"""
from typing import List, Optional
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    '''
    Application settings loaded from environment variables.
    Supports both local Docker and cloud deployments.
    '''

    # Application Settings
    environment: str = Field(default="development")
    app_name: str = Field(default="Jenosize AI Content Generator")
    api_version: str = Field(default="v1")
    debug: bool = Field(default=False)

    # Server Configuration
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)
    port: int = Field(default=8000)  # For Railway

    # API Keys
    anthropic_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)

    # Qdrant Configuration
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_grpc_port: int = Field(default=6334)
    qdrant_collection_name: str = Field(default="jenosize_articles")
    qdrant_use_grpc: bool = Field(default=False)

    # Qdrant Cloud Support
    qdrant_api_key: Optional[str] = Field(default=None)
    qdrant_use_https: bool = Field(default=False)

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # LLM Configuration
    llm_model: str = Field(default="claude-sonnet-4-5-20250929")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    llm_max_tokens: int = Field(default=4096, ge=100, le=8192)

    # RAG Configuration
    rag_top_k: int = Field(default=5, ge=1, le=20)
    rag_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    # Embeddings
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_dimensions: int = Field(default=384)

    # Content Generation
    default_article_length: int = Field(default=2000, ge=500, le=5000)
    min_article_length: int = Field(default=800, ge=300, le=2000)
    max_article_length: int = Field(default=4000, ge=1000, le=10000)

    # SEO
    generate_meta_description: bool = Field(default=True)
    generate_keywords: bool = Field(default=True)
    max_keywords: int = Field(default=10, ge=3, le=20)

    # Logging
    log_level: str = Field(default="INFO")
    enable_debug_logs: bool = Field(default=False)

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100)
    rate_limit_period: int = Field(default=3600)

    # Storage
    storage_path: str = Field(default="./data/generated")
    sample_data_path: str = Field(default="./data/samples")

    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v_upper

    @property
    def qdrant_url(self) -> str:
        protocol = "https" if self.qdrant_use_https else "http"
        return f"{protocol}://{self.qdrant_host}:{self.qdrant_port}"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
"""
