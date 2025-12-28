"""
Article Generation Models

Pydantic models for article generation requests, responses, and metadata.
Defines the core data structures for the Jenosize content generation API.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class IndustryType(str, Enum):
    """Supported industry types for content generation."""

    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    HOSPITALITY = "hospitality"
    AUTOMOTIVE = "automotive"
    ENERGY = "energy"
    AGRICULTURE = "agriculture"
    ENTERTAINMENT = "entertainment"
    TELECOMMUNICATIONS = "telecommunications"
    GENERAL = "general"


class AudienceType(str, Enum):
    """Target audience types for content."""

    EXECUTIVES = "executives"
    MANAGERS = "managers"
    ENTREPRENEURS = "entrepreneurs"
    INVESTORS = "investors"
    PROFESSIONALS = "professionals"
    STUDENTS = "students"
    GENERAL_PUBLIC = "general_public"
    TECHNICAL = "technical"
    NON_TECHNICAL = "non_technical"


class ContentTone(str, Enum):
    """Content tone options."""

    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    ACADEMIC = "academic"
    INSPIRATIONAL = "inspirational"
    ANALYTICAL = "analytical"


class ArticleGenerationRequest(BaseModel):
    """
    Request model for article generation.

    Validates and structures all input parameters needed to generate
    a high-quality business trend article using the RAG pipeline.
    """

    # Required Fields
    topic: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Main topic or subject for the article",
        examples=["Artificial Intelligence in Healthcare", "Future of Remote Work"]
    )

    # Optional Context Fields
    industry: IndustryType = Field(
        default=IndustryType.GENERAL,
        description="Target industry for the content"
    )

    audience: AudienceType = Field(
        default=AudienceType.PROFESSIONALS,
        description="Target audience for the content"
    )

    keywords: Optional[List[str]] = Field(
        default=None,
        max_length=10,
        description="SEO keywords to incorporate (max 10)",
        examples=[["AI", "machine learning", "automation", "digital transformation"]]
    )

    # Content Parameters
    target_length: Optional[int] = Field(
        default=2000,
        ge=800,
        le=4000,
        description="Target article length in words"
    )

    tone: ContentTone = Field(
        default=ContentTone.PROFESSIONAL,
        description="Writing tone for the article"
    )

    include_examples: bool = Field(
        default=True,
        description="Include real-world examples and case studies"
    )

    include_statistics: bool = Field(
        default=True,
        description="Include relevant statistics and data"
    )

    # SEO Parameters
    generate_seo_metadata: bool = Field(
        default=True,
        description="Generate SEO meta description and tags"
    )

    # Advanced Options
    use_rag: bool = Field(
        default=True,
        description="Use RAG to retrieve similar articles for context"
    )

    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="LLM temperature (overrides default if provided)"
    )

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, v):
        """Validate and clean keywords list."""
        if v is None:
            return v
        # Remove duplicates and empty strings
        cleaned = list(set([k.strip() for k in v if k.strip()]))
        if len(cleaned) > 10:
            raise ValueError("Maximum 10 keywords allowed")
        return cleaned if cleaned else None

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v):
        """Validate topic is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Topic cannot be empty or whitespace only")
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "topic": "The Future of Sustainable Energy in Southeast Asia",
                "industry": "energy",
                "audience": "executives",
                "keywords": ["renewable energy", "solar power", "sustainability", "green technology"],
                "target_length": 2500,
                "tone": "professional",
                "include_examples": True,
                "include_statistics": True,
                "generate_seo_metadata": True,
                "use_rag": True
            }
        }
    )


class ArticleMetadata(BaseModel):
    """Article metadata including SEO information."""

    title: str = Field(..., description="Generated article title")
    meta_description: Optional[str] = Field(
        None,
        max_length=160,
        description="SEO meta description (max 160 chars)"
    )
    keywords: List[str] = Field(default_factory=list, description="Extracted/generated keywords")
    reading_time_minutes: int = Field(..., ge=1, description="Estimated reading time in minutes")
    word_count: int = Field(..., ge=0, description="Total word count")

    industry: str = Field(..., description="Content industry")
    audience: str = Field(..., description="Target audience")
    tone: str = Field(..., description="Content tone")

    # Generation metadata
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Article generation timestamp"
    )
    model_used: str = Field(..., description="LLM model used for generation")
    rag_sources_count: int = Field(
        default=0,
        ge=0,
        description="Number of similar articles used in RAG"
    )


class GeneratedArticle(BaseModel):
    """Complete generated article with content and metadata."""

    content: str = Field(..., min_length=100, description="Full article content in markdown format")
    metadata: ArticleMetadata = Field(..., description="Article metadata")

    # Optional sections
    sections: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Article sections with titles and content"
    )
    references: Optional[List[str]] = Field(
        None,
        description="References or sources used"
    )
    related_topics: Optional[List[str]] = Field(
        None,
        description="Related topics for further reading"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "# The Future of Sustainable Energy in Southeast Asia\n\n## Introduction\n...",
                "metadata": {
                    "title": "The Future of Sustainable Energy in Southeast Asia",
                    "meta_description": "Explore how Southeast Asia is leading the renewable energy revolution...",
                    "keywords": ["renewable energy", "solar power", "sustainability"],
                    "reading_time_minutes": 8,
                    "word_count": 2456,
                    "industry": "energy",
                    "audience": "executives",
                    "tone": "professional",
                    "generated_at": "2024-01-15T10:30:00Z",
                    "model_used": "claude-3-5-sonnet-20241022",
                    "rag_sources_count": 5
                },
                "sections": [
                    {"title": "Introduction", "content": "..."},
                    {"title": "Current State", "content": "..."}
                ],
                "references": ["Source 1", "Source 2"],
                "related_topics": ["Green Technology", "Climate Change"]
            }
        }
    )


class ArticleGenerationResponse(BaseModel):
    """Response model for article generation endpoint."""

    success: bool = Field(..., description="Generation success status")
    article: Optional[GeneratedArticle] = Field(None, description="Generated article (if successful)")
    error: Optional[str] = Field(None, description="Error message (if failed)")

    generation_time_seconds: float = Field(..., ge=0.0, description="Time taken to generate article")
    request_id: Optional[str] = Field(None, description="Unique request identifier")

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "article": {
                    "content": "# Article content here...",
                    "metadata": {
                        "title": "The Future of Sustainable Energy",
                        "word_count": 2456,
                        "reading_time_minutes": 8
                    }
                },
                "error": None,
                "generation_time_seconds": 12.5,
                "request_id": "req_abc123xyz",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )
