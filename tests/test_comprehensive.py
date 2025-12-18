#!/usr/bin/env python3
"""
Phase 6: Comprehensive Test Suite
Tests all phases (1-5) end-to-end for production readiness.

Usage:
    python test_comprehensive.py [--verbose] [--skip-slow]
"""

import requests
import sys
import time
import argparse
from typing import Dict, List, Optional

BASE_URL = "http://localhost:8000"
PASSED = 0
FAILED = 0
SKIPPED = 0
WARNINGS = 0

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text: str, level: int = 1):
    """Print formatted section headers."""
    if level == 1:
        print(f"\n{Colors.BLUE}{'=' * 80}")
        print(f"  {text}")
        print(f"{'=' * 80}{Colors.RESET}")
    else:
        print(f"\n{Colors.BLUE}{'─' * 80}")
        print(f"  {text}")
        print(f"{'─' * 80}{Colors.RESET}")


class TestResult:
    def __init__(self, name: str, passed: bool, error: Optional[str] = None, warning: Optional[str] = None):
        self.name = name
        self.passed = passed
        self.error = error
        self.warning = warning


def test_endpoint(name: str, url: str, required_fields: List[str], verbose: bool = False) -> TestResult:
    """Test an endpoint and verify required fields exist."""
    global PASSED, FAILED, WARNINGS
    
    if verbose:
        print(f"\n🔍 Testing: {name}")
        print(f"   URL: {url}")
    else:
        print(f"Testing {name}...", end=" ")
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            if verbose:
                print(f"   {Colors.RED}❌ FAILED - Status {response.status_code}{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌{Colors.RESET}")
            FAILED += 1
            return TestResult(name, False, f"Status {response.status_code}")
        
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
            if verbose:
                print(f"   {Colors.RED}❌ FAILED - Missing fields: {', '.join(missing)}{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌{Colors.RESET}")
            FAILED += 1
            return TestResult(name, False, f"Missing: {', '.join(missing)}")
        
        if verbose:
            print(f"   {Colors.GREEN}✅ PASSED{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}✅{Colors.RESET}")
        PASSED += 1
        return TestResult(name, True)
        
    except requests.exceptions.Timeout:
        if verbose:
            print(f"   {Colors.RED}❌ FAILED - Timeout{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ TIMEOUT{Colors.RESET}")
        FAILED += 1
        return TestResult(name, False, "Timeout")
    except Exception as e:
        if verbose:
            print(f"   {Colors.RED}❌ FAILED - Error: {e}{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌{Colors.RESET}")
        FAILED += 1
        return TestResult(name, False, str(e))


def test_performance(name: str, url: str, max_time_ms: int, verbose: bool = False) -> TestResult:
    """Test endpoint performance."""
    global PASSED, FAILED, WARNINGS
    
    if verbose:
        print(f"\n⚡ Performance Test: {name}")
        print(f"   URL: {url}")
        print(f"   Max time: {max_time_ms}ms")
    else:
        print(f"Performance {name}...", end=" ")
    
    try:
        start = time.time()
        response = requests.get(url, timeout=15)
        elapsed_ms = (time.time() - start) * 1000
        
        if response.status_code != 200:
            if verbose:
                print(f"   {Colors.RED}❌ FAILED - Status {response.status_code}{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌{Colors.RESET}")
            FAILED += 1
            return TestResult(name, False, f"Status {response.status_code}")
        
        if elapsed_ms <= max_time_ms:
            if verbose:
                print(f"   {Colors.GREEN}✅ PASSED - {elapsed_ms:.0f}ms{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}✅ {elapsed_ms:.0f}ms{Colors.RESET}")
            PASSED += 1
            return TestResult(name, True)
        else:
            if verbose:
                print(f"   {Colors.YELLOW}⚠️  WARNING - {elapsed_ms:.0f}ms (expected <{max_time_ms}ms){Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️  {elapsed_ms:.0f}ms{Colors.RESET}")
            WARNINGS += 1
            return TestResult(name, True, warning=f"Slow: {elapsed_ms:.0f}ms")
        
    except Exception as e:
        if verbose:
            print(f"   {Colors.RED}❌ FAILED - Error: {e}{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌{Colors.RESET}")
        FAILED += 1
        return TestResult(name, False, str(e))


