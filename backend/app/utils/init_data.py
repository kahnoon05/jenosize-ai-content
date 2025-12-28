"""
Data Initialization Utility

Script to initialize Qdrant vector database with sample Jenosize-style articles.
Loads sample articles, generates embeddings, and populates the vector database.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any

from app.services.qdrant_service import get_qdrant_service
from app.services.langchain_service import get_langchain_service
from app.core.logging import logger
from app.core.config import settings


async def load_sample_articles(sample_file: str = None) -> List[Dict[str, Any]]:
    """
    Load sample articles from JSON file.

    Args:
        sample_file: Path to sample articles JSON file (optional)

    Returns:
        List of article dictionaries
    """
    if sample_file is None:
        # Default path to sample articles
        sample_file = Path(__file__).parent.parent.parent / "data" / "samples" / "sample_articles.json"

    logger.info(f"Loading sample articles from: {sample_file}")

    try:
        with open(sample_file, "r", encoding="utf-8") as f:
            articles = json.load(f)

        logger.info(f"Loaded {len(articles)} sample articles")
        return articles

    except FileNotFoundError:
        logger.error(f"Sample file not found: {sample_file}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in sample file: {str(e)}")
        return []


async def initialize_qdrant_with_samples(recreate_collection: bool = False):
    """
    Initialize Qdrant vector database with sample articles.

    Args:
        recreate_collection: If True, delete and recreate collection

    Returns:
        Number of articles added
    """
    logger.info("=" * 60)
    logger.info("Initializing Qdrant with sample articles")
    logger.info("=" * 60)

    # Get services
    qdrant_service = get_qdrant_service()
    langchain_service = get_langchain_service()

    # Step 1: Initialize collection
    logger.info(f"Initializing collection: {settings.qdrant_collection_name}")
    success = await qdrant_service.initialize_collection(recreate=recreate_collection)

    if not success:
        logger.error("Failed to initialize collection")
        return 0

    # Step 2: Load sample articles
    articles = await load_sample_articles()

    if not articles:
        logger.warning("No sample articles to load")
        return 0

    # Step 3: Generate embeddings for all articles
    logger.info("Generating embeddings for sample articles...")

    try:
        # Prepare texts for embedding (combine title and content)
        texts_to_embed = []
        for article in articles:
            text = f"{article['title']} {article['content']}"
            texts_to_embed.append(text)

        # Generate embeddings in batch
        embeddings = await langchain_service.generate_embeddings_batch(texts_to_embed)

        logger.info(f"Generated {len(embeddings)} embeddings")

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        logger.info("Attempting to continue without embeddings...")
        return 0

    # Step 4: Prepare articles for insertion
    articles_with_embeddings = []

    for i, article in enumerate(articles):
        article_data = {
            "embedding": embeddings[i],
            "title": article["title"],
            "content": article["content"],
            "topic": article["topic"],
            "industry": article["industry"],
            "metadata": {
                "keywords": article.get("keywords", []),
                "audience": article.get("audience", "professionals"),
                "word_count": article.get("word_count", len(article["content"].split())),
            },
        }
        articles_with_embeddings.append(article_data)

    # Step 5: Insert articles into Qdrant
    logger.info(f"Inserting {len(articles_with_embeddings)} articles into Qdrant...")

    try:
        point_ids = await qdrant_service.add_articles_batch(articles_with_embeddings)

        logger.info(f"Successfully inserted {len(point_ids)} articles")

        # Get collection stats
        stats = await qdrant_service.get_collection_stats()
        logger.info(f"Collection stats: {stats}")

        logger.info("=" * 60)
        logger.info("Qdrant initialization completed successfully")
        logger.info("=" * 60)

        return len(point_ids)

    except Exception as e:
        logger.error(f"Failed to insert articles: {str(e)}")
        return 0


async def verify_qdrant_data():
    """
    Verify Qdrant data by performing a sample search.

    Returns:
        True if verification successful, False otherwise
    """
    logger.info("Verifying Qdrant data...")

    try:
        qdrant_service = get_qdrant_service()
        langchain_service = get_langchain_service()

        # Generate embedding for test query
        test_query = "artificial intelligence and machine learning in business"
        query_embedding = await langchain_service.generate_embedding(test_query)

        # Search for similar articles
        similar_articles = await qdrant_service.search_similar_articles(
            query_embedding=query_embedding,
            top_k=3,
            min_score=0.5,
        )

        if similar_articles:
            logger.info(f"Verification successful! Found {len(similar_articles)} similar articles")
            logger.info("Top result:")
            logger.info(f"  Title: {similar_articles[0]['title']}")
            logger.info(f"  Score: {similar_articles[0]['score']:.3f}")
            logger.info(f"  Topic: {similar_articles[0]['topic']}")
            return True
        else:
            logger.warning("No similar articles found - database may be empty")
            return False

    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return False


async def main():
    """
    Main function to run initialization.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Initialize Qdrant with sample articles")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate collection (delete existing data)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing data without initialization",
    )

    args = parser.parse_args()

    try:
        if args.verify_only:
            # Only verify
            await verify_qdrant_data()
        else:
            # Initialize
            count = await initialize_qdrant_with_samples(recreate_collection=args.recreate)

            if count > 0:
                # Verify
                await verify_qdrant_data()
            else:
                logger.error("Initialization failed - no articles added")

    except Exception as e:
        logger.error(f"Initialization script failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
