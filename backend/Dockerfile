# Optimized Dockerfile for Railway deployment
# Build context is backend/ directory when Root Directory is set to "backend"

FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies first (cached layer)
RUN poetry install --only main --no-root

# Copy application code
COPY app ./app

# Install the app package in the virtualenv
RUN poetry install --only-root

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/samples /app/data/generated /app/logs && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Run the application with Railway's dynamic PORT
# Note: Railway handles healthchecks via railway.json configuration
# Use python -m to avoid PATH issues with uvicorn binary
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
