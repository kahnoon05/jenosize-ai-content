"""
Jenosize Ideas Article Scraper & Data Pipeline
==============================================

This script scrapes articles from Jenosize Ideas website and builds a dataset
for fine-tuning language models. It implements the Data Engineering requirement
by creating a robust pipeline that handles data extraction, cleaning, and preprocessing.

Features:
- Web scraping with retry logic
- Data cleaning and validation
- Topic categorization (F/U/T/U/R/E framework)
- Export to fine-tuning formats (JSONL, CSV, JSON)
- Synthetic data generation based on Jenosize style
"""

import json
import csv
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup
import hashlib


@dataclass
class Article:
    """Structured article data model"""
    title: str
    topic: str  # F/U/T/U/R/E category
    industry: str
    content: str
    keywords: List[str]
    meta_description: str
    url: Optional[str] = None
    published_date: Optional[str] = None
    word_count: int = 0

    def __post_init__(self):
        """Calculate word count after initialization"""
        if not self.word_count:
            self.word_count = len(self.content.split())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def to_finetuning_format(self) -> Dict:
        """
        Convert to OpenAI fine-tuning format (JSONL)
        System prompt -> User prompt -> Assistant response
        """
        system_prompt = (
            "You are a Jenosize content writer specializing in trend analysis "
            "and future ideas for businesses. Write insightful, engaging articles "
            "that help businesses understand and prepare for future trends."
        )

        user_prompt = (
            f"Write a {self.topic} article about {self.industry} trends. "
            f"Focus on: {', '.join(self.keywords[:3])}. "
            f"Target word count: {self.word_count} words."
        )

        assistant_response = f"# {self.title}\n\n{self.content}"

        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant_response}
            ]
        }


class JenosizeScraper:
    """
    Web scraper for Jenosize Ideas articles with robust error handling
    """

    BASE_URL = "https://www.jenosize.com/en/ideas"

    # F/U/T/U/R/E Topic Mapping
    TOPICS = {
        "F": {"name": "Futurist", "slug": "futurist"},
        "U1": {"name": "Understand People & Consumer", "slug": "understand-people-consumer"},
        "T": {"name": "Transformation & Technology", "slug": "transformation-technology"},
        "U2": {"name": "Utility for Our World", "slug": "utility-world"},
        "R": {"name": "Real-time Marketing", "slug": "realtime-marketing"},
        "E": {"name": "Experience the New World", "slug": "experience-new-world"}
    }

    def __init__(self, max_retries: int = 3, delay: int = 2):
        """
        Initialize scraper with retry configuration

        Args:
            max_retries: Maximum retry attempts for failed requests
            delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_with_retry(self, url: str) -> Optional[str]:
        """
        Fetch URL with retry logic

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    print(f"❌ URL not found: {url}")
                    return None
                else:
                    print(f"⚠️  Status {response.status_code} for {url}, retrying...")
            except requests.RequestException as e:
                print(f"⚠️  Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")

            if attempt < self.max_retries - 1:
                time.sleep(self.delay * (attempt + 1))  # Exponential backoff

        return None

    def scrape_article_list(self, topic_slug: str, limit: int = 4) -> List[str]:
        """
        Scrape article URLs from a topic page

        Args:
            topic_slug: Topic slug (e.g., 'futurist')
            limit: Maximum number of articles to scrape

        Returns:
            List of article URLs
        """
        url = f"{self.BASE_URL}/{topic_slug}"
        html = self.fetch_with_retry(url)

        if not html:
            print(f"⚠️  Could not fetch topic page: {topic_slug}")
            return []

        soup = BeautifulSoup(html, 'html.parser')
        article_urls = []

        # Try multiple selectors to find article links
        selectors = [
            'a[href*="/ideas/"]',
            '.article-link',
            '.post-link',
            'article a'
        ]

        for selector in selectors:
            links = soup.select(selector)
            for link in links[:limit]:
                href = link.get('href')
                if href and '/ideas/' in href and href not in article_urls:
                    if href.startswith('/'):
                        href = f"https://www.jenosize.com{href}"
                    article_urls.append(href)
                    if len(article_urls) >= limit:
                        break
            if article_urls:
                break

        return article_urls[:limit]

    def scrape_article_content(self, url: str) -> Optional[Dict]:
        """
        Scrape content from an article page

        Args:
            url: Article URL

        Returns:
            Article data dictionary or None
        """
        html = self.fetch_with_retry(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # Extract title
        title = None
        for selector in ['h1', '.article-title', '.post-title', 'title']:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break

        # Extract content
        content = ""
        for selector in ['article', '.article-content', '.post-content', 'main']:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove scripts and styles
                for elem in content_elem(['script', 'style', 'nav', 'footer']):
                    elem.decompose()
                content = content_elem.get_text(separator='\n').strip()
                break

        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_desc = meta_tag.get('content', '')

        if title and content and len(content) > 500:  # Minimum content length
            return {
                'title': title,
                'content': self._clean_content(content),
                'meta_description': meta_desc,
                'url': url
            }

        return None

    def _clean_content(self, content: str) -> str:
        """
        Clean and normalize article content

        Args:
            content: Raw content

        Returns:
            Cleaned content
        """
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)

        # Remove special characters but keep punctuation
        content = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'\n]', '', content)

        return content.strip()


