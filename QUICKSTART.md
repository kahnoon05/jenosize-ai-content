# Quick Start Guide

Get the Jenosize AI Content Generation System running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- [ ] Docker Desktop installed and running
- [ ] Anthropic API key (get from https://console.anthropic.com/)
- [ ] At least 8GB RAM available
- [ ] Ports 3000, 8000, 6333 available

## Step-by-Step Setup

### 1. Configure API Key

Open the `.env` file and add your Anthropic API key:

```bash
# Edit .env file
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Where to find your API key:**
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new key or copy existing one
5. Paste it in the `.env` file

### 2. Build the Services

Open a terminal in the project directory and run:

```bash
# Build all Docker images (takes 5-10 minutes first time)
docker-compose build
```

**What's happening:**
- Building Python backend with FastAPI and LangChain
- Building Next.js frontend with React
- Downloading Qdrant vector database image

### 3. Start the System

```bash
# Start all services in detached mode
docker-compose up -d
```

**Services starting:**
- Qdrant (Vector Database) - Port 6333
- Backend (FastAPI) - Port 8000
- Frontend (Next.js) - Port 3000

### 4. Verify Everything is Running

```bash
# Check service status
docker-compose ps
```

You should see all three services as "Up" and "healthy".

### 5. Access the Application

Open your browser and visit:

- **Main Application**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### 6. Test the API

```bash
# Test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "qdrant": "connected",
    "claude": "available"
  }
}
```

## Troubleshooting

### Problem: Services won't start

**Solution:**
```bash
# Check logs for errors
docker-compose logs

# Restart services
docker-compose restart
```

### Problem: "ANTHROPIC_API_KEY not found"

**Solution:**
1. Verify `.env` file exists in project root
2. Ensure API key is set correctly
3. Restart services: `docker-compose restart backend`

### Problem: Port conflicts

**Solution:**
```bash
# Check what's using the ports
# Windows:
netstat -ano | findstr "3000 8000 6333"

# Linux/Mac:
lsof -i :3000
lsof -i :8000
lsof -i :6333

# Kill conflicting process or change ports in docker-compose.yml
```

### Problem: "Cannot connect to Docker daemon"

**Solution:**
1. Ensure Docker Desktop is running
2. On Windows: Check Docker Desktop is in Linux container mode
3. Restart Docker Desktop

## Next Steps

Now that your system is running:

1. **Add Sample Articles**: Place Jenosize article samples in `data/samples/`
2. **Test Generation**: Visit http://localhost:3000 and generate your first article
3. **Review API**: Explore http://localhost:8000/docs for all available endpoints
4. **Customize**: Modify prompts in `backend/app/prompts/` to adjust output style

## Common Commands

```bash
# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# Stop all services
docker-compose down

# Restart after code changes
docker-compose up -d --build

# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh
```

## Production Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET` in `.env` to a strong random value
- [ ] Update `CORS_ORIGINS` to your production domain
- [ ] Enable HTTPS with reverse proxy (nginx/traefik)
- [ ] Set up monitoring and logging
- [ ] Configure backup for Qdrant data
- [ ] Review and adjust rate limits
- [ ] Use production builds: `docker-compose -f docker-compose.yml build --target production`

## Getting Help

- **Documentation**: See main README.md for detailed information
- **API Docs**: http://localhost:8000/docs (interactive documentation)
- **Logs**: `docker-compose logs -f` for real-time debugging

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Network                   │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Next.js    │─────>│   FastAPI    │─────>│  Claude   │ │
│  │   :3000      │<─────│   :8000      │<─────│    API    │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│                              │                               │
│                              │                               │
│                              ▼                               │
│                        ┌──────────┐                          │
│                        │  Qdrant  │                          │
│                        │  :6333   │                          │
│                        └──────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

**Estimated Setup Time**: 10-15 minutes (first time)

Ready to generate amazing content!
