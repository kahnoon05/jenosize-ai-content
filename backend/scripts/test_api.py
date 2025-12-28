#!/usr/bin/env python3
"""
API Testing Script

Quick script to test the Jenosize AI Content Generation API endpoints.
Tests health checks, article generation, and various options.
"""

import sys
import asyncio
import json
from typing import Dict, Any

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx")
    sys.exit(1)


API_BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test health check endpoint."""
    print("\n" + "=" * 60)
    print("Testing Health Check...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health Status: {data.get('status')}")
                print(f"  Version: {data.get('version')}")
                print(f"  Environment: {data.get('environment')}")
                print(f"  Services: {data.get('services')}")
                return True
            else:
                print(f"✗ Health check failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def test_supported_options():
    """Test supported options endpoint."""
    print("\n" + "=" * 60)
    print("Testing Supported Options...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/api/v1/supported-options")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Industries: {len(data.get('industries', []))} available")
                print(f"  Examples: {', '.join(data.get('industries', [])[:5])}")
                print(f"✓ Audiences: {len(data.get('audiences', []))} available")
                print(f"  Examples: {', '.join(data.get('audiences', [])[:5])}")
                print(f"✓ Tones: {', '.join(data.get('tones', []))}")
                return True
            else:
                print(f"✗ Failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def test_validate_request():
    """Test request validation endpoint."""
    print("\n" + "=" * 60)
    print("Testing Request Validation...")
    print("=" * 60)

    request_data = {
        "topic": "Future of Artificial Intelligence in Business",
        "industry": "technology",
        "audience": "executives",
        "keywords": ["AI", "automation", "innovation"],
        "target_length": 2000
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/validate-request",
                json=request_data
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Validation successful: {data.get('message')}")
                print(f"  Request data: {data.get('data')}")
                return True
            else:
                print(f"✗ Validation failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def test_article_generation(quick_test: bool = True):
    """Test article generation endpoint."""
    print("\n" + "=" * 60)
    print("Testing Article Generation...")
    print("=" * 60)

    # Use shorter length for quick testing
    request_data = {
        "topic": "The Impact of AI on Modern Business",
        "industry": "technology",
        "audience": "professionals",
        "keywords": ["AI", "business transformation", "innovation"],
        "target_length": 1000 if quick_test else 2000,
        "tone": "professional",
        "include_examples": True,
        "include_statistics": True,
        "generate_seo_metadata": True,
        "use_rag": True
    }

    print("\nRequest Parameters:")
    print(f"  Topic: {request_data['topic']}")
    print(f"  Industry: {request_data['industry']}")
    print(f"  Target Length: {request_data['target_length']} words")
    print(f"  RAG Enabled: {request_data['use_rag']}")
    print("\nGenerating... (this may take 10-20 seconds)")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/generate-article",
                json=request_data
            )
            print(f"\nStatus Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                if data.get("success"):
                    article = data.get("article", {})
                    metadata = article.get("metadata", {})

                    print("\n✓ Article generated successfully!")
                    print(f"\n  Title: {metadata.get('title')}")
                    print(f"  Word Count: {metadata.get('word_count')}")
                    print(f"  Reading Time: {metadata.get('reading_time_minutes')} minutes")
                    print(f"  Keywords: {', '.join(metadata.get('keywords', [])[:5])}")
                    print(f"  RAG Sources: {metadata.get('rag_sources_count')}")
                    print(f"  Generation Time: {data.get('generation_time_seconds')}s")

                    print(f"\n  Meta Description:")
                    print(f"    {metadata.get('meta_description')}")

                    print(f"\n  Content Preview (first 300 chars):")
                    content = article.get("content", "")
                    print(f"    {content[:300]}...")

                    return True
                else:
                    print(f"\n✗ Generation failed: {data.get('error')}")
                    return False

            else:
                print(f"✗ Request failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except httpx.TimeoutException:
            print("✗ Request timed out (article generation takes 10-20s)")
            print("  Try increasing timeout or check if services are running")
            return False
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def test_generation_stats():
    """Test generation statistics endpoint."""
    print("\n" + "=" * 60)
    print("Testing Generation Statistics...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/api/v1/generation-stats")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✓ Statistics retrieved:")

                vector_db = data.get("vector_database", {})
                print(f"\n  Vector Database:")
                print(f"    Articles Indexed: {vector_db.get('points_count', 0)}")
                print(f"    Collection: {vector_db.get('collection_name')}")
                print(f"    Status: {vector_db.get('status')}")

                model_config = data.get("model_configuration", {})
                print(f"\n  Model Configuration:")
                print(f"    Model: {model_config.get('llm_model')}")
                print(f"    Temperature: {model_config.get('temperature')}")
                print(f"    Max Tokens: {model_config.get('max_tokens')}")

                return True
            else:
                print(f"✗ Failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


async def run_all_tests(include_generation: bool = False):
    """Run all API tests."""
    print("\n" + "=" * 60)
    print("JENOSIZE AI CONTENT GENERATION API - TEST SUITE")
    print("=" * 60)

    results = {
        "health_check": False,
        "supported_options": False,
        "validate_request": False,
        "generation_stats": False,
        "article_generation": False,
    }

    # Test 1: Health Check
    results["health_check"] = await test_health_check()

    # Test 2: Supported Options
    results["supported_options"] = await test_supported_options()

    # Test 3: Validate Request
    results["validate_request"] = await test_validate_request()

    # Test 4: Generation Stats
    results["generation_stats"] = await test_generation_stats()

    # Test 5: Article Generation (optional, takes time)
    if include_generation:
        results["article_generation"] = await test_article_generation()
    else:
        print("\n" + "=" * 60)
        print("Skipping Article Generation Test (use --generate to include)")
        print("=" * 60)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL" if test_name in results else "⊘ SKIP"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n✓ All tests passed! API is ready to use.")
        return True
    else:
        print(f"\n⚠ {total_tests - passed_tests} test(s) failed. Check the output above.")
        return False


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Jenosize AI Content Generation API")
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Include article generation test (takes 10-20 seconds)"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    global API_BASE_URL
    API_BASE_URL = args.url

    print(f"Testing API at: {API_BASE_URL}")

    # Check if API is reachable
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(f"{API_BASE_URL}/")
    except Exception as e:
        print(f"\n✗ ERROR: Cannot connect to API at {API_BASE_URL}")
        print(f"  {str(e)}")
        print("\nMake sure the backend is running:")
        print("  docker-compose up -d")
        print("  or")
        print("  poetry run uvicorn app.main:app --reload")
        sys.exit(1)

    # Run tests
    success = await run_all_tests(include_generation=args.generate)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
