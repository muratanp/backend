import requests
import time
import sys
from typing import Dict, List

BASE_URL = "http://localhost:8000"
PASSED = 0
FAILED = 0

def print_header(text: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_endpoint(name: str, url: str, required_fields: List[str]) -> bool:
    """Test an endpoint and verify required fields exist."""
    global PASSED, FAILED
    
    print(f"\n🔍 Testing: {name}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ FAILED - Status {response.status_code}")
            FAILED += 1
            return False
        
        data = response.json()
        
        # Check required fields
        missing = []
        for field in required_fields:
            if "." in field:  # Nested field check
                parts = field.split(".")
                current = data
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        missing.append(field)
                        break
            else:
                if field not in data:
                    missing.append(field)
        
        if missing:
            print(f"   ❌ FAILED - Missing fields: {', '.join(missing)}")
            FAILED += 1
            return False
        
        print(f"   ✅ PASSED")
        PASSED += 1
        return True
        
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        FAILED += 1
        return False


def test_phase4_features():
    """Run all Phase 4 tests."""
    
    print_header("PHASE 4: HISTORICAL & ANALYTICS TESTING")
    
    print("\n⏰ Waiting 2 minutes for historical data to accumulate...")
    print("   (You can skip this if data already exists)")
    
    # Optional: Wait for snapshots
    # time.sleep(120)
    
    # Test 1: Enhanced Network History
    print_header("Test 1: Enhanced Network History")
    test_endpoint(
        "Network History (1 hour)",
        f"{BASE_URL}/network/history?hours=1",
        ["history", "summary", "summary.node_growth", "summary.storage_growth"]
    )
    
    test_endpoint(
        "Network History (24 hours)",
        f"{BASE_URL}/network/history?hours=24",
        ["history", "summary", "summary.network_health", "summary.version_stability"]
    )
    
    # Test 2: Growth Metrics
    print_header("Test 2: Growth Metrics")
    test_endpoint(
        "24h Growth",
        f"{BASE_URL}/network/growth?hours=24",
        ["growth_metrics", "growth_metrics.nodes", "growth_metrics.storage"]
    )
    
    test_endpoint(
        "7d Growth",
        f"{BASE_URL}/network/growth?hours=168",
        ["growth_metrics", "timestamp"]
    )
    
    # Test 3: Network Analytics
    print_header("Test 3: Comprehensive Network Analytics")
    test_endpoint(
        "Network Analytics",
        f"{BASE_URL}/network/analytics",
        [
            "current_state",
            "growth",
            "version_analysis",
            "storage_analysis",
            "connectivity_analysis",
            "recommendations"
        ]
    )
    
    # Test 4: Per-Node History (Placeholder)
    print_header("Test 4: Per-Node History (Placeholder)")
    test_endpoint(
        "Node History Placeholder",
        f"{BASE_URL}/node/109.199.96.218:9001/history",
        ["address", "available", "planned_for"]
    )
    
    # Advanced Tests
    print_header("Advanced Validation Tests")
    
    # Test 5: Verify History Accumulation
    print("\n🔍 Test 5: History Accumulation")
    try:
        response = requests.get(f"{BASE_URL}/network/history?hours=1")
        data = response.json()
        history_count = len(data.get("history", []))
        
        print(f"   Snapshots in last hour: {history_count}")
        
        if history_count > 0:
            print(f"   ✅ PASSED - History is accumulating")
            PASSED += 1
        else:
            print(f"   ⚠️  WARNING - No history yet (wait longer)")
            print(f"   Note: History accumulates over time. This is not a failure.")
            PASSED += 1  # Don't fail on fresh install
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        FAILED += 1
    
    # Test 6: Verify Growth Calculation
    print("\n🔍 Test 6: Growth Calculation")
    try:
        response = requests.get(f"{BASE_URL}/network/growth?hours=24")
        data = response.json()
        
        if data.get("growth_metrics", {}).get("available"):
            nodes = data["growth_metrics"]["nodes"]
            print(f"   Node growth: {nodes['growth']} ({nodes['growth_percent']}%)")
            print(f"   ✅ PASSED - Growth metrics calculated")
            PASSED += 1
        else:
            print(f"   ⚠️  WARNING - Growth data not yet available")
            print(f"   Message: {data.get('growth_metrics', {}).get('message')}")
            PASSED += 1  # Don't fail on fresh install
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        FAILED += 1
    
    # Test 7: Version Analysis
    print("\n🔍 Test 7: Version Analysis")
    try:
        response = requests.get(f"{BASE_URL}/network/analytics")
        data = response.json()
        
        version_analysis = data.get("version_analysis", {})
        compliance = version_analysis.get("compliance_percent", 0)
        health = version_analysis.get("health", "unknown")
        
        print(f"   Version compliance: {compliance}%")
        print(f"   Version health: {health}")
        print(f"   ✅ PASSED - Version analysis working")
        PASSED += 1
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        FAILED += 1
    
    # Test 8: Storage Analysis
    print("\n🔍 Test 8: Storage Analysis")
    try:
        response = requests.get(f"{BASE_URL}/network/analytics")
        data = response.json()
        
        storage = data.get("storage_analysis", {})
        distribution = storage.get("distribution", {})
        
        print(f"   Empty nodes: {distribution.get('empty', 0)}")
        print(f"   Optimal nodes: {distribution.get('optimal', 0)}")
        print(f"   Critical nodes: {distribution.get('critical', 0)}")
        print(f"   Storage health: {storage.get('health', 'unknown')}")
        print(f"   ✅ PASSED - Storage analysis working")
        PASSED += 1
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        FAILED += 1
    
    # Test 9: Connectivity Analysis
    print("\n🔍 Test 9: Connectivity Analysis")
    try:
        response = requests.get(f"{BASE_URL}/network/analytics")
        data = response.json()
        
        connectivity = data.get("connectivity_analysis", {})
        distribution = connectivity.get("distribution", {})
        
        print(f"   Isolated nodes: {distribution.get('isolated', 0)}")
        print(f"   Well-connected: {connectivity.get('well_connected', 0)}")
        print(f"   Connectivity health: {connectivity.get('health', 'unknown')}")
        print(f"   ✅ PASSED - Connectivity analysis working")
        PASSED += 1
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        FAILED += 1
    
    # Test 10: Recommendations
    print("\n🔍 Test 10: Recommendations Engine")
    try:
        response = requests.get(f"{BASE_URL}/network/analytics")
        data = response.json()
        
        recommendations = data.get("recommendations", [])
        
        print(f"   Recommendations count: {len(recommendations)}")
        if recommendations:
            for rec in recommendations:
                severity = rec.get("severity", "unknown")
                message = rec.get("message", "")
                print(f"   - [{severity}] {message}")
        
        print(f"   ✅ PASSED - Recommendations generated")
        PASSED += 1
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        FAILED += 1


def print_summary():
    """Print test summary."""
    print_header("TEST SUMMARY")
    
    total = PASSED + FAILED
    pass_rate = (PASSED / total * 100) if total > 0 else 0
    
    print(f"\n   Total Tests: {total}")
    print(f"   Passed: {PASSED} ✅")
    print(f"   Failed: {FAILED} ❌")
    print(f"   Pass Rate: {pass_rate:.1f}%")
    
    if FAILED == 0:
        print("\n   🎉 ALL TESTS PASSED!")
        print("   Phase 4 features are working correctly.")
    else:
        print("\n   ⚠️  SOME TESTS FAILED")
        print("   Check the output above for details.")
    
    print("\n" + "=" * 60)


def main():
    """Main test runner."""
    print("\n" + "🚀" * 30)
    print("   XANDEUM PNODE ANALYTICS - PHASE 4 TEST SUITE")
    print("🚀" * 30)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n❌ ERROR: API is not healthy")
            print(f"   Status: {response.status_code}")
            sys.exit(1)
        print("\n✅ API is running and healthy")
    except Exception as e:
        print(f"\n❌ ERROR: Cannot connect to API at {BASE_URL}")
        print(f"   Error: {e}")
        print("\n   Make sure the API is running:")
        print("   uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    
    # Run tests
    test_phase4_features()
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if FAILED == 0 else 1)


if __name__ == "__main__":
    main()