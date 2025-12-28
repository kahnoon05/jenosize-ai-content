# Optimized Dockerfile for Railway deployment
# Build context is backend/ directory when Root Directory is set to "backend"

FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/code/.venv/bin:$PATH" \
    PYTHONPATH="/code:$PYTHONPATH"

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

# Install dependencies only
RUN poetry install --only main --no-root

# Copy application code
# This creates /code/app/ directory with all the Python modules
COPY app ./app

# Create necessary directories
RUN mkdir -p /code/data/samples /code/data/generated /code/logs && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /code

USER appuser

# Expose port
EXPOSE 8000

# Run uvicorn
# With PYTHONPATH=/code, Python can find 'app' package at /code/app
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
