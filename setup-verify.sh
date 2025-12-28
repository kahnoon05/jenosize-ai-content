#!/bin/bash
# Setup Verification Script for Jenosize AI Content Generation System
# This script verifies that all prerequisites are met before running the system

set -e

echo "======================================"
echo "Jenosize AI Setup Verification"
echo "======================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    FAILED=1
}

check_warn() {
    echo -e "${YELLOW}!${NC} $1"
}

FAILED=0

echo "Checking prerequisites..."
echo ""

# Check Docker
echo "1. Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    check_pass "Docker is installed (version $DOCKER_VERSION)"

    # Check if Docker is running
    if docker info &> /dev/null; then
        check_pass "Docker daemon is running"
    else
        check_fail "Docker daemon is not running. Please start Docker Desktop."
    fi
else
    check_fail "Docker is not installed. Please install Docker Desktop."
fi
echo ""

# Check Docker Compose
echo "2. Checking Docker Compose..."
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | awk '{print $4}' | sed 's/,//')
    else
        COMPOSE_VERSION=$(docker compose version --short)
    fi
    check_pass "Docker Compose is installed (version $COMPOSE_VERSION)"
else
    check_fail "Docker Compose is not installed."
fi
echo ""

# Check .env file
echo "3. Checking environment configuration..."
if [ -f ".env" ]; then
    check_pass ".env file exists"

    # Check for API key
    if grep -q "ANTHROPIC_API_KEY=sk-ant-" .env; then
        check_pass "ANTHROPIC_API_KEY is configured"
    elif grep -q "ANTHROPIC_API_KEY=your_anthropic_api_key_here" .env; then
        check_fail "ANTHROPIC_API_KEY is not configured (still has placeholder value)"
        echo "   Please edit .env and add your actual Anthropic API key"
    else
        check_warn "ANTHROPIC_API_KEY format couldn't be verified"
    fi
else
    check_fail ".env file not found. Please copy .env.template to .env"
fi
echo ""

# Check project structure
echo "4. Checking project structure..."
REQUIRED_DIRS=("backend" "frontend" "data" "data/samples" "data/generated")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directory exists: $dir"
    else
        check_fail "Missing directory: $dir"
    fi
done
echo ""

REQUIRED_FILES=("docker-compose.yml" "backend/Dockerfile" "backend/pyproject.toml" "frontend/Dockerfile" "frontend/package.json")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "File exists: $file"
    else
        check_fail "Missing file: $file"
    fi
done
echo ""

# Check port availability
echo "5. Checking port availability..."
PORTS=(3000 8000 6333)
for port in "${PORTS[@]}"; do
    if command -v lsof &> /dev/null; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            check_warn "Port $port is already in use"
        else
            check_pass "Port $port is available"
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -ano | grep ":$port.*LISTEN" > /dev/null 2>&1; then
            check_warn "Port $port is already in use"
        else
            check_pass "Port $port is available"
        fi
    else
        check_warn "Cannot check port $port (no lsof or netstat available)"
    fi
done
echo ""

# Check disk space
echo "6. Checking disk space..."
if command -v df &> /dev/null; then
    AVAILABLE_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_GB" -ge 10 ]; then
        check_pass "Sufficient disk space available (${AVAILABLE_GB}GB free)"
    else
        check_warn "Low disk space (${AVAILABLE_GB}GB free, 10GB recommended)"
    fi
else
    check_warn "Cannot check disk space"
fi
echo ""

# Summary
echo "======================================"
echo "Verification Summary"
echo "======================================"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC} You're ready to build and run the system."
    echo ""
    echo "Next steps:"
    echo "  1. docker-compose build"
    echo "  2. docker-compose up -d"
    echo "  3. Visit http://localhost:3000"
    echo ""
    exit 0
else
    echo -e "${RED}Some checks failed.${NC} Please fix the issues above before proceeding."
    echo ""
    echo "Common solutions:"
    echo "  - Install Docker Desktop: https://docs.docker.com/get-docker/"
    echo "  - Start Docker Desktop application"
    echo "  - Copy .env.template to .env and configure API keys"
    echo "  - Free up disk space (need at least 10GB)"
    echo ""
    exit 1
fi
