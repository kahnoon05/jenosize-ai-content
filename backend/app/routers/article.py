"""
Article Generation Router

Handles all article generation endpoints including generation requests,
statistics, and article management.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from uuid import uuid4

from app.models.article import ArticleGenerationRequest, ArticleGenerationResponse
from app.models.common import MessageResponse
from app.services.content_generator import get_content_generator
from app.core.logging import logger

router = APIRouter(prefix="/api/v1", tags=["articles"])


@router.post(
    "/generate-article",
    response_model=ArticleGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Article",
    description="Generate a business trend article based on provided parameters using AI and RAG",
)
async def generate_article(
    request: ArticleGenerationRequest,
) -> ArticleGenerationResponse:
    """
    Generate a high-quality business article using Claude 3.5 Sonnet and RAG pipeline.

    This endpoint:
    1. Validates input parameters
    2. Retrieves similar articles from Qdrant (if RAG enabled)
    3. Generates article content using Claude with context
    4. Extracts metadata and performs quality checks
    5. Returns complete article with metadata

    Args:
        request: Article generation parameters including topic, industry, audience, keywords, etc.

    Returns:
        ArticleGenerationResponse with generated article or error message

    Raises:
        HTTPException: If generation fails or invalid parameters provided
    """
    try:
        # Generate unique request ID
        request_id = str(uuid4())

        logger.info(
            f"Article generation request received (ID: {request_id}): "
            f"topic='{request.topic}', industry={request.industry.value}, "
            f"audience={request.audience.value}"
        )

        # Get content generator service
        content_gen = get_content_generator()

        # Generate article
        response = await content_gen.generate_article(
            request=request,
            request_id=request_id,
        )

        if response.success:
            logger.info(
                f"Article generated successfully (ID: {request_id}): "
                f"{response.article.metadata.word_count} words, "
                f"{response.generation_time_seconds}s"
            )
        else:
            logger.error(f"Article generation failed (ID: {request_id}): {response.error}")

        return response

    except ValueError as e:
        logger.error(f"Validation error in article generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error in article generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate article: {str(e)}",
        )


@router.get(
    "/generation-stats",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Generation Statistics",
    description="Get statistics about the article generation system and vector database",
)
async def get_generation_stats() -> Dict[str, Any]:
    """
    Get statistics about the content generation system.

    Returns:
        Dict containing:
        - Vector database statistics (article count, collection info)
        - Model configuration
        - RAG settings

    Raises:
        HTTPException: If unable to retrieve statistics
    """
    try:
        content_gen = get_content_generator()

        # Get Qdrant stats
        qdrant_stats = await content_gen.qdrant_service.get_collection_stats()

        stats = {
            "vector_database": qdrant_stats,
            "model_configuration": {
                "llm_model": content_gen.langchain_service.llm.model,
                "temperature": content_gen.langchain_service.llm.temperature,
                "max_tokens": content_gen.langchain_service.llm.max_tokens,
            },
            "rag_configuration": {
                "top_k": content_gen.qdrant_service.client._collections,
                "similarity_threshold": "configured per request",
            },
        }

        logger.info("Generation stats retrieved successfully")
        return stats

    except Exception as e:
        logger.error(f"Failed to retrieve generation stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}",
        )


@router.post(
    "/validate-request",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate Generation Request",
    description="Validate article generation parameters without generating content",
)
async def validate_generation_request(
    request: ArticleGenerationRequest,
) -> MessageResponse:
    """
    Validate article generation request parameters without actually generating content.

    Useful for frontend validation and checking if parameters are acceptable.

    Args:
        request: Article generation request to validate

    Returns:
        MessageResponse indicating validation success

    Raises:
        HTTPException: If validation fails
    """
    try:
        # Pydantic validation happens automatically
        # Additional custom validation can be added here

        logger.info(f"Validation successful for topic: {request.topic}")

        return MessageResponse(
            message="Request parameters are valid",
            success=True,
            data={
                "topic": request.topic,
                "industry": request.industry.value,
                "audience": request.audience.value,
                "estimated_length": request.target_length,
            },
        )

    except ValueError as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get(
    "/supported-options",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Supported Options",
    description="Get all supported industries, audiences, and tones for article generation",
)
async def get_supported_options() -> Dict[str, Any]:
    """
    Get all supported options for article generation.

    Returns:
        Dict with supported industries, audiences, tones, and other options
    """
    from app.models.article import IndustryType, AudienceType, ContentTone

    return {
        "industries": [industry.value for industry in IndustryType],
        "audiences": [audience.value for audience in AudienceType],
        "tones": [tone.value for tone in ContentTone],
        "length_constraints": {
            "min": 800,
            "max": 4000,
            "default": 2000,
        },
        "features": {
            "rag_enabled": True,
            "seo_metadata": True,
            "example_generation": True,
            "statistics_inclusion": True,
        },
    }
