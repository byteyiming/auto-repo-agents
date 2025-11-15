#!/bin/bash
# Oracle Cloud Deployment Script
# This script helps automate the deployment process on Oracle Cloud

set -e

echo "🚀 OmniDoc Oracle Cloud Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please do not run as root. Use a regular user with sudo privileges.${NC}"
   exit 1
fi

# Configuration
APP_DIR="/opt/omnidoc"
APP_USER=$(whoami)

echo -e "${GREEN}Step 1: Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y git curl wget build-essential postgresql postgresql-contrib redis-server

echo -e "${GREEN}Step 2: Installing Node.js 18+...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

echo -e "${GREEN}Step 3: Installing Python 3.9+...${NC}"
sudo apt-get install -y python3.9 python3.9-venv python3-pip

echo -e "${GREEN}Step 4: Setting up PostgreSQL...${NC}"
read -sp "Enter PostgreSQL password for 'omnidoc' user: " DB_PASSWORD
echo

sudo -u postgres psql <<EOF
CREATE DATABASE omnidoc;
CREATE USER omnidoc WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE omnidoc TO omnidoc;
\q
EOF

echo -e "${GREEN}Step 5: Setting up Redis...${NC}"
read -sp "Enter Redis password: " REDIS_PASSWORD
echo

sudo sed -i "s/# requirepass foobared/requirepass $REDIS_PASSWORD/" /etc/redis/redis.conf
sudo systemctl restart redis-server

echo -e "${GREEN}Step 6: Cloning repository...${NC}"
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p $APP_DIR
    read -p "Enter GitHub repository URL (or press Enter for default): " REPO_URL
    REPO_URL=${REPO_URL:-"https://github.com/yimgao/OmniDoc.git"}
    sudo git clone $REPO_URL $APP_DIR
    sudo chown -R $APP_USER:$APP_USER $APP_DIR
else
    echo -e "${YELLOW}Directory $APP_DIR already exists. Skipping clone.${NC}"
fi

cd $APP_DIR

echo -e "${GREEN}Step 7: Running setup script...${NC}"
./scripts/setup.sh

echo -e "${GREEN}Step 8: Configuring environment...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file with production settings...${NC}"
    cat > .env <<EOF
# Database
DATABASE_URL=postgresql://omnidoc:$DB_PASSWORD@localhost:5432/omnidoc

# Redis
REDIS_URL=redis://:$REDIS_PASSWORD@localhost:6379/0

# Security
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=prod

# CORS - Production domain
ALLOWED_ORIGINS=https://omnidoc.info,https://www.omnidoc.info

# LLM Provider (update with your API key)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF
    echo -e "${GREEN}.env file created. Please update GEMINI_API_KEY with your actual API key.${NC}"
    read -p "Press Enter to continue..."
fi

echo -e "${GREEN}Step 9: Installing Nginx...${NC}"
sudo apt-get install -y nginx

echo -e "${GREEN}Step 9.1: Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/omnidoc > /dev/null <<EOF
# Frontend (Next.js)
server {
    listen 80;
    server_name omnidoc.info www.omnidoc.info;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

# Backend API (FastAPI)
server {
    listen 80;
    server_name api.omnidoc.info;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/omnidoc /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${GREEN}Step 9.2: Setting up SSL with Let's Encrypt...${NC}"
sudo apt-get install -y certbot python3-certbot-nginx
echo -e "${YELLOW}Setting up SSL certificates for omnidoc.info...${NC}"
read -p "Enter your email for Let's Encrypt notifications: " CERTBOT_EMAIL
CERTBOT_EMAIL=${CERTBOT_EMAIL:-"admin@omnidoc.info"}
echo -e "${GREEN}Obtaining SSL certificates...${NC}"
sudo certbot --nginx -d omnidoc.info -d www.omnidoc.info -d api.omnidoc.info --non-interactive --agree-tos --email $CERTBOT_EMAIL --redirect

echo -e "${GREEN}SSL certificates configured!${NC}"
echo -e "${GREEN}Auto-renewal is configured automatically.${NC}"

echo -e "${GREEN}Step 10: Creating systemd services...${NC}"

# Backend service
sudo tee /etc/systemd/system/omnidoc-backend.service > /dev/null <<EOF
[Unit]
Description=OmniDoc Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/.venv/bin"
ExecStart=$APP_DIR/.venv/bin/python backend/uvicorn_dev.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery service
sudo tee /etc/systemd/system/omnidoc-celery.service > /dev/null <<EOF
[Unit]
Description=OmniDoc Celery Worker
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/.venv/bin"
ExecStart=$APP_DIR/.venv/bin/celery -A src.tasks.celery_app worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Step 11: Setting up PM2 for frontend...${NC}"
sudo npm install -g pm2

echo -e "${GREEN}Step 12: Configuring firewall...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo -e "${GREEN}Step 13: Enabling services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable omnidoc-backend omnidoc-celery
sudo systemctl start omnidoc-backend omnidoc-celery

# Build frontend
echo -e "${GREEN}Step 13.1: Building frontend...${NC}"
cd $APP_DIR/frontend

# Create frontend .env.local with production API URL
cat > .env.local <<EOF
NEXT_PUBLIC_API_BASE=https://api.omnidoc.info
EOF

npm run build
pm2 start npm --name "omnidoc-frontend" -- start
pm2 save
pm2 startup

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${GREEN}Production URLs:${NC}"
echo "  Frontend: https://omnidoc.info"
echo "  API: https://api.omnidoc.info"
echo "  API Docs: https://api.omnidoc.info/docs"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "1. Update GEMINI_API_KEY in .env file with your actual API key"
echo "2. Configure Oracle Cloud security rules to allow HTTP/HTTPS traffic"
echo "3. Ensure DNS records point to this server:"
echo "   - A record: omnidoc.info → $(curl -s ifconfig.me)"
echo "   - A record: www.omnidoc.info → $(curl -s ifconfig.me)"
echo "   - A record: api.omnidoc.info → $(curl -s ifconfig.me)"
echo ""
echo "Check service status:"
echo "  sudo systemctl status omnidoc-backend"
echo "  sudo systemctl status omnidoc-celery"
echo "  sudo systemctl status nginx"
echo "  pm2 status"
echo ""
echo "View logs:"
echo "  sudo journalctl -u omnidoc-backend -f"
echo "  sudo journalctl -u omnidoc-celery -f"
echo "  pm2 logs omnidoc-frontend"

