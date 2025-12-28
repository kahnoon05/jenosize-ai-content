"""
LangChain RAG Pipeline Service

Manages the LangChain-based RAG (Retrieval-Augmented Generation) pipeline for article generation.
Integrates OpenAI GPT models, prompt templates, and retrieval chains.
"""

from typing import List, Dict, Any, Optional
import time
import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage

from app.core.config import settings
from app.core.logging import logger
from app.core.constants import (
    WORDS_PER_MINUTE,
    MIN_READING_TIME_MINUTES,
    CONTENT_PREVIEW_LENGTH,
    METADATA_EXTRACTION_CONTENT_LIMIT,
)
from app.models.article import ArticleGenerationRequest


class LangChainService:
    """
    Service for managing LangChain RAG pipeline and LLM interactions.

    Handles:
    - OpenAI GPT model initialization
    - Embedding generation for semantic search
    - Prompt engineering for Jenosize-style content
    - RAG chain execution
    """

    def __init__(self):
        """Initialize LangChain service with OpenAI LLM and embeddings."""
        try:
            # Get OpenAI API key from environment
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")

            # Initialize OpenAI LLM (GPT-3.5 or GPT-4)
            self.llm = ChatOpenAI(
                openai_api_key=openai_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
            logger.info(f"Initialized OpenAI LLM: {settings.llm_model}")

            # Initialize OpenAI embeddings
            # Uses 'text-embedding-3-small' - fast, high quality, API-based
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=openai_key,
                model="text-embedding-3-small"
            )
            logger.info("Initialized OpenAI embeddings: text-embedding-3-small")

            # Initialize prompt templates
            self._setup_prompts()

        except Exception as e:
            logger.error(f"Failed to initialize LangChain service: {str(e)}")
            raise

    def _setup_prompts(self):
        """Set up prompt templates for article generation."""

        # System prompt for Jenosize-style content
        self.system_prompt = """You are an expert business content writer for Jenosize, a leading business consulting and insights company.

Your writing style is:
- Professional yet engaging and accessible
- Data-driven with real-world examples
- Forward-thinking and insightful
- Well-structured with clear sections
- SEO-optimized while maintaining quality
- Focused on actionable insights for business leaders

You specialize in creating trend analysis and future ideas articles that help executives and business professionals understand emerging opportunities and challenges in their industries.

Your articles should:
1. Start with a compelling hook that highlights the relevance
2. Provide clear context and background
3. Present well-researched insights with examples
4. Include forward-looking perspectives
5. End with actionable takeaways or thought-provoking conclusions
6. Use markdown formatting for structure and readability"""

        # Main article generation prompt template
        self.article_template = """Write a comprehensive business article about: {topic}

**Context:**
- Target Industry: {industry}
- Target Audience: {audience}
- Desired Tone: {tone}
- Target Length: ~{target_length} words
- Include Examples: {include_examples}
- Include Statistics: {include_statistics}

{rag_context}

**Requirements:**
1. Create an engaging, SEO-friendly title
2. Structure the article with clear H2 and H3 headings using markdown
3. Include an introduction that hooks the reader
4. Provide well-researched insights with specific examples
5. Incorporate relevant trends and future perspectives
6. End with actionable conclusions or thought-provoking questions
7. Use professional but accessible language
8. Naturally incorporate these keywords if provided: {keywords}

**Output Format:**
Return ONLY the article content in markdown format, starting with the H1 title.
Do not include any preamble or meta-commentary."""

        # RAG context template (for when we have similar articles)
        self.rag_context_template = """**Reference Context from Similar Articles:**

{similar_articles}

Use these reference articles to inform your writing, but create original content. Extract relevant insights, trends, and perspectives, but do not copy directly."""

        # Metadata extraction prompt
        self.metadata_template = """Based on the following article, extract structured metadata:

**Article:**
{article_content}

**Extract:**
1. A concise meta description (max 150 characters) for SEO
2. 5-7 relevant keywords
3. 3-5 related topics for further reading

Return as JSON:
{{
  "meta_description": "...",
  "keywords": ["keyword1", "keyword2", ...],
  "related_topics": ["topic1", "topic2", ...]
}}"""

        logger.info("Prompt templates configured")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI embeddings.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector

        Raises:
            ValueError: If embeddings service not initialized
        """
        if not self.embeddings:
            raise ValueError("Embeddings service not initialized. Provide OPENAI_API_KEY.")

        try:
            embedding = await self.embeddings.aembed_query(text)
            logger.debug(f"Generated embedding for text (length: {len(text)} chars)")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not self.embeddings:
            raise ValueError("Embeddings service not initialized. Provide OPENAI_API_KEY.")

        try:
            embeddings = await self.embeddings.aembed_documents(texts)
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise

    def _format_rag_context(self, similar_articles: List[Dict[str, Any]]) -> str:
        """
        Format retrieved similar articles into context for the prompt.

        Takes the list of similar articles from vector search and formats them
        into a structured context string that can be included in the generation prompt.

        Args:
            similar_articles: List of similar articles from vector search

        Returns:
            Formatted context string for inclusion in prompt, or empty string if no articles
        """
        if not similar_articles:
            return ""

        context_parts = []
        for i, article in enumerate(similar_articles, 1):
            # Include a preview of content (first CONTENT_PREVIEW_LENGTH chars)
            content_preview = article['content'][:CONTENT_PREVIEW_LENGTH]
            context_parts.append(
                f"**Reference {i}:** {article['title']}\n"
                f"Topic: {article['topic']} | Industry: {article['industry']}\n"
                f"Key insights: {content_preview}...\n"
            )

        formatted_context = self.rag_context_template.format(
            similar_articles="\n".join(context_parts)
        )

        return formatted_context

    async def generate_article(
        self,
        request: ArticleGenerationRequest,
        similar_articles: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Generate article content using OpenAI GPT with optional RAG context.

        Args:
            request: Article generation request with all parameters
            similar_articles: Optional list of similar articles for RAG context

        Returns:
            Generated article content in markdown format
        """
        try:
            start_time = time.time()

            # Format RAG context if available
            rag_context = ""
            if request.use_rag and similar_articles:
                rag_context = self._format_rag_context(similar_articles)
                logger.info(f"Using RAG context from {len(similar_articles)} similar articles")

            # Format keywords
            keywords_str = ", ".join(request.keywords) if request.keywords else "None specified"

            # Build the prompt
            article_prompt = self.article_template.format(
                topic=request.topic,
                industry=request.industry.value,
                audience=request.audience.value,
                tone=request.tone.value,
                target_length=request.target_length,
                include_examples="Yes" if request.include_examples else "No",
                include_statistics="Yes" if request.include_statistics else "No",
                rag_context=rag_context,
                keywords=keywords_str,
            )

            # Create messages for OpenAI
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=article_prompt),
            ]

            # Use custom temperature if provided
            llm = self.llm
            if request.temperature is not None:
                openai_key = os.getenv("OPENAI_API_KEY")
                llm = ChatOpenAI(
                    openai_api_key=openai_key,
                    model=settings.llm_model,
                    temperature=request.temperature,
                    max_tokens=settings.llm_max_tokens,
                )

            # Generate content
            logger.info(f"Generating article for topic: {request.topic}")
            response = await llm.ainvoke(messages)

            article_content = response.content

            generation_time = time.time() - start_time
            logger.info(
                f"Article generated successfully in {generation_time:.2f}s "
                f"(length: {len(article_content)} chars)"
            )

            return article_content

        except Exception as e:
            logger.error(f"Failed to generate article: {str(e)}")
            raise

    async def extract_metadata(self, article_content: str) -> Dict[str, Any]:
        """
        Extract metadata from generated article using OpenAI GPT.

        Sends the article content to the LLM for structured metadata extraction,
        limiting content length to avoid token limits.

        Args:
            article_content: Generated article content

        Returns:
            Dict with meta_description, keywords, and related_topics
        """
        try:
            # Create metadata extraction prompt (limit content to avoid token limits)
            prompt = self.metadata_template.format(
                article_content=article_content[:METADATA_EXTRACTION_CONTENT_LIMIT]
            )

            messages = [HumanMessage(content=prompt)]

            response = await self.llm.ainvoke(messages)

            # Parse JSON response
            import json
            metadata = json.loads(response.content)

            logger.info("Extracted metadata successfully")
            return metadata

        except Exception as e:
            logger.error(f"Failed to extract metadata: {str(e)}")
            # Return defaults on failure to ensure generation continues
            return {
                "meta_description": article_content[:150] + "...",
                "keywords": [],
                "related_topics": [],
            }

    def calculate_reading_time(self, text: str) -> int:
        """
        Calculate estimated reading time in minutes.

        Uses standard reading speed metric of 200 words per minute.
        Ensures minimum of 1 minute for very short content.

        Args:
            text: Article text to calculate reading time for

        Returns:
            Estimated reading time in minutes (minimum 1)
        """
        word_count = len(text.split())
        reading_time = max(MIN_READING_TIME_MINUTES, round(word_count / WORDS_PER_MINUTE))
        return reading_time

    def extract_title_from_content(self, content: str) -> str:
        """
        Extract title (first H1) from markdown content.

        Searches for the first H1 heading (lines starting with '# ') and
        extracts the title text.

        Args:
            content: Markdown article content

        Returns:
            Extracted title or "Untitled Article" if no H1 found
        """
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                # Remove the '# ' prefix and any trailing whitespace
                return line[2:].strip()
        return "Untitled Article"

    async def health_check(self) -> tuple[bool, str]:
        """
        Check if LangChain service is healthy.

        Returns:
            Tuple of (is_healthy: bool, status_message: str)
        """
        try:
            # Try a simple invocation
            messages = [HumanMessage(content="Hello")]
            response = await self.llm.ainvoke(messages)

            embeddings_status = "enabled" if self.embeddings else "disabled"

            return True, f"OpenAI API operational (embeddings: {embeddings_status})"

        except Exception as e:
            logger.error(f"LangChain health check failed: {str(e)}")
            return False, f"Error: {str(e)}"


# Global LangChain service instance
_langchain_service: Optional[LangChainService] = None


def get_langchain_service() -> LangChainService:
    """
    Get or create the global LangChain service instance.

    Returns:
        LangChainService: Singleton LangChain service instance
    """
    global _langchain_service
    if _langchain_service is None:
        _langchain_service = LangChainService()
    return _langchain_service
