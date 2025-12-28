# Jenosize AI Content Generation Backend

FastAPI-based backend service for generating high-quality business trend and future ideas articles using LangChain, Claude 3.5 Sonnet, and Qdrant vector database.

## Architecture Overview

```
┌─────────────────┐
│   FastAPI App   │ ← HTTP/REST API
└────────┬────────┘
         │
         ├─── Content Generator Service (Orchestration)
         │         │
         │         ├─── LangChain Service (Claude 3.5 Sonnet + Prompts)
         │         │
         │         └─── Qdrant Service (Vector Search for RAG)
         │
         └─── API Routers
              ├─── /health (Health checks)
              └─── /api/v1/generate-article (Article generation)
```

## Features

- **AI-Powered Generation**: Uses Claude 3.5 Sonnet for high-quality content
- **RAG Pipeline**: Retrieval-Augmented Generation using Qdrant vector database
- **Flexible Parameters**: Customize topic, industry, audience, tone, keywords
- **SEO Optimization**: Automatic meta descriptions and keyword extraction
- **Quality Control**: Validation, length checks, and content quality metrics
- **Production-Ready**: Comprehensive logging, error handling, health checks

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   └── logging.py         # Logging setup
│   ├── models/
│   │   ├── article.py         # Article request/response models
│   │   └── common.py          # Common models (health, errors)
│   ├── services/
│   │   ├── qdrant_service.py  # Qdrant vector database operations
│   │   ├── langchain_service.py # LangChain + Claude integration
│   │   └── content_generator.py # Main content generation logic
│   ├── routers/
│   │   ├── health.py          # Health check endpoints
│   │   └── article.py         # Article generation endpoints
│   └── utils/
│       └── init_data.py       # Database initialization utility
├── scripts/
│   └── init_database.py       # Database initialization script
├── Dockerfile
├── pyproject.toml             # Poetry dependencies
└── README.md
```

## API Endpoints

### Health Check
```
GET /health
```
Returns health status of API and all services (Qdrant, Claude).

### Generate Article
```
POST /api/v1/generate-article
```

**Request Body:**
```json
{
  "topic": "The Future of Sustainable Energy in Southeast Asia",
  "industry": "energy",
  "audience": "executives",
  "keywords": ["renewable energy", "solar power", "sustainability"],
  "target_length": 2500,
  "tone": "professional",
  "include_examples": true,
  "include_statistics": true,
  "generate_seo_metadata": true,
  "use_rag": true
}
```

**Response:**
```json
{
  "success": true,
  "article": {
    "content": "# Article title\n\n## Section...",
    "metadata": {
      "title": "Article Title",
      "meta_description": "SEO description...",
      "keywords": ["keyword1", "keyword2"],
      "reading_time_minutes": 8,
      "word_count": 2456,
      "industry": "energy",
      "audience": "executives",
      "model_used": "claude-3-5-sonnet-20241022",
      "rag_sources_count": 5
    }
  },
  "generation_time_seconds": 12.5,
  "request_id": "req_abc123"
}
```

### Supported Options
```
GET /api/v1/supported-options
```
Returns all supported industries, audiences, tones, and features.

### Validate Request
```
POST /api/v1/validate-request
```
Validates article generation parameters without generating content.

## Configuration

All configuration is managed through environment variables (see `.env` file):

### Required Variables
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude
- `OPENAI_API_KEY`: OpenAI API key for embeddings (required for RAG)

### Qdrant Settings
- `QDRANT_HOST`: Qdrant server host (default: `qdrant` in Docker)
- `QDRANT_PORT`: Qdrant REST API port (default: `6333`)
- `QDRANT_COLLECTION_NAME`: Collection name (default: `jenosize_articles`)

### LLM Settings
- `LLM_MODEL`: Claude model (default: `claude-3-5-sonnet-20241022`)
- `LLM_TEMPERATURE`: Temperature 0-1 (default: `0.7`)
- `LLM_MAX_TOKENS`: Max tokens (default: `4096`)

### RAG Settings
- `RAG_TOP_K`: Number of similar articles to retrieve (default: `5`)
- `RAG_SIMILARITY_THRESHOLD`: Minimum similarity score (default: `0.7`)

## Installation & Setup

### Option 1: Docker (Recommended)

The backend is already configured to run via Docker Compose. See the main project README.

### Option 2: Local Development

```bash
# Install Poetry
pip install poetry

