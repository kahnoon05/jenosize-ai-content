#!/bin/bash
# Backend Startup Script
# Starts the FastAPI server with appropriate settings based on environment

set -e

echo "=========================================="
echo "Jenosize AI Backend - Startup"
echo "=========================================="

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.template to .env and configure your API keys."
    exit 1
fi

# Load environment variables
export $(grep -v '^#' ../.env | xargs)

echo "Environment: ${ENVIRONMENT:-development}"
echo "Port: ${BACKEND_PORT:-8000}"
echo ""

# Check if running in Docker
if [ -f "/.dockerenv" ]; then
    echo "Running in Docker container"
    RELOAD_FLAG=""
else
    echo "Running locally"
    RELOAD_FLAG="--reload"
fi

# Start Uvicorn
echo "Starting FastAPI server..."
echo ""

exec uvicorn app.main:app \
    --host ${BACKEND_HOST:-0.0.0.0} \
    --port ${BACKEND_PORT:-8000} \
    --log-level ${LOG_LEVEL:-info} \
    $RELOAD_FLAG
