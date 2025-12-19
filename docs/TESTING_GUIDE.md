# Testing Guide - Xandeum PNode Analytics API

**Version:** 1.1.0  
**Last Updated:** December 2024

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Testing](#quick-start-testing)
3. [Automated Testing](#automated-testing)
4. [Manual Testing](#manual-testing)
5. [Endpoint Testing](#endpoint-testing)
6. [Performance Testing](#performance-testing)
7. [Integration Testing](#integration-testing)
8. [Production Testing](#production-testing)

---

## ✅ Prerequisites

### Required Tools

```bash
# 1. Python 3.11+
python --version

# 2. Required packages
pip install requests pytest httpx

# 3. Optional: jq for JSON parsing
# macOS: brew install jq
# Ubuntu: sudo apt install jq
# Windows: choco install jq

# 4. Ensure API is running
uvicorn app.main:app --reload --port 8000
```

### Test Environment

```bash
# Set base URL for tests
export BASE_URL="http://localhost:8000"

# Or for production
export BASE_URL="https://web-production-b4440.up.railway.app"
```

---

## 🚀 Quick Start Testing

### Run All Tests

```bash
# 1. Quick API test (< 30 seconds)
./tests/test_api.sh

# 2. Comprehensive test suite (2-3 minutes)
python tests/test_comprehensive.py

# 3. Phase-specific tests
python tests/test_phase4.py  # Historical & analytics
python tests/test_phase5.py  # Advanced features
```

### Expected Output

```
✅ All tests passed!
Results: 25 passed, 0 failed
Pass Rate: 100%
```

---

## 🤖 Automated Testing

### Test Suite 1: Quick API Test (test_api.sh)

**Purpose:** Verify all core endpoints respond correctly

**Runtime:** ~30 seconds

```bash
# Run against local
./tests/test_api.sh

# Run against production
./tests/test_api.sh https://web-production-b4440.up.railway.app

# Run with verbose output
./tests/test_api.sh http://localhost:8000 --verbose
```

**What it tests:**
- ✅ Health endpoint
- ✅ Root endpoint (API overview)
- ✅ Online nodes
- ✅ All nodes
- ✅ Recommendations
- ✅ Network topology
- ✅ Network health
- ✅ Operators
- ✅ Network history
- ✅ Network analytics
- ✅ Network growth
- ✅ Network consistency
- ✅ Alerts (all)
- ✅ Alerts (critical)
- ✅ Registry

---

### Test Suite 2: Comprehensive Tests (test_comprehensive.py)

**Purpose:** End-to-end testing of all phases

**Runtime:** 2-3 minutes

```bash
# Run with default settings
python tests/test_comprehensive.py

# Run with verbose output
python tests/test_comprehensive.py --verbose

# Skip slow tests (performance benchmarks)
python tests/test_comprehensive.py --skip-slow

# Test against custom URL
python tests/test_comprehensive.py --url https://your-api.com
```

**What it tests:**
- Phase 0: System health
- Phase 1: Core endpoints
- Phase 2 & 3: Scoring & unified endpoints
- Phase 4: Historical data
- Phase 5: Advanced features
- Performance benchmarks
- Integration tests
- Data consistency tests
- Null-safety validation

---

### Test Suite 3: Phase 4 Tests (test_phase4.py)

**Purpose:** Test historical tracking and analytics

**Runtime:** ~1 minute

```bash
python tests/test_phase4.py
```

**What it tests:**
- ✅ Network history endpoint
- ✅ Growth metrics
- ✅ Network analytics
- ✅ Historical data accumulation
- ✅ Growth calculation
- ✅ Version analysis
- ✅ Storage analysis
- ✅ Connectivity analysis
- ✅ Recommendations engine

---

### Test Suite 4: Phase 5 Tests (test_phase5.py)

**Purpose:** Test advanced features

**Runtime:** ~1 minute

```bash
python tests/test_phase5.py
```

**What it tests:**
- ✅ Per-node alerts
- ✅ Network-wide alerts
- ✅ Node comparison
- ✅ Gossip consistency tracking
- ✅ Alert filtering
- ✅ Comparison winners
- ✅ Consistency score validation
- ✅ Alert severity levels

---

## 🧪 Manual Testing

### 1. Health Check

```bash
# Test health endpoint
curl http://localhost:8000/health | jq '.'

# Expected fields:
# - status: "healthy"
# - snapshot_age_seconds: < 120
# - last_updated: recent timestamp
# - total_pnodes: > 0
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "snapshot_age_seconds": 45,
  "last_updated": 1703001234,
  "cache_ttl": 60,
  "total_pnodes": 120,
  "total_ip_nodes": 9,
  "timestamp": 1703001279
}
```

---

### 2. Root Endpoint (API Overview)

```bash
# Test root endpoint
curl http://localhost:8000/ | jq '.'

# Check specific sections
curl http://localhost:8000/ | jq '.system_status'
curl http://localhost:8000/ | jq '.core_endpoints'
curl http://localhost:8000/ | jq '.features'
```

**Verify:**
- ✅ `api_name`: "Xandeum PNode Analytics API"
- ✅ `version`: "2.0.0"
- ✅ `system_status.status`: "operational"
- ✅ `system_status.nodes_tracked`: > 0

---

### 3. Get Online Nodes

```bash
# Get first 10 online nodes
curl "http://localhost:8000/pnodes?status=online&limit=10" | jq '.'

# Check structure
curl "http://localhost:8000/pnodes?limit=1" | jq '.pnodes[0]'

# Verify scoring
curl "http://localhost:8000/pnodes?limit=1" | jq '.pnodes[0].scores'
```

**Verify:**
- ✅ `summary.online_pnodes`: > 0
- ✅ All nodes have `is_online`: true
- ✅ All nodes have `score` field
- ✅ All nodes have `scores.trust`, `scores.capacity`, `scores.stake_confidence`

---

### 4. Get All Nodes (Online + Offline)

```bash
# Get mix of online and offline
curl "http://localhost:8000/pnodes?status=all&limit=20" | jq '.'

# Count online vs offline
curl "http://localhost:8000/pnodes?status=all&limit=1000" | \
  jq '.pnodes | map(select(.is_online)) | length'
```

**Verify:**
- ✅ `summary.total_pnodes` = online + offline
- ✅ Mix of `is_online`: true and false
- ✅ Offline nodes have `offline_duration` field

---

### 5. Get Staking Recommendations

```bash
# Get top 5 nodes for staking
curl "http://localhost:8000/recommendations?limit=5&min_uptime_days=7" | jq '.'

# Verify sorting (highest score first)
curl "http://localhost:8000/recommendations?limit=10" | \
  jq '.recommendations | map(.score)'
```

**Verify:**
- ✅ All nodes have `score` >= 0
- ✅ Sorted by score (descending)
- ✅ All nodes meet minimum uptime
- ✅ All nodes are online

---

### 6. Network Topology

```bash
# Get graph structure
curl http://localhost:8000/network/topology | jq '.'

# Count nodes and edges
curl http://localhost:8000/network/topology | jq '.stats'
```

**Verify:**
- ✅ `nodes` array contains IP nodes and pNodes
- ✅ `edges` array contains gossip connections
- ✅ `stats.total_connections` > 0

---

### 7. Network Health

```bash
# Get health metrics
curl http://localhost:8000/network/health | jq '.'

# Check health score
curl http://localhost:8000/network/health | jq '.health.health_score'

# Check alerts
curl http://localhost:8000/network/health | jq '.alerts'
```

**Verify:**
- ✅ `health.health_score`: 0-100
- ✅ `health.status`: "healthy", "fair", "degraded", or "critical"
- ✅ `alerts` array (may be empty)

---

### 8. Operators

```bash
# Get operator distribution
curl "http://localhost:8000/operators?limit=10&min_nodes=2" | jq '.'

# Check decentralization
curl http://localhost:8000/operators | jq '.summary.decentralization_score'
```

**Verify:**
- ✅ Operators sorted by `node_count` (descending)
- ✅ Only operators with >= `min_nodes`
- ✅ `decentralization_score`: 0-100

---

### 9. Network History

```bash
# Get 24 hours of history
curl "http://localhost:8000/network/history?hours=24" | jq '.'

# Check data points
curl "http://localhost:8000/network/history?hours=24" | \
  jq '.summary.data_points'

# Check growth trends
curl "http://localhost:8000/network/history?hours=24" | \
  jq '.summary.node_growth'
```

**Verify:**
- ✅ `history` array with timestamped entries
- ✅ `summary.node_growth` shows trend
- ✅ `summary.storage_growth` shows trend

---

### 10. Network Growth

```bash
# 24-hour growth comparison
curl "http://localhost:8000/network/growth?hours=24" | jq '.'

# 7-day growth comparison
curl "http://localhost:8000/network/growth?hours=168" | jq '.'
```

**Verify:**
- ✅ `growth_metrics.available`: true
- ✅ `nodes.growth_percent` calculated
- ✅ `storage.growth_percent` calculated

---

### 11. Network Analytics

```bash
# Comprehensive analytics
curl http://localhost:8000/network/analytics | jq '.'

# Version analysis
curl http://localhost:8000/network/analytics | jq '.version_analysis'

# Storage analysis
curl http://localhost:8000/network/analytics | jq '.storage_analysis'

# Connectivity analysis
curl http://localhost:8000/network/analytics | jq '.connectivity_analysis'
```

**Verify:**
- ✅ All analysis sections present
- ✅ `recommendations` array with actionable items
- ✅ Health indicators: "good", "fair", "poor"

---

### 12. Network Consistency

```bash
# Get gossip consistency metrics
curl "http://localhost:8000/network/consistency?min_consistency=0.8" | jq '.'

# Check flapping nodes
curl http://localhost:8000/network/consistency | jq '.flapping_nodes'
```

**Verify:**
- ✅ `summary.avg_consistency_score`: 0.0-1.0
- ✅ `flapping_nodes` array (nodes with score < 0.8)
- ✅ `network_health`: "excellent", "good", "fair", "poor"

---

### 13. Node-Specific Alerts

```bash
# Replace with actual node address
NODE_ADDR="109.199.96.218:9001"

# Get alerts for node
curl "http://localhost:8000/pnodes/$NODE_ADDR/alerts" | jq '.'

# Check alert summary
curl "http://localhost:8000/pnodes/$NODE_ADDR/alerts" | jq '.summary'
```

**Verify:**
- ✅ `alerts` array (may be empty if node is healthy)
- ✅ `summary` with counts by severity
- ✅ `node_info` with basic status

---

### 14. All Network Alerts

```bash
# Get all alerts
curl http://localhost:8000/alerts | jq '.'

# Get only critical alerts
curl http://localhost:8000/alerts/critical | jq '.'

# Filter by severity
curl "http://localhost:8000/alerts?severity=warning" | jq '.'
```

**Verify:**
- ✅ `summary` with alert counts
- ✅ `critical_nodes` array
- ✅ `nodes_checked` count

---

### 15. Node Comparison

```bash
# Get two online node addresses
ADDR1=$(curl -s "http://localhost:8000/pnodes?limit=1&skip=0" | jq -r '.pnodes[0].address')
ADDR2=$(curl -s "http://localhost:8000/pnodes?limit=1&skip=1" | jq -r '.pnodes[0].address')

# Compare nodes
curl "http://localhost:8000/pnodes/compare?addresses=$ADDR1,$ADDR2" | jq '.'

# Check winners
curl "http://localhost:8000/pnodes/compare?addresses=$ADDR1,$ADDR2" | jq '.winners'
```

**Verify:**
- ✅ `comparison` array with full node objects
- ✅ `winners` with best in each category
- ✅ `recommendation` with suggested choice

---

### 16. Node Consistency Details

```bash
# Get consistency for specific node
NODE_ADDR="109.199.96.218:9001"

curl "http://localhost:8000/node/$NODE_ADDR/consistency" | jq '.'

# Check consistency score
curl "http://localhost:8000/node/$NODE_ADDR/consistency" | jq '.consistency.score'
```

**Verify:**
- ✅ `consistency.score`: 0.0-1.0
- ✅ `recent_activity` with timestamps
- ✅ `recommendations` array

---

### 17. Per-Node History

```bash
# Get 30 days of node history
NODE_ADDR="109.199.96.218:9001"

curl "http://localhost:8000/node/$NODE_ADDR/history?days=30" | jq '.'

# Check trends
curl "http://localhost:8000/node/$NODE_ADDR/history?days=30" | jq '.trends'
```

**Verify:**
- ✅ `history` array with timestamps
- ✅ `trends` with calculated changes
- ✅ `availability` percentage
- ✅ May return "not available" if data not yet accumulated

---

### 18. Registry Endpoints

```bash
# Get registry (historical nodes)
curl "http://localhost:8000/registry?limit=10" | jq '.'

# Get specific node from registry
NODE_ADDR="109.199.96.218:9001"
curl "http://localhost:8000/registry/$NODE_ADDR" | jq '.'

# Get graveyard (inactive nodes)
curl "http://localhost:8000/graveyard?days=90" | jq '.'
```

---

## ⚡ Performance Testing

### Response Time Testing

```bash
#!/bin/bash
# test_performance.sh

BASE_URL="${1:-http://localhost:8000}"

echo "Performance Testing: $BASE_URL"
echo "================================"

# Test each endpoint
endpoints=(
  "/health"
  "/pnodes?limit=10"
  "/pnodes?limit=100"
  "/recommendations"
  "/network/topology"
  "/network/health"
  "/network/analytics"
  "/network/history?hours=24"
)

for endpoint in "${endpoints[@]}"; do
  echo -n "Testing $endpoint... "
  time=$(curl -o /dev/null -s -w '%{time_total}\n' "$BASE_URL$endpoint")
  time_ms=$(echo "$time * 1000" | bc)
  echo "${time_ms%.*}ms"
done
```

**Run:**
```bash
chmod +x test_performance.sh
./test_performance.sh
```

**Expected Times:**
- `/health`: < 100ms
- `/pnodes?limit=10`: < 300ms
- `/pnodes?limit=100`: < 500ms
- `/recommendations`: < 600ms
- `/network/health`: < 800ms

---

### Load Testing (Optional)

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test with 100 concurrent requests
ab -n 100 -c 10 http://localhost:8000/health

# Test sustained load
ab -n 1000 -c 20 -t 60 http://localhost:8000/pnodes?limit=10
```

---

## 🔗 Integration Testing

### Test Data Flow

```bash
#!/bin/bash
# test_integration.sh

echo "Integration Test: Complete Data Flow"
echo "====================================="

# 1. Verify system is healthy
echo "1. Checking system health..."
HEALTH=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$HEALTH" != "healthy" ]; then
  echo "❌ System unhealthy"
  exit 1
fi
echo "✅ System healthy"

# 2. Get a sample node
echo "2. Fetching sample node..."
NODE_ADDR=$(curl -s "http://localhost:8000/pnodes?limit=1" | jq -r '.pnodes[0].address')
if [ -z "$NODE_ADDR" ]; then
  echo "❌ No nodes found"
  exit 1
fi
echo "✅ Found node: $NODE_ADDR"

# 3. Check node has scores
echo "3. Verifying node scoring..."
SCORE=$(curl -s "http://localhost:8000/pnodes?limit=1" | jq -r '.pnodes[0].score')
if [ "$SCORE" = "null" ]; then
  echo "❌ Node has no score"
  exit 1
fi
echo "✅ Node scored: $SCORE/100"

# 4. Check node in registry
echo "4. Verifying registry entry..."
REGISTRY=$(curl -s "http://localhost:8000/registry/$NODE_ADDR" | jq -r '.entry.address')
if [ "$REGISTRY" != "$NODE_ADDR" ]; then
  echo "❌ Node not in registry"
  exit 1
fi
echo "✅ Registry entry found"

# 5. Check node alerts
echo "5. Checking node alerts..."
ALERTS=$(curl -s "http://localhost:8000/pnodes/$NODE_ADDR/alerts" | jq -r '.summary.total')
echo "✅ Alerts checked: $ALERTS total"

# 6. Verify historical data
echo "6. Checking historical data..."
HISTORY=$(curl -s "http://localhost:8000/network/history?hours=1" | jq -r '.history | length')
echo "✅ History available: $HISTORY data points"

echo ""
echo "================================="
echo "✅ Integration test passed!"
echo "================================="
```

---

## 🌐 Production Testing

### Pre-Deployment Tests

```bash
# 1. Run all test suites
./tests/test_api.sh
python tests/test_comprehensive.py
python tests/test_phase4.py
python tests/test_phase5.py

# 2. Verify no errors
echo "✅ All tests must pass before deploying"
```

### Post-Deployment Tests

```bash
# Set production URL
PROD_URL="https://web-production-b4440.up.railway.app"

# 1. Quick smoke test
./tests/test_api.sh $PROD_URL

# 2. Verify data freshness
curl "$PROD_URL/health" | jq '.snapshot_age_seconds'
# Should be < 120

# 3. Check all endpoints
python tests/test_comprehensive.py --url $PROD_URL

# 4. Monitor for 5 minutes
for i in {1..5}; do
  echo "Check $i/5..."
  curl -s "$PROD_URL/health" | jq '.status'
  sleep 60
done
```

---

## ✅ Testing Checklist

### Before Committing Code

- [ ] All automated tests pass
- [ ] Manual testing of changed endpoints
- [ ] Performance acceptable (< 500ms)
- [ ] No errors in logs
- [ ] Documentation updated

### Before Deploying

- [ ] All tests pass on staging
- [ ] Performance benchmarks met
- [ ] Integration tests pass
- [ ] Database migrations tested
- [ ] Rollback plan ready

### After Deploying

- [ ] Smoke tests pass
- [ ] All endpoints respond
- [ ] Data is fresh
- [ ] No errors in production logs
- [ ] Monitoring alerts configured

---

## 📞 Reporting Test Failures

If you find a bug:

1. **Note the endpoint and parameters**
2. **Save the full response**
3. **Check logs:**
   ```bash
   # Local
   tail -f logs/app.log
   
   # Production
   railway logs  # or heroku logs --tail
   ```
4. **Create GitHub issue** with:
   - Endpoint tested
   - Expected behavior
   - Actual behavior
   - Steps to reproduce
   - Logs/screenshots

---

<div align="center">

**Xandeum PNode Analytics - Testing Guide v2.0.0**

[Back to README](../README.md) • [API Reference](API_REFERENCE.md) • [Deployment](DEPLOYMENT.md)

*Testing is key to production readiness!*

</div>