"""
Qdrant Cloud Database Initialization Script
============================================
Initializes Qdrant Cloud vector database with sample Jenosize articles.

Usage:
    python tests/scripts/initialize_qdrant_cloud.py

Author: Jenosize AI Team
Date: 2025-12-28
"""

import sys
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import openai

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class QdrantCloudInitializer:
    """Initializes Qdrant Cloud database with sample data"""

    def __init__(self):
        # Get configuration from environment
        self.qdrant_host = os.getenv("QDRANT_HOST")
        self.qdrant_port = os.getenv("QDRANT_PORT", "6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.use_https = os.getenv("QDRANT_USE_HTTPS", "false").lower() == "true"
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "jenosize_articles")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Determine URL
        protocol = "https" if self.use_https else "http"
        self.qdrant_url = f"{protocol}://{self.qdrant_host}:{self.qdrant_port}"

        self.client = None
        self.embedding_dim = 1536  # OpenAI text-embedding-3-small dimension

        # Paths
        self.project_root = project_root
        self.sample_data_path = self.project_root / "data" / "samples" / "sample_articles.json"

    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

    def print_status(self, message: str, status: str = "info"):
        """Print status message"""
        color = {
            "success": Colors.GREEN,
            "error": Colors.RED,
            "warning": Colors.YELLOW,
            "info": Colors.BLUE
        }.get(status, Colors.BLUE)

        prefix = {
            "success": "[OK]",
            "error": "[ERROR]",
            "warning": "[WARN]",
            "info": "[INFO]"
        }.get(status, "[*]")

        print(f"{color}{prefix} {message}{Colors.END}")

    def connect_to_qdrant(self) -> bool:
        """Connect to Qdrant Cloud instance"""
        self.print_header("1. Connecting to Qdrant Cloud")

        if not self.qdrant_host:
            self.print_status("QDRANT_HOST not set in .env", "error")
            return False

        if not self.qdrant_api_key:
            self.print_status("QDRANT_API_KEY not set in .env", "error")
            return False

        try:
            # Connect to Qdrant Cloud
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
            )

            # Test connection
            collections = self.client.get_collections()
            self.print_status(
                f"Connected to Qdrant Cloud at {self.qdrant_host}",
                "success"
            )
            self.print_status(
                f"Existing collections: {[c.name for c in collections.collections]}",
                "info"
            )
            return True

        except Exception as e:
            self.print_status(f"Failed to connect to Qdrant Cloud: {e}", "error")
            self.print_status(f"URL: {self.qdrant_url}", "info")
            return False

    def create_collection(self) -> bool:
        """Create or recreate the collection"""
        self.print_header("2. Creating Collection")

        try:
            # Check if collection exists
            collections = self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)

            if exists:
                self.print_status(f"Collection '{self.collection_name}' already exists", "warning")
                response = input("Delete and recreate? (y/N): ")
                if response.lower() != 'y':
                    self.print_status("Using existing collection", "info")
                    return True

                # Delete existing collection
                self.client.delete_collection(collection_name=self.collection_name)
                self.print_status(f"Deleted existing collection", "success")

            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )

            # Create payload indexes for faster filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="industry",
                field_schema="keyword",
            )

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="topic",
                field_schema="text",
            )

            self.print_status(f"Created collection '{self.collection_name}'", "success")
            self.print_status(f"Vector dimension: {self.embedding_dim}", "info")
            self.print_status(f"Distance metric: Cosine", "info")
            return True

        except Exception as e:
            self.print_status(f"Failed to create collection: {e}", "error")
            return False

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        if not self.openai_api_key:
            self.print_status("OPENAI_API_KEY not set, using dummy embeddings", "warning")
            # Return dummy embeddings for testing
            import random
            return [[random.random() for _ in range(self.embedding_dim)] for _ in texts]

        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]

        except Exception as e:
            self.print_status(f"Failed to generate embeddings: {e}", "error")
            # Return dummy embeddings as fallback
            import random
            return [[random.random() for _ in range(self.embedding_dim)] for _ in texts]

    def load_sample_articles(self) -> List[Dict[str, Any]]:
        """Load sample articles from JSON file"""
        self.print_header("3. Loading Sample Articles")

        if not self.sample_data_path.exists():
            self.print_status(f"Sample data not found: {self.sample_data_path}", "error")
            return []

        try:
            with open(self.sample_data_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)

            self.print_status(f"Loaded {len(articles)} sample articles", "success")
            return articles

        except Exception as e:
            self.print_status(f"Failed to load sample articles: {e}", "error")
            return []

    def upload_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Upload articles to Qdrant with embeddings"""
        self.print_header("4. Uploading Articles to Qdrant Cloud")

        if not articles:
            self.print_status("No articles to upload", "error")
            return False

        try:
            # Prepare texts for embedding
            texts = [
                f"{article.get('title', '')} {article.get('content', '')[:500]}"
                for article in articles
            ]

            self.print_status(f"Generating embeddings for {len(texts)} articles...", "info")
            embeddings = self.generate_embeddings(texts)

            # Create points
            points = []
            for idx, (article, embedding) in enumerate(zip(articles, embeddings)):
                point = PointStruct(
                    id=idx + 1,
                    vector=embedding,
                    payload={
                        "title": article.get("title", ""),
                        "content": article.get("content", ""),
                        "topic": article.get("topic", ""),
                        "industry": article.get("industry", ""),
                        "keywords": article.get("keywords", []),
                        "audience": article.get("audience", ""),
                        "word_count": article.get("word_count", 0),
                    }
                )
                points.append(point)

            # Upload to Qdrant
            self.print_status(f"Uploading {len(points)} points to Qdrant Cloud...", "info")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            self.print_status(f"Successfully uploaded {len(points)} articles", "success")
            return True

        except Exception as e:
            self.print_status(f"Failed to upload articles: {e}", "error")
            return False

    def verify_upload(self) -> bool:
        """Verify that articles were uploaded correctly"""
        self.print_header("5. Verifying Upload")

        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)

            self.print_status(f"Collection: {self.collection_name}", "success")
            self.print_status(f"Points count: {collection_info.points_count}", "success")
            self.print_status(f"Status: {collection_info.status}", "success")

            if collection_info.points_count > 0:
                # Test search
                dummy_vector = [0.0] * self.embedding_dim
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=dummy_vector,
                    limit=1
                )

                if results:
                    self.print_status(f"Search test successful", "success")
                    self.print_status(f"Sample article: {results[0].payload.get('title', 'N/A')}", "info")

            return True

        except Exception as e:
            self.print_status(f"Verification failed: {e}", "error")
            return False

    def run(self) -> bool:
        """Run the full initialization process"""
        print(f"{Colors.BOLD}Jenosize AI - Qdrant Cloud Initialization{Colors.END}\n")
        print(f"Project root: {self.project_root}")
        print(f"Qdrant URL: {self.qdrant_url}")
        print(f"Collection: {self.collection_name}\n")

        steps = [
            ("Connect to Qdrant Cloud", self.connect_to_qdrant),
            ("Create Collection", self.create_collection),
        ]

        for step_name, step_func in steps:
            if not step_func():
                self.print_status(f"Initialization failed at: {step_name}", "error")
                return False

        # Load and upload articles
        articles = self.load_sample_articles()
        if not articles:
            return False

        if not self.upload_articles(articles):
            return False

        if not self.verify_upload():
            return False

        # Success!
        self.print_header("✓ Initialization Complete!")
        print(f"\n{Colors.GREEN}{Colors.BOLD}Qdrant Cloud is ready to use!{Colors.END}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.END}")
        print(f"  1. Start your backend: docker-compose up backend")
        print(f"  2. Test article generation via API")
        print(f"  3. Or deploy to Railway/Vercel\n")

        return True


def main():
    """Main entry point"""
    initializer = QdrantCloudInitializer()

    try:
        success = initializer.run()
        return 0 if success else 1

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Initialization cancelled by user{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
