# Railway Setup Instructions

## Current Status
✅ Code pushed to GitHub: https://github.com/kahnoon05/jenosize-ai-content
✅ Railway configuration file (`railway.json`) is in the repository
⏳ Need to configure Railway manually

---

## Step-by-Step Railway Configuration

### 1. Go to Railway Dashboard
Visit: https://railway.app

### 2. Login with GitHub
- Click "Login"
- Select "Login with GitHub"
- Authorize Railway

### 3. Create New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose: `kahnoon05/jenosize-ai-content`
- Railway will start auto-detecting your project

### 4. Configure the Service Manually

**IMPORTANT**: Railway might not detect the backend correctly. You need to configure it manually.

Click on your service, then go to **Settings** tab:

#### Build Settings:
- **Builder**: Select `Dockerfile` (NOT Railpack)
- **Dockerfile Path**: `backend/Dockerfile`
- **Docker Build Context**: `backend`
- **Watch Paths**: `/backend/**`

#### Deploy Settings:
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Healthcheck Path**: `/health`
- **Healthcheck Timeout**: `100`
- **Restart Policy**: `On Failure`

### 5. Add Environment Variables

Go to **Variables** tab → Click "RAW Editor" → Paste the contents from `RAILWAY_ENV_VARS.txt`

**The file contains your actual API keys (not in GitHub for security)**

### 6. Deploy
- Click "Deploy" or "Redeploy"
- Wait 10-15 minutes for build
- Watch logs for errors

### 7. Get Your Backend URL
- Go to **Settings** tab
- Under **Networking** → **Public Networking**
- Click "Generate Domain"
- Copy the URL (example: `your-backend.up.railway.app`)

### 8. Test Backend
```bash
curl https://your-backend.up.railway.app/health
```

Should return:
```json
{"status":"healthy","version":"v1","environment":"production"}
```

---

## Troubleshooting

### Build fails with "pyproject.toml not found"
- Check that **Docker Build Context** is set to `backend`
- Make sure **Dockerfile Path** is `backend/Dockerfile`
- Try redeploying

### Railway uses Railpack instead of Dockerfile
- Go to Settings → Build
- Manually change Builder to "Dockerfile"
- Save and redeploy

### Health check fails
- Wait 2-3 minutes after deployment
- Check Railway logs for errors
- Verify environment variables are set correctly

### 502 Bad Gateway
- Check if all environment variables are added
- Verify Qdrant connection details
- Check Railway logs for startup errors

---

## What's Next?

After Railway backend is deployed successfully:

1. ✅ Get your backend URL
2. Deploy frontend to Vercel (use `START_HERE.md`)
3. Test the application
4. Create `LIVE_DEMO_URLS.txt` with your URLs

---

## Important Files

- `RAILWAY_ENV_VARS.txt` - Your actual API keys (copy to Railway)
- `START_HERE.md` - Overall deployment guide
- `DEPLOYMENT_CHECKLIST.md` - Complete checklist
- `DEPLOY_NOW.md` - Detailed instructions

---

**Start with Step 1 above!** 🚀
