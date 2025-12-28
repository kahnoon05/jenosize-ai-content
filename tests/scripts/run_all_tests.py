"""
Master Test Runner Script
=========================
Runs all tests in sequence and generates comprehensive report.

Author: Jenosize AI Team
Date: 2025-12-23
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_banner(text: str, color=Colors.CYAN):
    """Print a formatted banner"""
    width = 70
    print(f"\n{color}{Colors.BOLD}{'='*width}{Colors.END}")
    print(f"{color}{Colors.BOLD}{text.center(width)}{Colors.END}")
    print(f"{color}{Colors.BOLD}{'='*width}{Colors.END}\n")


def print_step(step_num: int, title: str, description: str):
    """Print step header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Step {step_num}: {title}{Colors.END}")
    print(f"{Colors.BLUE}{description}{Colors.END}\n")


def run_test_script(script_name: str, timeout: int = 300) -> tuple:
    """
    Run a test script and return success status and output

    Args:
        script_name: Name of the Python script to run
        timeout: Timeout in seconds

    Returns:
        (success: bool, output: str, duration: float)
    """
    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        return False, f"Script not found: {script_path}", 0

    print(f"{Colors.YELLOW}Running {script_name}...{Colors.END}")

    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        duration = time.time() - start_time

        success = result.returncode == 0
        output = result.stdout if result.stdout else result.stderr

        return success, output, duration

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return False, f"Timeout after {timeout} seconds", duration
    except Exception as e:
        duration = time.time() - start_time
        return False, str(e), duration


def check_docker_services() -> bool:
    """Check if Docker services are running"""
    print_step(0, "Pre-Flight Check", "Verifying Docker services are running")

    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"{Colors.RED}Docker Compose is not running{Colors.END}")
            print(f"\nPlease start services first:")
            print(f"  docker compose up -d")
            return False

        # Simple check: if we get output, services exist
        if result.stdout:
            print(f"{Colors.GREEN}Docker services detected{Colors.END}")
            return True
        else:
            print(f"{Colors.YELLOW}No Docker services found{Colors.END}")
            print(f"\nPlease start services:")
            print(f"  docker compose up -d")
            return False

    except FileNotFoundError:
        print(f"{Colors.RED}Docker not found. Please install Docker.{Colors.END}")
        return False
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}Timeout checking Docker services{Colors.END}")
        return False


