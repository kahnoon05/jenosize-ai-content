"""
Qdrant Database Initialization Script
=====================================
Initializes Qdrant vector database with sample Jenosize articles.

Author: Jenosize AI Team
Date: 2025-12-23
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class QdrantInitializer:
    """Initializes Qdrant database with sample data"""

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "jenosize_articles"
    ):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.client = None
        self.embedding_dim = 1536  # OpenAI text-embedding-3-small dimension

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

        print(f"{color}[{status.upper()}]{Colors.END} {message}")

    def connect_to_qdrant(self) -> bool:
        """Connect to Qdrant instance"""
        self.print_header("1. Connecting to Qdrant")

        try:
            self.client = QdrantClient(url=self.qdrant_url)

            # Test connection
            collections = self.client.get_collections()
            self.print_status(
                f"Connected to Qdrant at {self.qdrant_url}",
                "success"
            )
            self.print_status(
                f"Existing collections: {[c.name for c in collections.collections]}",
                "info"
            )
            return True

        except Exception as e:
            self.print_status(f"Failed to connect to Qdrant: {e}", "error")
            return False

    def create_collection(self) -> bool:
        """Create or recreate the collection"""
        self.print_header("2. Creating Collection")

        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name in collection_names:
                self.print_status(
                    f"Collection '{self.collection_name}' already exists",
                    "warning"
                )

                # Ask to recreate
                print(f"{Colors.YELLOW}Do you want to recreate it? (y/n): {Colors.END}", end='')
                response = input().strip().lower()

                if response == 'y':
                    self.client.delete_collection(self.collection_name)
                    self.print_status(f"Deleted existing collection", "success")
                else:
                    self.print_status(f"Using existing collection", "info")
                    return True

            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )

            self.print_status(
                f"Created collection '{self.collection_name}' with dimension {self.embedding_dim}",
                "success"
            )
            return True

        except Exception as e:
            self.print_status(f"Failed to create collection: {e}", "error")
            return False

    def get_sample_articles(self) -> List[Dict[str, Any]]:
        """Get sample articles for Jenosize"""
        self.print_header("3. Preparing Sample Articles")

        sample_articles = [
            {
                "id": 1,
                "title": "The Future of AI in Business: Trends and Predictions",
                "content": """
                Artificial Intelligence is rapidly transforming the business landscape. Organizations
                across industries are leveraging AI to enhance decision-making, automate processes,
                and create personalized customer experiences. From predictive analytics to natural
                language processing, AI technologies are becoming integral to competitive advantage.

                Key trends include the rise of generative AI, which enables businesses to create
                content, code, and designs at scale. Machine learning models are becoming more
                accessible through cloud platforms, democratizing AI capabilities for businesses
                of all sizes. Additionally, ethical AI and responsible deployment are emerging as
                critical considerations for enterprises.

                Looking ahead, we expect to see increased integration of AI with IoT devices,
                advancement in edge computing for real-time AI processing, and more sophisticated
                AI-driven automation in knowledge work. Organizations that embrace these trends
                while maintaining ethical standards will lead the next wave of digital transformation.
                """,
                "metadata": {
                    "industry": "Technology",
                    "topic": "Artificial Intelligence",
                    "keywords": ["AI", "machine learning", "automation", "digital transformation"],
                    "date": "2024-01-15",
                    "author": "Jenosize Research Team"
                }
            },
            {
                "id": 2,
                "title": "Sustainable Business Practices: The New Competitive Advantage",
                "content": """
                Sustainability is no longer optional for modern businesses. Consumers, investors,
                and regulators increasingly demand environmentally and socially responsible practices.
                Companies that embrace sustainability are finding it's not just good ethics—it's
                good business.

                Leading organizations are implementing circular economy principles, reducing waste,
                and designing products for longevity and recyclability. Carbon neutrality targets
                are becoming standard, with many companies committing to net-zero emissions by 2030
                or 2050. Supply chain transparency and ethical sourcing are also critical components
                of sustainable business models.

                The business case for sustainability is compelling: reduced operational costs through
                energy efficiency, enhanced brand reputation, improved employee engagement, and
                access to sustainable investment capital. As climate change impacts intensify,
                businesses that proactively adapt will be better positioned for long-term success.
                """,
                "metadata": {
                    "industry": "Sustainability",
                    "topic": "Green Business",
                    "keywords": ["sustainability", "ESG", "circular economy", "carbon neutral"],
                    "date": "2024-02-01",
                    "author": "Jenosize Sustainability Team"
                }
            },
            {
                "id": 3,
                "title": "Digital Transformation in Healthcare: Patient-Centric Innovation",
                "content": """
                Healthcare is undergoing a digital revolution driven by technology and changing
                patient expectations. Telemedicine, electronic health records, and AI-powered
                diagnostics are transforming how care is delivered and experienced.

                The COVID-19 pandemic accelerated digital adoption, normalizing virtual consultations
                and remote patient monitoring. Wearable devices and mobile health apps now enable
                continuous health tracking, empowering patients to take proactive roles in their
                wellbeing. AI and machine learning are enhancing diagnostic accuracy and enabling
                personalized treatment plans.

                Looking forward, we anticipate greater integration of genomics and precision medicine,
                expansion of AI-assisted surgery, and blockchain for secure health data management.
                The healthcare organizations that successfully balance technology innovation with
                human-centered care will define the future of medicine.
                """,
                "metadata": {
                    "industry": "Healthcare",
                    "topic": "Digital Health",
                    "keywords": ["telemedicine", "AI diagnostics", "digital health", "patient care"],
                    "date": "2024-02-15",
                    "author": "Jenosize Healthcare Analysts"
                }
            },
            {
                "id": 4,
                "title": "The Remote Work Revolution: Building Distributed Organizations",
                "content": """
                The shift to remote and hybrid work models represents one of the most significant
                workplace transformations in modern history. Organizations are rethinking traditional
                office-centric structures and embracing distributed teams.

                Successful remote work strategies require robust digital infrastructure, clear
                communication protocols, and strong organizational culture. Tools for collaboration,
                project management, and virtual engagement have become essential. Companies are
                also addressing challenges around work-life balance, employee wellbeing, and
                maintaining team cohesion across distances.

                The future of work is increasingly flexible, with employees expecting options for
                where and when they work. Organizations that embrace this flexibility while maintaining
                productivity and culture will have access to global talent pools and improved employee
                satisfaction. Remote work is not just a trend—it's a fundamental shift in how work
                gets done.
                """,
                "metadata": {
                    "industry": "Human Resources",
                    "topic": "Future of Work",
                    "keywords": ["remote work", "hybrid work", "digital collaboration", "workplace culture"],
                    "date": "2024-03-01",
                    "author": "Jenosize Workplace Research"
                }
            },
            {
                "id": 5,
                "title": "Fintech Innovation: Reshaping Financial Services",
                "content": """
                Financial technology is disrupting traditional banking and financial services.
                From mobile payments to decentralized finance, technology is making financial
                services more accessible, efficient, and customer-centric.

                Key innovations include blockchain and cryptocurrencies, which enable peer-to-peer
                transactions without intermediaries. AI-powered robo-advisors are democratizing
                investment management. Open banking APIs allow third-party developers to build
                innovative financial applications. Digital wallets and contactless payments are
                becoming the norm.

                The future of finance will be increasingly embedded, invisible, and personalized.
                Embedded finance will integrate financial services into non-financial platforms.
                Central bank digital currencies may reshape monetary systems. Financial institutions
                that embrace innovation while maintaining security and trust will thrive in this
                new landscape.
                """,
                "metadata": {
                    "industry": "Finance",
                    "topic": "Fintech",
                    "keywords": ["fintech", "blockchain", "digital payments", "open banking"],
                    "date": "2024-03-15",
                    "author": "Jenosize Finance Team"
                }
            }
        ]

        self.print_status(f"Prepared {len(sample_articles)} sample articles", "success")
        return sample_articles

    def create_simple_embeddings(self, text: str) -> List[float]:
        """
        Create simple embeddings for demonstration.
        In production, this should use actual embedding models (OpenAI, etc.)
        """
        # For demo purposes, create simple hash-based embeddings
        # In production, replace with actual embedding API calls
        import hashlib

        # Create a deterministic but distributed embedding
        hash_bytes = hashlib.sha256(text.encode()).digest()
        embedding = []

        for i in range(self.embedding_dim):
            # Use rolling hash to generate values
            byte_idx = i % len(hash_bytes)
            value = (hash_bytes[byte_idx] / 255.0) * 2 - 1  # Normalize to [-1, 1]
            embedding.append(value)

        # Normalize the vector
        norm = sum(x*x for x in embedding) ** 0.5
        embedding = [x / norm for x in embedding]

        return embedding

    def insert_sample_data(self, articles: List[Dict[str, Any]]) -> bool:
        """Insert sample articles into Qdrant"""
        self.print_header("4. Inserting Sample Data")

        try:
            points = []

            for article in articles:
                # Create embedding from title and content
                text_for_embedding = f"{article['title']} {article['content']}"
                embedding = self.create_simple_embeddings(text_for_embedding)

                # Create point
                point = PointStruct(
                    id=article['id'],
                    vector=embedding,
                    payload={
                        "title": article['title'],
                        "content": article['content'],
                        **article['metadata']
                    }
                )
                points.append(point)

                self.print_status(
                    f"Prepared: {article['title'][:60]}...",
                    "info"
                )

            # Insert all points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            self.print_status(
                f"Inserted {len(points)} articles into collection",
                "success"
            )
            return True

        except Exception as e:
            self.print_status(f"Failed to insert data: {e}", "error")
            return False

    def verify_data(self) -> bool:
        """Verify inserted data"""
        self.print_header("5. Verifying Data")

        try:
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)

            self.print_status(
                f"Collection: {collection_info.name}",
                "info"
            )
            self.print_status(
                f"Points count: {collection_info.points_count}",
                "success"
            )
            self.print_status(
                f"Vector size: {collection_info.config.params.vectors.size}",
                "info"
            )

            # Test search
            test_query = self.create_simple_embeddings("artificial intelligence future")
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=test_query,
                limit=3
            )

            self.print_status(
                f"Test search returned {len(search_results)} results",
                "success"
            )

            for i, result in enumerate(search_results, 1):
                self.print_status(
                    f"  {i}. {result.payload.get('title', 'N/A')[:60]}... (score: {result.score:.3f})",
                    "info"
                )

            return True

        except Exception as e:
            self.print_status(f"Verification failed: {e}", "error")
            return False

    def run_initialization(self) -> bool:
        """Run complete initialization process"""
        print(f"{Colors.BOLD}Jenosize AI Content Generator - Qdrant Initialization{Colors.END}\n")

        steps = [
            ("Connect to Qdrant", self.connect_to_qdrant),
            ("Create Collection", self.create_collection),
            ("Insert Sample Data", lambda: self.insert_sample_data(self.get_sample_articles())),
            ("Verify Data", self.verify_data),
        ]

        for step_name, step_func in steps:
            try:
                if not step_func():
                    self.print_status(
                        f"Initialization failed at: {step_name}",
                        "error"
                    )
                    return False
            except Exception as e:
                self.print_status(
                    f"Exception in {step_name}: {str(e)}",
                    "error"
                )
                return False

        self.print_header("Initialization Complete")
        self.print_status(
            "Qdrant database is ready for use!",
            "success"
        )

        print(f"\nNext steps:")
        print(f"  1. Test backend API: python tests/scripts/test_backend_api.py")
        print(f"  2. Run E2E tests: python tests/scripts/test_e2e.py")
        print(f"  3. Access Qdrant dashboard: {self.qdrant_url}/dashboard")

        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Initialize Qdrant Database")
    parser.add_argument(
        "--url",
        default="http://localhost:6333",
        help="Qdrant URL (default: http://localhost:6333)"
    )
    parser.add_argument(
        "--collection",
        default="jenosize_articles",
        help="Collection name (default: jenosize_articles)"
    )

    args = parser.parse_args()

    initializer = QdrantInitializer(
        qdrant_url=args.url,
        collection_name=args.collection
    )

    success = initializer.run_initialization()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
