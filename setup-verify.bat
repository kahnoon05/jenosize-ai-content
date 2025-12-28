@echo off
REM Setup Verification Script for Jenosize AI Content Generation System (Windows)
REM This script verifies that all prerequisites are met before running the system

setlocal enabledelayedexpansion
set FAILED=0

echo ======================================
echo Jenosize AI Setup Verification
echo ======================================
echo.

echo Checking prerequisites...
echo.

REM Check Docker
echo 1. Checking Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%v in ('docker --version') do set DOCKER_VERSION=%%v
    echo [OK] Docker is installed ^(version !DOCKER_VERSION!^)

    REM Check if Docker is running
    docker info >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Docker daemon is running
    ) else (
        echo [FAIL] Docker daemon is not running. Please start Docker Desktop.
        set FAILED=1
    )
) else (
    echo [FAIL] Docker is not installed. Please install Docker Desktop.
    set FAILED=1
)
echo.

REM Check Docker Compose
echo 2. Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=4" %%v in ('docker-compose --version') do set COMPOSE_VERSION=%%v
    echo [OK] Docker Compose is installed ^(version !COMPOSE_VERSION!^)
) else (
    docker compose version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=4" %%v in ('docker compose version') do set COMPOSE_VERSION=%%v
        echo [OK] Docker Compose is installed ^(version !COMPOSE_VERSION!^)
    ) else (
        echo [FAIL] Docker Compose is not installed.
        set FAILED=1
    )
)
echo.

REM Check .env file
echo 3. Checking environment configuration...
if exist ".env" (
    echo [OK] .env file exists

    REM Check for API key
    findstr /C:"ANTHROPIC_API_KEY=sk-ant-" .env >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] ANTHROPIC_API_KEY is configured
    ) else (
        findstr /C:"ANTHROPIC_API_KEY=your_anthropic_api_key_here" .env >nul 2>&1
        if !errorlevel! equ 0 (
            echo [FAIL] ANTHROPIC_API_KEY is not configured ^(still has placeholder value^)
            echo        Please edit .env and add your actual Anthropic API key
            set FAILED=1
        ) else (
            echo [WARN] ANTHROPIC_API_KEY format couldn't be verified
        )
    )
) else (
    echo [FAIL] .env file not found. Please copy .env.template to .env
    set FAILED=1
)
echo.

REM Check project structure
echo 4. Checking project structure...
set DIRS=backend frontend data data\samples data\generated
for %%d in (%DIRS%) do (
    if exist "%%d\" (
        echo [OK] Directory exists: %%d
    ) else (
        echo [FAIL] Missing directory: %%d
        set FAILED=1
    )
)
echo.

set FILES=docker-compose.yml backend\Dockerfile backend\pyproject.toml frontend\Dockerfile frontend\package.json
for %%f in (%FILES%) do (
    if exist "%%f" (
        echo [OK] File exists: %%f
    ) else (
        echo [FAIL] Missing file: %%f
        set FAILED=1
    )
)
echo.

REM Check port availability
echo 5. Checking port availability...
set PORTS=3000 8000 6333
for %%p in (%PORTS%) do (
    netstat -ano | findstr ":%%p.*LISTENING" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [WARN] Port %%p is already in use
    ) else (
        echo [OK] Port %%p is available
    )
)
echo.

REM Summary
echo ======================================
echo Verification Summary
echo ======================================
echo.

if %FAILED% equ 0 (
    echo [SUCCESS] All checks passed! You're ready to build and run the system.
    echo.
    echo Next steps:
    echo   1. docker-compose build
    echo   2. docker-compose up -d
    echo   3. Visit http://localhost:3000
    echo.
    exit /b 0
) else (
    echo [ERROR] Some checks failed. Please fix the issues above before proceeding.
    echo.
    echo Common solutions:
    echo   - Install Docker Desktop: https://docs.docker.com/get-docker/
    echo   - Start Docker Desktop application
    echo   - Copy .env.template to .env and configure API keys
    echo   - Stop services using ports 3000, 8000, or 6333
    echo.
    exit /b 1
)
