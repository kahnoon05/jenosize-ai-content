# 🚀 Live Deployment Guide - Jenosize AI Content Generator

Complete guide to deploy your application to the cloud with live URLs.

---

## 🎯 Deployment Architecture

```
Frontend (Vercel)     →  Backend (Railway)     →  Qdrant Cloud
https://your-app.vercel.app  https://your-api.up.railway.app  cloud.qdrant.io
```

**Total Time**: ~1-2 hours
**Cost**: $0 (using free tiers)

---

## 📦 Prerequisites

Before starting, ensure you have:
- [ ] GitHub account
- [ ] Qdrant Cloud account (create at https://cloud.qdrant.io)
- [ ] Railway account (create at https://railway.app) OR Render account
- [ ] Vercel account (create at https://vercel.com)
- [ ] Your API keys ready (ANTHROPIC_API_KEY or OPENAI_API_KEY)

---

## 🗄️ STEP 1: Deploy Qdrant Vector Database (15 minutes)

### 1.1 Create Qdrant Cloud Cluster

1. **Sign up at Qdrant Cloud**:
   - Go to https://cloud.qdrant.io/login
   - Sign up with GitHub or email
   - Verify your email

2. **Create a Free Cluster**:
   ```
   - Click "Create Cluster"
   - Name: jenosize-articles
   - Plan: Free (1GB storage)
   - Region: Choose closest to you (e.g., AWS us-east-1)
   - Click "Create"
   ```

3. **Get Connection Details**:
   - Wait for cluster to be ready (~2 minutes)
   - Click on your cluster
   - Copy the following:
     - **Cluster URL**: `https://xxxxx.aws.cloud.qdrant.io:6333`
     - **API Key**: Click "Generate API Key" and copy it

4. **Save credentials**:
   ```
   QDRANT_HOST=xxxxx.aws.cloud.qdrant.io
   QDRANT_PORT=6333
   QDRANT_API_KEY=your-api-key-here
   QDRANT_USE_HTTPS=true
   ```

### 1.2 Initialize Qdrant Collection

Option A: **Use provided initialization script**

```bash
# Update .env with Qdrant Cloud credentials
QDRANT_HOST=xxxxx.aws.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=your-qdrant-api-key

# Run initialization
cd D:\test\trend_and_future_ideas_articles
python tests/scripts/initialize_qdrant.py
```

Option B: **Manual initialization** (if script doesn't work)
- Collection will be auto-created on first article generation
- Or upload sample articles via backend API after deployment

---

## 🔧 STEP 2: Deploy Backend to Railway (20 minutes)

### 2.1 Prepare Backend for Deployment

1. **Update backend configuration** for cloud Qdrant:

Create `backend/app/core/config_cloud.py`:
```python
# Add to existing config.py Settings class

qdrant_api_key: Optional[str] = Field(
    default=None,
    description="Qdrant Cloud API key"
)
qdrant_use_https: bool = Field(
    default=False,
    description="Use HTTPS for Qdrant connection"
)
```

2. **Update Qdrant service** to support API key:

Edit `backend/app/services/qdrant_service.py`, update `__init__` method:

```python
def __init__(self):
    """Initialize Qdrant service with connection to Qdrant server"""
    self.collection_name = settings.qdrant_collection_name
    self.vector_size = settings.embedding_dimensions

    # Cloud vs Local configuration
    if settings.qdrant_use_https or settings.qdrant_api_key:
        # Qdrant Cloud connection
        self.client = QdrantClient(
            url=f"https://{settings.qdrant_host}:{settings.qdrant_port}",
            api_key=settings.qdrant_api_key,
        )
        logger.info(f"Connected to Qdrant Cloud at {settings.qdrant_host}")
    else:
        # Local connection (existing code)
        if settings.qdrant_use_grpc:
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_grpc_port,
                prefer_grpc=True,
            )
        else:
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
        logger.info(f"Connected to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")
```

3. **Create Railway-specific files**:

Create `backend/railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

Create `backend/Dockerfile.railway` (optimized for Railway):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (production only)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data/samples /app/data/generated /app/logs

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application (Railway sets $PORT)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 2.2 Deploy to Railway

1. **Push code to GitHub** (if not already):
   ```bash
   cd D:\test\trend_and_future_ideas_articles

   # Initialize git (if needed)
   git init
   git add .
   git commit -m "Prepare for Railway deployment"

   # Create GitHub repo and push
   # (Create repo at github.com first)
   git remote add origin https://github.com/YOUR_USERNAME/jenosize-ai-content.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your repository
   - Railway will auto-detect the Dockerfile

3. **Configure Environment Variables**:
   Click on your service → Variables → Add all these:

   ```bash
   # Required API Keys
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
   # OR
   OPENAI_API_KEY=sk-xxxxxxxxxxxxx

   # Qdrant Cloud Configuration
   QDRANT_HOST=xxxxx.aws.cloud.qdrant.io
   QDRANT_PORT=6333
   QDRANT_API_KEY=your-qdrant-api-key
   QDRANT_USE_HTTPS=true
   QDRANT_COLLECTION_NAME=jenosize_articles

   # Model Configuration
   LLM_MODEL=claude-sonnet-4-5-20250929
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=4096

   # Embedding Model (local)
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   EMBEDDING_DIMENSIONS=384

   # RAG Configuration
   RAG_TOP_K=5
   RAG_SIMILARITY_THRESHOLD=0.7

   # App Configuration
   ENVIRONMENT=production
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000
   CORS_ORIGINS=*

   # Content Settings
   DEFAULT_ARTICLE_LENGTH=2000
   MIN_ARTICLE_LENGTH=800
   MAX_ARTICLE_LENGTH=4000

   # Logging
   LOG_LEVEL=INFO
   ```

4. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (~5-10 minutes)
   - Once deployed, Railway will provide a URL like: `https://your-app.up.railway.app`

5. **Test Backend**:
   ```bash
   # Test health endpoint
   curl https://your-app.up.railway.app/health

   # Should return:
   # {"status":"healthy","version":"v1","environment":"production"}
   ```

6. **Copy your backend URL** - you'll need it for frontend deployment

---

## 🎨 STEP 3: Deploy Frontend to Vercel (15 minutes)

### 3.1 Prepare Frontend

1. **Update frontend configuration**:

Edit `frontend/.env.production`:
```bash
# Create this file
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_APP_NAME=Jenosize AI Content Generator
NODE_ENV=production
```

2. **Update next.config.js** for production:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Disable telemetry in production
  telemetry: false,
}

module.exports = nextConfig
```

### 3.2 Deploy to Vercel

1. **Option A: Deploy via Vercel Dashboard**:
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository
   - Configure:
     - Framework Preset: Next.js
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `.next`

2. **Option B: Deploy via Vercel CLI** (faster):
   ```bash
   # Install Vercel CLI
   npm install -g vercel

   # Login
   vercel login

   # Deploy
   cd frontend
   vercel --prod

   # Follow prompts:
   # - Link to existing project? No
   # - Project name: jenosize-ai-content
   # - Directory: ./
   # - Build settings: Auto-detected
   ```

3. **Configure Environment Variables in Vercel**:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
     NEXT_PUBLIC_APP_NAME=Jenosize AI Content Generator
     NODE_ENV=production
     ```

4. **Redeploy** to apply environment variables:
   - Click "Deployments"
   - Click "..." on latest deployment → "Redeploy"

5. **Get your live URL**:
   - Vercel provides: `https://jenosize-ai-content.vercel.app`
   - You can also add custom domain if you have one

---

## ✅ STEP 4: Test Your Live Application (10 minutes)

### 4.1 Test Backend API

```bash
# 1. Health check
curl https://your-backend.up.railway.app/health

# 2. Get supported options
curl https://your-backend.up.railway.app/api/v1/supported-options

# 3. Generate test article
curl -X POST https://your-backend.up.railway.app/api/v1/generate-article \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Future of AI in Business",
    "industry": "technology",
    "audience": "executives",
    "keywords": ["AI", "automation", "innovation"],
    "target_length": 1500,
    "tone": "professional",
    "use_rag": true
  }'
```

### 4.2 Test Frontend

1. Open your frontend URL: `https://your-app.vercel.app`
2. Fill in the article generation form
3. Click "Generate Article"
4. Verify article is generated successfully

### 4.3 Common Issues & Fixes

**Backend not responding:**
- Check Railway logs: `railway logs`
- Verify environment variables are set
- Check Qdrant connection

**Frontend can't connect to backend:**
- Verify NEXT_PUBLIC_API_URL is correct
- Check CORS settings in backend
- Update CORS_ORIGINS to include your Vercel URL

**Qdrant connection fails:**
- Verify API key is correct
- Check cluster is running in Qdrant Cloud
- Verify QDRANT_USE_HTTPS=true

---

## 🎉 STEP 5: Share Your Live URLs

Your deployed application:

```
Frontend: https://jenosize-ai-content.vercel.app
Backend API: https://your-backend.up.railway.app
API Docs: https://your-backend.up.railway.app/docs
```

### For Assignment Submission:

Create a file `LIVE_DEMO.md`:
```markdown
# Live Demo URLs

## Application
- **Frontend**: https://jenosize-ai-content.vercel.app
- **Backend API**: https://your-backend.up.railway.app
- **API Documentation**: https://your-backend.up.railway.app/docs

## Test Credentials
(If you added authentication)
- Username: demo
- Password: demo123

## Quick Test
1. Visit the frontend URL
2. Enter topic: "Future of AI in Healthcare"
3. Click "Generate Article"
4. Wait 30-60 seconds
5. See AI-generated article!

## Architecture
- Frontend: Vercel (Next.js)
- Backend: Railway (FastAPI)
- Database: Qdrant Cloud
- AI Model: Claude Sonnet 4.5 / GPT-3.5

## Performance
- Article generation: 30-60 seconds
- 5 similar articles retrieved via RAG
- SEO metadata automatically generated
```

---

## 💰 Cost Breakdown (Free Tier)

| Service | Free Tier | Upgrade Cost |
|---------|-----------|--------------|
| **Vercel** | Unlimited hobby projects | $20/month Pro |
| **Railway** | $5 free credits/month | $5/month per service |
| **Qdrant Cloud** | 1GB storage | $25/month for 2GB |
| **Total** | **$0 - $5/month** | $50/month for full scale |

**Free tier is sufficient for:**
- 1000+ article generations/month
- Demo and portfolio purposes
- Assignment submission

---

## 🔧 Advanced: Custom Domain (Optional)

### Add Custom Domain to Vercel

1. Buy domain from Namecheap/GoDaddy (~$10/year)
2. In Vercel project settings:
   - Go to "Domains"
   - Add your domain: `ai.yourdomain.com`
   - Follow DNS configuration instructions
3. Wait for DNS propagation (5-10 minutes)
4. Your app is now at `https://ai.yourdomain.com`

---

## 📊 Monitoring & Maintenance

### View Logs

**Railway Logs:**
```bash
railway logs --tail 100
```

**Vercel Logs:**
- Go to Vercel dashboard → Deployments → View Logs

### Monitor Performance

**Railway:**
- Dashboard shows CPU, Memory, Network usage
- Set up alerts for downtime

**Vercel:**
- Analytics tab shows page views, performance
- Real User Monitoring available

### Update Application

**Backend (Railway):**
```bash
# Push to GitHub
git add .
git commit -m "Update backend"
git push

# Railway auto-deploys from GitHub
```

**Frontend (Vercel):**
```bash
# Push to GitHub
git add .
git commit -m "Update frontend"
git push

# Vercel auto-deploys from GitHub
```

---

## 🐛 Troubleshooting Guide

### Issue: Backend build fails on Railway

**Solution:**
1. Check Railway build logs
2. Verify `pyproject.toml` dependencies
3. Ensure Dockerfile is correct
4. Try building locally first:
   ```bash
   docker build -f backend/Dockerfile.railway -t test-backend ./backend
   ```

### Issue: Frontend shows 502 Bad Gateway

**Solution:**
1. Backend is not running - check Railway
2. NEXT_PUBLIC_API_URL is wrong - verify in Vercel settings
3. CORS issue - update backend CORS_ORIGINS

### Issue: Article generation fails

**Solution:**
1. Check API key is set correctly
2. Verify Qdrant connection
3. Check backend logs for errors
4. Test API directly with curl

### Issue: Qdrant "collection not found"

**Solution:**
1. Run initialization script
2. Or generate one article - collection auto-creates
3. Check collection exists in Qdrant Cloud dashboard

---

## 📈 Scaling for Production

When you need to scale:

1. **Upgrade Railway** ($20/month):
   - More CPU/RAM
   - Better performance
   - Priority support

2. **Add Redis Caching**:
   - Cache generated embeddings
   - Cache API responses
   - Reduce API calls

3. **Load Balancing**:
   - Deploy multiple backend instances
   - Use Railway's load balancer

4. **CDN for Frontend**:
   - Vercel includes CDN by default
   - Add custom caching rules

---

## ✅ Deployment Checklist

Before going live:

- [ ] Qdrant Cloud cluster created and running
- [ ] Sample articles uploaded to Qdrant
- [ ] Backend deployed to Railway
- [ ] All environment variables configured
- [ ] Backend health check passes
- [ ] Frontend deployed to Vercel
- [ ] Frontend can communicate with backend
- [ ] Test article generation works
- [ ] API documentation accessible
- [ ] CORS configured for frontend domain
- [ ] Error monitoring set up
- [ ] URLs documented for assignment submission

---

## 🎓 For Assignment Submission

Include in your submission:

1. **LIVE_DEMO.md** with URLs
2. **Screenshot** of working application
3. **Test API response** (curl output)
4. **Update README.md** with deployment section:
   ```markdown
   ## Live Demo

   🌐 **Live Application**: https://jenosize-ai-content.vercel.app
   📡 **API Endpoint**: https://your-backend.up.railway.app
   📚 **API Docs**: https://your-backend.up.railway.app/docs

   ### Quick Test
   Visit the live app and generate an article about "Future of AI"!
   ```

---

**Deployment Time**: 1-2 hours total
**Cost**: $0 (free tier)
**Difficulty**: Medium
**Result**: Professional live demo for your assignment! 🚀
