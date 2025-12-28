# 🚀 DEPLOY NOW - Step by Step

Your code is on GitHub! Now let's deploy to get live URLs.

---

## ✅ STEP 1: Deploy Backend to Railway (NOW!)

### 1. Go to Railway
Visit: https://railway.app

### 2. Sign Up / Login
- Click "Login" → "Login with GitHub"
- Authorize Railway to access your GitHub

### 3. Create New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Find and select: `kahnoon05/jenosize-ai-content`
- Railway will detect the Dockerfile automatically

### 4. Configure Root Directory
- Railway might ask for root directory
- **Root Directory**: Leave blank (it will auto-detect backend)
- Or specify: `backend` if needed

### 5. Add Environment Variables
Click on your service → **Variables** tab → Add these:

```bash
# === REQUIRED: Your API Keys ===
# Add your actual Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ACTUAL_KEY_HERE

# Add your actual OpenAI API key
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE

# === Qdrant Cloud (Your credentials) ===
QDRANT_HOST=6bd2e007-f709-4b41-bcdd-06d8106c6736.us-east4-0.gcp.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.aDmU9M3Q21RnDh5Tpwaenz9785OCosGM1M0O_3eO_-0
QDRANT_USE_HTTPS=true
QDRANT_COLLECTION_NAME=jenosize_articles

# === Model Configuration ===
LLM_MODEL=ft:gpt-3.5-turbo-0125:futuretrendarticle:jenosize:Cr7ayny6
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# === Embeddings ===
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# === RAG Settings ===
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7

# === App Configuration ===
ENVIRONMENT=production
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=*
LOG_LEVEL=INFO

# === Content Settings ===
DEFAULT_ARTICLE_LENGTH=2000
MIN_ARTICLE_LENGTH=800
MAX_ARTICLE_LENGTH=4000
GENERATE_META_DESCRIPTION=true
GENERATE_KEYWORDS=true
```

### 6. Deploy
- Click "Deploy"
- Wait ~5-10 minutes for build to complete
- Watch the logs for any errors

### 7. Get Your Backend URL
- Once deployed, Railway will show your URL
- Example: `https://jenosize-backend-production.up.railway.app`
- **SAVE THIS URL** - you need it for Vercel!

### 8. Test Backend
```bash
# Replace with your actual Railway URL
curl https://your-backend.up.railway.app/health

# Should return:
# {"status":"healthy","version":"v1","environment":"production"}
```

---

## ✅ STEP 2: Deploy Frontend to Vercel

### Option A: Vercel Dashboard (Easier)

1. **Go to Vercel**: https://vercel.com
2. **Login with GitHub**
3. **New Project** → Import `kahnoon05/jenosize-ai-content`
4. **Configure**:
   - Framework Preset: Next.js (auto-detected)
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

5. **Add Environment Variable**:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-backend.up.railway.app` (from Step 1.7)

6. **Deploy** → Wait ~3-5 minutes

7. **Get Your Frontend URL**:
   - Example: `https://jenosize-ai-content.vercel.app`

### Option B: Vercel CLI (Faster)

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Deploy
vercel --prod

# When prompted:
# - Link to existing project? No
# - Project name: jenosize-ai-content
# - Directory: ./
# - Override settings? No

# After deployment, add environment variable via dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

---

## ✅ STEP 3: Test Your Live Application!

### 1. Open Frontend URL
Visit your Vercel URL: `https://jenosize-ai-content.vercel.app`

### 2. Generate Test Article
- **Topic**: "Future of AI in Healthcare"
- **Industry**: Healthcare
- **Audience**: Executives
- **Keywords**: AI, automation, innovation
- **Length**: 1500 words
- **Tone**: Professional

### 3. Click "Generate Article"
- Wait 30-60 seconds
- Article should appear!

### 4. Verify
- Check if article is generated
- Check if it's in Jenosize style
- Check if SEO metadata is present
- Try downloading the article

---

## 🎉 SUCCESS! You Now Have:

✅ **Frontend**: https://jenosize-ai-content.vercel.app
✅ **Backend API**: https://your-backend.up.railway.app
✅ **API Docs**: https://your-backend.up.railway.app/docs
✅ **Vector DB**: Qdrant Cloud (10 articles indexed)
✅ **Fine-tuned Model**: GPT-3.5 Turbo (Jenosize style)

---

## 📝 For Assignment Submission

Create file: `LIVE_DEMO_URLS.txt`

```
JENOSIZE AI CONTENT GENERATOR - LIVE DEMO

==========================================================
LIVE URLS
==========================================================

Frontend Application:
https://jenosize-ai-content.vercel.app

Backend API:
https://your-backend-name.up.railway.app

API Documentation:
https://your-backend-name.up.railway.app/docs

GitHub Repository:
https://github.com/kahnoon05/jenosize-ai-content

==========================================================
TECHNOLOGY STACK
==========================================================

✓ Frontend: Next.js 14 (Vercel)
✓ Backend: FastAPI (Railway)
✓ Vector DB: Qdrant Cloud (GCP)
✓ AI Model: GPT-3.5 Turbo Fine-tuned
✓ Embeddings: OpenAI text-embedding-3-small

==========================================================
FEATURES
==========================================================

✓ AI-powered article generation
✓ RAG with 5 similar articles retrieval
✓ Fine-tuned for Jenosize writing style
✓ SEO metadata auto-generation
✓ Production-ready cloud deployment
✓ Comprehensive documentation

==========================================================
QUICK TEST
==========================================================

1. Visit frontend URL above
2. Enter topic: "Future of AI"
3. Select industry and audience
4. Click "Generate Article"
5. See professional article in 30-60 seconds!

==========================================================
ASSIGNMENT COMPLETION
==========================================================

✓ Model Selection & Fine-Tuning (40%)
✓ Data Engineering (20%)
✓ Model Deployment (20%)
✓ Documentation (20%)

Total: 100% Complete! 🎉

==========================================================
```

---

## 🐛 Troubleshooting

**Backend not starting?**
- Check Railway logs for errors
- Verify all environment variables are set
- Check API keys are valid
- Try redeploying

**Frontend can't connect to backend?**
- Verify `NEXT_PUBLIC_API_URL` in Vercel
- Check CORS is set to `*` in Railway
- Test backend health endpoint directly

**Qdrant errors?**
- Collection already exists (this is OK!)
- Verify API key is correct
- Check Qdrant Cloud dashboard

**Article generation fails?**
- Check Railway logs
- Verify OpenAI/Anthropic API key is valid
- Check Qdrant connection

---

## ⏱️ Time Estimate

- Railway Deployment: 10-15 minutes
- Vercel Deployment: 5-10 minutes
- Testing: 5 minutes
- **Total: ~25 minutes to live URLs!**

---

## 🎯 Next Steps

1. Deploy to Railway (10 min) ← **START HERE**
2. Deploy to Vercel (5 min)
3. Test application (5 min)
4. Create LIVE_DEMO_URLS.txt
5. Submit assignment! 🚀

**Start with Railway deployment above!**
