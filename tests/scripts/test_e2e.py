"""
End-to-End Testing Script
=========================
Complete end-to-end testing of the RAG pipeline and article generation flow.

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
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


class E2ETester:
    """End-to-end testing of the complete system"""

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.results: List[Tuple[str, bool, str]] = []
        self.session = requests.Session()
        self.generated_articles: List[Dict[str, Any]] = []

    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}\n")

    def print_result(self, test_name: str, passed: bool, message: str = ""):
        """Print test result with color coding"""
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
        print(f"[{status}] {test_name}")
        if message:
            print(f"      {message}")
        self.results.append((test_name, passed, message))

    def test_rag_pipeline(self) -> bool:
        """Test the complete RAG pipeline"""
        self.print_header("1. RAG Pipeline Testing")

        # Test with RAG enabled
        payload_with_rag = {
            "topic": "Future of Sustainable Energy",
            "industry": "Energy & Utilities",
            "target_audience": "Business Leaders",
            "tone": "Professional",
            "keywords": ["sustainability", "renewable energy", "climate"],
            "article_type": "future_prediction",
            "use_rag": True,
            "min_length": 1200,
            "max_length": 2000
        }

        try:
            print(f"{Colors.YELLOW}Testing with RAG enabled...{Colors.END}")

            response = self.session.post(
                f"{self.backend_url}/api/v1/articles/generate",
                json=payload_with_rag,
                timeout=120
            )

            rag_success = response.status_code == 200
            self.print_result(
                "Article generation with RAG",
                rag_success,
                f"Status: {response.status_code}"
            )

            if rag_success:
                article_with_rag = response.json()
                self.generated_articles.append({
                    "type": "with_rag",
                    "data": article_with_rag
                })

                # Check if RAG sources are included
                metadata = article_with_rag.get("metadata", {})
                has_sources = "sources_used" in metadata or "rag_sources" in metadata
                self.print_result(
                    "RAG sources in metadata",
                    has_sources,
                    f"Sources: {metadata.get('sources_used', metadata.get('rag_sources', 'None'))}"
                )

                # Check content quality
                content = article_with_rag.get("content", "")
                content_length = len(content)
                length_ok = content_length >= 1000
                self.print_result(
                    "Content meets length requirement",
                    length_ok,
                    f"Generated {content_length} characters"
                )

            return rag_success

        except requests.exceptions.Timeout:
            self.print_result("RAG pipeline", False, "Request timeout")
            return False
        except Exception as e:
            self.print_result("RAG pipeline", False, str(e))
            return False

    def test_multiple_industries(self) -> bool:
        """Test article generation across different industries"""
        self.print_header("2. Multi-Industry Testing")

        test_cases = [
            {
                "topic": "AI-Powered Customer Service",
                "industry": "Technology",
                "target_audience": "Tech Professionals",
                "tone": "Professional"
            },
            {
                "topic": "Digital Transformation in Banking",
                "industry": "Finance",
                "target_audience": "Financial Executives",
                "tone": "Formal"
            },
            {
                "topic": "Telemedicine Revolution",
                "industry": "Healthcare",
                "target_audience": "Healthcare Professionals",
                "tone": "Professional"
            }
        ]

        success_count = 0

        for i, test_case in enumerate(test_cases, 1):
            try:
                payload = {
                    **test_case,
                    "article_type": "trend_analysis",
                    "use_rag": True,
                    "min_length": 800,
                    "max_length": 1500
                }

                print(f"{Colors.YELLOW}Testing: {test_case['topic']}...{Colors.END}")

                response = self.session.post(
                    f"{self.backend_url}/api/v1/articles/generate",
                    json=payload,
                    timeout=120
                )

                success = response.status_code == 200
                self.print_result(
                    f"Industry test {i}: {test_case['industry']}",
                    success,
                    f"Topic: {test_case['topic']}"
                )

                if success:
                    success_count += 1
                    article = response.json()
                    self.generated_articles.append({
                        "type": f"industry_{test_case['industry']}",
                        "data": article
                    })

                # Add delay to avoid rate limiting
                if i < len(test_cases):
                    time.sleep(2)

            except Exception as e:
                self.print_result(
                    f"Industry test {i}",
                    False,
                    str(e)
                )

        all_passed = success_count == len(test_cases)
        self.print_result(
            "All industry tests passed",
            all_passed,
            f"{success_count}/{len(test_cases)} succeeded"
        )

        return all_passed

    def test_different_article_types(self) -> bool:
        """Test different article types"""
        self.print_header("3. Article Type Variation Testing")

        article_types = [
            ("trend_analysis", "Current Trends in Remote Work"),
            ("future_prediction", "Future of Quantum Computing"),
            ("how_to_guide", "How to Implement AI in Your Business"),
            ("case_study", "Success Story: Digital Transformation")
        ]

        success_count = 0

        for article_type, topic in article_types:
            try:
                payload = {
                    "topic": topic,
                    "industry": "Technology",
                    "target_audience": "Business Leaders",
                    "tone": "Professional",
                    "article_type": article_type,
                    "use_rag": True,
                    "min_length": 800,
                    "max_length": 1500
                }

                print(f"{Colors.YELLOW}Testing article type: {article_type}...{Colors.END}")

                response = self.session.post(
                    f"{self.backend_url}/api/v1/articles/generate",
                    json=payload,
                    timeout=120
                )

                success = response.status_code == 200
                self.print_result(
                    f"Article type: {article_type}",
                    success,
                    f"Topic: {topic}"
                )

                if success:
                    success_count += 1
                    article = response.json()

                    # Verify article type is reflected in metadata
                    metadata = article.get("metadata", {})
                    type_match = metadata.get("article_type") == article_type
                    self.print_result(
                        f"Metadata matches type: {article_type}",
                        type_match,
                        f"Metadata type: {metadata.get('article_type', 'N/A')}"
                    )

                time.sleep(2)

            except Exception as e:
                self.print_result(
                    f"Article type test: {article_type}",
                    False,
                    str(e)
                )

        return success_count >= len(article_types) // 2  # At least 50% success

    def test_content_quality(self) -> bool:
        """Test quality of generated content"""
        self.print_header("4. Content Quality Assessment")

        if not self.generated_articles:
            self.print_result(
                "Content quality assessment",
                False,
                "No articles generated to assess"
            )
            return False

        quality_checks = []

        for i, article_data in enumerate(self.generated_articles[:3], 1):  # Check first 3
            article = article_data["data"]
            content = article.get("content", "")
            title = article.get("title", "")

            # Check 1: Content has proper structure (paragraphs)
            has_paragraphs = content.count('\n\n') >= 3
            quality_checks.append(("Has paragraphs", has_paragraphs))
            self.print_result(
                f"Article {i}: Has structured paragraphs",
                has_paragraphs,
                f"Paragraph breaks: {content.count(chr(10) + chr(10))}"
            )

            # Check 2: Title is meaningful
            title_ok = len(title) > 10 and len(title) < 200
            quality_checks.append(("Title length", title_ok))
            self.print_result(
                f"Article {i}: Title is appropriate length",
                title_ok,
                f"Title: {title[:60]}..."
            )

            # Check 3: Content includes keywords
            metadata = article.get("metadata", {})
            keywords = metadata.get("keywords", [])
            if keywords:
                keywords_used = sum(1 for kw in keywords if kw.lower() in content.lower())
                keywords_ok = keywords_used > 0
                quality_checks.append(("Keywords used", keywords_ok))
                self.print_result(
                    f"Article {i}: Keywords present in content",
                    keywords_ok,
                    f"{keywords_used}/{len(keywords)} keywords found"
                )

            # Check 4: No template placeholders
            has_placeholders = any(
                placeholder in content
                for placeholder in ["[INSERT", "[TODO", "XXXX", "{{"]
            )
            no_placeholders = not has_placeholders
            quality_checks.append(("No placeholders", no_placeholders))
            self.print_result(
                f"Article {i}: No template placeholders",
                no_placeholders,
                "Clean content" if no_placeholders else "Contains placeholders"
            )

        # Overall quality score
        passed_checks = sum(1 for _, passed in quality_checks if passed)
        total_checks = len(quality_checks)
        quality_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        quality_ok = quality_score >= 70  # 70% pass rate
        self.print_result(
            "Overall content quality",
            quality_ok,
            f"Quality score: {quality_score:.1f}% ({passed_checks}/{total_checks} checks passed)"
        )

        return quality_ok

    def test_error_recovery(self) -> bool:
        """Test system's error handling and recovery"""
        self.print_header("5. Error Handling & Recovery")

        # Test 1: Invalid industry
        try:
            payload = {
                "topic": "Test Topic",
                "industry": "NonExistentIndustry123",
                "target_audience": "General",
                "tone": "Professional",
                "article_type": "trend_analysis"
            }

            response = self.session.post(
                f"{self.backend_url}/api/v1/articles/generate",
                json=payload,
                timeout=30
            )

            # Should either accept (flexible) or reject gracefully
            handles_invalid = response.status_code in [200, 400, 422]
            self.print_result(
                "Handles invalid industry gracefully",
                handles_invalid,
                f"Status: {response.status_code}"
            )

        except Exception as e:
            self.print_result("Invalid industry test", False, str(e))

        # Test 2: Extreme length requirements
        try:
            payload = {
                "topic": "Test",
                "industry": "Technology",
                "target_audience": "General",
                "tone": "Professional",
                "article_type": "trend_analysis",
                "min_length": 10000,  # Very high
                "max_length": 100
            }

            response = self.session.post(
                f"{self.backend_url}/api/v1/articles/generate",
                json=payload,
                timeout=30
            )

            validates_length = response.status_code in [400, 422]
            self.print_result(
                "Validates conflicting length requirements",
                validates_length,
                f"Status: {response.status_code}"
            )

        except Exception as e:
            self.print_result("Length validation test", False, str(e))

        # Test 3: System recovery after errors
        try:
            # Make a valid request after error tests
            payload = {
                "topic": "Recovery Test",
                "industry": "Technology",
                "target_audience": "General",
                "tone": "Professional",
                "article_type": "trend_analysis",
                "min_length": 500,
                "max_length": 1000
            }

            response = self.session.post(
                f"{self.backend_url}/api/v1/articles/generate",
                json=payload,
                timeout=120
            )

            recovers = response.status_code == 200
            self.print_result(
                "System recovers after errors",
                recovers,
                "Successfully generated article after error tests"
            )

        except Exception as e:
            self.print_result("System recovery test", False, str(e))

        return True

    def test_performance(self) -> bool:
        """Test system performance metrics"""
        self.print_header("6. Performance Testing")

        # Test response time
        try:
            payload = {
                "topic": "Performance Test Article",
                "industry": "Technology",
                "target_audience": "General",
                "tone": "Professional",
                "article_type": "trend_analysis",
                "use_rag": True,
                "min_length": 800,
                "max_length": 1200
            }

            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/api/v1/articles/generate",
                json=payload,
                timeout=120
            )
            end_time = time.time()

            response_time = end_time - start_time

            # Reasonable response time (under 90 seconds for generation)
            performance_ok = response.status_code == 200 and response_time < 90
            self.print_result(
                "Article generation performance",
                performance_ok,
                f"Response time: {response_time:.2f} seconds"
            )

            # Test metadata includes timing info
            if response.status_code == 200:
                data = response.json()
                metadata = data.get("metadata", {})
                has_timing = "generation_time" in metadata or "timestamp" in metadata
                self.print_result(
                    "Metadata includes timing information",
                    has_timing,
                    f"Metadata fields: {list(metadata.keys())}"
                )

            return performance_ok

        except requests.exceptions.Timeout:
            self.print_result(
                "Performance test",
                False,
                "Request exceeded timeout (120s)"
            )
            return False
        except Exception as e:
            self.print_result("Performance test", False, str(e))
            return False

    def generate_test_report(self) -> str:
        """Generate a comprehensive test report"""
        self.print_header("7. Test Report Generation")

        report = []
        report.append("="*70)
        report.append("END-TO-END TEST REPORT")
        report.append("="*70)
        report.append(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Backend URL: {self.backend_url}")
        report.append("")

        # Summary
        total = len(self.results)
        passed = sum(1 for _, p, _ in self.results if p)
        failed = total - passed

        report.append(f"SUMMARY")
        report.append(f"  Total Tests: {total}")
        report.append(f"  Passed: {passed}")
        report.append(f"  Failed: {failed}")
        report.append(f"  Success Rate: {(passed/total*100):.1f}%")
        report.append("")

        # Articles generated
        report.append(f"ARTICLES GENERATED: {len(self.generated_articles)}")
        for i, article_data in enumerate(self.generated_articles, 1):
            article = article_data["data"]
            report.append(f"\n  Article {i} ({article_data['type']}):")
            report.append(f"    Title: {article.get('title', 'N/A')}")
            report.append(f"    Length: {len(article.get('content', ''))} characters")
            metadata = article.get("metadata", {})
            report.append(f"    Industry: {metadata.get('industry', 'N/A')}")
            report.append(f"    Type: {metadata.get('article_type', 'N/A')}")

        report.append("\n" + "="*70)

        report_text = "\n".join(report)

        # Save report
        report_path = Path(__file__).parent.parent / "e2e_test_report.txt"
        report_path.write_text(report_text)

        self.print_result(
            "Test report generated",
            True,
            f"Saved to: {report_path}"
        )

        print(f"\n{report_text}\n")

        return report_text

    def print_summary(self):
        """Print test summary"""
        self.print_header("Final Summary")

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

        return failed == 0

    def run_all_tests(self) -> bool:
        """Run all E2E tests"""
        print(f"{Colors.BOLD}Jenosize AI Content Generator - End-to-End Tests{Colors.END}")
        print(f"Backend URL: {self.backend_url}\n")

        tests = [
            self.test_rag_pipeline,
            self.test_multiple_industries,
            self.test_different_article_types,
            self.test_content_quality,
            self.test_error_recovery,
            self.test_performance,
        ]

        for test in tests:
            try:
                test()
                time.sleep(1)  # Brief pause between test suites
            except Exception as e:
                self.print_result(test.__name__, False, f"Exception: {str(e)}")

        # Generate report
        self.generate_test_report()

        return self.print_summary()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="End-to-End Testing for Jenosize AI")
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Backend API URL (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    tester = E2ETester(backend_url=args.backend_url)
    success = tester.run_all_tests()

    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All E2E tests passed!{Colors.END}")
        print(f"\nThe system is ready for production evaluation.")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some E2E tests failed.{Colors.END}")
        print(f"Review the report above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
