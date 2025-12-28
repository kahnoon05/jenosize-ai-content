# Jenosize AI Backend - FastAPI Service

This is the backend service for the Jenosize AI Content Generation System, built with FastAPI, LangChain, and Claude 3.5 Sonnet.

## Features

- **Content Generation API**: RESTful endpoints for article generation
- **LangChain Integration**: Advanced AI workflow orchestration
- **RAG Pipeline**: Retrieval-Augmented Generation with Qdrant
- **Claude 3.5 Sonnet**: State-of-the-art language model
- **Few-Shot Learning**: Jenosize-style content generation
- **Vector Search**: Semantic similarity search for context

## Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API endpoints
│   ├── core/                # Core configuration
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   ├── utils/               # Utilities
│   └── prompts/             # LangChain prompts
├── tests/                   # Tests
├── data/                    # Data storage
├── Dockerfile               # Docker configuration
└── pyproject.toml           # Dependencies
```

## Local Development

### With Docker (Recommended)
```bash
# From project root
docker-compose up backend
```

### Without Docker
```bash
cd backend

# Install dependencies
poetry install

# Set environment variables
export ANTHROPIC_API_KEY=your_key_here
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# Run server
poetry run uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test
poetry run pytest tests/test_content_generator.py -v
```

## Code Quality

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Lint
poetry run flake8

# Type check
poetry run mypy app
```

## Environment Variables

See `.env.template` in project root for all available options.

Required variables:
- `ANTHROPIC_API_KEY`: Claude API key
- `QDRANT_HOST`: Qdrant hostname
- `QDRANT_PORT`: Qdrant port
