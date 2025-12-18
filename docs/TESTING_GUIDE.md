# Testing Guide - Xandeum PNode Analytics API

## Prerequisites

```bash
# Ensure API is running
uvicorn app.main:app --reload --port 8000

# Install testing tools
pip install httpx pytest
```

---

## Manual Testing (Using curl)

### 1. Health Check
```bash
curl http://localhost:8000/health | jq '.'

# Expected: status "healthy", snapshot_age_seconds < 120
```

### 2. Get All Online Nodes
```bash
curl "http://localhost:8000/pnodes?status=online&limit=10" | jq '.'

# Expected: 
# - summary.online_pnodes > 0
# - pnodes array with scored entries
# - All nodes have is_online: true
```

### 3. Get All Nodes (Online + Offline)
```bash
curl "http://localhost:8000/pnodes?status=all&limit=20" | jq '.'

# Expected:
# - summary.total_pnodes = online + offline
# - Mix of online and offline nodes
```

### 4. Get Staking Recommendations
```bash
curl "http://localhost:8000/recommendations?limit=5&min_uptime_days=7" | jq '.'

# Expected:
# - recommendations array sorted by score (highest first)
# - All nodes have uptime >= 7 days
# - All nodes are online
```

### 5. Get Network Topology
```bash
curl http://localhost:8000/network/topology | jq '.'

# Expected:
# - nodes array with ip_node and pnode types
# - edges array with gossip_connection entries
# - stats with total counts
```

### 6. Get Network Health
```bash
curl http://localhost:8000/network/health | jq '.'

# Expected:
# - health.health_score between 0-100
# - health.status (healthy/fair/degraded/critical)
# - alerts array (may be empty)
```

### 7. Get Operators
```bash
curl "http://localhost:8000/operators?limit=10&min_nodes=2" | jq '.'

# Expected:
# - operators array sorted by node_count
# - summary.decentralization_score
# - Only operators with 2+ nodes
```

### 8. Get Network History
```bash
curl "http://localhost:8000/network/history?hours=24" | jq '.'

# Expected:
# - history array with timestamps
# - summary.growth with trends
# - May be empty if just started
```

### 9. Get Registry (Historical)
```bash
curl "http://localhost:8000/registry?limit=10&skip=0" | jq '.'

# Expected:
# - items array with registry entries
# - Each has is_online flag
# - count = returned items
```

### 10. Get Single Node Details
```bash
# Replace with actual address from /pnodes response
curl "http://localhost:8000/registry/109.199.96.218:9001" | jq '.'

# Expected:
# - entry with all node data
# - status object
# - is_online flag
```

---

## Testing Null-Safety

### Test with Missing Data

Create a test node with None/missing values:

```python
# In Python console or test script
import requests

# This tests how the API handles nodes with missing data
# (You can't create bad data manually, but this shows the protection)

# Get a real node
response = requests.get("http://localhost:8000/pnodes?limit=1")
nodes = response.json()["pnodes"]

if nodes:
    node = nodes[0]
    print("Node has required fields:")
    print(f"- address: {node.get('address')}")
    print(f"- uptime: {node.get('uptime')} (handles None: {node.get('uptime', 0)})")
    print(f"- peer_sources: {len(node.get('peer_sources', []))}")
```

### Test Sorting with None Values

```bash
# Sort by various fields (should not crash even with None)
curl "http://localhost:8000/pnodes?sort_by=uptime&sort_order=desc&limit=5" | jq '.pnodes[] | {address, uptime}'

curl "http://localhost:8000/pnodes?sort_by=storage_used&sort_order=asc&limit=5" | jq '.pnodes[] | {address, storage_used}'

curl "http://localhost:8000/pnodes?sort_by=score&sort_order=desc&limit=5" | jq '.pnodes[] | {address, score, tier}'
```

---

## Automated Test Script