class JenosizeDataPipeline:
    """
    Complete data pipeline for Jenosize article dataset creation
    Handles scraping, synthetic generation, cleaning, and export
    """

    def __init__(self, output_dir: str = "./data/finetuning"):
        """
        Initialize data pipeline

        Args:
            output_dir: Directory to save processed data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scraper = JenosizeScraper()
        self.articles: List[Article] = []

    def scrape_all_topics(self, articles_per_topic: int = 4) -> int:
        """
        Scrape articles from all F/U/T/U/R/E topics

        Args:
            articles_per_topic: Number of articles to scrape per topic

        Returns:
            Number of successfully scraped articles
        """
        print("\n🔍 Starting web scraping from Jenosize Ideas...")
        print("=" * 60)

        scraped_count = 0

        for topic_key, topic_info in self.scraper.TOPICS.items():
            topic_name = topic_info['name']
            topic_slug = topic_info['slug']

            print(f"\n📚 Scraping topic: {topic_name}")
            print(f"   URL: {self.scraper.BASE_URL}/{topic_slug}")

            # Get article URLs
            article_urls = self.scraper.scrape_article_list(topic_slug, articles_per_topic)

            if not article_urls:
                print(f"   ⚠️  No articles found, will use synthetic data")
                continue

            # Scrape each article
            for i, url in enumerate(article_urls, 1):
                print(f"   [{i}/{len(article_urls)}] Scraping: {url}")
                article_data = self.scraper.scrape_article_content(url)

                if article_data:
                    # Create Article object
                    article = Article(
                        title=article_data['title'],
                        topic=topic_name,
                        industry=self._infer_industry(article_data['content']),
                        content=article_data['content'],
                        keywords=self._extract_keywords(article_data['content']),
                        meta_description=article_data['meta_description'],
                        url=article_data['url'],
                        published_date=datetime.now().isoformat()
                    )
                    self.articles.append(article)
                    scraped_count += 1
                    print(f"   ✅ Successfully scraped ({len(article.content.split())} words)")
                else:
                    print(f"   ❌ Failed to extract content")

                time.sleep(1)  # Be respectful to the server

        print(f"\n{'=' * 60}")
        print(f"✅ Scraping complete: {scraped_count} articles scraped")
        return scraped_count

    def generate_synthetic_articles(self, count_per_topic: int = 4):
        """
        Generate synthetic Jenosize-style articles to supplement scraped data

        Args:
            count_per_topic: Number of synthetic articles per topic
        """
        print(f"\n🤖 Generating {count_per_topic} synthetic articles per topic...")
        print("=" * 60)

        templates = self._load_article_templates()
        generated_count = 0

        for topic_key, topic_info in self.scraper.TOPICS.items():
            topic_name = topic_info['name']

            for i in range(count_per_topic):
                template = templates[i % len(templates)]
                article = self._generate_from_template(template, topic_name)
                self.articles.append(article)
                generated_count += 1
                print(f"   ✅ Generated: {article.title}")

        print(f"\n{'=' * 60}")
        print(f"✅ Generation complete: {generated_count} synthetic articles created")

    def _load_article_templates(self) -> List[Dict]:
        """Load article templates for synthetic generation"""
        # Load existing sample articles as templates
        sample_file = Path(__file__).parent.parent / "data" / "samples" / "sample_articles.json"

        if sample_file.exists():
            with open(sample_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Fallback templates
        return [
            {
                "title": "Future of Digital Transformation",
                "industry": "Technology",
                "content": "Digital transformation continues to reshape business landscapes...",
                "keywords": ["digital transformation", "technology", "innovation"]
            }
        ]

    def _generate_from_template(self, template: Dict, topic: str) -> Article:
        """Generate article from template"""
        # Customize template based on topic
        title_variations = {
            "Futurist": f"The Future of {template.get('industry', 'Business')}: ",
            "Understand People & Consumer": f"Understanding Consumer Behavior in {template.get('industry', 'Business')}: ",
            "Transformation & Technology": f"Digital Transformation in {template.get('industry', 'Business')}: ",
            "Utility for Our World": f"Sustainable Solutions for {template.get('industry', 'Business')}: ",
            "Real-time Marketing": f"Real-time Marketing Strategies in {template.get('industry', 'Business')}: ",
            "Experience the New World": f"New Experiences in {template.get('industry', 'Business')}: "
        }

        prefix = title_variations.get(topic, "")
        base_title = template.get('title', 'Business Trends')

        return Article(
            title=f"{prefix}{base_title}",
            topic=topic,
            industry=template.get('industry', 'General Business'),
            content=template.get('content', ''),
            keywords=template.get('keywords', []),
            meta_description=template.get('meta_description', ''),
            published_date=datetime.now().isoformat()
        )

    def _infer_industry(self, content: str) -> str:
        """Infer industry from content keywords"""
        industry_keywords = {
            'Technology': ['AI', 'software', 'digital', 'tech', 'innovation', 'data'],
            'Retail': ['retail', 'customer', 'shopping', 'commerce', 'store'],
            'Finance': ['finance', 'banking', 'investment', 'payment', 'fintech'],
            'Healthcare': ['health', 'medical', 'patient', 'healthcare', 'wellness'],
            'Manufacturing': ['manufacturing', 'production', 'supply chain', 'factory'],
            'Marketing': ['marketing', 'advertising', 'brand', 'campaign', 'social media']
        }

        content_lower = content.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return industry

        return 'General Business'

    def _extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction (in production, use NLP libraries)
        words = re.findall(r'\b[a-z]{4,}\b', content.lower())
        word_freq = {}

        # Common stop words to exclude
        stop_words = {'that', 'this', 'with', 'from', 'have', 'will', 'been', 'were', 'their'}

        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_keywords[:max_keywords]]

    def clean_and_validate(self) -> int:
        """
        Clean and validate all articles

        Returns:
            Number of invalid articles removed
        """
        print("\n🧹 Cleaning and validating dataset...")
        print("=" * 60)

        initial_count = len(self.articles)
        valid_articles = []

        for article in self.articles:
            # Validation rules
            if (article.title and
                len(article.title) > 10 and
                article.content and
                len(article.content) > 500 and
                article.word_count >= 100 and
                article.keywords):

                valid_articles.append(article)
            else:
                print(f"   ❌ Removed invalid article: {article.title[:50]}...")

        self.articles = valid_articles
        removed = initial_count - len(valid_articles)

        print(f"\n✅ Validation complete")
        print(f"   Valid articles: {len(valid_articles)}")
        print(f"   Removed: {removed}")
        return removed

    def export_to_jsonl(self, filename: str = "finetuning_dataset.jsonl"):
        """Export dataset to JSONL format for OpenAI fine-tuning"""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            for article in self.articles:
                json_line = json.dumps(article.to_finetuning_format(), ensure_ascii=False)
                f.write(json_line + '\n')

        print(f"✅ Exported to JSONL: {output_path}")
        return output_path

    def export_to_csv(self, filename: str = "articles_dataset.csv"):
        """Export dataset to CSV format"""
        output_path = self.output_dir / filename

        if not self.articles:
            print("⚠️  No articles to export")
            return

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['title', 'topic', 'industry', 'content', 'keywords',
                         'meta_description', 'url', 'published_date', 'word_count']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for article in self.articles:
                row = article.to_dict()
                row['keywords'] = ', '.join(row['keywords'])
                writer.writerow(row)

        print(f"✅ Exported to CSV: {output_path}")
        return output_path

    def export_to_json(self, filename: str = "articles_dataset.json"):
        """Export dataset to JSON format"""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            data = [article.to_dict() for article in self.articles]
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported to JSON: {output_path}")
        return output_path

    def generate_statistics(self):
        """Generate and display dataset statistics"""
        if not self.articles:
            print("⚠️  No articles in dataset")
            return

        print("\n📊 Dataset Statistics")
        print("=" * 60)
        print(f"Total articles: {len(self.articles)}")
        print(f"Average word count: {sum(a.word_count for a in self.articles) / len(self.articles):.0f}")

        # Articles by topic
        print("\n📚 Articles by Topic:")
        topic_counts = {}
        for article in self.articles:
            topic_counts[article.topic] = topic_counts.get(article.topic, 0) + 1

        for topic, count in sorted(topic_counts.items()):
            print(f"   {topic}: {count} articles")

        # Articles by industry
        print("\n🏭 Articles by Industry:")
        industry_counts = {}
        for article in self.articles:
            industry_counts[article.industry] = industry_counts.get(article.industry, 0) + 1

        for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {industry}: {count} articles")

        print("\n" + "=" * 60)


def main():
    """Main execution function"""
    print("\n" + "=" * 60)
    print("🚀 JENOSIZE IDEAS DATA PIPELINE")
    print("=" * 60)
    print("\nThis pipeline will:")
    print("1. Scrape articles from Jenosize Ideas website (F/U/T/U/R/E topics)")
    print("2. Generate synthetic articles to supplement scraped data")
    print("3. Clean and validate all articles")
    print("4. Export to multiple formats (JSONL, CSV, JSON)")
    print("\n" + "=" * 60)

    # Initialize pipeline
    pipeline = JenosizeDataPipeline(output_dir="./data/finetuning")

    # Step 1: Try to scrape real articles
    scraped_count = pipeline.scrape_all_topics(articles_per_topic=4)

    # Step 2: Generate synthetic articles (to ensure we have enough data)
    # Generate 4 per topic if we got less than 2 from scraping per topic
    articles_per_topic_target = 4
    current_per_topic = scraped_count // len(pipeline.scraper.TOPICS) if scraped_count > 0 else 0

    if current_per_topic < articles_per_topic_target:
        synthetic_needed = articles_per_topic_target - current_per_topic
        pipeline.generate_synthetic_articles(count_per_topic=synthetic_needed)

    # Step 3: Clean and validate
    pipeline.clean_and_validate()

    # Step 4: Export to all formats
    print("\n💾 Exporting dataset...")
    print("=" * 60)
    pipeline.export_to_jsonl("jenosize_finetuning.jsonl")
    pipeline.export_to_csv("jenosize_articles.csv")
    pipeline.export_to_json("jenosize_articles.json")

    # Step 5: Display statistics
    pipeline.generate_statistics()

    print("\n✅ Data pipeline execution complete!")
    print("=" * 60)
    print(f"\n📁 Output directory: {pipeline.output_dir.absolute()}")
    print("\nFiles created:")
    print("   - jenosize_finetuning.jsonl  (for OpenAI fine-tuning)")
    print("   - jenosize_articles.csv      (for analysis)")
    print("   - jenosize_articles.json     (for general use)")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
