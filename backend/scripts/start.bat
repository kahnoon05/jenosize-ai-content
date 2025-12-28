@echo off
REM Backend Startup Script for Windows
REM Starts the FastAPI server

echo ==========================================
echo Jenosize AI Backend - Startup
echo ==========================================

REM Check if .env file exists
if not exist "..\\.env" (
    echo ERROR: .env file not found!
    echo Please copy .env.template to .env and configure your API keys.
    exit /b 1
)

echo Starting FastAPI server...
echo.

REM Start Uvicorn
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
