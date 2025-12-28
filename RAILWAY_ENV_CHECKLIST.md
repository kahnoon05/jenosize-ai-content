# Railway Environment Variables Checklist

## ✅ Required Environment Variables for Railway Deployment

### Critical API Keys
- [ ] `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude models
- [ ] `OPENAI_API_KEY` - Your OpenAI API key for embeddings and GPT models

### Qdrant Cloud Configuration
- [ ] `QDRANT_HOST` - Your Qdrant Cloud cluster URL
- [ ] `QDRANT_PORT` - Port (default: 6333)
- [ ] `QDRANT_API_KEY` - Your Qdrant Cloud API key
- [ ] `QDRANT_USE_HTTPS` - Set to `true` for Qdrant Cloud
- [ ] `QDRANT_COLLECTION_NAME` - Collection name (default: jenosize_articles)

### Application Settings
- [ ] `ENVIRONMENT` - Set to `production`
- [ ] `LLM_MODEL` - Your model (e.g., `ft:gpt-3.5-turbo-0125:futuretrendarticle:jenosize:Cr7ayny6`)
- [ ] `LLM_TEMPERATURE` - Model temperature (default: 0.7)
- [ ] `LLM_MAX_TOKENS` - Max tokens (default: 4096)

### Optional but Recommended
- [ ] `CORS_ORIGINS` - Allowed CORS origins (e.g., `https://your-frontend.vercel.app`)
- [ ] `LOG_LEVEL` - Logging level (default: INFO)
- [ ] `RAG_TOP_K` - Number of similar articles to retrieve (default: 5)
- [ ] `RAG_SIMILARITY_THRESHOLD` - Similarity threshold (default: 0.7)

## 🔍 How to Verify in Railway

1. Go to your Railway project dashboard
2. Click on your service (jenosize-ai-content)
3. Go to the "Variables" tab
4. Ensure all variables above are set

## 🚨 Common Issues

### Issue: "uvicorn: not found"
**Solution:** Fixed by using `python -m uvicorn` in Dockerfile CMD

### Issue: "Qdrant connection failed"
**Solution:**
- Verify `QDRANT_USE_HTTPS=true` is set
- Check `QDRANT_HOST` doesn't include `https://` prefix
- Verify `QDRANT_API_KEY` is correct

### Issue: "Claude API failed"
**Solution:**
- Check `ANTHROPIC_API_KEY` is valid
- Ensure you have API credits
- Verify the model name is correct

### Issue: "OpenAI API failed"
**Solution:**
- Check `OPENAI_API_KEY` is valid
- For fine-tuned models, use full model ID: `ft:gpt-3.5-turbo-0125:org:name:id`

## 📝 Configuration Template for Railway

Copy these settings to Railway Variables tab (use your actual values from local `.env`):

```bash
# API Keys (⚠️ USE YOUR ACTUAL KEYS FROM .env FILE)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx

# Qdrant Cloud (⚠️ USE YOUR ACTUAL QDRANT CREDENTIALS)
QDRANT_HOST=your-cluster-id.region.gcp.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_USE_HTTPS=true
QDRANT_COLLECTION_NAME=jenosize_articles

# Model Configuration
LLM_MODEL=ft:gpt-3.5-turbo-0125:futuretrendarticle:jenosize:Cr7ayny6
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# RAG Settings
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7
```

**⚠️ IMPORTANT:** Replace the placeholder values above with your actual credentials from your local `.env` file!

## 🎯 Railway-Specific Settings

Railway automatically provides:
- `PORT` - Dynamic port assignment (your app should use `${PORT}`)
- `RAILWAY_ENVIRONMENT` - Railway environment name
- `RAILWAY_PROJECT_ID` - Your project ID

Your Dockerfile is configured to use `${PORT:-8000}` which will use Railway's port.

## 🔗 Health Check

Railway will check: `http://your-service.railway.app/health`

Make sure your FastAPI `/health` endpoint is working correctly.
