# System Architecture Documentation

## Overview

The Jenosize AI Content Generation System is a production-grade microservices architecture designed to generate high-quality business trend articles using Claude 3.5 Sonnet, LangChain, and RAG (Retrieval-Augmented Generation).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Browser                              │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                │ HTTP/HTTPS
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Next.js Frontend (Port 3000)                     │
│                                                                      │
│  ├─ React 18 Components                                             │
│  ├─ TanStack Query (Data Fetching)                                  │
│  ├─ React Hook Form + Zod Validation                                │
│  └─ Tailwind CSS Styling                                            │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                │ REST API (JSON)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     API Layer                                 │  │
│  │  ├─ /api/v1/generate (POST)                                  │  │
│  │  ├─ /api/v1/articles (GET)                                   │  │
│  │  ├─ /api/v1/articles/{id} (GET)                              │  │
│  │  └─ /health (GET)                                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Service Layer                               │  │
│  │  ├─ ContentGeneratorService                                  │  │
│  │  ├─ LangChainService                                         │  │
│  │  ├─ QdrantService                                            │  │
│  │  └─ EmbeddingService                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  LangChain Pipeline                           │  │
│  │  ├─ Prompt Templates                                         │  │
│  │  ├─ Few-Shot Examples                                        │  │
│  │  ├─ RAG Chain                                                │  │
│  │  └─ Output Parsers                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────┬───────────────────────────────┬─────────────────────┘
              │                               │
              │ Vector Search                 │ LLM API
              ▼                               ▼
┌─────────────────────────┐     ┌──────────────────────────────┐
│   Qdrant Vector DB      │     │   Anthropic Claude API       │
│   (Port 6333)           │     │   (claude-3-5-sonnet)        │
│                         │     │                              │
│ ├─ Article Embeddings   │     │ ├─ Text Generation           │
│ ├─ Semantic Search      │     │ ├─ Context Understanding     │
│ └─ Similarity Matching  │     │ └─ Style Adaptation          │
└─────────────────────────┘     └──────────────────────────────┘
```

## Component Details

### 1. Frontend Layer (Next.js)

**Technology Stack:**
- Next.js 14 with App Router
- React 18 with Server Components
- TypeScript for type safety
- Tailwind CSS for styling
- TanStack Query for data fetching
- React Hook Form + Zod for form validation

**Responsibilities:**
- User interface for article generation
- Input validation and sanitization
- API request/response handling
- Article preview and formatting
- Error handling and user feedback

**Key Features:**
- Server-side rendering (SSR) for SEO
- Client-side caching with TanStack Query
- Responsive design for all devices
- Real-time validation feedback
- Markdown rendering for previews

**API Client Architecture:**
```typescript
// lib/api.ts
class APIClient {
  baseURL: string

  async generateArticle(params: GenerateRequest): Promise<Article>
  async getArticles(): Promise<Article[]>
  async getArticleById(id: string): Promise<Article>
}
```

### 2. Backend Layer (FastAPI)

**Technology Stack:**
- FastAPI with Pydantic v2
- Python 3.11 with async/await
- Poetry for dependency management
- Uvicorn ASGI server
- Python-Jose for JWT authentication
- Loguru for structured logging

**Responsibilities:**
- RESTful API endpoints
- Request validation and authentication
- Business logic orchestration
- LangChain pipeline execution
- Error handling and logging
- Rate limiting and caching

**Architecture Patterns:**
- **Dependency Injection**: FastAPI's built-in DI for services
- **Service Layer**: Separates business logic from API layer
- **Repository Pattern**: Abstract data access
- **Factory Pattern**: Create LangChain components

**API Structure:**
```
app/
├── main.py                  # FastAPI application setup
├── api/
│   ├── routes/
│   │   ├── generate.py      # Content generation endpoints
│   │   ├── articles.py      # Article management endpoints
│   │   └── health.py        # Health check endpoints
│   └── deps.py              # Dependency injection
├── core/
│   ├── config.py            # Settings management
│   ├── security.py          # Authentication/authorization
│   └── logging.py           # Logging configuration
├── services/
│   ├── content_generator.py # Main generation service
│   ├── langchain_service.py # LangChain orchestration
│   ├── qdrant_service.py    # Vector DB operations
│   └── embedding_service.py # Embedding generation
├── models/
│   ├── article.py           # Article data models
│   ├── request.py           # API request schemas
│   └── response.py          # API response schemas
└── prompts/
    ├── article_generation.py # Prompt templates
    └── few_shot_examples.py  # Example articles
