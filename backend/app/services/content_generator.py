"""
Content Generation Service

Orchestrates the complete content generation pipeline:
1. Generate embeddings for query
2. Retrieve similar articles from Qdrant (RAG)
3. Generate article using Claude with RAG context
4. Extract metadata and perform quality checks
5. Return complete article with metadata
"""

from typing import Optional, List, Dict, Any
import time
import re

from app.models.article import (
    ArticleGenerationRequest,
    ArticleGenerationResponse,
    GeneratedArticle,
    ArticleMetadata,
)
from app.services.qdrant_service import get_qdrant_service
from app.services.langchain_service import get_langchain_service
from app.core.config import settings
from app.core.logging import logger


class ContentGeneratorService:
    """
    Main service for orchestrating article generation.

    Combines Qdrant retrieval, LangChain generation, and quality control
    to produce high-quality business articles.
    """

    def __init__(self):
        """Initialize content generator with required services."""
        self.qdrant_service = get_qdrant_service()
        self.langchain_service = get_langchain_service()
        logger.info("ContentGeneratorService initialized")

    async def generate_article(
        self,
        request: ArticleGenerationRequest,
        request_id: Optional[str] = None,
    ) -> ArticleGenerationResponse:
        """
        Generate a complete article based on request parameters.

        This is the main orchestration method that:
        1. Validates input
        2. Performs RAG retrieval if enabled
        3. Generates content using Claude
        4. Extracts metadata
        5. Performs quality checks
        6. Returns complete article

        Args:
            request: Article generation request
            request_id: Optional unique request identifier

        Returns:
            ArticleGenerationResponse with generated article or error
        """
        start_time = time.time()

        try:
            logger.info(f"Starting article generation for topic: {request.topic}")

            # Step 1: Retrieve similar articles using RAG (if enabled and embeddings available)
            similar_articles = []
            rag_sources_count = 0

            if request.use_rag:
                similar_articles = await self._retrieve_similar_articles(request)
                rag_sources_count = len(similar_articles)

                if rag_sources_count > 0:
                    logger.info(f"Retrieved {rag_sources_count} similar articles for RAG context")
                else:
                    logger.info("No similar articles found or RAG disabled")

            # Step 2: Generate article content using Claude
            article_content = await self.langchain_service.generate_article(
                request=request,
                similar_articles=similar_articles,
            )

            # Step 3: Validate content quality
            validation_result = self._validate_article_content(article_content, request)
            if not validation_result["valid"]:
                logger.warning(f"Article validation issues: {validation_result['issues']}")
                # Continue anyway but log the issues

            # Step 4: Extract metadata
            metadata = await self._extract_article_metadata(
                content=article_content,
                request=request,
                rag_sources_count=rag_sources_count,
            )

            # Step 5: Build complete article structure
            article = GeneratedArticle(
                content=article_content,
                metadata=metadata,
                sections=self._extract_sections(article_content),
                related_topics=metadata.keywords[:5] if metadata.keywords else None,
            )

            # Calculate generation time
            generation_time = time.time() - start_time

            logger.info(
                f"Article generated successfully in {generation_time:.2f}s "
                f"({metadata.word_count} words, {metadata.reading_time_minutes} min read)"
            )

            return ArticleGenerationResponse(
                success=True,
                article=article,
                error=None,
                generation_time_seconds=round(generation_time, 2),
                request_id=request_id,
            )

        except Exception as e:
            generation_time = time.time() - start_time
            error_message = f"Failed to generate article: {str(e)}"
            logger.error(error_message, exc_info=True)

            return ArticleGenerationResponse(
                success=False,
                article=None,
                error=error_message,
                generation_time_seconds=round(generation_time, 2),
                request_id=request_id,
            )

    async def _retrieve_similar_articles(
        self,
        request: ArticleGenerationRequest,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar articles from Qdrant for RAG context.

        Args:
            request: Article generation request

        Returns:
            List of similar articles with content and metadata
        """
        try:
            # Generate embedding for the query (topic + keywords)
            query_text = request.topic
            if request.keywords:
                query_text += " " + " ".join(request.keywords)

            query_embedding = await self.langchain_service.generate_embedding(query_text)

            # Search for similar articles
            similar_articles = await self.qdrant_service.search_similar_articles(
                query_embedding=query_embedding,
                top_k=settings.rag_top_k,
                min_score=settings.rag_similarity_threshold,
                filter_industry=request.industry.value if request.industry.value != "general" else None,
            )

            return similar_articles

        except Exception as e:
            logger.warning(f"Failed to retrieve similar articles: {str(e)}")
            # Return empty list on failure - generation will continue without RAG
            return []

    def _validate_article_content(
        self,
        content: str,
        request: ArticleGenerationRequest,
    ) -> Dict[str, Any]:
        """
        Validate generated article content for quality.

        Checks:
        - Minimum length requirements
        - Presence of title
        - Proper markdown structure
        - No placeholder text

        Args:
            content: Generated article content
            request: Original request for validation

        Returns:
            Dict with validation result and any issues
        """
        issues = []

        # Check minimum length
        word_count = len(content.split())
        if word_count < settings.min_article_length:
            issues.append(
                f"Article too short: {word_count} words (minimum: {settings.min_article_length})"
            )

        # Check for title (H1 heading)
        if not re.search(r'^#\s+.+$', content, re.MULTILINE):
            issues.append("No H1 title found")

        # Check for placeholder text
        placeholders = ["[Insert", "[Add", "[TODO", "lorem ipsum"]
        for placeholder in placeholders:
            if placeholder.lower() in content.lower():
                issues.append(f"Placeholder text detected: {placeholder}")

        # Check for proper structure (should have multiple headings)
        headings = re.findall(r'^#{2,3}\s+.+$', content, re.MULTILINE)
        if len(headings) < 3:
            issues.append("Article may lack proper structure (few headings)")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "word_count": word_count,
        }

    async def _extract_article_metadata(
        self,
        content: str,
        request: ArticleGenerationRequest,
        rag_sources_count: int,
    ) -> ArticleMetadata:
        """
        Extract comprehensive metadata from article.

        Args:
            content: Article content
            request: Original generation request
            rag_sources_count: Number of RAG sources used

        Returns:
            ArticleMetadata with all extracted information
        """
        # Extract title
        title = self.langchain_service.extract_title_from_content(content)

        # Calculate word count and reading time
        word_count = len(content.split())
        reading_time = self.langchain_service.calculate_reading_time(content)

        # Extract metadata using Claude (if enabled)
        extracted_metadata = {"meta_description": None, "keywords": [], "related_topics": []}

        if request.generate_seo_metadata:
            try:
                extracted_metadata = await self.langchain_service.extract_metadata(content)
            except Exception as e:
                logger.warning(f"Failed to extract metadata: {str(e)}")

        # Combine request keywords with extracted keywords
        all_keywords = list(set(
            (request.keywords or []) + extracted_metadata.get("keywords", [])
        ))[:settings.max_keywords]

        # Generate meta description
        meta_description = extracted_metadata.get("meta_description")
        if not meta_description:
            # Fallback: use first 150 chars
            meta_description = content[:150].replace("#", "").strip() + "..."

        # Ensure meta description is not too long
        if len(meta_description) > 160:
            meta_description = meta_description[:157] + "..."

        from datetime import datetime, timezone

        return ArticleMetadata(
            title=title,
            meta_description=meta_description,
            keywords=all_keywords,
            reading_time_minutes=reading_time,
            word_count=word_count,
            industry=request.industry.value,
            audience=request.audience.value,
            tone=request.tone.value,
            model_used=settings.llm_model,
            rag_sources_count=rag_sources_count,
            generated_at=datetime.now(timezone.utc),
        )

    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Extract article sections based on markdown headings.

        Args:
            content: Article content in markdown

        Returns:
            List of sections with titles and content
        """
        sections = []

        # Split by H2 headings
        h2_pattern = r'^##\s+(.+)$'
        parts = re.split(h2_pattern, content, flags=re.MULTILINE)

        # Skip the first part (before first H2) if it exists
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    section_title = parts[i].strip()
                    section_content = parts[i + 1].strip()
                    sections.append({
                        "title": section_title,
                        "content": section_content,
                    })

        return sections if sections else None

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of all content generation components.

        Returns:
            Dict with health status of all services
        """
        health_status = {
            "content_generator": "healthy",
            "services": {},
        }

        # Check Qdrant
        try:
            qdrant_healthy, qdrant_msg = await self.qdrant_service.health_check()
            health_status["services"]["qdrant"] = {
                "status": "healthy" if qdrant_healthy else "unhealthy",
                "message": qdrant_msg,
            }
        except Exception as e:
            health_status["services"]["qdrant"] = {
                "status": "unhealthy",
                "message": str(e),
            }

        # Check LangChain/Claude
        try:
            langchain_healthy, langchain_msg = await self.langchain_service.health_check()
            health_status["services"]["langchain"] = {
                "status": "healthy" if langchain_healthy else "unhealthy",
                "message": langchain_msg,
            }
        except Exception as e:
            health_status["services"]["langchain"] = {
                "status": "unhealthy",
                "message": str(e),
            }

        # Overall status
        all_healthy = all(
            svc["status"] == "healthy"
            for svc in health_status["services"].values()
        )
        health_status["overall_status"] = "healthy" if all_healthy else "degraded"

        return health_status


# Global content generator instance
_content_generator: Optional[ContentGeneratorService] = None


def get_content_generator() -> ContentGeneratorService:
    """
    Get or create the global content generator instance.

    Returns:
        ContentGeneratorService: Singleton content generator instance
    """
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGeneratorService()
    return _content_generator
