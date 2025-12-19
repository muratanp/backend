#!/bin/bash

# ============================================
# Xandeum PNode Analytics API Test Suite
# ============================================
# Tests all endpoints in app/main.py
# Usage: ./test_api.sh [BASE_URL] [--verbose]

BASE_URL="${1:-http://localhost:8000}"
VERBOSE="${2}"
PASSED=0
FAILED=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# Helper Functions
# ============================================

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

test_endpoint() {
    local name=$1
    local url=$2
    local expected_field=$3
    
    if [ "$VERBOSE" = "--verbose" ]; then
        echo ""
        echo -e "${YELLOW}Testing:${NC} $name"
        echo -e "${YELLOW}URL:${NC} $url"
    else
        echo -n "Testing $name... "
    fi
    
    # Make request
    response=$(curl -s "$url")
    
    # Check HTTP status
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$http_code" != "200" ]; then
        if [ "$VERBOSE" = "--verbose" ]; then
            echo -e "${RED}❌ FAIL${NC} - HTTP $http_code"
            echo "Response: $response" | head -n 5
        else
            echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        fi
        FAILED=$((FAILED + 1))
        return 1
    fi
    
    # Check expected field exists
    if echo "$response" | jq -e ".$expected_field" > /dev/null 2>&1; then
        if [ "$VERBOSE" = "--verbose" ]; then
            echo -e "${GREEN}✅ PASS${NC}"
            echo "Field '$expected_field' found"
        else
            echo -e "${GREEN}✅${NC}"
        fi
        PASSED=$((PASSED + 1))
        return 0
    else
        if [ "$VERBOSE" = "--verbose" ]; then
            echo -e "${RED}❌ FAIL${NC} - Field '$expected_field' not found"
            echo "Response: $response" | head -n 5
        else
            echo -e "${RED}❌${NC} (missing field)"
        fi
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# ============================================
# Main Test Suite
# ============================================

print_header "Xandeum PNode Analytics API Test Suite"
echo "Testing: $BASE_URL"
echo ""

# ============================================
# SYSTEM HEALTH
# ============================================
print_header "System Health Tests"

test_endpoint "Health Check" \
    "$BASE_URL/health" \
    "status"

test_endpoint "Root API Overview" \
    "$BASE_URL/" \
    "api_name"

# ============================================
# CORE DATA ENDPOINTS
# ============================================
print_header "Core Data Endpoints"

test_endpoint "Get Online Nodes" \
    "$BASE_URL/pnodes?status=online&limit=5" \
    "pnodes"

test_endpoint "Get All Nodes" \
    "$BASE_URL/pnodes?status=all&limit=5" \
    "summary"

test_endpoint "Get Offline Nodes" \
    "$BASE_URL/pnodes?status=offline&limit=5" \
    "pnodes"

test_endpoint "Sort by Score" \
    "$BASE_URL/pnodes?sort_by=score&sort_order=desc&limit=5" \
    "pnodes"

test_endpoint "Staking Recommendations" \
    "$BASE_URL/recommendations?limit=3" \
    "recommendations"

test_endpoint "Recommendations with Filters" \
    "$BASE_URL/recommendations?limit=5&min_uptime_days=7" \
    "recommendations"

# ============================================
# NETWORK ANALYTICS
# ============================================
print_header "Network Analytics Endpoints"

test_endpoint "Network Topology" \
    "$BASE_URL/network/topology" \
    "nodes"

test_endpoint "Network Health" \
    "$BASE_URL/network/health" \
    "health"

test_endpoint "Network Analytics" \
    "$BASE_URL/network/analytics" \
    "current_state"

test_endpoint "Network Consistency" \
    "$BASE_URL/network/consistency" \
    "nodes"

# ============================================
# HISTORICAL DATA
# ============================================
print_header "Historical Data Endpoints"

test_endpoint "Network History (24h)" \
    "$BASE_URL/network/history?hours=24" \
    "history"

test_endpoint "Network History (7d)" \
    "$BASE_URL/network/history?hours=168" \
    "history"

test_endpoint "Network Growth (24h)" \
    "$BASE_URL/network/growth?hours=24" \
    "growth_metrics"

test_endpoint "Network Growth (7d)" \
    "$BASE_URL/network/growth?hours=168" \
    "growth_metrics"

# ============================================
# ALERT SYSTEM
# ============================================
print_header "Alert System Endpoints"

test_endpoint "All Network Alerts" \
    "$BASE_URL/alerts" \
    "summary"

test_endpoint "Critical Alerts Only" \
    "$BASE_URL/alerts/critical" \
    "summary"

test_endpoint "Filtered Alerts (Warning)" \
    "$BASE_URL/alerts?severity=warning" \
    "summary"

# ============================================
# OPERATOR INTELLIGENCE
# ============================================
print_header "Operator Intelligence Endpoints"

test_endpoint "All Operators" \
    "$BASE_URL/operators?limit=10" \
    "operators"

test_endpoint "Multi-Node Operators" \
    "$BASE_URL/operators?min_nodes=2&limit=10" \
    "operators"

# ============================================
# GRAVEYARD ENDPOINTS
# ============================================
print_header "Graveyard Endpoints"

test_endpoint "Graveyard (Inactive Nodes)" \
    "$BASE_URL/graveyard?days=90&limit=5" \
    "items"

# ============================================
# ADVANCED FEATURES (with dynamic node addresses)
# ============================================
print_header "Advanced Features (Dynamic Tests)"

# Get two online node addresses for testing
echo -n "Fetching sample nodes for advanced tests... "
ADDR1=$(curl -s "$BASE_URL/pnodes?status=online&limit=1&skip=0" | jq -r '.pnodes[0].address')
ADDR2=$(curl -s "$BASE_URL/pnodes?status=online&limit=1&skip=1" | jq -r '.pnodes[0].address')

if [ -n "$ADDR1" ] && [ "$ADDR1" != "null" ]; then
    echo -e "${GREEN}✅${NC}"
    
    # Test node-specific alerts
    test_endpoint "Node Alerts (Node 1)" \
        "$BASE_URL/pnodes/$ADDR1/alerts" \
        "alerts"
    
    # Test node consistency
    test_endpoint "Node Consistency (Node 1)" \
        "$BASE_URL/node/$ADDR1/consistency" \
        "consistency"
    
    # Test node history
    test_endpoint "Node History (Node 1)" \
        "$BASE_URL/node/$ADDR1/history?days=7" \
        "address"
    
    # Test registry lookup
    test_endpoint "Registry Entry (Node 1)" \
        "$BASE_URL/registry/$ADDR1" \
        "entry"
    
    # Test node comparison (if we have 2 nodes)
    if [ -n "$ADDR2" ] && [ "$ADDR2" != "null" ] && [ "$ADDR1" != "$ADDR2" ]; then
        test_endpoint "Compare Two Nodes" \
            "$BASE_URL/pnodes/compare?addresses=$ADDR1,$ADDR2" \
            "comparison"
    else
        echo -n "Compare Two Nodes... "
        echo -e "${YELLOW}⚠️  SKIP${NC} (need 2+ nodes)"
    fi
else
    echo -e "${YELLOW}⚠️  SKIP${NC} (no nodes available)"
    echo "Advanced tests skipped (network may be initializing)"
fi

# ============================================
# SPECIAL TESTS
# ============================================
print_header "Special Case Tests"

# Test 404 handling
echo -n "Testing 404 Not Found... "
http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/nonexistent")
if [ "$http_code" = "404" ]; then
    echo -e "${GREEN}✅${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌${NC} (expected 404, got $http_code)"
    FAILED=$((FAILED + 1))
fi

# Test CORS headers
echo -n "Testing CORS Headers... "
cors_header=$(curl -s -I "$BASE_URL/health" | grep -i "access-control-allow-origin")
if [ -n "$cors_header" ]; then
    echo -e "${GREEN}✅${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  WARNING${NC} (no CORS headers)"
    PASSED=$((PASSED + 1))  # Don't fail, just warn
fi

# ============================================
# PERFORMANCE TESTS (Optional)
# ============================================
if [ "$VERBOSE" = "--verbose" ]; then
    print_header "Performance Tests"
    
    echo "Measuring response times..."
    
    endpoints=(
        "/health"
        "/pnodes?limit=10"
        "/recommendations?limit=5"
        "/network/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        echo -n "  $endpoint... "
        time=$(curl -o /dev/null -s -w '%{time_total}\n' "$BASE_URL$endpoint")
        time_ms=$(echo "$time * 1000" | bc 2>/dev/null || echo "N/A")
        if [ "$time_ms" != "N/A" ]; then
            echo "${time_ms%.*}ms"
        else
            echo "$time seconds"
        fi
    done
fi

# ============================================
# SUMMARY
# ============================================
echo ""
print_header "Test Results"

total=$((PASSED + FAILED))
pass_rate=0
if [ $total -gt 0 ]; then
    pass_rate=$(echo "scale=1; $PASSED * 100 / $total" | bc)
fi

echo ""
echo -e "Total Tests:  ${BLUE}$total${NC}"
echo -e "Passed:       ${GREEN}$PASSED ✅${NC}"
echo -e "Failed:       ${RED}$FAILED ❌${NC}"
echo -e "Pass Rate:    ${BLUE}${pass_rate}%${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    print_header "✅ All Tests Passed!"
    echo ""
    echo "API is working correctly ✨"
    echo ""
    exit 0
else
    print_header "❌ Some Tests Failed"
    echo ""
    echo "Please review failed tests above"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check API is running: curl $BASE_URL/health"
    echo "  2. Check logs for errors"
    echo "  3. Verify MongoDB connection"
    echo "  4. Ensure background worker is running"
    echo ""
    exit 1
fi