```

### 3. LangChain Layer

**Components:**

**a) Prompt Engineering:**
```python
# System prompt for Jenosize style
SYSTEM_PROMPT = """
You are an expert business analyst writing for Jenosize,
a leading business insights platform. Your writing is:
- Professional yet engaging
- Data-driven with strategic insights
- Forward-thinking and trend-aware
- SEO-optimized
"""

# Article generation template
ARTICLE_TEMPLATE = PromptTemplate(
    input_variables=["topic", "industry", "context", "keywords"],
    template="{system_prompt}\n\nGenerate an article about {topic}..."
)
```

**b) RAG Pipeline:**
```python
# RAG chain structure
retriever = QdrantRetriever(
    client=qdrant_client,
    collection_name="jenosize_articles",
    top_k=5
)

rag_chain = (
    {"context": retriever, "query": RunnablePassthrough()}
    | prompt_template
    | claude_llm
    | output_parser
)
```

**c) Few-Shot Learning:**
```python
# Few-shot examples structure
FEW_SHOT_EXAMPLES = [
    {
        "input": {
            "topic": "AI in Retail",
            "industry": "Retail Technology"
        },
        "output": "Full example article in Jenosize style..."
    },
    # 3-5 high-quality examples
]
```

**LangChain Flow:**
```
Input Parameters
      ↓
Embedding Generation
      ↓
Vector Search (Qdrant) → Retrieved Context
      ↓
Prompt Construction (with Few-Shot Examples + Context)
      ↓
Claude API Call
      ↓
Response Parsing & Validation
      ↓
Structured Output
```

### 4. Vector Database Layer (Qdrant)

**Technology:**
- Qdrant 1.7+ (latest)
- REST API (Port 6333)
- gRPC API (Port 6334)
- Persistent storage with Docker volumes

**Collections Structure:**
```json
{
  "collection_name": "jenosize_articles",
  "vector_size": 1536,
  "distance": "Cosine",
  "payload_schema": {
    "title": "string",
    "content": "string",
    "topic": "string",
    "industry": "string",
    "keywords": ["string"],
    "created_at": "timestamp"
  }
}
```

**Operations:**
- **Indexing**: Store sample article embeddings
- **Search**: Retrieve similar articles for RAG
- **Filtering**: Search by metadata (industry, topic)
- **Scoring**: Cosine similarity for relevance

**Search Pipeline:**
```python
# Query Qdrant for similar articles
results = qdrant_client.search(
    collection_name="jenosize_articles",
    query_vector=embedding,
    limit=5,
    score_threshold=0.7,
    filter={
        "must": [
            {"key": "industry", "match": {"value": industry}}
        ]
    }
)
```

### 5. External Services

**a) Anthropic Claude API:**
- Model: `claude-3-5-sonnet-20241022`
- Max Tokens: 4096
- Temperature: 0.7 (balanced creativity)
- API Version: 2023-06-01

**b) OpenAI API (Optional):**
- Embeddings: `text-embedding-3-small` (1536 dimensions)
- Used for vector search similarity matching
- Fallback for generation if needed

## Data Flow

### Article Generation Flow

```
1. User Input (Frontend)
   ├─ Topic
   ├─ Industry
   ├─ Target Audience
   ├─ SEO Keywords
   └─ Article Length

2. API Request (Next.js → FastAPI)
   ├─ Validation (Pydantic models)
   ├─ Authentication check
   └─ Rate limiting

3. Content Generation (Backend Service)
   ├─ Generate query embedding
   ├─ Search Qdrant for similar articles (RAG)
   ├─ Construct prompt with:
   │   ├─ System prompt (Jenosize style)
   │   ├─ Few-shot examples
   │   ├─ Retrieved context
   │   └─ User parameters
   ├─ Call Claude API
   ├─ Parse and validate response
   └─ Generate metadata (SEO, keywords)

4. Response (FastAPI → Next.js)
   ├─ Article content
   ├─ Metadata
   ├─ Generation statistics
   └─ Quality metrics

5. Display (Frontend)
   ├─ Markdown rendering
   ├─ SEO preview
   └─ Export options
```

## Infrastructure & Deployment

### Docker Compose Architecture

```yaml
services:
  qdrant:      # Vector database
  backend:     # FastAPI service (depends on qdrant)
  frontend:    # Next.js service (depends on backend)