# Install dependencies
cd backend
poetry install

# Set up environment variables
cp ../.env.template ../.env
# Edit .env and add your API keys

# Run the application
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Initialization

Before generating articles, initialize Qdrant with sample data:

### Using Docker
```bash
docker-compose exec backend python scripts/init_database.py
```

### Local
```bash
cd backend
poetry run python scripts/init_database.py
```

**Options:**
- `--recreate`: Delete existing collection and recreate (destroys data)
- `--verify-only`: Only verify existing data

## Sample Data

The backend includes 10 sample Jenosize-style articles covering various industries:
- Technology (AI, blockchain, edge computing, quantum computing)
- Healthcare (personalized medicine)
- Manufacturing (sustainable supply chain)
- Retail (voice commerce)
- Energy (circular economy)
- General business trends

These articles are used for RAG context when generating new content.

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Quality
```bash
# Format code
poetry run black app/

# Sort imports
poetry run isort app/

# Linting
poetry run flake8 app/

# Type checking
poetry run mypy app/
```

### Logging

Logs are written to:
- Console (colored, structured)
- `logs/app_YYYY-MM-DD.log` (daily rotation)
- `logs/error_YYYY-MM-DD.log` (errors only)

Log level is configured via `LOG_LEVEL` environment variable.

## RAG Pipeline Details

The RAG (Retrieval-Augmented Generation) pipeline works as follows:

1. **Query Embedding**: Generate embedding for user's topic + keywords
2. **Vector Search**: Search Qdrant for top-k similar articles using cosine similarity
3. **Context Formation**: Format retrieved articles as context
4. **Prompt Engineering**: Combine context with Jenosize-style writing instructions
5. **Generation**: Claude generates article using RAG context for insights
6. **Post-Processing**: Extract metadata, validate quality, structure sections

## Content Quality Checks

Generated articles are validated for:
- Minimum length requirements (800-4000 words)
- Proper markdown structure (H1, H2, H3 headings)
- No placeholder text
- SEO metadata generation
- Reading time calculation

## Error Handling

The API provides detailed error responses:
- `422 Unprocessable Entity`: Validation errors with field details
- `500 Internal Server Error`: Unexpected errors (with details in dev mode)
- All errors are logged with full stack traces

## Performance Considerations

- **Embeddings**: Batch embedding generation for efficiency
- **Caching**: LRU cache for settings
- **Async**: All I/O operations are async (Qdrant, Claude API)
- **Connection Pooling**: Qdrant client reuses connections

Typical generation time: 10-20 seconds (depending on article length and RAG retrieval)

## Security

- API keys loaded from environment (never committed)
- CORS configured for frontend origins only
- Input validation via Pydantic
- Rate limiting configurable (via `RATE_LIMIT_*` settings)

## Troubleshooting

### "Failed to connect to Qdrant"
- Ensure Qdrant container is running: `docker-compose ps`
- Check Qdrant logs: `docker-compose logs qdrant`
- Verify `QDRANT_HOST` and `QDRANT_PORT` settings

### "Embeddings service not initialized"
- Ensure `OPENAI_API_KEY` is set in `.env`
- RAG requires embeddings - it will be disabled without OpenAI key

### "Claude API check failed"
- Verify `ANTHROPIC_API_KEY` is correct
- Check API key has sufficient credits
- Review Claude API status page

### "Collection not found"
- Run database initialization: `python scripts/init_database.py`
- Check Qdrant web UI: `http://localhost:6333/dashboard`

## API Documentation

Once running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Use `/health/detailed` endpoint for diagnostics
3. Review environment variables and configuration
4. Verify all services are healthy via health check

## License

Copyright Jenosize AI Team