def run_all_tests(verbose: bool = False, skip_slow: bool = False):
    """Run comprehensive test suite."""
    
    print_header("XANDEUM PNODE ANALYTICS - COMPREHENSIVE TEST SUITE", 1)
    print(f"Testing against: {BASE_URL}")
    print(f"Verbose mode: {verbose}")
    print(f"Skip slow tests: {skip_slow}")
    
    # Phase 0: Health Check
    print_header("Phase 0: System Health", 2)
    
    test_endpoint(
        "API Health Check",
        f"{BASE_URL}/health",
        ["status", "snapshot_age_seconds"],
        verbose
    )
    
    # Phase 1: Core Endpoints
    print_header("Phase 1: Core Endpoints", 2)
    
    test_endpoint(
        "Root Endpoint",
        f"{BASE_URL}/",
        ["api_name", "version", "core_endpoints"],
        verbose
    )
    
    test_endpoint(
        "Legacy All Nodes",
        f"{BASE_URL}/all-nodes",
        ["summary", "nodes"],
        verbose
    )
    
    test_endpoint(
        "Registry List",
        f"{BASE_URL}/registry?limit=10",
        ["count", "items"],
        verbose
    )
    
    # Phase 2 & 3: Unified Endpoints with Scoring
    print_header("Phase 2 & 3: Unified Endpoints with Scoring", 2)
    
    test_endpoint(
        "Get Online Nodes",
        f"{BASE_URL}/pnodes?status=online&limit=10",
        ["summary", "pnodes", "network_stats"],
        verbose
    )
    
    test_endpoint(
        "Get All Nodes",
        f"{BASE_URL}/pnodes?status=all&limit=20",
        ["summary", "pnodes", "pagination"],
        verbose
    )
    
    test_endpoint(
        "Staking Recommendations",
        f"{BASE_URL}/recommendations?limit=5",
        ["recommendations", "total_evaluated"],
        verbose
    )
    
    test_endpoint(
        "Network Topology",
        f"{BASE_URL}/network/topology",
        ["nodes", "edges", "stats"],
        verbose
    )
    
    test_endpoint(
        "Network Health",
        f"{BASE_URL}/network/health",
        ["health", "network_stats", "alerts"],
        verbose
    )
    
    test_endpoint(
        "Operators List",
        f"{BASE_URL}/operators?limit=10",
        ["summary", "operators"],
        verbose
    )
    
    # Phase 4: Historical & Analytics
    print_header("Phase 4: Historical & Analytics", 2)
    
    test_endpoint(
        "Network History",
        f"{BASE_URL}/network/history?hours=24",
        ["history", "summary"],
        verbose
    )
    
    test_endpoint(
        "Network Growth",
        f"{BASE_URL}/network/growth?hours=24",
        ["growth_metrics", "timestamp"],
        verbose
    )
    
    test_endpoint(
        "Network Analytics",
        f"{BASE_URL}/network/analytics",
        ["current_state", "growth", "version_analysis", "recommendations"],
        verbose
    )
    
    # Phase 5: Advanced Features
    print_header("Phase 5: Advanced Features", 2)
    
    test_endpoint(
        "All Alerts",
        f"{BASE_URL}/alerts?limit=10",
        ["summary", "nodes_checked"],
        verbose
    )
    
    test_endpoint(
        "Critical Alerts",
        f"{BASE_URL}/alerts/critical",
        ["summary", "critical_nodes"],
        verbose
    )
    
    test_endpoint(
        "Network Consistency",
        f"{BASE_URL}/network/consistency",
        ["nodes", "summary", "flapping_nodes"],
        verbose
    )
    
    # Performance Tests
    if not skip_slow:
        print_header("Performance Tests", 2)
        
        test_performance("Health (<100ms)", f"{BASE_URL}/health", 100, verbose)
        test_performance("PNodes (<500ms)", f"{BASE_URL}/pnodes?limit=100", 500, verbose)
        test_performance("Recommendations (<600ms)", f"{BASE_URL}/recommendations", 600, verbose)
        test_performance("Topology (<400ms)", f"{BASE_URL}/network/topology", 400, verbose)
        test_performance("Network Health (<800ms)", f"{BASE_URL}/network/health", 800, verbose)
    
    # Integration Tests
    print_header("Integration Tests", 2)
    
    print("Testing node-specific endpoints...", end=" ")
    try:
        # Get a sample node
        response = requests.get(f"{BASE_URL}/pnodes?status=online&limit=1")
        nodes = response.json().get("pnodes", [])
        
        if nodes:
            address = nodes[0].get("address")
            
            # Test registry lookup
            reg_response = requests.get(f"{BASE_URL}/registry/{address}")
            if reg_response.status_code == 200:
                print(f"{Colors.GREEN}✅{Colors.RESET}")
                global PASSED
                PASSED += 1
            else:
                print(f"{Colors.RED}❌{Colors.RESET}")
                global FAILED
                FAILED += 1
        else:
            print(f"{Colors.YELLOW}⚠️  SKIPPED (no nodes){Colors.RESET}")
            global SKIPPED
            SKIPPED += 1
    except Exception as e:
        print(f"{Colors.RED}❌ {e}{Colors.RESET}")
        FAILED += 1
    
    # Data Consistency Tests
    print_header("Data Consistency Tests", 2)
    
    print("Checking node counts consistency...", end=" ")
    try:
        response = requests.get(f"{BASE_URL}/pnodes?status=all&limit=10000")
        data = response.json()
        
        summary = data.get("summary", {})
        pnodes = data.get("pnodes", [])
        
        total_summary = summary.get("total_pnodes", 0)
        online_summary = summary.get("online_pnodes", 0)
        offline_summary = summary.get("offline_pnodes", 0)
        
        # Count from actual data
        online_count = sum(1 for n in pnodes if n.get("is_online", False))
        offline_count = sum(1 for n in pnodes if not n.get("is_online", True))
        
        if online_count == online_summary and offline_count == offline_summary:
            print(f"{Colors.GREEN}✅{Colors.RESET}")
            PASSED += 1
        else:
            print(f"{Colors.RED}❌ Count mismatch{Colors.RESET}")
            FAILED += 1
    except Exception as e:
        print(f"{Colors.RED}❌ {e}{Colors.RESET}")
        FAILED += 1
    
    # Null-Safety Tests
    print_header("Null-Safety Tests", 2)
    
    print("Testing sorting with null values...", end=" ")
    try:
        # Try sorting by various fields
        fields = ["uptime", "storage_used", "score", "last_seen"]
        all_passed = True
        
        for field in fields:
            response = requests.get(f"{BASE_URL}/pnodes?sort_by={field}&limit=5")
            if response.status_code != 200:
                all_passed = False
                break
        
        if all_passed:
            print(f"{Colors.GREEN}✅{Colors.RESET}")
            PASSED += 1
        else:
            print(f"{Colors.RED}❌{Colors.RESET}")
            FAILED += 1
    except Exception as e:
        print(f"{Colors.RED}❌ {e}{Colors.RESET}")
        FAILED += 1


