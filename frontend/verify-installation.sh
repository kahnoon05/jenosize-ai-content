#!/bin/bash

# Frontend Installation Verification Script
# Checks if all dependencies are installed and configured correctly

set -e

echo "================================================"
echo "Jenosize AI Frontend - Installation Verification"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_node() {
    echo -n "Checking Node.js version... "
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v)
        echo -e "${GREEN}✓${NC} Found: $NODE_VERSION"

        # Extract major version
        MAJOR_VERSION=$(echo $NODE_VERSION | sed 's/v\([0-9]*\).*/\1/')
        if [ "$MAJOR_VERSION" -lt 18 ]; then
            echo -e "${RED}✗${NC} Error: Node.js 18+ required, found v$MAJOR_VERSION"
            exit 1
        fi
    else
        echo -e "${RED}✗${NC} Node.js not found"
        echo "Please install Node.js 18+ from https://nodejs.org"
        exit 1
    fi
}

check_npm() {
    echo -n "Checking npm version... "
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm -v)
        echo -e "${GREEN}✓${NC} Found: v$NPM_VERSION"
    else
        echo -e "${RED}✗${NC} npm not found"
        exit 1
    fi
}

check_dependencies() {
    echo -n "Checking if dependencies are installed... "
    if [ -d "node_modules" ]; then
        echo -e "${GREEN}✓${NC} node_modules exists"
    else
        echo -e "${YELLOW}⚠${NC} node_modules not found"
        echo "Running npm install..."
        npm install
        echo -e "${GREEN}✓${NC} Dependencies installed"
    fi
}

check_env_file() {
    echo -n "Checking .env.local file... "
    if [ -f ".env.local" ]; then
        echo -e "${GREEN}✓${NC} Found"

        # Check required variables
        if grep -q "NEXT_PUBLIC_API_URL" .env.local; then
            API_URL=$(grep "NEXT_PUBLIC_API_URL" .env.local | cut -d '=' -f2)
            echo "  → API URL: $API_URL"
        else
            echo -e "${YELLOW}⚠${NC} NEXT_PUBLIC_API_URL not set"
        fi
    else
        echo -e "${RED}✗${NC} Not found"
        echo "Creating default .env.local file..."
        cat > .env.local << EOF
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_APP_NAME=Jenosize AI Content Generator
NEXT_PUBLIC_APP_DESCRIPTION=Generate high-quality business trend and future ideas articles
EOF
        echo -e "${GREEN}✓${NC} Created .env.local with defaults"
    fi
}

check_backend() {
    echo -n "Checking backend connection... "

    # Get API URL from .env.local
    API_URL=$(grep "NEXT_PUBLIC_API_URL" .env.local | cut -d '=' -f2)

    if command -v curl &> /dev/null; then
        if curl -s -f "$API_URL/health" > /dev/null; then
            echo -e "${GREEN}✓${NC} Backend is running at $API_URL"
        else
            echo -e "${YELLOW}⚠${NC} Backend not responding at $API_URL"
            echo "  Please ensure the backend is running:"
            echo "  cd ../backend && docker-compose up"
        fi
    else
        echo -e "${YELLOW}⚠${NC} curl not found, skipping backend check"
    fi
}

check_typescript() {
    echo -n "Checking TypeScript configuration... "
    if [ -f "tsconfig.json" ]; then
        echo -e "${GREEN}✓${NC} Found"
    else
        echo -e "${RED}✗${NC} tsconfig.json not found"
        exit 1
    fi
}

check_tailwind() {
    echo -n "Checking Tailwind CSS configuration... "
    if [ -f "tailwind.config.js" ]; then
        echo -e "${GREEN}✓${NC} Found"
    else
        echo -e "${RED}✗${NC} tailwind.config.js not found"
        exit 1
    fi
}

check_next_config() {
    echo -n "Checking Next.js configuration... "
    if [ -f "next.config.js" ]; then
        echo -e "${GREEN}✓${NC} Found"
    else
        echo -e "${RED}✗${NC} next.config.js not found"
        exit 1
    fi
}

verify_file_structure() {
    echo ""
    echo "Verifying file structure..."

    REQUIRED_DIRS=(
        "app"
        "components"
        "hooks"
        "lib"
    )

    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "  ${GREEN}✓${NC} $dir/"
        else
            echo -e "  ${RED}✗${NC} $dir/ (missing)"
        fi
    done

    REQUIRED_FILES=(
        "app/layout.tsx"
        "app/page.tsx"
        "app/providers.tsx"
        "app/globals.css"
        "components/ArticleGenerationForm.tsx"
        "components/ArticleDisplay.tsx"
        "lib/api-client.ts"
        "lib/types.ts"
        "lib/validation.ts"
    )

    echo ""
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo -e "  ${GREEN}✓${NC} $file"
        else
            echo -e "  ${RED}✗${NC} $file (missing)"
        fi
    done
}

run_type_check() {
    echo ""
    echo -n "Running TypeScript type check... "
    if npm run type-check &> /dev/null; then
        echo -e "${GREEN}✓${NC} No type errors"
    else
        echo -e "${YELLOW}⚠${NC} Type errors found (run 'npm run type-check' for details)"
    fi
}

# Run all checks
echo "Running installation checks..."
echo ""

check_node
check_npm
check_dependencies
check_env_file
check_typescript
check_tailwind
check_next_config
check_backend

verify_file_structure

run_type_check

# Final summary
echo ""
echo "================================================"
echo -e "${GREEN}✓ Installation verification complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Start development server:"
echo "     npm run dev"
echo ""
echo "  2. Open browser:"
echo "     http://localhost:3000"
echo ""
echo "  3. Ensure backend is running:"
echo "     http://localhost:8000/health"
echo ""
echo "================================================"
