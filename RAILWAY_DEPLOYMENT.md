# Railway Deployment Guide

Complete guide for deploying OmniDoc backend on Railway.

## 🚀 Quick Start

### Prerequisites

- Railway account (https://railway.app)
- GitHub account (for repository connection)
- Neon database (see [NEON_SETUP.md](NEON_SETUP.md))
- Upstash Redis (see [UPSTASH_SETUP.md](UPSTASH_SETUP.md))

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Sign up or log in
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Select your OmniDoc repository

### Step 2: Configure Backend Service

1. Railway will detect the `Dockerfile`
2. Click on the service to configure it
3. Set the following:

**Service Settings:**
- **Name**: `omnidoc-backend`
- **Root Directory**: `/` (root of repository)
- **Dockerfile Path**: `Dockerfile` (default, should auto-detect)

**Note**: The Dockerfile defaults to running the API server. No custom start command needed for the backend.

### Step 3: Configure Environment Variables

Go to **Variables** tab and add:

#### Database (Neon)
```
DATABASE_URL=postgresql://neondb_owner:npg_wUg5P3SnCMcF@ep-divine-meadow-a4epnyhw-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

#### Redis (Upstash)
```
REDIS_URL=redis://default:AXVjAAIncDJlNDY0OGUwNzdkMjc0M2U5OGE2Yzg4ZGUzYWU3YWVlZXAyMzAwNTE@right-loon-30051.upstash.io:6379
UPSTASH_REDIS_REST_URL=https://right-loon-30051.upstash.io
UPSTASH_REDIS_REST_TOKEN=AXVjAAIncDJlNDY0OGUwNzdkMjc0M2U5OGE2Yzg4ZGUzYWU3YWVlZXAyMzAwNTE
```

#### LLM Provider
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Environment
```
ENVIRONMENT=prod
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### CORS
```
ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info,https://*.vercel.app
```

#### Security
```
JWT_SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

#### Rate Limiting (Gemini Free Tier)
```
RATE_LIMIT_PER_MINUTE=2
RATE_LIMIT_PER_DAY=50
```

#### Backend
```
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### Step 4: Configure Port

1. Go to **Settings** → **Networking**
2. Set **Port**: `8000`
3. Railway will automatically generate a public URL

### Step 5: Deploy

1. Click **"Deploy"** or push to your main branch
2. Railway will automatically build and deploy
3. Wait for deployment to complete (2-5 minutes)

### Step 6: Configure Custom Domain (Optional)

1. Go to **Settings** → **Domains**
2. Click **"Custom Domain"**
3. Add `api.omnidoc.info`
4. Follow DNS configuration instructions
5. Railway will automatically configure SSL

## 🔄 Setting Up Celery Worker

### Create Separate Service

1. In your Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select the same repository (same as backend)
3. Configure:
   - **Name**: `omnidoc-celery-worker`
   - **Root Directory**: `/`
   - **Dockerfile Path**: `Dockerfile` (same as backend)

4. **Set Custom Start Command**:
   - Go to **Settings** → **Deploy**
   - Scroll to **"Custom Start Command"**
   - Click **"+ Start Command"**
   - Enter:
     ```
     celery -A src.tasks.celery_app worker --loglevel=info --concurrency=1
     ```

5. **Configure Environment Variables**:
   - Go to **Variables** tab
   - Add the same environment variables as backend (except `ALLOWED_ORIGINS` and `JWT_SECRET_KEY` which are not needed for Celery)

6. **Configure Port** (optional, Celery doesn't need HTTP port):
   - Go to **Settings** → **Networking**
   - Railway may still require a port, but Celery won't use it

7. Deploy!

## 🔄 Updating Backend

### Automatic Updates (Recommended)

Railway automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "feat: update backend"
git push origin main
```

Railway will:
1. Detect the push
2. Build new Docker image
3. Deploy automatically

### Manual Deploy

1. Go to Railway dashboard
2. Click on your service
3. Click **"Redeploy"**

## 📊 Monitoring

### View Logs

1. Go to your service in Railway
2. Click **"Logs"** tab
3. View real-time logs

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request count

## 💰 Pricing

Railway offers:
- **Free**: $5/month credit
- **Pro**: $20/month (more resources)
- **Team**: Custom pricing

For most projects, the free tier is sufficient.

## 🐛 Troubleshooting

### Build Fails

1. Check logs in Railway dashboard
2. Verify Dockerfile is correct
3. Ensure all dependencies are in `requirements.txt`

### Service Won't Start

1. Check environment variables are set correctly
2. Verify `DATABASE_URL` and `REDIS_URL` are correct
3. Check logs for specific errors

### Database Connection Issues

1. Verify `DATABASE_URL` is correct
2. Check Neon dashboard for service status
3. Ensure SSL mode is set: `?sslmode=require`

### Redis Connection Issues

1. Verify `REDIS_URL` is correct
2. Check Upstash dashboard for service status
3. Test connection: `redis-cli -u "$REDIS_URL" ping`

## 🔗 Related Documentation

- [Vercel Deployment](VERCEL_DEPLOYMENT.md) - Frontend deployment
- [Neon Setup](NEON_SETUP.md) - Database setup
- [Upstash Setup](UPSTASH_SETUP.md) - Redis setup

