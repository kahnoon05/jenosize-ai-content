"""
Docker Setup Verification Script
=================================
This script verifies that all Docker services are properly configured
and ready for deployment.

Author: Jenosize AI Team
Date: 2025-12-23
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import socket

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DockerSetupVerifier:
    """Verifies Docker setup and configuration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docker_compose_path = project_root / "docker-compose.yml"
        self.env_path = project_root / ".env"
        self.results: List[Tuple[str, bool, str]] = []

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

    def check_docker_installed(self) -> bool:
        """Verify Docker is installed and running"""
        self.print_header("1. Docker Installation Check")

        # Check Docker CLI
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            docker_version = result.stdout.strip()
            self.print_result(
                "Docker CLI installed",
                result.returncode == 0,
                docker_version
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.print_result("Docker CLI installed", False, "Docker not found in PATH")
            return False

        # Check Docker daemon
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.print_result(
                "Docker daemon running",
                result.returncode == 0,
                "Docker is active and accessible"
            )
            if result.returncode != 0:
                self.print_result("Docker daemon", False, result.stderr)
                return False
        except subprocess.TimeoutExpired:
            self.print_result("Docker daemon running", False, "Timeout waiting for Docker daemon")
            return False

        # Check Docker Compose
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            compose_version = result.stdout.strip()
            self.print_result(
                "Docker Compose installed",
                result.returncode == 0,
                compose_version
            )
        except subprocess.TimeoutExpired:
            self.print_result("Docker Compose installed", False, "Timeout checking version")
            return False

        return True

    def check_configuration_files(self) -> bool:
        """Verify all required configuration files exist"""
        self.print_header("2. Configuration Files Check")

        # Check docker-compose.yml
        compose_exists = self.docker_compose_path.exists()
        self.print_result(
            "docker-compose.yml exists",
            compose_exists,
            str(self.docker_compose_path) if compose_exists else "File not found"
        )

        # Check .env file
        env_exists = self.env_path.exists()
        self.print_result(
            ".env file exists",
            env_exists,
            str(self.env_path) if env_exists else "File not found"
        )

        # Check Dockerfiles
        backend_dockerfile = self.project_root / "backend" / "Dockerfile"
        backend_exists = backend_dockerfile.exists()
        self.print_result(
            "Backend Dockerfile exists",
            backend_exists,
            str(backend_dockerfile) if backend_exists else "File not found"
        )

        frontend_dockerfile = self.project_root / "frontend" / "Dockerfile"
        frontend_exists = frontend_dockerfile.exists()
        self.print_result(
            "Frontend Dockerfile exists",
            frontend_exists,
            str(frontend_dockerfile) if frontend_exists else "File not found"
        )

        return compose_exists and env_exists and backend_exists and frontend_exists

    def check_environment_variables(self) -> bool:
        """Verify required environment variables are set"""
        self.print_header("3. Environment Variables Check")

        if not self.env_path.exists():
            self.print_result("Environment file", False, ".env file not found")
            return False

        required_vars = [
            "ANTHROPIC_API_KEY",
            "QDRANT_HOST",
            "QDRANT_PORT",
            "NEXT_PUBLIC_API_URL",
        ]

        # Load .env file
        env_vars = {}
        with open(self.env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

        all_present = True
        for var in required_vars:
            present = var in env_vars and env_vars[var] and env_vars[var] != f"your_{var.lower()}_here"
            self.print_result(
                f"{var} configured",
                present,
                "Set" if present else "Missing or using template value"
            )
            if not present:
                all_present = False

        return all_present

    def check_docker_compose_config(self) -> bool:
        """Verify docker-compose.yml is valid"""
        self.print_header("4. Docker Compose Configuration Check")

        if not self.docker_compose_path.exists():
            self.print_result("docker-compose.yml", False, "File not found")
            return False

        # Parse YAML
        try:
            with open(self.docker_compose_path, 'r') as f:
                compose_config = yaml.safe_load(f)
            self.print_result("docker-compose.yml syntax", True, "Valid YAML")
        except yaml.YAMLError as e:
            self.print_result("docker-compose.yml syntax", False, f"Invalid YAML: {e}")
            return False

        # Check services
        services = compose_config.get('services', {})
        required_services = ['qdrant', 'backend', 'frontend']

        for service in required_services:
            exists = service in services
            self.print_result(
                f"Service '{service}' defined",
                exists,
                "Configured" if exists else "Missing"
            )

        # Check networks
        networks_defined = 'networks' in compose_config
        self.print_result(
            "Networks configured",
            networks_defined,
            "jenosize-network defined" if networks_defined else "Missing"
        )

        # Check volumes
        volumes_defined = 'volumes' in compose_config
        self.print_result(
            "Volumes configured",
            volumes_defined,
            "qdrant_storage defined" if volumes_defined else "Missing"
        )

        return True

    def check_port_availability(self) -> bool:
        """Check if required ports are available"""
        self.print_header("5. Port Availability Check")

        required_ports = [
            (3000, "Frontend"),
            (8000, "Backend API"),
            (6333, "Qdrant REST API"),
            (6334, "Qdrant gRPC API")
        ]

        all_available = True
        for port, service in required_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            available = result != 0  # Port is available if connection fails
            self.print_result(
                f"Port {port} ({service})",
                available,
                "Available" if available else "Already in use - stop existing service"
            )
            if not available:
                all_available = False

        return all_available

    def check_docker_compose_validation(self) -> bool:
        """Validate docker-compose configuration with Docker"""
        self.print_header("6. Docker Compose Validation")

        try:
            os.chdir(self.project_root)
            result = subprocess.run(
                ["docker", "compose", "config"],
                capture_output=True,
                text=True,
                timeout=10
            )

            valid = result.returncode == 0
            self.print_result(
                "docker-compose config validation",
                valid,
                "Configuration is valid" if valid else f"Error: {result.stderr}"
            )
            return valid
        except subprocess.TimeoutExpired:
            self.print_result("docker-compose validation", False, "Timeout during validation")
            return False
        except Exception as e:
            self.print_result("docker-compose validation", False, str(e))
            return False

    def check_project_structure(self) -> bool:
        """Verify project directory structure"""
        self.print_header("7. Project Structure Check")

        required_paths = [
            ("backend/app", "Backend application directory"),
            ("backend/pyproject.toml", "Backend dependencies"),
            ("frontend/app", "Frontend application directory"),
            ("frontend/package.json", "Frontend dependencies"),
            ("data", "Data directory"),
        ]

        all_exist = True
        for path, description in required_paths:
            full_path = self.project_root / path
            exists = full_path.exists()
            self.print_result(
                description,
                exists,
                str(full_path) if exists else "Not found"
            )
            if not exists:
                all_exist = False

        return all_exist

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

    def run_all_checks(self) -> bool:
        """Run all verification checks"""
        print(f"{Colors.BOLD}Jenosize AI Content Generator - Docker Setup Verification{Colors.END}")
        print(f"Project Root: {self.project_root}\n")

        checks = [
            self.check_docker_installed,
            self.check_configuration_files,
            self.check_environment_variables,
            self.check_docker_compose_config,
            self.check_port_availability,
            self.check_docker_compose_validation,
            self.check_project_structure,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.print_result(check.__name__, False, f"Exception: {str(e)}")

        return self.print_summary()


def main():
    """Main entry point"""
    # Get project root (parent of tests directory)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent

    verifier = DockerSetupVerifier(project_root)
    success = verifier.run_all_checks()

    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All checks passed! Ready to start Docker services.{Colors.END}")
        print(f"\nNext steps:")
        print(f"  1. Run: docker compose up -d")
        print(f"  2. Wait for services to start (check: docker compose ps)")
        print(f"  3. Run backend tests: python tests/scripts/test_backend_api.py")
        print(f"  4. Access frontend: http://localhost:3000")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some checks failed. Please fix the issues above before proceeding.{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
