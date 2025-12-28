#!/usr/bin/env python3
"""
Database Initialization Script

Convenience script to initialize Qdrant vector database with sample articles.
Can be run standalone or imported as a module.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.utils.init_data import initialize_qdrant_with_samples, verify_qdrant_data
from app.core.logging import logger


async def run_initialization(recreate: bool = False):
    """
    Run the database initialization process.

    Args:
        recreate: Whether to recreate the collection
    """
    logger.info("Starting database initialization...")

    try:
        # Initialize
        count = await initialize_qdrant_with_samples(recreate_collection=recreate)

        if count > 0:
            logger.info(f"✓ Successfully initialized database with {count} articles")

            # Verify
            logger.info("Verifying database...")
            verified = await verify_qdrant_data()

            if verified:
                logger.info("✓ Database verification successful")
                return True
            else:
                logger.warning("⚠ Database verification failed")
                return False
        else:
            logger.error("✗ Failed to initialize database")
            return False

    except Exception as e:
        logger.error(f"✗ Initialization failed: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize Qdrant vector database with sample Jenosize articles"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete existing collection and recreate (WARNING: destroys existing data)",
    )

    args = parser.parse_args()

    if args.recreate:
        logger.warning("⚠ RECREATE MODE: This will delete all existing data!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Initialization cancelled")
            sys.exit(0)

    # Run initialization
    success = asyncio.run(run_initialization(recreate=args.recreate))

    if success:
        logger.info("=" * 60)
        logger.info("Database initialization completed successfully!")
        logger.info("You can now start the FastAPI server and generate articles.")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("Database initialization failed. Please check the logs.")
        sys.exit(1)
