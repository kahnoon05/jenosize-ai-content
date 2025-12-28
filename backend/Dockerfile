# Optimized Multi-stage Dockerfile for Railway deployment
# Build context is backend/ directory when Root Directory is set to "backend"

# ============================================
# Stage 1: Builder - Install dependencies only
# ============================================
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

WORKDIR /build

# Install build dependencies (only needed for compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Copy only dependency files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies only (without the app package yet)
RUN poetry install --only main --no-root

# Copy app code to enable package installation
COPY app ./app

# Now install the app package itself (makes 'app' module importable)
RUN poetry install --only-root

# ============================================
# Stage 2: Production - Minimal runtime image
# ============================================
FROM python:3.11-slim as production

WORKDIR /app

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Copy only the virtual environment from builder (no Poetry, no build tools)
COPY --from=builder /build/.venv /app/.venv

# Copy only application code (not pyproject.toml, poetry.lock, tests, etc.)
COPY app /app/app

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
