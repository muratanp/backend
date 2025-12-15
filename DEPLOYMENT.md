# Production Deployment Guide

Complete guide for deploying Xandeum pNode Analytics API to production.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Deployment Platforms](#deployment-platforms)
4. [MongoDB Setup](#mongodb-setup)
5. [Configuration](#configuration)
6. [Deployment Process](#deployment-process)
7. [Post-Deployment](#post-deployment)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### ✅ Code Readiness

- [ ] All tests pass (`python test_comprehensive.py`)
- [ ] Performance benchmarks met
- [ ] No TODO/FIXME comments in production code
- [ ] Error handling comprehensive
- [ ] Logging configured properly

### ✅ Documentation

- [ ] README.md updated
- [ ] API reference complete
- [ ] Deployment guide reviewed
- [ ] Environment variables documented

### ✅ Infrastructure

- [ ] MongoDB Atlas cluster created
- [ ] Database indexes created
- [ ] Deployment platform selected
- [ ] Domain name configured (optional)
- [ ] SSL certificate ready (optional)

---

## Environment Setup

### Required Environment Variables

Create a `.env` file:

```bash
# MongoDB Configuration (REQUIRED)
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=xandeum-monitor

# Cache Configuration
CACHE_TTL=60

# IP Nodes (Optional - uses defaults if not set)
IP_NODES=173.212.203.145,173.212.220.65,161.97.97.41,192.190.136.36,192.190.136.37,192.190.136.38,192.190.136.28,192.190.136.29,207.244.255.1

# Port (Optional - for local testing)
PORT=8000
```

### Security Considerations

**Never commit `.env` to git!**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo ".env.local" >> .gitignore
```

---

## Deployment Platforms

### Option 1: Heroku (Easiest)

#### 1. Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
```

#### 2. Create Heroku App

```bash
heroku login
heroku create xandeum-pnode-analytics

# Set buildpack
heroku buildpacks:set heroku/python
```

#### 3. Configure Environment

```bash
# Set MongoDB URI
heroku config:set MONGO_URI="mongodb+srv://..."

# Set database name
heroku config:set MONGO_DB="xandeum-monitor"

# Set cache TTL
heroku config:set CACHE_TTL=60

# Optional: Set IP nodes
heroku config:set IP_NODES="173.212.203.145,173.212.220.65,..."
```

#### 4. Deploy

```bash
git push heroku main

# Check logs
heroku logs --tail
```

#### 5. Scale

```bash
# Use basic dyno (free/hobby)
heroku ps:scale web=1

# Or upgrade to standard dyno
heroku ps:type standard-1x
```

**Cost:** $7-25/month depending on dyno type

---

### Option 2: Railway (Modern Alternative)

#### 1. Install Railway CLI

```bash
npm i -g @railway/cli
```

#### 2. Initialize Project

```bash
railway login
railway init
```

#### 3. Configure Environment

Create `railway.json`:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

#### 4. Set Environment Variables

```bash
railway variables set MONGO_URI="mongodb+srv://..."
railway variables set MONGO_DB="xandeum-monitor"
railway variables set CACHE_TTL=60
```

#### 5. Deploy

```bash
railway up
```

**Cost:** $5-20/month

---

### Option 3: Render (Simple & Reliable)

#### 1. Connect Repository

- Go to https://render.com
- Click "New +" → "Web Service"
- Connect your GitHub repository

#### 2. Configure Service

```yaml
# render.yaml
services:
  - type: web
    name: xandeum-pnode-analytics
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: MONGO_URI
        sync: false  # Add manually in dashboard
      - key: MONGO_DB
        value: xandeum-monitor
      - key: CACHE_TTL
        value: 60
```

#### 3. Deploy

- Push to GitHub
- Render auto-deploys on push to main branch

**Cost:** $7-21/month

---

### Option 4: DigitalOcean App Platform

#### 1. Create App

```bash
# Install doctl
brew install doctl

# Login
doctl auth init
```

#### 2. Configure via UI

- Go to DigitalOcean App Platform
- Create New App from GitHub
- Select repository

#### 3. App Spec

```yaml
name: xandeum-pnode-analytics
services:
  - name: web
    github:
      repo: your-username/repo-name
      branch: main
    build_command: pip install -r requirements.txt
    run_command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    health_check:
      http_path: /health
    envs:
      - key: MONGO_URI
        scope: RUN_TIME
        type: SECRET
      - key: MONGO_DB
        value: xandeum-monitor
      - key: CACHE_TTL
        value: "60"
```

**Cost:** $5-12/month

---

### Option 5: Self-Hosted (VPS)

#### Requirements

- Ubuntu 22.04 LTS
- 2GB RAM minimum
- 20GB disk space
- Python 3.11+

#### Setup Script

```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install nginx
sudo apt install nginx -y

# Clone repository
cd /opt
sudo git clone https://github.com/your-repo/xandeum-pnode-analytics.git
cd xandeum-pnode-analytics

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
sudo nano .env
# Add your environment variables

# Create systemd service
sudo tee /etc/systemd/system/xandeum-api.service > /dev/null <<EOF
[Unit]
Description=Xandeum pNode Analytics API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/xandeum-pnode-analytics
Environment="PATH=/opt/xandeum-pnode-analytics/venv/bin"
ExecStart=/opt/xandeum-pnode-analytics/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable xandeum-api
sudo systemctl start xandeum-api

# Configure nginx
sudo tee /etc/nginx/sites-available/xandeum-api > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/xandeum-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "API running at http://your-domain.com"
```

**Cost:** $5-10/month (VPS)

---

## MongoDB Setup

### MongoDB Atlas (Recommended)

#### 1. Create Cluster

1. Go to https://mongodb.com/cloud/atlas
2. Create free account
3. Create cluster:
   - **Tier:** M0 (Free) or M2+ (Paid)
   - **Region:** Choose closest to your app
   - **Name:** xandeum-cluster

#### 2. Create Database User

```
Username: xandeum-api
Password: [generate strong password]
Roles: readWrite
```

#### 3. Whitelist IPs

For cloud platforms, whitelist all IPs:
```
0.0.0.0/0
```

For self-hosted, whitelist your VPS IP.

#### 4. Get Connection String

```
mongodb+srv://xandeum-api:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
```

Replace `<password>` with your actual password.

#### 5. Create Database

```javascript
// Connect via MongoDB Compass or CLI
use xandeum-monitor

// Indexes will be created automatically on first run
// via setup_indexes() in app/db.py
```

---

## Configuration

### Optimal Settings

```bash
# Production .env
MONGO_URI=mongodb+srv://...         # Your Atlas connection string
MONGO_DB=xandeum-monitor            # Database name
CACHE_TTL=60                        # Refresh every 60 seconds
IP_NODES=173.212.203.145,...        # Comma-separated IP nodes

# Optional: Increase if network is slow
# CACHE_TTL=120
```

### Performance Tuning

**For < 100 nodes:**
```bash
CACHE_TTL=60
```

**For 100-500 nodes:**
```bash
CACHE_TTL=90
```

**For 500+ nodes:**
```bash
CACHE_TTL=120
```

---

## Deployment Process

### Step-by-Step Deployment

#### 1. Prepare Code

```bash
# Run tests
python test_comprehensive.py

# Verify all tests pass
# Fix any failures before deploying
```

#### 2. Create Production Branch

```bash
git checkout -b production
git push origin production
```

#### 3. Deploy to Platform

**Heroku:**
```bash
git push heroku production:main
```

**Railway:**
```bash
railway up --detach
```

**Render:**
```bash
# Auto-deploys on git push
git push origin production
```

#### 4. Verify Deployment

```bash
# Check health
curl https://your-app.com/health

# Check data
curl https://your-app.com/pnodes?limit=5
```

#### 5. Monitor Logs

**Heroku:**
```bash
heroku logs --tail
```

**Railway:**
```bash
railway logs
```

**Self-hosted:**
```bash
sudo journalctl -u xandeum-api -f
```

---

## Post-Deployment

### Verification Checklist

- [ ] Health endpoint returns `healthy`
- [ ] All endpoints return 200 status
- [ ] Data is updating (check snapshot_age_seconds)
- [ ] Background worker is running
- [ ] MongoDB connection stable
- [ ] No errors in logs

### Performance Check

```bash
# Run comprehensive tests against production
python test_comprehensive.py --url https://your-app.com

# Check response times
time curl https://your-app.com/pnodes?limit=100
```

### Set Up Monitoring

#### UptimeRobot (Free)

1. Go to https://uptimerobot.com
2. Add monitor:
   - **Type:** HTTP(s)
   - **URL:** `https://your-app.com/health`
   - **Interval:** 5 minutes
   - **Alert contacts:** Your email

#### Better Stack (Paid)

1. Go to https://betterstack.com
2. Create uptime check
3. Add incident management
4. Configure Slack/email alerts

---

## Monitoring

### Key Metrics to Track

1. **API Health**
   - Endpoint: `/health`
   - Check every 5 minutes
   - Alert if status != "healthy"

2. **Snapshot Age**
   - Endpoint: `/health`
   - Field: `snapshot_age_seconds`
   - Alert if > 300 seconds (5 min)

3. **Response Times**
   - All endpoints should be < 1 second
   - Alert if p95 > 2 seconds

4. **Node Counts**
   - Endpoint: `/pnodes?status=all`
   - Track total_pnodes over time
   - Alert on sudden drops (> 20%)

5. **Error Rate**
   - Monitor application logs
   - Alert on 5xx errors

### Logging Best Practices

```python
# app/main.py - Add logging middleware

import logging
import time
from fastapi import Request

logger = logging.getLogger("api")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"- {response.status_code} - {duration:.3f}s"
    )
    return response
```

---

## Troubleshooting

### Issue: Health check fails

**Symptoms:**
```json
{"status": "unhealthy", "reason": "No snapshot available"}
```

**Solutions:**
1. Check background worker is running
2. Verify MongoDB connection
3. Check IP nodes are accessible
4. Restart the application

```bash
# Heroku
heroku restart

# Railway
railway restart

# Self-hosted
sudo systemctl restart xandeum-api
```

---

### Issue: Slow response times

**Symptoms:**
- Endpoints taking > 2 seconds
- Timeout errors

**Solutions:**

1. **Check MongoDB indexes:**
```bash
# In MongoDB shell
db.pnodes_registry.getIndexes()

# Should show indexes on:
# - address (unique)
# - pubkey
# - last_seen
```

2. **Increase CACHE_TTL:**
```bash
# .env
CACHE_TTL=90
```

3. **Upgrade server resources:**
- More RAM
- Better CPU
- Closer to MongoDB region

---

### Issue: MongoDB connection errors

**Symptoms:**
```
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions:**

1. **Check connection string:**
```bash
# Verify format
mongodb+srv://username:password@cluster.mongodb.net/
```

2. **Verify IP whitelist:**
- Add `0.0.0.0/0` in Atlas Network Access

3. **Check credentials:**
- Username and password correct
- User has readWrite permissions

---

### Issue: Background worker not updating

**Symptoms:**
- `snapshot_age_seconds` keeps growing
- Data is stale

**Solutions:**

1. **Check logs for errors:**
```bash
# Look for RPC errors
heroku logs --tail | grep "RPC"
```

2. **Verify IP nodes are accessible:**
```bash
# Test manually
curl -X POST http://173.212.203.145:6000/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"get-version","id":1}'
```

3. **Restart application:**
```bash
heroku restart
```

---

### Issue: High memory usage

**Symptoms:**
- App crashes with R14 (Heroku)
- Out of memory errors

**Solutions:**

1. **Limit pagination:**
```python
# app/main.py
# Change max limit from 1000 to 500
limit: int = Query(100, ge=1, le=500)
```

2. **Clear Joblib cache periodically:**
```python
# app/fetcher.py
# Add cache cleanup
memory.clear(warn=False)
```

3. **Upgrade server tier:**
```bash
# Heroku
heroku ps:type standard-1x
```

---

## Backup & Recovery

### Database Backups

**MongoDB Atlas:**
- Auto-backups enabled by default (M10+)
- Manual backup: Cluster → Backup → Create Snapshot

**Manual Backup:**
```bash
mongodump --uri="mongodb+srv://..." --out=backup-$(date +%Y%m%d)
```

**Restore:**
```bash
mongorestore --uri="mongodb+srv://..." backup-20241214/
```

### Code Backups

- Keep code in Git (GitHub/GitLab)
- Tag releases: `git tag v2.0.0`
- Maintain production branch

---

## Scaling

### Vertical Scaling (More Resources)

**When to scale:**
- Response times > 2 seconds
- CPU usage consistently > 70%
- Memory usage > 80%

**How to scale:**
```bash
# Heroku
heroku ps:type standard-2x

# Railway
# Upgrade plan in dashboard

# Self-hosted
# Upgrade VPS tier
```

### Horizontal Scaling (Multiple Instances)

**Not currently supported** - background worker would conflict.

Future: Use Redis for distributed locking.

---

## Security Checklist

- [ ] MongoDB credentials in environment variables (not code)
- [ ] `.env` file in `.gitignore`
- [ ] MongoDB IP whitelist configured
- [ ] HTTPS enabled (via platform or nginx)
- [ ] Regular security updates (`pip install --upgrade`)
- [ ] Monitor for vulnerabilities (`pip audit`)

---

## Maintenance

### Regular Tasks

**Daily:**
- Check health endpoint
- Review error logs
- Monitor response times

**Weekly:**
- Review MongoDB storage usage
- Check for slow queries
- Update dependencies

**Monthly:**
- Review analytics trends
- Update IP nodes list (if needed)
- Plan capacity upgrades

---

## Support

### Getting Help

1. **Documentation:** This guide + API reference
2. **GitHub Issues:** Report bugs/features
3. **Community:** Discord/Telegram
4. **Professional:** Contact dev team

---

## Summary

✅ **You're ready to deploy!**

Quick deployment:
```bash
# 1. Set up MongoDB Atlas
# 2. Choose platform (Heroku recommended)
# 3. Configure environment variables
# 4. Deploy
# 5. Verify health endpoint
# 6. Set up monitoring
```

**Estimated time:** 30-60 minutes

**Total cost:** $5-25/month depending on platform

Good luck! 🚀