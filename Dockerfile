# Railway Deployment Dockerfile - Optimized for smaller image size
# This Dockerfile is at the root level to work with Railway's default build context

# Builder stage with build dependencies
FROM python:3.11-slim as builder

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

# Install build dependencies (only in builder)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

# Copy dependency files
COPY backend/pyproject.toml backend/poetry.lock* ./

# Install dependencies into .venv
RUN poetry install --only main --no-root

# Production stage - clean slim image without build tools
FROM python:3.11-slim as production

WORKDIR /app

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy backend application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p /app/data/samples /app/data/generated /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Run the application
# Railway sets PORT environment variable, default to 8000 if not set
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
