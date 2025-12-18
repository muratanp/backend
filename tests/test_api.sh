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