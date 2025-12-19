# Xandeum PNode Analytics - Production Deployment Guide

**Version:** 1.1.0  
**Last Updated:** December 2024  
**Status:** Production-Ready

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Deployment Platforms](#deployment-platforms)
4. [MongoDB Setup](#mongodb-setup)
5. [Configuration](#configuration)
6. [Deployment Process](#deployment-process)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Backup & Recovery](#backup--recovery)

---

## ✅ Pre-Deployment Checklist

### Code Readiness

```bash
# 1. Run comprehensive test suite
python tests/test_comprehensive.py

# 2. Run API endpoint tests
./tests/test_api.sh

# 3. Verify all tests pass
python tests/test_phase4.py
python tests/test_phase5.py

# 4. Check code quality
python -m pylint app/ --errors-only

# 5. Verify environment configuration
python -c "from app.config import *; print('✅ Config loaded')"
```

### Documentation Checklist

- [x] README.md updated with latest features
- [x] API_REFERENCE.md complete
- [x] ARCHITECTURE.md reflects current design
- [x] TESTING_GUIDE.md has all test procedures
- [x] Environment variables documented in .env.example

### Infrastructure Checklist

- [x] MongoDB Atlas cluster created
- [x] Database indexes will be auto-created on first run
- [x] Deployment platform selected
- [ ] Domain name configured (optional)
- [x] SSL/TLS certificate ready (handled by platform)

---

## 🔧 Environment Setup

### Required Environment Variables

Create a `.env` file with these variables:

```bash
# ============================================
# REQUIRED - MongoDB Configuration
# ============================================
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=xandeum-monitor

# ============================================
# OPTIONAL - Performance Tuning
# ============================================
# Data refresh interval (seconds)
CACHE_TTL=60

# ============================================
# OPTIONAL - Network Configuration
# ============================================
# Comma-separated IP nodes (uses defaults if not set)
IP_NODES=173.212.203.145,173.212.220.65,161.97.97.41,192.190.136.36,192.190.136.37,192.190.136.38,192.190.136.28,192.190.136.29,207.244.255.1

# ============================================
# OPTIONAL - Local Development
# ============================================
PORT=8000
```

### Security Best Practices

```bash
# 1. Never commit .env files
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo ".env.local" >> .gitignore

# 2. Use strong MongoDB passwords
# Generate with: openssl rand -base64 32

# 3. Rotate credentials quarterly
# Update MongoDB password every 90 days

# 4. Limit MongoDB network access
# Only whitelist deployment server IPs
```

---

## 🚀 Deployment Platforms

### Option 1: Railway (Recommended) ⭐

**Why Railway:**
- ✅ Automatic HTTPS
- ✅ One-click deployment
- ✅ Built-in monitoring
- ✅ Easy rollbacks
- ✅ Free trial, then $5-20/month

#### Step 1: Install Railway CLI

```bash
# Install
npm i -g @railway/cli

# Verify
railway --version
```

#### Step 2: Initialize Project

```bash
# Login to Railway
railway login

# Initialize in your project directory
cd pnode-aggregation-api
railway init
```

#### Step 3: Configure Environment

```bash
# Set MongoDB URI
railway variables set MONGO_URI="mongodb+srv://..."

# Set database name
railway variables set MONGO_DB="xandeum-monitor"

# Set cache TTL
railway variables set CACHE_TTL=60

# Optional: Set custom IP nodes
railway variables set IP_NODES="173.212.203.145,..."
```

#### Step 4: Create railway.json

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

#### Step 5: Deploy

```bash
# Deploy to Railway
railway up

# View logs
railway logs

# Get deployment URL
railway domain
```

#### Step 6: Verify Deployment

```bash
# Get your Railway URL (e.g., your-app.railway.app)
RAILWAY_URL=$(railway domain)

# Test health endpoint
curl "https://$RAILWAY_URL/health" | jq '.'

# Test root endpoint
curl "https://$RAILWAY_URL/" | jq '.api_name'

# Run full test suite against production
./tests/test_api.sh "$RAILWAY_URL"
```

**Cost:** Free ($5 credit) → $5-20/month depending on usage

---

### Option 2: Heroku (Classic & Reliable)

**Why Heroku:**
- ✅ Mature platform
- ✅ Extensive documentation
- ✅ Add-on marketplace
- ✅ Easy scaling

#### Step 1: Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh

# Windows
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

#### Step 2: Create Heroku App

```bash
# Login
heroku login

# Create app
heroku create pnode-aggregation-api

# Set buildpack
heroku buildpacks:set heroku/python
```

#### Step 3: Configure Environment

```bash
# Set environment variables
heroku config:set MONGO_URI="mongodb+srv://..."
heroku config:set MONGO_DB="xandeum-monitor"
heroku config:set CACHE_TTL=60

# Optional: Custom IP nodes
heroku config:set IP_NODES="173.212.203.145,..."

# Verify configuration
heroku config
```

#### Step 4: Deploy

```bash
# Deploy via Git
git push heroku main

# Or deploy specific branch
git push heroku production:main

# View logs
heroku logs --tail
```

#### Step 5: Scale

```bash
# Start with free dyno
heroku ps:scale web=1

# Upgrade for better performance
heroku ps:type hobby  # $7/month
heroku ps:type standard-1x  # $25/month
heroku ps:type standard-2x  # $50/month
```

#### Step 6: Verify

```bash
# Get app URL
heroku info

# Test deployment
curl "https://your-domain.herokuapp.com/health"

# Run tests
./tests/test_api.sh "https://your-domain.herokuapp.com"
```

**Cost:** Free (550 hours/month) → $7-50/month

---

### Option 3: Render (Simple & Modern)

**Why Render:**
- ✅ Auto-deploy from Git
- ✅ Pull request previews
- ✅ Built-in SSL
- ✅ Generous free tier

#### Step 1: Connect Repository

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select branch (main)

#### Step 2: Configure Service

```yaml
# render.yaml
services:
  - type: web
    name: xandeum-pnode-platform
    env: python
    region: oregon
    plan: free  # or starter ($7/mo)
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: MONGO_URI
        sync: false  # Set in dashboard
      - key: MONGO_DB
        value: xandeum-monitor
      - key: CACHE_TTL
        value: 60
```

#### Step 3: Set Environment Variables

In Render dashboard:
1. Go to Environment
2. Add `MONGO_URI` (mark as secret)
3. Add other variables as needed

#### Step 4: Deploy

- Push to GitHub → Render auto-deploys
- Monitor build logs in dashboard
- Get deployment URL from dashboard

#### Step 5: Verify

```bash
# Test deployment
curl "https://your-domain.onrender.com/health"

# Run test suite
./tests/test_api.sh "https://your-domain.onrender.com"
```

**Cost:** Free → $7-21/month

---

### Option 4: Self-Hosted VPS (Full Control)

**Why Self-Hosted:**
- ✅ Complete control
- ✅ Predictable costs
- ✅ No vendor lock-in
- ✅ Custom optimizations

#### Requirements

- Ubuntu 22.04 LTS
- 2GB RAM minimum (4GB recommended)
- 20GB disk space
- Python 3.11+
- Public IP address

#### Complete Setup Script

```bash
#!/bin/bash
set -e

echo "🚀 Xandeum PNode Platform - VPS Deployment"
echo "============================================"

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install system dependencies
sudo apt install -y nginx certbot python3-certbot-nginx git

# Create application user
echo "👤 Creating application user..."
sudo useradd -m -s /bin/bash xandeum
sudo mkdir -p /opt/xandeum-pnode-platform
sudo chown xandeum:xandeum /opt/xandeum-pnode-platform

# Clone repository
echo "📥 Cloning repository..."
cd /opt/xandeum-pnode-platform
sudo -u xandeum git clone https://github.com/lucadavid075/pnode-aggregation-api.git .

# Create virtual environment
echo "🔧 Setting up Python environment..."
sudo -u xandeum python3.11 -m venv venv
sudo -u xandeum venv/bin/pip install --upgrade pip
sudo -u xandeum venv/bin/pip install -r requirements.txt

# Create .env file
echo "⚙️ Creating environment configuration..."
sudo -u xandeum tee .env > /dev/null <<EOF
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=xandeum-monitor
CACHE_TTL=60
EOF

echo "⚠️  Please edit /opt/xandeum-pnode-analytics/.env with your MongoDB credentials"
echo "Run: sudo nano /opt/xandeum-pnode-analytics/.env"
read -p "Press enter when ready..."

# Create systemd service
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/xandeum-api.service > /dev/null <<EOF
[Unit]
Description=Xandeum PNode Analytics API
After=network.target

[Service]
Type=simple
User=xandeum
WorkingDirectory=/opt/xandeum-pnode-platform
Environment="PATH=/opt/xandeum-pnode-platform/venv/bin"
ExecStart=/opt/xandeum-pnode-platform/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/xandeum-pnode-platform

[Install]
WantedBy=multi-user.target
EOF

# Start service
echo "▶️ Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable xandeum-api
sudo systemctl start xandeum-api

# Check service status
echo "✅ Service status:"
sudo systemctl status xandeum-api --no-pager

# Configure nginx
echo "🌐 Configuring nginx..."
sudo tee /etc/nginx/sites-available/xandeum-api > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (for future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint (for monitoring)
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/xandeum-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Update nginx config with your domain:"
echo "   sudo nano /etc/nginx/sites-available/xandeum-api"
echo ""
echo "2. Get SSL certificate (replace your-domain.com):"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo "3. Test deployment:"
echo "   curl http://localhost/health"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u xandeum-api -f"
echo ""
echo "5. Restart service:"
echo "   sudo systemctl restart xandeum-api"
```

#### Save and Run

```bash
# Save script
nano deploy_vps.sh

# Make executable
chmod +x deploy_vps.sh

# Run
sudo ./deploy_vps.sh
```

#### Post-Setup SSL Certificate

```bash
# Install SSL certificate (replace with your domain)
sudo certbot --nginx -d api.xandeum.com

# Test auto-renewal
sudo certbot renew --dry-run
```

**Cost:** $5-10/month (DigitalOcean, Linode, Vultr)

---

## 🗄️ MongoDB Setup

### MongoDB Atlas (Recommended)

#### Step 1: Create Cluster

1. Go to https://cloud.mongodb.com
2. Sign up / Log in
3. Click "Build a Cluster"
4. Choose:
   - **Tier:** M0 (Free) or M2+ (Paid, $9/mo)
   - **Provider:** AWS, Google Cloud, or Azure
   - **Region:** Choose closest to your app server
   - **Name:** xandeum-cluster

#### Step 2: Configure Security

```bash
# Create database user
Username: xandeum-api
Password: [Generate strong password - save in password manager]
Roles: readWrite on xandeum-monitor database
```

#### Step 3: Network Access

```bash
# For cloud deployments (Railway, Heroku, Render)
Add IP: 0.0.0.0/0 (Allow from anywhere)

# For self-hosted VPS
Add IP: [Your VPS IP address]
```

#### Step 4: Get Connection String

```
mongodb+srv://xandeum-api:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
```

Replace `<password>` with actual password!

#### Step 5: Create Database

```bash
# Connect via MongoDB Compass or CLI
mongosh "mongodb+srv://cluster.mongodb.net/" --username xandeum-api

# Create database
use xandeum-monitor

# Indexes will be auto-created on first API startup
# via setup_indexes() function in app/db.py
```

### Verify MongoDB Connection

```bash
# Test connection from deployment server
python3 << EOF
from pymongo import MongoClient
uri = "mongodb+srv://xandeum-api:PASSWORD@cluster.mongodb.net/"
client = MongoClient(uri)
print("✅ MongoDB connection successful!")
print(f"Databases: {client.list_database_names()}")
EOF
```

---

## ⚙️ Configuration

### Optimal Settings by Network Size

#### Small Network (< 100 nodes)

```bash
CACHE_TTL=60
# Standard refresh, minimal load
```

#### Medium Network (100-500 nodes)

```bash
CACHE_TTL=90
# Slightly slower refresh, better stability
```

#### Large Network (500+ nodes)

```bash
CACHE_TTL=120
# Longer refresh, prevents overload
```

### Performance Tuning

#### For Better Response Times

```bash
# Use MongoDB M2+ cluster (not free tier)
# Add read replicas for geographic distribution
# Upgrade server resources (2x RAM, 2x CPU)
```

#### For Higher Reliability

```bash
# Enable MongoDB backups
# Use multi-region deployment
# Add health check monitoring
```

---

## 🔍 Post-Deployment Verification

### Automated Verification Script

```bash
#!/bin/bash
# verify_deployment.sh

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0

echo "============================================"
echo "Xandeum PNode Analytics - Deployment Test"
echo "Testing: $BASE_URL"
echo "============================================"
echo ""

# Test 1: Health Check
echo -n "1. Health Check... "
HEALTH=$(curl -s "$BASE_URL/health" | jq -r '.status')
if [ "$HEALTH" = "healthy" ]; then
    echo "✅ PASS"
    ((PASSED++))
else
    echo "❌ FAIL (Status: $HEALTH)"
    ((FAILED++))
fi

# Test 2: Root Endpoint
echo -n "2. Root Endpoint... "
API_NAME=$(curl -s "$BASE_URL/" | jq -r '.api_name')
if [ "$API_NAME" = "Xandeum PNode Analytics API" ]; then
    echo "✅ PASS"
    ((PASSED++))
else
    echo "❌ FAIL"
    ((FAILED++))
fi

# Test 3: PNodes Endpoint
echo -n "3. PNodes Endpoint... "
PNODES=$(curl -s "$BASE_URL/pnodes?limit=1" | jq -r '.pnodes[0].address')
if [ -n "$PNODES" ]; then
    echo "✅ PASS"
    ((PASSED++))
else
    echo "❌ FAIL"
    ((FAILED++))
fi

# Test 4: Recommendations
echo -n "4. Recommendations... "
RECS=$(curl -s "$BASE_URL/recommendations?limit=1" | jq -r '.recommendations[0].score')
if [ -n "$RECS" ]; then
    echo "✅ PASS"
    ((PASSED++))
else
    echo "❌ FAIL"
    ((FAILED++))
fi

# Test 5: Network Health
echo -n "5. Network Health... "
HEALTH_SCORE=$(curl -s "$BASE_URL/network/health" | jq -r '.health.health_score')
if [ "$HEALTH_SCORE" != "null" ]; then
    echo "✅ PASS"
    ((PASSED++))
else
    echo "❌ FAIL"
    ((FAILED++))
fi

echo ""
echo "============================================"
echo "Results: $PASSED passed, $FAILED failed"
echo "============================================"

if [ $FAILED -eq 0 ]; then
    echo "✅ Deployment verified successfully!"
    exit 0
else
    echo "❌ Deployment verification failed"
    exit 1
fi
```

### Run Verification

```bash
# Make executable
chmod +x verify_deployment.sh

# Test local deployment
./verify_deployment.sh http://localhost:8000

# Test production deployment
./verify_deployment.sh https://your-app.railway.app
```

### Manual Verification Checklist

```bash
# 1. Health endpoint returns healthy
curl https://your-app.railway.app/health | jq '.status'
# Expected: "healthy"

# 2. Data is fresh (< 2 minutes old)
curl https://your-app.railway.app/health | jq '.snapshot_age_seconds'
# Expected: < 120

# 3. Nodes are being tracked
curl https://your-app.railway.app/ | jq '.system_status.nodes_tracked'
# Expected: > 0

# 4. Background worker is running
curl https://your-app.railway.app/health | jq '.last_updated'
# Should update every 60 seconds

# 5. All endpoints respond
./tests/test_api.sh https://your-app.railway.app
```

---

## 📊 Monitoring & Maintenance

### Set Up Monitoring

#### UptimeRobot (Free)

1. Go to https://uptimerobot.com
2. Add Monitor:
   - **Type:** HTTP(s)
   - **URL:** `https://your-app.railway.app/health`
   - **Monitoring Interval:** 5 minutes
   - **Alert Contacts:** Your email/SMS

#### Better Stack (Paid - Recommended)

```bash
# 1. Sign up at https://betterstack.com
# 2. Create uptime monitor
# 3. Add heartbeat endpoint
# 4. Configure Slack/email alerts
```

### Daily Maintenance Tasks

```bash
# Check health
curl https://your-app.railway.app/health | jq '.'

# View logs
railway logs  # or heroku logs --tail

# Monitor resource usage
railway status  # or heroku ps
```

### Weekly Maintenance Tasks

```bash
# 1. Review error logs
railway logs | grep ERROR

# 2. Check MongoDB storage
# Login to MongoDB Atlas → Metrics

# 3. Verify backup status
# MongoDB Atlas → Backups

# 4. Review performance
curl https://your-app.railway.app/network/analytics | jq '.performance'
```

### Monthly Maintenance Tasks

```bash
# 1. Update dependencies
pip list --outdated
pip install --upgrade [package]

# 2. Review and prune old data
# Automatic (30-day retention)

# 3. Rotate MongoDB credentials
# Update password in MongoDB Atlas
# Update MONGO_URI environment variable

# 4. Review cost/usage
# Check platform billing dashboard
```

---

## 🐛 Troubleshooting

### Issue: Health Check Returns "unhealthy"

**Symptoms:**
```json
{"status": "unhealthy", "reason": "No snapshot available"}
```

**Solutions:**

```bash
# 1. Check background worker logs
railway logs | grep "Background worker"

# 2. Verify MongoDB connection
railway logs | grep "MongoDB"

# 3. Check IP nodes are accessible
for ip in 173.212.203.145 173.212.220.65; do
  curl -X POST http://$ip:6000/rpc \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"get-version","id":1}'
done

# 4. Restart application
railway restart  # or heroku restart
```

---

### Issue: Slow Response Times

**Symptoms:**
- Endpoints taking > 2 seconds
- Timeout errors

**Solutions:**

```bash
# 1. Check MongoDB indexes
mongosh "mongodb+srv://..." --eval "db.pnodes_registry.getIndexes()"

# 2. Upgrade MongoDB tier
# M0 (free) → M2 ($9/mo) for better performance

# 3. Increase CACHE_TTL
railway variables set CACHE_TTL=90

# 4. Upgrade server resources
railway settings  # Upgrade plan
```

---

### Issue: MongoDB Connection Errors

**Symptoms:**
```
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions:**

```bash
# 1. Verify connection string format
echo $MONGO_URI
# Should be: mongodb+srv://user:pass@cluster.mongodb.net/

# 2. Check IP whitelist
# MongoDB Atlas → Network Access
# Add 0.0.0.0/0 for cloud deployments

# 3. Verify credentials
# Try connecting with mongosh

# 4. Check MongoDB cluster status
# MongoDB Atlas → Clusters (should show "Active")
```

---

### Issue: Background Worker Not Updating

**Symptoms:**
- `snapshot_age_seconds` keeps growing
- Data is stale

**Solutions:**

```bash
# 1. Check worker logs
railway logs | grep "Aggregation cycle"

# 2. Verify IP nodes respond
python verify_pnode.py 173.212.203.145

# 3. Check for RPC errors
railway logs | grep "RPC"

# 4. Restart application
railway restart

# 5. If persistent, check CACHE_TTL
railway variables get CACHE_TTL
```

---

## 💾 Backup & Recovery

### Automated MongoDB Backups

#### MongoDB Atlas (M2+ clusters)

```bash
# Backups are automatic on paid tiers
# Check: MongoDB Atlas → Clusters → Backup
# Retention: 7 days (configurable)
```

#### Manual Backup

```bash
# Backup entire database
mongodump --uri="mongodb+srv://..." --out=backup-$(date +%Y%m%d)

# Backup specific collection
mongodump --uri="mongodb+srv://..." \
  --db=xandeum-monitor \
  --collection=pnodes_registry \
  --out=backup-registry

# Compress backup
tar -czf backup-$(date +%Y%m%d).tar.gz backup-$(date +%Y%m%d)/
```

### Restore from Backup

```bash
# Restore entire database
mongorestore --uri="mongodb+srv://..." backup-20241219/

# Restore specific collection
mongorestore --uri="mongodb+srv://..." \
  --db=xandeum-monitor \
  --collection=pnodes_registry \
  backup-registry/xandeum-monitor/pnodes_registry.bson
```

### Disaster Recovery Plan

#### Scenario 1: Application Crash

```bash
# 1. Check logs
railway logs

# 2. Restart application
railway restart

# 3. Verify recovery
curl https://your-app.railway.app/health

# 4. Monitor for stability
watch -n 10 'curl -s https://your-app.railway.app/health | jq ".status"'
```

#### Scenario 2: Database Corruption

```bash
# 1. Stop application
railway service stop

# 2. Restore from backup
mongorestore --uri="mongodb+srv://..." backup-latest/

# 3. Verify data integrity
mongosh "mongodb+srv://..." --eval "db.pnodes_registry.count()"

# 4. Restart application
railway service start

# 5. Force fresh snapshot
# Wait 60 seconds for background worker
```

#### Scenario 3: Complete Data Loss

```bash
# 1. Create new MongoDB cluster
# 2. Update MONGO_URI environment variable
# 3. Deploy application
# 4. Background worker will rebuild from scratch
# Note: Historical data (30 days) will be lost
```

---

## 📈 Scaling Guide

### When to Scale

Monitor these metrics:

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Response Time (p95) | > 500ms | > 1000ms | Upgrade server |
| CPU Usage | > 70% | > 85% | Add resources |
| Memory Usage | > 80% | > 90% | Upgrade RAM |
| Error Rate | > 1% | > 5% | Investigate |
| Snapshot Age | > 120s | > 300s | Check worker |

### Vertical Scaling (Recommended First)

```bash
# Railway
railway settings  # Upgrade to Pro plan ($20/mo)

# Heroku
heroku ps:type standard-2x  # $50/mo, 2x resources

# MongoDB
# M0 (free) → M2 ($9/mo) → M5 ($25/mo)
```

### Horizontal Scaling (Future)

**Requires:**
- Redis for distributed locking
- Load balancer
- Multiple API instances

See [ARCHITECTURE.md](ARCHITECTURE.md) for horizontal scaling design.

---

## ✅ Deployment Checklist

### Pre-Deploy

- [ ] All tests pass
- [ ] MongoDB cluster ready
- [ ] Environment variables configured
- [ ] Documentation updated

### Deploy

- [ ] Application deployed
- [ ] Health endpoint responds
- [ ] Background worker running
- [ ] Data is fresh (< 2 min)

### Post-Deploy

- [ ] All endpoints tested
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Team notified

---

## 📞 Support

### Getting Help

1. **Check logs first**
   ```bash
   railway logs  # or heroku logs --tail
   ```

2. **Review troubleshooting section**
   - Common issues documented above

3. **Community support**
   - Discord: https://discord.gg/uqRSmmM5m

---

<div align="center">

**Xandeum PNode Analytics - Deployment Guide v1.1.0**

[Back to README](../README.md) • [Architecture](ARCHITECTURE.md) • [API Reference](API_REFERENCE.md)

*Your deployment should take 15-30 minutes*

🚀 **Ready to deploy!**

</div>