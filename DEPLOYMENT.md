# OmniDoc Deployment Guide

Complete guide for deploying OmniDoc in production environments.

## 📋 Table of Contents

1. [Deployment Strategy](#deployment-strategy)
2. [Architecture Overview](#architecture-overview)
3. [Oracle Cloud Deployment](#oracle-cloud-deployment)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Environment Configuration](#environment-configuration)
6. [Pre-Deployment Checklist](#pre-deployment-checklist)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Troubleshooting](#troubleshooting)

## 🎯 Deployment Strategy

**Recommendation: Deploy First, Then Iterate**

See [DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md) for detailed strategy on when to deploy vs. when to update UI first.

### Quick Decision Guide

- ✅ **Deploy Now** if:
  - Core functionality works
  - Critical bugs are fixed
  - Basic accessibility is in place
  - You want real user feedback

- ⏸️ **Wait** if:
  - Critical security issues exist
  - Core features are broken
  - No basic error handling

## 🏗️ Architecture Overview

### Production Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Vercel)      │
│ omnidoc.info    │
└────────┬────────┘
         │ HTTPS
         │
┌────────▼────────┐
│   Backend API   │
│ (Oracle Cloud)  │
│ api.omnidoc.info│
└────┬───────┬────┘
     │       │
┌────▼───┐ ┌─▼──────┐
│ Neon   │ │Upstash │
│  DB    │ │ Redis  │
└────────┘ └────────┘
```

### Components

- **Frontend**: Next.js on Vercel (https://omnidoc.info)
- **Backend**: FastAPI on Oracle Cloud (https://api.omnidoc.info)
- **Database**: Neon (managed PostgreSQL)
- **Cache/Queue**: Upstash (managed Redis)
- **Task Queue**: Celery workers on Oracle Cloud

## 🚀 Deployment Options

### Option 1: Oracle Cloud (Current)

See [Oracle Cloud Deployment](#oracle-cloud-deployment) section below.

### Option 2: Azure (Alternative)

See [Azure Deployment Guide](AZURE_DEPLOYMENT.md) for complete Azure setup instructions.

**Quick Comparison:**
- **Oracle Cloud**: Free tier available, more manual setup
- **Azure**: Easier deployment (App Service), less free tier options

## 🚀 Oracle Cloud Deployment

### Prerequisites

- Oracle Cloud Free Tier account
- Ubuntu 22.04 LTS instance (Always Free eligible)
- Domain name configured (omnidoc.info)
- SSH access to your instance

### Quick Deployment

Use the automated deployment script:

```bash
# On your Oracle Cloud instance
git clone https://github.com/yimgao/OmniDoc.git
cd OmniDoc
chmod +x scripts/deploy_oracle_cloud.sh
./scripts/deploy_oracle_cloud.sh
```

The script will:
1. ✅ Install system dependencies (Node.js, Python, Nginx)
2. ✅ Configure Neon database (managed PostgreSQL)
3. ✅ Configure Upstash Redis (managed Redis)
4. ✅ Set up environment variables
5. ✅ Initialize database tables
6. ✅ Configure Nginx for API endpoint
7. ✅ Set up SSL certificates
8. ✅ Create systemd services
9. ✅ Start all services

### Manual Deployment Steps

<details>
<summary>Click to expand detailed manual deployment steps</summary>

#### 1. Initial Server Setup

```bash
# Connect to your instance
ssh ubuntu@<your-server-ip>

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install basic tools
sudo apt-get install -y git curl wget build-essential
```

#### 2. Install Node.js and Python

```bash
# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python 3.9+
sudo apt-get install -y python3.9 python3.9-venv python3-pip
```

#### 3. Configure Environment

```bash
# Clone repository
git clone https://github.com/yimgao/OmniDoc.git
cd OmniDoc

# Copy production environment file
cp .env.production .env

# Update with your API keys
nano .env
# Set GEMINI_API_KEY and JWT_SECRET_KEY
```

#### 4. Setup Application

```bash
# Run setup script
./scripts/setup.sh

# Initialize database
./scripts/init_database.sh
```

#### 5. Configure Nginx

The deployment script automatically configures Nginx. For manual setup, see the script's Nginx configuration section.

#### 6. Setup SSL

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.omnidoc.info --non-interactive --agree-tos --email your-email@example.com --redirect
```

#### 7. Create Systemd Services

The deployment script automatically creates services. For manual setup, see the script's systemd configuration section.

#### 8. Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable omnidoc-backend omnidoc-celery
sudo systemctl start omnidoc-backend omnidoc-celery
```

</details>

### Key Configuration

**Environment Variables** (`.env`):
- Use `.env.production` as template
- Update `GEMINI_API_KEY` with your actual API key
- Database and Redis are pre-configured for production

**Services**:
- Backend: `sudo systemctl status omnidoc-backend`
- Celery: `sudo systemctl status omnidoc-celery`
- Nginx: `sudo systemctl status nginx`

## 🌐 Frontend Deployment (Vercel)

### Quick Setup

1. Go to https://vercel.com
2. Import your GitHub repository
3. Configure:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (or `pnpm build`)
   - **Output Directory**: `.next`
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_BASE=https://api.omnidoc.info
   ```
5. Deploy!

### Custom Domain

1. Go to Project Settings → Domains
2. Add `omnidoc.info` and `www.omnidoc.info`
3. Follow Vercel's DNS instructions

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed instructions.

## ⚙️ Environment Configuration

### Backend Environment Files

**Development** (`.env.development`):
- Local PostgreSQL and Redis
- DEBUG logging
- Development CORS settings

**Production** (`.env.production`):
- Neon database (managed PostgreSQL)
- Upstash Redis (managed Redis)
- Production CORS settings
- INFO/JSON logging

**Usage**:
```bash
# Development
cp .env.development .env

# Production
cp .env.production .env
# Then update GEMINI_API_KEY and JWT_SECRET_KEY
```

### Frontend Environment Files

**Development** (`frontend/.env.development`):
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

**Production** (`frontend/.env.production`):
```
NEXT_PUBLIC_API_BASE=https://api.omnidoc.info
```

**For Vercel**: Set environment variables in Vercel dashboard.

## ✅ Pre-Deployment Checklist

### Code Readiness
- [ ] All tests pass (`pytest`)
- [ ] No linter errors
- [ ] Documentation updated

### Security
- [ ] Review [SECURITY.md](SECURITY.md) checklist
- [ ] Environment variables secured
- [ ] CORS configured for production domains
- [ ] Rate limiting configured
- [ ] SSL/TLS certificates configured

### Database & Services
- [ ] Neon database configured and accessible
- [ ] Upstash Redis configured and accessible
- [ ] Database tables initialized (`./scripts/init_database.sh`)
- [ ] Connection strings tested

### Configuration
- [ ] `.env` file configured for production
- [ ] `GEMINI_API_KEY` set
- [ ] `JWT_SECRET_KEY` generated (use `openssl rand -hex 32`)
- [ ] `ALLOWED_ORIGINS` set to production domains
- [ ] Logging level set appropriately

### Infrastructure
- [ ] Backend services running
- [ ] Celery workers running
- [ ] Nginx configured
- [ ] SSL certificates installed
- [ ] DNS configured correctly

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for complete checklist.

## 🔍 Post-Deployment Verification

### Health Checks

```bash
# Backend health
curl https://api.omnidoc.info/health

# API documentation
curl https://api.omnidoc.info/docs

# Database connection
psql "$DATABASE_URL" -c "SELECT 1;"

# Redis connection
redis-cli -u "$REDIS_URL" ping
```

### Service Status

```bash
# Check services
sudo systemctl status omnidoc-backend
sudo systemctl status omnidoc-celery
sudo systemctl status nginx

# View logs
sudo journalctl -u omnidoc-backend -f
sudo journalctl -u omnidoc-celery -f
```

### Frontend Verification

1. Visit https://omnidoc.info
2. Test document generation
3. Verify WebSocket connections work
4. Check browser console for errors

## 🐛 Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check logs
sudo journalctl -u omnidoc-backend -n 50

# Verify environment variables
cat .env | grep -v "^#"

# Test database connection
psql "$DATABASE_URL" -c "SELECT 1;"
```

**Celery not processing tasks:**
```bash
# Check worker status
sudo systemctl status omnidoc-celery

# Check Redis connection
redis-cli -u "$REDIS_URL" ping

# View worker logs
sudo journalctl -u omnidoc-celery -f
```

**CORS errors:**
- Verify `ALLOWED_ORIGINS` includes your frontend domain
- Check backend logs for CORS errors
- Restart backend: `sudo systemctl restart omnidoc-backend`

**Database connection issues:**
- Verify `DATABASE_URL` is correct
- Check Neon dashboard for service status
- Ensure SSL mode is set: `?sslmode=require`

**Redis connection issues:**
- Verify `REDIS_URL` is correct
- Check Upstash dashboard for service status
- Test connection: `redis-cli -u "$REDIS_URL" ping`

### Getting Help

- Check [MAINTENANCE.md](MAINTENANCE.md) for detailed troubleshooting
- Review logs in `logs/` directory
- Check service status with systemctl
- Verify environment variables are set correctly

## 📚 Additional Resources

### Setup Guides
- [Neon Database Setup](NEON_SETUP.md) - Configure managed PostgreSQL
- [Upstash Redis Setup](UPSTASH_SETUP.md) - Configure managed Redis
- [Vercel Deployment](VERCEL_DEPLOYMENT.md) - Frontend deployment
- [Azure Deployment](AZURE_DEPLOYMENT.md) - Azure deployment guide (alternative to Oracle Cloud)

### Documentation
- [Backend Guide](BACKEND.md) - API and architecture
- [Frontend Guide](FRONTEND.md) - Frontend development
- [Security Guide](SECURITY.md) - Security configuration
- [Maintenance Guide](MAINTENANCE.md) - Operations and maintenance

### Production Domain
- [Production Domain Config](PRODUCTION_DOMAIN.md) - Domain and DNS setup

## 🔄 Migration from Development

### Key Changes

**Before (Development)**:
- Local PostgreSQL
- Local Redis
- SQLite (old)

**After (Production)**:
- Neon (managed PostgreSQL)
- Upstash (managed Redis)
- All data in database (no file storage)

### Migration Steps

1. Export data from local database (if needed):
   ```bash
   pg_dump -h localhost -U omnidoc omnidoc > backup.sql
   ```

2. Import to Neon:
   ```bash
   psql "$DATABASE_URL" < backup.sql
   ```

3. Update `.env` with production connection strings
4. Restart services

## 📝 Next Steps

After deployment:

1. **Monitor**: Set up monitoring and alerting
2. **Backup**: Configure automated backups
3. **Optimize**: Monitor performance and optimize as needed
4. **Iterate**: Use user feedback to prioritize improvements

---

**Need Help?** Check the troubleshooting sections or open an issue on GitHub.

