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