def print_final_summary():
    """Print final test summary with statistics."""
    print_header("FINAL TEST SUMMARY", 1)
    
    total = PASSED + FAILED + SKIPPED
    pass_rate = (PASSED / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BLUE}Statistics:{Colors.RESET}")
    print(f"  Total Tests:    {total}")
    print(f"  {Colors.GREEN}Passed:{Colors.RESET}         {PASSED} ✅")
    print(f"  {Colors.RED}Failed:{Colors.RESET}         {FAILED} ❌")
    print(f"  {Colors.YELLOW}Warnings:{Colors.RESET}       {WARNINGS} ⚠️")
    print(f"  Skipped:        {SKIPPED}")
    print(f"  {Colors.BLUE}Pass Rate:{Colors.RESET}      {pass_rate:.1f}%")
    
    if FAILED == 0 and WARNINGS == 0:
        print(f"\n{Colors.GREEN}{'=' * 80}")
        print(f"  🎉 ALL TESTS PASSED - PRODUCTION READY!")
        print(f"{'=' * 80}{Colors.RESET}")
        return 0
    elif FAILED == 0:
        print(f"\n{Colors.YELLOW}{'=' * 80}")
        print(f"  ⚠️  ALL TESTS PASSED WITH WARNINGS")
        print(f"  Review performance warnings above")
        print(f"{'=' * 80}{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}{'=' * 80}")
        print(f"  ❌ SOME TESTS FAILED")
        print(f"  Review failures above before deployment")
        print(f"{'=' * 80}{Colors.RESET}")
        return 1


def check_prerequisites():
    """Check if API is running and healthy."""
    print_header("Pre-Flight Checks", 2)
    
    print("Checking API availability...", end=" ")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅{Colors.RESET}")
            data = response.json()
            
            status = data.get("status")
            age = data.get("snapshot_age_seconds", 0)
            
            if status == "healthy":
                print(f"  Status: {Colors.GREEN}Healthy{Colors.RESET}")
                print(f"  Snapshot age: {age}s")
                return True
            else:
                print(f"  {Colors.YELLOW}⚠️  Status: {status}{Colors.RESET}")
                print(f"  Snapshot age: {age}s")
                print(f"  {Colors.YELLOW}Proceeding with tests...{Colors.RESET}")
                return True
        else:
            print(f"{Colors.RED}❌ Status {response.status_code}{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ {e}{Colors.RESET}")
        print(f"\n{Colors.RED}ERROR: Cannot connect to API at {BASE_URL}{Colors.RESET}")
        print("\nMake sure the API is running:")
        print("  uvicorn app.main:app --reload --port 8000")
        return False


def main():
    """Main test runner with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test suite for Xandeum pNode Analytics API"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed test output"
    )
    parser.add_argument(
        "--skip-slow", "-s",
        action="store_true",
        help="Skip performance tests"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    global BASE_URL
    BASE_URL = args.url
    
    print(f"\n{Colors.BLUE}{'🚀' * 40}")
    print(f"  XANDEUM PNODE ANALYTICS - PHASE 6 COMPREHENSIVE TEST")
    print(f"{'🚀' * 40}{Colors.RESET}")
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Run all tests
    try:
        run_all_tests(verbose=args.verbose, skip_slow=args.skip_slow)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test run interrupted by user{Colors.RESET}")
        sys.exit(1)
    
    # Print summary and exit
    exit_code = print_final_summary()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()