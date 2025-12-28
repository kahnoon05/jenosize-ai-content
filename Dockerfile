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
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy backend application code with explicit structure
COPY backend/app /app/app
COPY backend/start.sh /app/start.sh

# Make startup script executable and create necessary directories
RUN chmod +x start.sh && \
    mkdir -p /app/data/samples /app/data/generated /app/logs && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Run the application using startup script
CMD ["./start.sh"]