Save as `test_api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected_field=$3
    
    echo -n "Testing $name... "
    response=$(curl -s "$url")
    
    if echo "$response" | jq -e ".$expected_field" > /dev/null 2>&1; then
        echo "✅ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "❌ FAIL"
        echo "Response: $response" | head -n 5
        FAILED=$((FAILED + 1))
    fi
}

echo "================================"
echo "Xandeum API Test Suite"
echo "================================"
echo ""

test_endpoint "Health Check" "$BASE_URL/health" "status"
test_endpoint "Get Online Nodes" "$BASE_URL/pnodes?status=online&limit=5" "pnodes"
test_endpoint "Get All Nodes" "$BASE_URL/pnodes?status=all&limit=5" "summary"
test_endpoint "Recommendations" "$BASE_URL/recommendations?limit=3" "recommendations"
test_endpoint "Network Topology" "$BASE_URL/network/topology" "nodes"
test_endpoint "Network Health" "$BASE_URL/network/health" "health"
test_endpoint "Operators" "$BASE_URL/operators?limit=5" "operators"
test_endpoint "Network History" "$BASE_URL/network/history?hours=24" "history"
test_endpoint "Registry" "$BASE_URL/registry?limit=5" "items"

echo ""
echo "================================"
echo "Results: $PASSED passed, $FAILED failed"
echo "================================"

if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
```

Run with:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Python Test Suite

Save as `test_api.py`:

```python
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, expected_field):
    """Test a single endpoint."""
    print(f"\nTesting {name}...")
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"  ❌ Failed with status {response.status_code}")
            return False
        
        data = response.json()
        
        if expected_field not in data:
            print(f"  ❌ Missing field: {expected_field}")
            return False
        
        print(f"  ✅ Success")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Xandeum PNode API Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", f"{BASE_URL}/health", "status"),
        ("Online Nodes", f"{BASE_URL}/pnodes?status=online&limit=5", "pnodes"),
        ("All Nodes", f"{BASE_URL}/pnodes?status=all&limit=5", "summary"),
        ("Recommendations", f"{BASE_URL}/recommendations?limit=3", "recommendations"),
        ("Network Topology", f"{BASE_URL}/network/topology", "nodes"),
        ("Network Health", f"{BASE_URL}/network/health", "health"),
        ("Operators", f"{BASE_URL}/operators?limit=5", "operators"),
        ("Network History", f"{BASE_URL}/network/history?hours=24", "history"),
        ("Registry", f"{BASE_URL}/registry?limit=5", "items"),
    ]
    
    results = []
    for name, url, field in tests:
        results.append(test_endpoint(name, url, field))
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

Run with:
```bash
python test_api.py
```

---

## Common Issues & Solutions

### Issue: "Snapshot not available"
**Solution:** Background worker hasn't run yet. Wait 60 seconds and try again.

### Issue: Empty history array
**Solution:** Historical data accumulates over time. Wait a few minutes for snapshots to save.

### Issue: Low node count
**Solution:** Ensure IP nodes in .env are accessible and returning data.

### Issue: Scoring fails
**Solution:** Check logs for missing fields. Null-safety should handle this, but report if it crashes.

---

## Success Criteria

✅ All endpoints return 200 status
✅ No crashes with missing/None data
✅ Scores calculate correctly for all nodes
✅ Pagination works
✅ Sorting works (all fields)
✅ Historical data accumulates
✅ Health check shows "healthy"

---

## Performance Benchmarks

### Expected Response Times

| Endpoint | Expected Time | Acceptable Time |
|----------|---------------|-----------------|
| /health | < 50ms | < 100ms |
| /pnodes (100 limit) | < 300ms | < 500ms |
| /recommendations | < 400ms | < 600ms |
| /network/topology | < 200ms | < 400ms |
| /network/health | < 500ms | < 800ms |
| /operators | < 300ms | < 500ms |
| /network/history | < 200ms | < 400ms |

Test with:
```bash
time curl -s http://localhost:8000/pnodes?limit=100 > /dev/null
```

---

## Reporting Issues

If you find a bug:

1. Note the endpoint and parameters
2. Save the full response
3. Check logs: `tail -f logs/app.log`
4. Report with steps to reproduce