networks:
  jenosize-network:  # Shared bridge network

volumes:
  qdrant_storage:    # Persistent vector data
```

**Service Dependencies:**
```
Frontend → Backend → Qdrant
             ↓
        Claude API
```

**Health Checks:**
- All services implement health endpoints
- Docker monitors service health
- Auto-restart on failure

### Environment Configuration

**Development:**
- Hot reload enabled (both frontend and backend)
- Debug logging
- Mounted volumes for code changes
- Relaxed CORS settings

**Production:**
- Optimized builds
- Multiple workers (Uvicorn: 4 workers)
- Restricted CORS
- Enhanced security
- Rate limiting enabled

## Security Architecture

### API Authentication
```python
# JWT-based authentication
@router.post("/generate")
async def generate_article(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user)
):
    # Protected endpoint
```

### Rate Limiting
```python
# slowapi integration
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def generate_article():
    # Limited to 10 requests per minute
```

### Input Validation
```python
# Pydantic models for strict validation
class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)
    industry: str = Field(..., min_length=2, max_length=100)
    seo_keywords: List[str] = Field(..., max_items=10)
```

### CORS Configuration
```python
# Restricted to allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
)
```

## Performance Optimization

### Caching Strategy
- TanStack Query: Client-side API response caching
- Backend: Cache embeddings for common queries
- Qdrant: Optimized vector search indexes

### Async Operations
```python
# All I/O operations are async
async def generate_article():
    embedding = await generate_embedding_async()
    results = await qdrant_client.search_async()
    article = await claude_client.generate_async()
```

### Resource Management
- Connection pooling for Qdrant
- HTTP client reuse
- Graceful shutdown handling

## Monitoring & Logging

### Logging Structure
```python
# Structured logging with Loguru
logger.info(
    "Article generated",
    topic=topic,
    industry=industry,
    tokens_used=tokens,
    duration_ms=duration
)
```

### Metrics Tracked
- API response times
- Token usage
- Generation success/failure rates
- RAG retrieval relevance scores
- Cache hit rates

### Error Handling
```python
# Comprehensive error handling
try:
    article = await generate_article()
except ClaudeAPIError as e:
    logger.error("Claude API failed", error=str(e))
    raise HTTPException(status_code=502, detail="LLM service unavailable")
except QdrantError as e:
    logger.error("Qdrant query failed", error=str(e))
    # Fallback: generate without RAG context
```

## Scalability Considerations

### Horizontal Scaling
- Stateless backend services (can run multiple replicas)
- Shared Qdrant database
- Load balancer ready

### Vertical Scaling
- Adjustable worker processes (Uvicorn)
- Configurable Qdrant memory limits
- Resource limits in Docker Compose

### Performance Tuning
- Batch embedding generation
- Qdrant search optimization
- Prompt caching
- Response streaming for long articles

## Testing Strategy

### Unit Tests
```python
# Service layer tests
def test_content_generator():
    generator = ContentGenerator()
    article = generator.generate(topic="AI", industry="Tech")
    assert article.word_count >= 800
```

### Integration Tests
```python
# API endpoint tests
async def test_generate_endpoint(client):
    response = await client.post("/api/v1/generate", json={...})
    assert response.status_code == 200
```

### E2E Tests
- Full flow from frontend to article generation
- RAG pipeline validation
- Claude API integration tests

## Deployment Checklist

- [ ] Environment variables configured
- [ ] API keys secured
- [ ] Docker images built
- [ ] Qdrant volume persisted
- [ ] CORS configured for production domain
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Health checks passing
- [ ] Backup strategy for Qdrant data
- [ ] Monitoring alerts configured

## Future Enhancements

1. **Multi-Language Support**: Generate articles in Thai and English
2. **Streaming Responses**: Real-time article generation with Server-Sent Events
3. **Advanced RAG**: Hybrid search (vector + keyword), re-ranking
4. **Fine-Tuning**: Custom Claude fine-tuned model for Jenosize style
5. **Analytics Dashboard**: Track generation metrics and quality
6. **Collaborative Editing**: Multi-user article refinement
7. **Export Formats**: PDF, DOCX, HTML exports
8. **SEO Optimization**: Automated SEO scoring and suggestions

---

**Architecture Version**: 1.0
**Last Updated**: 2024-01-20
**Maintained By**: Jenosize AI Team