def main():
    """Main test execution"""
    print_banner("JENOSIZE AI CONTENT GENERATOR", Colors.MAGENTA)
    print_banner("COMPREHENSIVE TEST SUITE", Colors.CYAN)

    print(f"{Colors.BOLD}Test Suite Version:{Colors.END} 1.0")
    print(f"{Colors.BOLD}Start Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}Project:{Colors.END} Trend and Future Ideas Article Generator\n")

    # Track results
    test_results = []
    start_time = time.time()

    # Step 1: Docker Setup Verification
    print_step(
        1,
        "Docker Setup Verification",
        "Validating Docker configuration and environment"
    )

    success, output, duration = run_test_script("verify_docker_setup.py", timeout=60)
    test_results.append({
        "name": "Docker Setup Verification",
        "success": success,
        "duration": duration,
        "critical": True
    })

    if not success:
        print(f"\n{Colors.RED}{Colors.BOLD}Critical Error: Docker setup verification failed{Colors.END}")
        print(f"\n{output}")
        print(f"\nPlease fix the issues above before continuing.")
        return 1

    print(f"{Colors.GREEN}✓ Docker setup verified (took {duration:.1f}s){Colors.END}")
    time.sleep(2)

    # Check if services are running
    if not check_docker_services():
        print(f"\n{Colors.YELLOW}Starting Docker services...{Colors.END}")
        try:
            subprocess.run(["docker", "compose", "up", "-d"], check=True, timeout=120)
            print(f"{Colors.GREEN}Services started. Waiting for initialization...{Colors.END}")
            time.sleep(30)  # Wait for services to initialize
        except Exception as e:
            print(f"{Colors.RED}Failed to start services: {e}{Colors.END}")
            return 1

    # Step 2: Initialize Qdrant Database
    print_step(
        2,
        "Qdrant Database Initialization",
        "Populating vector database with sample articles"
    )

    success, output, duration = run_test_script("initialize_qdrant.py", timeout=120)
    test_results.append({
        "name": "Qdrant Initialization",
        "success": success,
        "duration": duration,
        "critical": True
    })

    if not success:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Warning: Qdrant initialization had issues{Colors.END}")
        print(f"\nContinuing with tests, but RAG functionality may be limited.")
    else:
        print(f"{Colors.GREEN}✓ Qdrant initialized (took {duration:.1f}s){Colors.END}")

    time.sleep(2)

    # Step 3: Backend API Testing
    print_step(
        3,
        "Backend API Testing",
        "Testing all FastAPI endpoints and functionality"
    )

    success, output, duration = run_test_script("test_backend_api.py", timeout=300)
    test_results.append({
        "name": "Backend API Tests",
        "success": success,
        "duration": duration,
        "critical": True
    })

    if not success:
        print(f"\n{Colors.RED}{Colors.BOLD}Critical Error: Backend API tests failed{Colors.END}")
        print(f"\nThe backend is not functioning correctly.")
        print(f"Review the output above for details.")
    else:
        print(f"{Colors.GREEN}✓ Backend API tests passed (took {duration:.1f}s){Colors.END}")

    time.sleep(2)

    # Step 4: End-to-End Testing
    print_step(
        4,
        "End-to-End Testing",
        "Complete system integration and RAG pipeline testing"
    )

    print(f"{Colors.YELLOW}This may take several minutes (multiple article generations)...{Colors.END}\n")

    success, output, duration = run_test_script("test_e2e.py", timeout=900)  # 15 min timeout
    test_results.append({
        "name": "End-to-End Tests",
        "success": success,
        "duration": duration,
        "critical": False
    })

    if not success:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Warning: Some E2E tests failed{Colors.END}")
        print(f"\nThis may indicate issues with content quality or performance.")
    else:
        print(f"{Colors.GREEN}✓ End-to-end tests passed (took {duration:.1f}s){Colors.END}")

    # Generate Summary Report
    total_duration = time.time() - start_time
    print_banner("TEST EXECUTION SUMMARY", Colors.MAGENTA)

    print(f"{Colors.BOLD}Total Duration:{Colors.END} {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)\n")

    print(f"{Colors.BOLD}Test Results:{Colors.END}")
    print(f"{'='*70}")
    print(f"{'Test Suite':<40} {'Status':<15} {'Duration':<15}")
    print(f"{'='*70}")

    critical_failures = 0
    total_tests = len(test_results)
    passed_tests = 0

    for result in test_results:
        status_color = Colors.GREEN if result['success'] else Colors.RED
        status_text = f"{status_color}{'PASS' if result['success'] else 'FAIL'}{Colors.END}"
        critical = " (CRITICAL)" if result['critical'] else ""

        print(f"{result['name']:<40} {status_text:<24} {result['duration']:>6.1f}s{critical}")

        if result['success']:
            passed_tests += 1
        elif result['critical']:
            critical_failures += 1

    print(f"{'='*70}\n")

    # Final Assessment
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"{Colors.BOLD}Summary:{Colors.END}")
    print(f"  Tests Passed: {Colors.GREEN}{passed_tests}/{total_tests}{Colors.END}")
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"  Critical Failures: {Colors.RED}{critical_failures}{Colors.END}\n")

    # Final Status
    if critical_failures > 0:
        print_banner("TESTS FAILED - CRITICAL ISSUES", Colors.RED)
        print(f"{Colors.RED}The system has critical failures that must be fixed.{Colors.END}")
        print(f"\nPlease review the test output above and:")
        print(f"  1. Check service logs: docker compose logs")
        print(f"  2. Verify environment variables in .env")
        print(f"  3. Ensure API keys are valid")
        print(f"  4. Review TESTING_GUIDE.md for troubleshooting\n")
        return 1

    elif success_rate >= 80:
        print_banner("ALL TESTS PASSED", Colors.GREEN)
        print(f"{Colors.GREEN}{Colors.BOLD}The system is ready for production evaluation!{Colors.END}\n")
        print(f"Next Steps:")
        print(f"  1. Review E2E test report: tests/e2e_test_report.txt")
        print(f"  2. Perform manual frontend testing: http://localhost:3000")
        print(f"  3. Prepare final documentation and assignment report")
        print(f"  4. Package for submission\n")

        print(f"{Colors.CYAN}Frontend URL:{Colors.END} http://localhost:3000")
        print(f"{Colors.CYAN}Backend API:{Colors.END} http://localhost:8000/docs")
        print(f"{Colors.CYAN}Qdrant Dashboard:{Colors.END} http://localhost:6333/dashboard\n")
        return 0

    else:
        print_banner("TESTS COMPLETED WITH WARNINGS", Colors.YELLOW)
        print(f"{Colors.YELLOW}Some non-critical tests failed.{Colors.END}")
        print(f"\nThe system is functional but may need improvements.")
        print(f"Review the test output and consider fixing issues before final submission.\n")
        return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        sys.exit(1)
