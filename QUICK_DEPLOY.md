# 🚀 QUICK DEPLOYMENT - Get Live URL in 1 Hour

You already have Qdrant Cloud! Let's deploy the rest.

## ✅ Step 1: Update Configuration (5 minutes)

### Update `.env` file:

```bash
# Qdrant Cloud Configuration
QDRANT_HOST=your-cluster-id.region.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_USE_HTTPS=true
QDRANT_COLLECTION_NAME=jenosize_articles

# Your AI API Key (add one of these)
ANTHROPIC_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here

# App Settings
ENVIRONMENT=production
LLM_MODEL=claude-sonnet-4-5-20250929
LLM_TEMPERATURE=0.7
CORS_ORIGINS=*
```

### Replace Qdrant service file:

```bash
copy backend\app\services\qdrant_service_cloud.py backend\app\services\qdrant_service.py
```

## 🚀 Step 2: Deploy Backend to Railway (15 minutes)

### A. Push to GitHub

```bash
cd D:\test\trend_and_future_ideas_articles

# Initialize git
git init
git add .
git commit -m "Ready for deployment"

# Create GitHub repo at github.com (name: jenosize-ai-content)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/jenosize-ai-content.git
git branch -M main
git push -u origin main
```

### B. Deploy on Railway

1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `jenosize-ai-content`
5. Railway auto-detects Docker

6. **Add Environment Variables** (click Variables tab):
   ```
   ANTHROPIC_API_KEY=your_actual_key
   QDRANT_HOST=your-cluster-id.region.cloud.qdrant.io
   QDRANT_PORT=6333
   QDRANT_API_KEY=your_qdrant_api_key_here
   QDRANT_USE_HTTPS=true
   QDRANT_COLLECTION_NAME=jenosize_articles
   LLM_MODEL=claude-sonnet-4-5-20250929
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=4096
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   EMBEDDING_DIMENSIONS=384
   RAG_TOP_K=5
   RAG_SIMILARITY_THRESHOLD=0.7
   ENVIRONMENT=production
   CORS_ORIGINS=*
   LOG_LEVEL=INFO
   ```

7. Click "Deploy"
8. Wait ~5 minutes
9. Copy your backend URL (e.g., `https://jenosize-backend.up.railway.app`)

### C. Test Backend

```bash
curl https://your-backend.up.railway.app/health
```

## 🎨 Step 3: Deploy Frontend to Vercel (10 minutes)

### A. Prepare Frontend

Create `frontend/.env.production`:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NODE_ENV=production
```

### B. Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod

# When prompted:
# - Project name: jenosize-ai-content
# - Directory: ./
# - Settings: Auto-detect

# Add environment variable:
# NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

**OR** use Vercel Dashboard:
1. Go to https://vercel.com
2. New Project → Import from GitHub
3. Select your repo
4. Root Directory: `frontend`
5. Add env var: `NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app`
6. Deploy

## ✅ Step 4: Initialize Qdrant Collection (5 minutes)

```bash
# Run initialization script
python tests/scripts/initialize_qdrant.py
```

## 🎉 DONE!

Your live URLs:
- **Frontend**: https://jenosize-ai-content.vercel.app
- **Backend**: https://your-backend.up.railway.app
- **API Docs**: https://your-backend.up.railway.app/docs

Test it:
1. Visit frontend URL
2. Generate an article
3. Success! 🚀

---

## 📝 For Assignment Submission

Create `LIVE_DEMO_URLS.txt`:
```
LIVE DEMO - Jenosize AI Content Generator

Frontend: https://jenosize-ai-content.vercel.app
Backend API: https://your-backend.up.railway.app
API Documentation: https://your-backend.up.railway.app/docs

Technology Stack:
- Frontend: Vercel (Next.js 14)
- Backend: Railway (FastAPI)
- Database: Qdrant Cloud (Vector DB)
- AI: Claude Sonnet 4.5

Quick Test:
1. Visit the frontend URL
2. Enter topic: "Future of AI in Healthcare"
3. Click "Generate Article"
4. Article appears in ~30 seconds

Architecture:
- RAG-based content generation
- 5 similar articles retrieved per generation
- SEO metadata auto-generated
- Production-ready deployment
```

---

## 🐛 Troubleshooting

**Backend not starting?**
```bash
# Check Railway logs
railway logs
```

**Frontend can't connect?**
```bash
# Update CORS in Railway variables:
CORS_ORIGINS=https://your-app.vercel.app,https://jenosize-ai-content.vercel.app,*
```

**Qdrant errors?**
```bash
# Verify credentials in Railway dashboard
# Check Qdrant Cloud dashboard
```

---

**Total Time**: ~45 minutes
**Cost**: $0 (free tiers)
**Result**: Professional live demo! 🎉
