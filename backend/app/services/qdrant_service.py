"""
Qdrant Vector Database Service

Handles all interactions with Qdrant vector database including:
- Collection management (create, delete, check existence)
- Vector storage (insert embeddings)
- Semantic search (similarity search for RAG)
- Vector retrieval and metadata management
"""

from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
import numpy as np
import time

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.constants import (
    QDRANT_MAX_RETRIES,
    QDRANT_INITIAL_RETRY_DELAY,
)


class QdrantService:
    """
    Service for managing Qdrant vector database operations.

    Provides methods for collection management, vector storage, and similarity search
    used in the RAG (Retrieval-Augmented Generation) pipeline.
    """

    def __init__(self):
        """
        Initialize Qdrant service with connection to Qdrant server.

        Connects to Qdrant using settings from configuration.
        Supports both HTTP/gRPC (local) and HTTPS (cloud) connections.
        Implements retry logic to handle temporary connection failures.
        """
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = settings.embedding_dimensions

        # Determine connection mode (Cloud vs Local)
        use_cloud = (
            hasattr(settings, 'qdrant_use_https') and settings.qdrant_use_https
        ) or (
            hasattr(settings, 'qdrant_api_key') and settings.qdrant_api_key
        )

        # Initialize Qdrant client
        if use_cloud:
            # Qdrant Cloud connection with HTTPS
            url = f"https://{settings.qdrant_host}:{settings.qdrant_port}"
            api_key = getattr(settings, 'qdrant_api_key', None)

            self.client = QdrantClient(
                url=url,
                api_key=api_key,
            )
            logger.info(f"✅ Connected to Qdrant Cloud at {settings.qdrant_host}")

        elif settings.qdrant_use_grpc:
            # Local gRPC connection
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_grpc_port,
                prefer_grpc=True,
            )
            logger.info(
                f"Initialized Qdrant client via gRPC at {settings.qdrant_host}:{settings.qdrant_grpc_port}"
            )
        else:
            # Local HTTP connection
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
            logger.info(
                f"Initialized Qdrant client via HTTP at {settings.qdrant_host}:{settings.qdrant_port}"
            )

        # Verify connection with retry logic and exponential backoff
        self._verify_connection_with_retry()

    def _verify_connection_with_retry(self) -> None:
        """
        Verify Qdrant connection with retry logic and exponential backoff.

        Attempts to connect to Qdrant multiple times with increasing delays
        between retries to handle temporary network issues or service startup delays.

        Raises:
            Exception: If connection fails after all retry attempts
        """
        retry_delay = QDRANT_INITIAL_RETRY_DELAY

        for attempt in range(1, QDRANT_MAX_RETRIES + 1):
            try:
                collections = self.client.get_collections()
                logger.info(f"Qdrant connection verified. Found {len(collections.collections)} collections")
                return  # Success - exit function
            except Exception as e:
                if attempt < QDRANT_MAX_RETRIES:
                    logger.warning(
                        f"Failed to connect to Qdrant (attempt {attempt}/{QDRANT_MAX_RETRIES}): {str(e)}. "
                        f"Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to Qdrant after {QDRANT_MAX_RETRIES} attempts: {str(e)}")
                    raise

    async def initialize_collection(self, recreate: bool = False) -> bool:
        """
        Initialize or recreate the articles collection in Qdrant.

        Creates a new collection with appropriate vector configuration and payload indices
        for efficient semantic search and filtering.

        Args:
            recreate: If True, delete existing collection and create new one

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if collection exists
            exists = self._collection_exists()

            if exists:
                if recreate:
                    logger.info(f"Deleting existing collection: {self.collection_name}")
                    self.client.delete_collection(collection_name=self.collection_name)
                else:
                    logger.info(f"Collection {self.collection_name} already exists")
                    return True

            # Create collection with cosine similarity for semantic search
            self._create_collection()

            # Create payload indices for faster filtering
            self._create_payload_indices()

            logger.info(f"Collection {self.collection_name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize collection: {str(e)}")
            return False

    def _collection_exists(self) -> bool:
        """
        Check if the collection exists in Qdrant.

        Returns:
            True if collection exists, False otherwise
        """
        collections = self.client.get_collections()
        return any(col.name == self.collection_name for col in collections.collections)

    def _create_collection(self) -> None:
        """
        Create the Qdrant collection with vector configuration.

        Uses cosine similarity distance metric for semantic search.
        """
        logger.info(f"Creating collection: {self.collection_name}")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=self.vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

    def _create_payload_indices(self) -> None:
        """
        Create payload indices for faster filtering on common fields.

        Indices on 'industry' (keyword) and 'topic' (text) enable
        efficient filtering during similarity search.
        """
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="industry",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )

        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="topic",
            field_schema=qdrant_models.PayloadSchemaType.TEXT,
        )

    async def add_article(
        self,
        embedding: List[float],
        title: str,
        content: str,
        topic: str,
        industry: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add an article embedding to Qdrant with metadata.

        Args:
            embedding: Article embedding vector
            title: Article title
            content: Article content (or excerpt)
            topic: Article topic
            industry: Article industry
            metadata: Additional metadata to store

        Returns:
            str: Unique point ID of the inserted vector
        """
        try:
            # Generate unique ID
            point_id = str(uuid4())

            # Prepare payload
            payload = {
                "title": title,
                "content": content,
                "topic": topic,
                "industry": industry,
                **(metadata or {}),
            }

            # Insert vector with payload
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload,
                    )
                ],
            )

            logger.info(f"Added article to Qdrant: {title} (ID: {point_id})")
            return point_id

        except Exception as e:
            logger.error(f"Failed to add article: {str(e)}")
            raise

    async def add_articles_batch(
        self,
        articles: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Add multiple articles to Qdrant in a batch operation.

        Args:
            articles: List of article dictionaries with 'embedding', 'title', 'content', 'topic', 'industry', 'metadata'

        Returns:
            List[str]: List of inserted point IDs
        """
        try:
            points = []
            point_ids = []

            for article in articles:
                point_id = str(uuid4())
                point_ids.append(point_id)

                payload = {
                    "title": article["title"],
                    "content": article["content"],
                    "topic": article["topic"],
                    "industry": article["industry"],
                    **article.get("metadata", {}),
                }

                points.append(
                    qdrant_models.PointStruct(
                        id=point_id,
                        vector=article["embedding"],
                        payload=payload,
                    )
                )

            # Batch upsert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            logger.info(f"Added {len(articles)} articles to Qdrant in batch")
            return point_ids

        except Exception as e:
            logger.error(f"Failed to add articles batch: {str(e)}")
            raise

    async def search_similar_articles(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_score: float = 0.7,
        filter_industry: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar articles using semantic similarity.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            min_score: Minimum similarity score threshold (0.0 to 1.0)
            filter_industry: Optional industry filter

        Returns:
            List of similar articles with content and metadata
        """
        try:
            # Build filter if industry specified
            query_filter = None
            if filter_industry:
                query_filter = qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="industry",
                            match=qdrant_models.MatchValue(value=filter_industry),
                        )
                    ]
                )

            # Perform similarity search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=min_score,
                query_filter=query_filter,
            )

            # Format results
            similar_articles = []
            for result in search_results:
                similar_articles.append({
                    "id": result.id,
                    "score": result.score,
                    "title": result.payload.get("title", ""),
                    "content": result.payload.get("content", ""),
                    "topic": result.payload.get("topic", ""),
                    "industry": result.payload.get("industry", ""),
                    "metadata": {
                        k: v for k, v in result.payload.items()
                        if k not in ["title", "content", "topic", "industry"]
                    },
                })

            logger.info(
                f"Found {len(similar_articles)} similar articles (threshold: {min_score})"
            )
            return similar_articles

        except Exception as e:
            logger.error(f"Failed to search similar articles: {str(e)}")
            return []

    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.

        Returns:
            Dict with collection statistics (count, size, etc.)
        """
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)

            stats = {
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "status": collection_info.status.value,
                "vector_size": self.vector_size,
            }

            logger.info(f"Collection stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}

    async def delete_collection(self) -> bool:
        """
        Delete the articles collection.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False

    async def health_check(self) -> Tuple[bool, str]:
        """
        Check if Qdrant is healthy and accessible.

        Returns:
            Tuple of (is_healthy: bool, status_message: str)
        """
        try:
            # Try to get collections
            collections = self.client.get_collections()

            # Check if our collection exists
            exists = any(col.name == self.collection_name for col in collections.collections)

            if exists:
                # Get collection info
                info = self.client.get_collection(collection_name=self.collection_name)
                return True, f"Connected - {info.points_count} articles indexed"
            else:
                return True, "Connected - collection not initialized"

        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return False, f"Error: {str(e)}"


# Global Qdrant service instance
_qdrant_service: Optional[QdrantService] = None


def get_qdrant_service() -> QdrantService:
    """
    Get or create the global Qdrant service instance.

    Returns:
        QdrantService: Singleton Qdrant service instance
    """
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
