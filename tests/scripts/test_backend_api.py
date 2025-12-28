"""
Backend API Testing Script
==========================
Comprehensive testing of all FastAPI backend endpoints.

Author: Jenosize AI Team
Date: 2025-12-23
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List, Tuple
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class BackendAPITester:
    """Tests backend API endpoints"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Tuple[str, bool, str]] = []
        self.session = requests.Session()

    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

    def print_result(self, test_name: str, passed: bool, message: str = ""):
        """Print test result with color coding"""
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
        print(f"[{status}] {test_name}")
        if message:
            print(f"      {message}")
        self.results.append((test_name, passed, message))

    def wait_for_service(self, max_attempts: int = 30, delay: int = 2) -> bool:
        """Wait for backend service to be ready"""
        self.print_header("0. Service Availability Check")

        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    self.print_result(
                        "Backend service available",
                        True,
                        f"Responded after {attempt * delay} seconds"
                    )
                    return True
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                continue

        self.print_result(
            "Backend service available",
            False,
            f"Service did not respond after {max_attempts * delay} seconds"
        )
        return False

    def test_health_endpoint(self) -> bool:
        """Test /health endpoint"""
        self.print_header("1. Health Check Endpoint")

        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)

            # Check status code
            status_ok = response.status_code == 200
            self.print_result(
                "Health endpoint returns 200",
                status_ok,
                f"Status: {response.status_code}"
            )

            # Check response structure
            data = response.json()
            has_status = "status" in data
            self.print_result(
                "Health response has 'status' field",
                has_status,
                f"Response: {json.dumps(data, indent=2)}"
            )

            return status_ok and has_status

        except Exception as e:
            self.print_result("Health endpoint", False, str(e))
            return False

    def test_qdrant_status(self) -> bool:
        """Test /api/v1/qdrant/status endpoint"""
        self.print_header("2. Qdrant Status Endpoint")

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/qdrant/status",
                timeout=10
            )

            status_ok = response.status_code == 200
            self.print_result(
                "Qdrant status endpoint returns 200",
                status_ok,
                f"Status: {response.status_code}"
            )

            data = response.json()

            # Check for connected field
            has_connected = "connected" in data
            self.print_result(
                "Response has 'connected' field",
                has_connected,
                f"Connected: {data.get('connected', 'N/A')}"
            )

            # Check if Qdrant is connected
            is_connected = data.get("connected", False)
            self.print_result(
                "Qdrant is connected",
                is_connected,
                f"Collections: {data.get('collections', [])}"
            )

            return status_ok and has_connected

        except Exception as e:
            self.print_result("Qdrant status endpoint", False, str(e))
            return False

    def test_collection_info(self) -> bool:
        """Test /api/v1/qdrant/collection/{collection_name}/info endpoint"""
        self.print_header("3. Collection Info Endpoint")

        collection_name = "jenosize_articles"

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/qdrant/collection/{collection_name}/info",
                timeout=10
            )

            # Collection might not exist yet, so 200 or 404 is acceptable
            status_ok = response.status_code in [200, 404]
            self.print_result(
                f"Collection info endpoint accessible",
                status_ok,
                f"Status: {response.status_code}"
            )

            if response.status_code == 200:
                data = response.json()
                has_name = "name" in data
                self.print_result(
                    "Collection exists",
                    has_name,
                    f"Vectors: {data.get('vectors_count', 0)}, Points: {data.get('points_count', 0)}"
                )
            else:
                self.print_result(
                    "Collection exists",
                    False,
                    "Collection not yet created (will be created on first use)"
                )

            return status_ok

        except Exception as e:
            self.print_result("Collection info endpoint", False, str(e))
            return False

    def test_generate_article_validation(self) -> bool:
        """Test article generation endpoint with invalid data"""
        self.print_header("4. Article Generation - Input Validation")

        # Test 1: Missing required fields
        try:
            payload = {}
            response = self.session.post(
                f"{self.base_url}/api/v1/articles/generate",
                json=payload,
                timeout=10
            )

            validation_works = response.status_code == 422
            self.print_result(
                "Rejects empty payload",
                validation_works,
                f"Status: {response.status_code}"
            )

        except Exception as e:
            self.print_result("Input validation test", False, str(e))
            return False

        # Test 2: Invalid field values
        try:
            payload = {
                "topic": "",  # Empty topic
                "industry": "Technology",
                "target_audience": "General",
                "tone": "Professional"
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/articles/generate",
                json=payload,
                timeout=10
            )

            validation_works = response.status_code in [400, 422]
            self.print_result(
                "Rejects empty topic",
                validation_works,
                f"Status: {response.status_code}"
            )

        except Exception as e:
            self.print_result("Empty topic validation", False, str(e))

        return True

    def test_generate_article_valid(self) -> bool:
        """Test article generation with valid data"""
        self.print_header("5. Article Generation - Valid Request")

        payload = {
            "topic": "Artificial Intelligence in Healthcare",
            "industry": "Healthcare",
            "target_audience": "Healthcare Professionals",
            "tone": "Professional",
            "keywords": ["AI", "healthcare", "diagnosis", "patient care"],
            "article_type": "trend_analysis",
            "use_rag": True,
            "min_length": 1000,
            "max_length": 2000
        }

        try:
            print(f"{Colors.YELLOW}Generating article (this may take 30-60 seconds)...{Colors.END}")

            response = self.session.post(
                f"{self.base_url}/api/v1/articles/generate",
                json=payload,
                timeout=120  # Longer timeout for generation
            )

            status_ok = response.status_code == 200
            self.print_result(
                "Article generation returns 200",
                status_ok,
                f"Status: {response.status_code}"
            )

            if not status_ok:
                error_detail = response.json().get("detail", "No error details")
                self.print_result(
                    "Article generation error",
                    False,
                    f"Error: {error_detail}"
                )
                return False

            data = response.json()

            # Check response structure
            has_title = "title" in data
            self.print_result(
                "Response has 'title'",
                has_title,
                f"Title: {data.get('title', 'N/A')[:80]}..."
            )

            has_content = "content" in data
            content_length = len(data.get("content", ""))
            self.print_result(
                "Response has 'content'",
                has_content,
                f"Length: {content_length} characters"
            )

            # Check content length meets requirements
            length_ok = content_length >= 800  # Min acceptable length
            self.print_result(
                "Content meets minimum length",
                length_ok,
                f"Generated {content_length} chars (min: 800)"
            )

            # Check for metadata
            has_metadata = "metadata" in data
            self.print_result(
                "Response has 'metadata'",
                has_metadata,
                f"Metadata fields: {list(data.get('metadata', {}).keys())}"
            )

            # Print sample of generated content
            if has_content:
                print(f"\n{Colors.BLUE}Sample of generated content:{Colors.END}")
                print(f"{data['content'][:300]}...\n")

            return status_ok and has_title and has_content and length_ok

        except requests.exceptions.Timeout:
            self.print_result(
                "Article generation",
                False,
                "Request timeout (exceeded 120 seconds)"
            )
            return False
        except Exception as e:
            self.print_result("Article generation", False, str(e))
            return False

    def test_article_parameters_endpoint(self) -> bool:
        """Test /api/v1/articles/parameters endpoint"""
        self.print_header("6. Article Parameters Endpoint")

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/articles/parameters",
                timeout=10
            )

            status_ok = response.status_code == 200
            self.print_result(
                "Parameters endpoint returns 200",
                status_ok,
                f"Status: {response.status_code}"
            )

            data = response.json()

            # Check for required parameter lists
            has_industries = "industries" in data
            self.print_result(
                "Has 'industries' list",
                has_industries,
                f"Count: {len(data.get('industries', []))}"
            )

            has_audiences = "target_audiences" in data
            self.print_result(
                "Has 'target_audiences' list",
                has_audiences,
                f"Count: {len(data.get('target_audiences', []))}"
            )

            has_tones = "tones" in data
            self.print_result(
                "Has 'tones' list",
                has_tones,
                f"Count: {len(data.get('tones', []))}"
            )

            has_types = "article_types" in data
            self.print_result(
                "Has 'article_types' list",
                has_types,
                f"Count: {len(data.get('article_types', []))}"
            )

            return status_ok and has_industries and has_audiences and has_tones

        except Exception as e:
            self.print_result("Parameters endpoint", False, str(e))
            return False

    def test_cors_headers(self) -> bool:
        """Test CORS configuration"""
        self.print_header("7. CORS Configuration")

        try:
            # Test preflight request
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }

            response = self.session.options(
                f"{self.base_url}/api/v1/articles/generate",
                headers=headers,
                timeout=10
            )

            has_cors = "Access-Control-Allow-Origin" in response.headers
            self.print_result(
                "CORS headers present",
                has_cors,
                f"Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}"
            )

            return has_cors

        except Exception as e:
            self.print_result("CORS configuration", False, str(e))
            return False

    def test_error_handling(self) -> bool:
        """Test error handling"""
        self.print_header("8. Error Handling")

        # Test 404 endpoint
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/nonexistent",
                timeout=10
            )

            is_404 = response.status_code == 404
            self.print_result(
                "Returns 404 for invalid endpoint",
                is_404,
                f"Status: {response.status_code}"
            )

        except Exception as e:
            self.print_result("404 error handling", False, str(e))

        # Test malformed JSON
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/articles/generate",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            handles_bad_json = response.status_code in [400, 422]
            self.print_result(
                "Handles malformed JSON",
                handles_bad_json,
                f"Status: {response.status_code}"
            )

        except Exception as e:
            self.print_result("Malformed JSON handling", False, str(e))

        return True

    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")

        total = len(self.results)
        passed = sum(1 for _, p, _ in self.results if p)
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")

        if failed > 0:
            print(f"{Colors.YELLOW}Failed Tests:{Colors.END}")
            for name, passed, message in self.results:
                if not passed:
                    print(f"  - {name}")
                    if message:
                        print(f"    {message}")

        return failed == 0

    def run_all_tests(self) -> bool:
        """Run all API tests"""
        print(f"{Colors.BOLD}Jenosize AI Content Generator - Backend API Tests{Colors.END}")
        print(f"Base URL: {self.base_url}\n")

        # Wait for service to be ready
        if not self.wait_for_service():
            print(f"\n{Colors.RED}Backend service is not available. Please ensure Docker services are running.{Colors.END}")
            print(f"Run: docker compose up -d")
            return False

        # Run all tests
        tests = [
            self.test_health_endpoint,
            self.test_qdrant_status,
            self.test_collection_info,
            self.test_article_parameters_endpoint,
            self.test_generate_article_validation,
            self.test_generate_article_valid,
            self.test_cors_headers,
            self.test_error_handling,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                self.print_result(test.__name__, False, f"Exception: {str(e)}")

        return self.print_summary()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Jenosize Backend API")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Backend API base URL (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    tester = BackendAPITester(base_url=args.url)
    success = tester.run_all_tests()

    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All API tests passed!{Colors.END}")
        print(f"\nNext steps:")
        print(f"  1. Test frontend: python tests/scripts/test_frontend.py")
        print(f"  2. Run E2E tests: python tests/scripts/test_e2e.py")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some tests failed. Please check the errors above.{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
