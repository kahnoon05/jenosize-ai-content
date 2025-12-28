# Backend Quick Start Guide

This guide will help you get the Jenosize AI Content Generation Backend up and running quickly.

## Prerequisites

- Docker and Docker Compose installed
- API Keys:
  - Anthropic API key (Claude) - **REQUIRED**
  - OpenAI API key (for embeddings) - **REQUIRED for RAG**

## Quick Start (Docker - Recommended)

### 1. Set Up Environment Variables

```bash
# From project root
cp .env.template .env

# Edit .env and add your API keys
# REQUIRED:
#   ANTHROPIC_API_KEY=sk-ant-xxxxx
#   OPENAI_API_KEY=sk-xxxxx
```

### 2. Start Services

```bash
# Start all services (Qdrant, Backend, Frontend)
docker-compose up -d

# Check services are running
docker-compose ps
```

Expected output:
```
NAME                    STATUS
jenosize-backend        Up (healthy)
jenosize-qdrant         Up (healthy)
jenosize-frontend       Up (healthy)
```

### 3. Initialize Database

```bash
# Populate Qdrant with sample articles
docker-compose exec backend python scripts/init_database.py

# Verify initialization
docker-compose exec backend python scripts/init_database.py --verify-only
```

### 4. Test the API

```bash
# Check health
curl http://localhost:8000/health

# Test article generation
curl -X POST http://localhost:8000/api/v1/generate-article \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Future of AI in Healthcare",
    "industry": "healthcare",
    "audience": "executives",
    "keywords": ["AI", "healthcare", "innovation"],
    "target_length": 1500
  }'
```

### 5. Access API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Local Development (Without Docker)

### 1. Install Dependencies

```bash
cd backend

# Install Poetry
pip install poetry

# Install dependencies
poetry install
```

### 2. Start Qdrant (Docker)

```bash
# From project root
docker-compose up -d qdrant
```

### 3. Configure Environment

```bash
# Edit .env in project root
# Set:
#   QDRANT_HOST=localhost  (not 'qdrant')
#   QDRANT_PORT=6333
```

### 4. Run Backend

```bash
# From backend directory
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Initialize Database

```bash
poetry run python scripts/init_database.py
```

## Verify Installation

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "v1",
  "environment": "development",
  "services": {
    "qdrant": "connected",
    "langchain": "healthy"
  }
}
```

### 2. Test Generation

Visit http://localhost:8000/docs and try the `/api/v1/generate-article` endpoint with:

```json
{
  "topic": "The Future of Remote Work",
  "industry": "technology",
  "audience": "professionals",
  "keywords": ["remote work", "digital transformation", "collaboration"],
  "target_length": 2000,
  "tone": "professional",
  "include_examples": true,
  "use_rag": true
}
```

You should get a complete article with metadata in 10-20 seconds.

## Common Issues

### Issue: "Failed to connect to Qdrant"

**Solution:**
```bash
# Check Qdrant is running
docker-compose ps qdrant

# Restart Qdrant
docker-compose restart qdrant

# Check logs
docker-compose logs qdrant
```

### Issue: "ANTHROPIC_API_KEY not set"

**Solution:**
```bash
# Verify .env file exists in project root
cat .env | grep ANTHROPIC_API_KEY

# Restart backend to reload environment
docker-compose restart backend
```

### Issue: "Embeddings service not initialized"

**Solution:**
- RAG requires OpenAI API key for embeddings
- Add `OPENAI_API_KEY` to `.env`
- Restart backend

### Issue: "Collection not found"

**Solution:**
```bash
# Initialize database
docker-compose exec backend python scripts/init_database.py

# Or with recreate flag
docker-compose exec backend python scripts/init_database.py --recreate
```

### Issue: Generation is slow

**Causes:**
- First request initializes services (slower)
- Claude API latency (10-15s typical)
- Network connection
- RAG retrieval adds 1-2s

**Normal generation time: 10-20 seconds**

## Development Workflow

### 1. Make Code Changes

Edit files in `backend/app/`

### 2. Auto-Reload (Docker)

Changes are automatically detected via volume mount:
```bash
# Check logs to see reload
docker-compose logs -f backend
```

### 3. Run Tests

```bash
docker-compose exec backend pytest
```

### 4. Check Logs

```bash
# Real-time logs
docker-compose logs -f backend

# Inside container
docker-compose exec backend cat logs/app_2024-01-15.log
```

### 5. Access Python Shell

```bash
docker-compose exec backend poetry run ipython

# Test imports
>>> from app.services.content_generator import get_content_generator
>>> gen = get_content_generator()
```

## Project Structure Overview

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── core/
│   │   ├── config.py        # Settings from .env
│   │   └── logging.py       # Loguru configuration
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   │   ├── qdrant_service.py
│   │   ├── langchain_service.py
│   │   └── content_generator.py
│   ├── routers/             # API endpoints
│   └── utils/               # Utilities
└── scripts/                 # Helper scripts
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/generate-article` | POST | Generate article |
| `/api/v1/supported-options` | GET | Get options |
| `/api/v1/validate-request` | POST | Validate params |
| `/docs` | GET | Swagger UI |

## Environment Variables

Key variables (see `.env.template` for full list):

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# Qdrant
QDRANT_HOST=qdrant  # 'localhost' for local dev
QDRANT_PORT=6333

# LLM Settings
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# RAG Settings
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7
```

## Next Steps

1. Test article generation via API docs: http://localhost:8000/docs
2. Integrate frontend with backend
3. Customize prompt templates in `app/services/langchain_service.py`
4. Add more sample articles to `data/samples/sample_articles.json`
5. Configure rate limiting and caching for production

## Support

- Check logs: `docker-compose logs backend`
- Health endpoint: http://localhost:8000/health/detailed
- API docs: http://localhost:8000/docs
- See full README: `backend/BACKEND_README.md`

## Success Criteria

You're ready to proceed when:
- [ ] Health endpoint returns "healthy"
- [ ] Qdrant shows articles indexed (check `/api/v1/generation-stats`)
- [ ] Sample article generation completes successfully
- [ ] API docs are accessible at `/docs`
- [ ] Logs show no errors in `docker-compose logs backend`

Congratulations! Your backend is ready for article generation.
