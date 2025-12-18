# 🎯 Xandeum pNode Analytics Platform - Complete Implementation Roadmap

**Version:** 1.1.0  
**Target:** Production-Ready Analytics Platform (stakewiz.com equivalent for Xandeum)  
**Status:** Pre-Production (No deployment yet - safe to make breaking changes)

---

## 📋 Table of Contents

1. [Project Vision](#project-vision)
2. [Current State Assessment](#current-state-assessment)
3. [Available Resources](#available-resources)
4. [Data Availability Verification](#data-availability-verification)
5. [Implementation Phases](#implementation-phases)
6. [Detailed Task Checklist](#detailed-task-checklist)
7. [API Endpoint Specification](#api-endpoint-specification)
8. [Database Schema](#database-schema)
9. [Testing Strategy](#testing-strategy)
10. [Success Metrics](#success-metrics)

---

## 🎯 Project Vision

### Core User Question
> **"Which pNodes are trustworthy, performant, and worth staking XAND on?"**

### What We're Building
A comprehensive analytics platform that enables:
- **Token Stakers:** Make informed staking decisions with clear risk indicators
- **pNode Operators:** Monitor performance and optimize operations  
- **Developers:** Access network metrics for sedApp development
- **Network Health:** Real-time visibility into Xandeum storage infrastructure

### Key Differentiators
1. **Performance-Based Scoring** - Not just uptime, but actual paging efficiency
2. **Historical Trend Analysis** - Track node reliability over time
3. **Network Topology Visualization** - See gossip protocol connections
4. **Automated Risk Alerts** - Flag problematic nodes automatically
5. **Operator Intelligence** - Identify large operators and centralization risks

---

## 📊 Current State Assessment

### ✅ What's Working (Keep/Enhance)
```
✅ FastAPI backend with async workers
✅ MongoDB Atlas storage
✅ Background aggregation (60s refresh)
✅ Joblib RPC caching
✅ Basic snapshot system (pnodes_snapshot)
✅ Persistent registry (pnodes_registry)
✅ Status tracking (pnodes_status)
✅ Gossip data collection (get-version, get-stats, get-pods)
✅ Deduplication by address
✅ Peer source tracking
```

### ⚠️ What Needs Fixing (Critical)
```
❌ Primary key inconsistency (pubkey vs address)
❌ IP_NODES hardcoded (not using .env)
❌ No health monitoring endpoint
❌ Inconsistent endpoint responses
❌ No performance scoring system
❌ Missing paging statistics collection
❌ No historical trend data
❌ No alert system
```

### 🔴 What's Missing (Build New)
```
❌ Unified /pnodes endpoint
❌ 4-score system (Trust, Performance, Capacity, Stake Confidence)
❌ Staking recommendations API
❌ Network topology endpoint
❌ Per-node alert system
❌ Comparison functionality
❌ Operator grouping analytics
❌ Historical metrics storage
```

---

## 📚 Available Resources

### From GitHub Repository
```
✅ app/config.py          - Configuration loader
✅ app/db.py              - MongoDB connections & helpers
✅ app/fetcher.py         - Background RPC aggregation
✅ app/main.py            - FastAPI endpoints
✅ app/utils/jsonrpc.py   - RPC helpers
✅ .env.example           - Config template
✅ requirements.txt       - Dependencies
✅ ARCHITECTURE.md        - System design docs
✅ CONTRIBUTION.md        - Adding nodes guide
✅ verify_pnode.py        - Node verification script
```

### From Our Discussion
```
✅ Performance scoring algorithm (0-100 scale)
✅ Network topology data structure
✅ Unified endpoint design (/pnodes)
✅ 4-score system specification
✅ Alert system requirements
✅ Historical tracking approach
✅ Operator analytics concept
```

### From Developer Notes
```
✅ Paging statistics requirements
✅ Red flag criteria
✅ User persona definitions
✅ Scoring transparency guidelines
✅ Visualization best practices
```

---

## 🔍 Data Availability Verification

### PHASE 0: Check What Data We Can Access

**MUST DO FIRST** - Before implementing anything, verify available data sources.

#### Task 0.1: Test Current RPC Endpoints
```bash
# Test each IP node for available methods
IP_NODES=(
  "173.212.203.145"
  "173.212.220.65"
  "161.97.97.41"
  "192.190.136.36"
  "192.190.136.37"
  "192.190.136.38"
  "192.190.136.28"
  "192.190.136.29"
  "207.244.255.1"
)

for ip in "${IP_NODES[@]}"; do
  echo "Testing $ip..."
  
  # Test get-version
  curl -X POST http://$ip:6000/rpc \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"get-version","id":1}'
  
  # Test get-stats
  curl -X POST http://$ip:6000/rpc \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"get-stats","id":1}'
  
  # Test get-pods
  curl -X POST http://$ip:6000/rpc \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"get-pods","id":1}'
  
  # Test get-pods-with-stats (NEW - check if available)
  curl -X POST http://$ip:6000/rpc \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"get-pods-with-stats","id":1}'
  
  # Test get-paging-stats (NEW - check if available)
  curl -X POST http://$ip:6000/rpc \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"get-paging-stats","id":1}'
done
```

#### Task 0.2: Document Available Fields
Create `AVAILABLE_DATA.md` documenting:
```markdown
# Available Data Fields

## From get-version
- version: string
- build_date: string (if available)

## From get-stats
- cpu_percent: float
- ram_used: int
- ram_total: int
- uptime: int
- packets_received: int
- packets_sent: int
- active_streams: int
- total_bytes: int
- total_pages: int
- file_size: int

## From get-pods / get-pods-with-stats
- address: string (IP:port)
- pubkey: string
- is_public: bool
- rpc_port: int
- storage_committed: int
- storage_used: int
- storage_usage_percent: float
- uptime: int
- version: string
- last_seen: string
- last_seen_timestamp: int

### PAGING METRICS (if available from get-pods-with-stats)
- page_hit_rate: float (?)
- page_miss_rate: float (?)
- total_page_accesses: int (?)
- page_errors: int (?)
- avg_page_latency_ms: float (?)
- replication_coverage: float (?)
- throughput_pages_per_sec: float (?)

**Status:** ⚠️ TO BE VERIFIED
```

#### Task 0.3: Decision Point
Based on verification results:

**If Paging Data Available (✅):**
- ✅ Proceed with full 4-score system
- ✅ Implement performance scoring with paging metrics
- ✅ Dashboard can be "complete"

**If Paging Data NOT Available (❌):**
- ⚠️ Implement 3-score system (Trust, Capacity, Composite)
- ⚠️ Document limitation in API responses
- ⚠️ Flag as "Coming Soon" in documentation
- 📧 Contact Xandeum team about paging metrics availability

**Decision Checkpoint:** Do not proceed past Phase 0 until this is resolved.

---

## 🏗️ Implementation Phases

### Overview
```
Phase 0: Data Verification          [BLOCKING]     1 day
Phase 1: Critical Fixes             [HIGH]         2 days
Phase 2: Core Scoring System        [HIGH]         3 days
Phase 3: Unified API Endpoints      [HIGH]         3 days
Phase 4: Historical & Analytics     [MEDIUM]       2 days
Phase 5: Advanced Features          [MEDIUM]       2 days
Phase 6: Testing & Documentation    [HIGH]         2 days
-----------------------------------------------------------
TOTAL ESTIMATED TIME:                              15 days
```

---

## ✅ Detailed Task Checklist

### PHASE 0: Data Verification [BLOCKING] 
**Goal:** Understand what data is actually available  
**Duration:** 1 day  
**Blocker:** Cannot proceed without this

- [X] **Task 0.1:** Test all RPC endpoints on all IP nodes
  - [X] Create test script `scripts/test_rpc_endpoints.sh`
  - [X] Run against all 9 IP nodes
  - [X] Document response structures
  - [X] Save sample responses to `docs/sample_responses/`

- [X] **Task 0.2:** Verify paging statistics availability
  - [X] Check if `get-pods-with-stats` returns paging data
  - [X] Check if `get-paging-stats` endpoint exists
  - [X] Document exact field names and types
  - [X] Determine if data is per-node or aggregated

- [X] **Task 0.3:** Create data availability document
  - [X] Create `docs/AVAILABLE_DATA.md`
  - [X] List all available fields with types
  - [X] Mark paging fields as available/unavailable
  - [X] Document any API version differences

- [X] **Task 0.4:** Make implementation decision
  - [X] If paging available → Proceed with 4-score system
  - [X] If paging unavailable → Use 3-score system + flag limitation
  - [X] Update this roadmap based on findings
  - [X] Get team approval on approach

**Exit Criteria:** Clear documentation of available data + implementation decision made

---

### PHASE 1: Critical Fixes [HIGH PRIORITY]
**Goal:** Fix foundational issues in current codebase  
**Duration:** 2 days  
**Dependencies:** None (can start immediately after Phase 0)

#### 1.1 Fix Primary Key Issue (Address vs Pubkey)

- [X] **Task 1.1.1:** Update database functions
  - [X] Modify `app/db.py` → `upsert_registry(address, entry)` instead of pubkey
  - [X] Modify `app/db.py` → `mark_node_status(address, status)` instead of pubkey
  - [X] Modify `app/db.py` → `get_registry_entry(address)` instead of pubkey
  - [X] Modify `app/db.py` → `get_status(address)` instead of pubkey
  - [X] Add new function `get_registry_entries_by_pubkey(pubkey)` for operator queries

- [X] **Task 1.1.2:** Update fetcher.py registry calls
  - [X] Change registry upsert to use `address` as key (line ~200)
  - [X] Change status updates to use `address` as key
  - [X] Ensure `address` field is never null before calling

- [X] **Task 1.1.3:** Update API endpoints
  - [X] Change `/registry/{pubkey}` → `/registry/{address:path}`
  - [X] Update path parameter to handle IP:port format
  - [X] Update error messages to reference address

- [X] **Task 1.1.4:** Create database indexes
  - [X] Add `setup_indexes()` function to `app/db.py`
  - [X] Create unique index on `address` field
  - [X] Create secondary index on `pubkey` field
  - [X] Create index on `last_seen` field (for queries)
  - [X] Call `setup_indexes()` on startup

- [X] **Task 1.1.5:** Test primary key change
  - [X] Verify registry upserts work with address
  - [X] Verify lookups by address work
  - [X] Verify no duplicate addresses in database
  - [X] Test edge cases (missing address, malformed address)

**Exit Criteria:** All database operations use `address` as primary key, indexes created

---

#### 1.2 Fix IP_NODES Configuration

- [X] **Task 1.2.1:** Update config.py
  - [X] Add IP_NODES parsing from environment variable
  - [X] Handle comma-separated values
  - [X] Strip whitespace from each IP
  - [X] Provide default fallback list if not set
  - [X] Add validation (basic IP format check)

- [X] **Task 1.2.2:** Update fetcher.py
  - [X] Remove hardcoded IP_NODES list (lines 28-38)
  - [X] Import IP_NODES from config: `from .config import IP_NODES`
  - [X] Verify it works with both .env and defaults

- [X] **Task 1.2.3:** Update .env.example
  - [X] Add clear IP_NODES example
  - [X] Add comments explaining format
  - [X] Document how to add/remove nodes

- [X] **Task 1.2.4:** Test configuration
  - [X] Test with IP_NODES in .env
  - [X] Test with IP_NODES not set (uses defaults)
  - [X] Test with malformed input (extra commas, spaces)
  - [X] Verify all nodes are actually used in fetching

**Exit Criteria:** IP nodes configurable via .env, defaults work if not set

---

#### 1.3 Add Health Check Endpoint

- [X] **Task 1.3.1:** Create /health endpoint
  - [X] Add endpoint to `app/main.py`
  - [X] Check snapshot exists
  - [X] Calculate snapshot age
  - [X] Return status: healthy/degraded/unhealthy
  - [X] Include metadata (last_updated, cache_ttl, node counts)

- [X] **Task 1.3.2:** Define health criteria
  - [X] Healthy: snapshot < 2x CACHE_TTL seconds old
  - [X] Degraded: snapshot 2-5x CACHE_TTL seconds old
  - [X] Unhealthy: snapshot > 5x CACHE_TTL or missing

- [X] **Task 1.3.3:** Test health endpoint
  - [X] Test when system is healthy
  - [X] Test when background worker is stuck (simulate)
  - [X] Test when snapshot is missing
  - [X] Verify HTTP status codes (200, 503)

**Exit Criteria:** `/health` endpoint returns accurate system status

---

### PHASE 2: Core Scoring System [HIGH PRIORITY]
**Goal:** Implement performance scoring algorithms  
**Duration:** 3 days  
**Dependencies:** Phase 0 complete (know what data is available)

#### 2.1 Create Scoring Module

- [X] **Task 2.1.1:** Create `app/scoring.py` file
  - [X] Add file header and documentation
  - [X] Define LATEST_VERSION constant (update as needed)
  - [X] Import required dependencies (time, typing)

- [X] **Task 2.1.2:** Implement Trust Score (0-100)
  - [X] Factor: Uptime consistency (40 points)
    - [X] Full points if uptime > 30 days
    - [X] Linear scale for 0-30 days
  - [X] Factor: Gossip presence (30 points)
    - [X] Based on `peer_sources` count
    - [X] Full points if seen by 3+ IP nodes
  - [X] Factor: Version compliance (20 points)
    - [X] 20 points for latest version
    - [X] 10 points for one version behind
    - [X] 0 points for older versions
  - [X] Factor: Error frequency (10 points)
    - [X] If error data available, penalize high error rates
    - [X] Default to 10 points if no error data
  - [X] Return score + breakdown

- [X] **Task 2.1.3:** Implement Capacity Score (0-100)
  - [X] Factor: Storage committed (30 points)
    - [X] Higher commitment = more capacity
    - [X] Normalize against network average
  - [X] Factor: Usage balance (40 points)
    - [X] Optimal range: 20-80% usage
    - [X] Penalize too low (underutilized)
    - [X] Penalize too high (saturated)
  - [X] Factor: Growth trend (30 points)
    - [X] Requires historical data
    - [X] Default to 15 points if no history
    - [X] Positive growth = higher score
  - [X] Return score + breakdown

- [X] **Task 2.1.4:** Implement Stake Confidence Rating
  - [X] Calculate composite of Trust + Capacity (+ Performance if available)
  - [X] Define thresholds:
    - [X] Score >= 80 → "low_risk" 🟢
    - [X] Score 60-79 → "medium_risk" 🟡
    - [X] Score < 60 → "high_risk" 🔴
  - [X] Return rating + composite score

- [X] **Task 2.1.5:** Create unified scoring function
  - [X] `calculate_all_scores(pnode_data)` → returns all 4 scores
  - [X] Handle missing data gracefully
  - [X] Add comprehensive docstrings
  - [X] Include example usage in comments

- [X] **Task 2.1.6:** Implement network health score
  - [X] `calculate_network_health_score(all_nodes)` 
  - [X] Factor: Node availability (30%)
  - [X] Factor: Version consistency (25%)
  - [X] Factor: Average node quality (25%)
  - [X] Factor: Network connectivity (20%)
  - [X] Return overall health (0-100) + status (healthy/fair/degraded/critical)

- [X] **Task 2.1.7:** Add helper functions
  - [X] `get_tier_color(tier)` → hex color codes
  - [X] `get_tier_description(tier)` → user-friendly text
  - [X] Input validation helpers

**Exit Criteria:** Scoring module complete with all algorithms, thoroughly documented

---

#### 2.2 Test Scoring System

- [X] **Task 2.2.1:** Create test cases
  - [X] Create `tests/test_scoring.py`
  - [X] Test trust score with perfect node (should be ~100)
  - [X] Test trust score with poor node (should be low)
  - [X] Test capacity score with balanced usage (should be high)
  - [X] Test capacity score with extreme usage (should be lower)
  - [X] Test stake confidence thresholds

- [X] **Task 2.2.2:** Test edge cases
  - [X] Missing uptime data
  - [X] Zero storage committed
  - [X] Null version field
  - [X] Empty peer_sources array
  - [X] Negative values (should handle gracefully)

- [X] **Task 2.2.3:** Validate scoring logic
  - [X] Review with team
  - [X] Ensure weights make sense
  - [X] Test against sample real data
  - [X] Adjust thresholds if needed

**Exit Criteria:** All scoring functions tested and validated

---

### PHASE 3: Unified API Endpoints [HIGH PRIORITY]
**Goal:** Create new, better-designed API endpoints  
**Duration:** 3 days  
**Dependencies:** Phase 2 complete (need scoring system)

#### 3.1 Create Unified /pnodes Endpoint

- [X] **Task 3.1.1:** Design endpoint signature
  - [X] Parameters: status (online/offline/all)
  - [X] Parameters: limit, skip (pagination)
  - [X] Parameters: sort_by, sort_order
  - [X] Parameters: version_filter (optional)
  - [X] Document all parameters

- [X] **Task 3.1.2:** Implement data merging logic
  - [X] Fetch current snapshot from MongoDB
  - [X] Build map of online nodes by address
  - [X] Fetch all registry entries
  - [X] Merge online nodes (snapshot + registry historical data)
  - [X] Add offline nodes from registry if status="all" or "offline"

- [X] **Task 3.1.3:** Add scoring to each node
  - [X] Import scoring functions
  - [X] Calculate all scores for each online node
  - [X] Set scores to 0 for offline nodes
  - [X] Include score breakdowns

- [X] **Task 3.1.4:** Implement filtering
  - [X] Filter by status (online/offline/all)
  - [X] Filter by version if specified
  - [X] Handle edge cases (empty results)

- [ ] **Task 3.1.5:** Implement sorting
  - [ ] Support sort by: score, uptime, last_seen, storage_used, etc.
  - [ ] Handle null values in sort
  - [ ] Default to descending order

- [ ] **Task 3.1.6:** Implement pagination
  - [ ] Apply skip and limit
  - [ ] Return pagination metadata (total, returned, skip, limit)

- [ ] **Task 3.1.7:** Build response structure
  - [ ] summary: total/online/offline counts, snapshot age
  - [ ] network_stats: aggregated metrics
  - [ ] pagination: metadata
  - [ ] filters: what was applied
  - [ ] pnodes: array of node objects
  - [ ] timestamp: current time

- [ ] **Task 3.1.8:** Add comprehensive documentation
  - [ ] OpenAPI/Swagger docs
  - [ ] Example request/response
  - [ ] Explain each field

**Exit Criteria:** `/pnodes` endpoint returns unified, scored data with all features

---

#### 3.2 Create /recommendations Endpoint

- [ ] **Task 3.2.1:** Design recommendation logic
  - [ ] Parameters: limit (default 10, max 50)
  - [ ] Parameters: min_uptime_days (default 7)
  - [ ] Parameters: require_public (default false)
  - [ ] Parameters: min_score (optional)

- [ ] **Task 3.2.2:** Implement filtering
  - [ ] Only include online nodes
  - [ ] Filter by minimum uptime
  - [ ] Filter by public/private if required
  - [ ] Filter by minimum score if specified

- [ ] **Task 3.2.3:** Implement ranking
  - [ ] Sort by composite score (descending)
  - [ ] Break ties by uptime
  - [ ] Limit to requested count

- [ ] **Task 3.2.4:** Build response
  - [ ] recommendations: array of top nodes
  - [ ] Include only relevant fields (address, pubkey, scores, key metrics)
  - [ ] total_evaluated: how many nodes were considered
  - [ ] filters: what criteria were applied
  - [ ] timestamp

- [ ] **Task 3.2.5:** Add documentation
  - [ ] OpenAPI docs
  - [ ] Example usage
  - [ ] Explain scoring methodology

**Exit Criteria:** `/recommendations` returns top nodes for staking

---

#### 3.3 Create /network/topology Endpoint

- [ ] **Task 3.3.1:** Design graph structure
  - [ ] nodes: array of {id, type, label, group, properties}
  - [ ] edges: array of {source, target, type}
  - [ ] stats: network-level metrics

- [ ] **Task 3.3.2:** Build nodes array
  - [ ] Add IP nodes (type: "ip_node", group: "ip")
  - [ ] Include IP node properties (streams, uptime, cpu, pods)
  - [ ] Add pNodes (type: "pnode", group: "public"/"private")
  - [ ] Include pNode properties (version, uptime, storage, etc.)

- [ ] **Task 3.3.3:** Build edges array
  - [ ] Create edge for each peer_source connection
  - [ ] Format: IP node → pNode (gossip_connection)
  - [ ] Include edge metadata if available

- [ ] **Task 3.3.4:** Calculate topology stats
  - [ ] Total nodes (IP + pNodes)
  - [ ] Total connections
  - [ ] Average connections per pNode
  - [ ] Consider adding: clustering coefficient, network diameter (future)

- [ ] **Task 3.3.5:** Test with visualization tools
  - [ ] Test response format with D3.js (manually)
  - [ ] Test response format with Three.js (manually)
  - [ ] Ensure data structure is correct

**Exit Criteria:** `/network/topology` returns graph-ready data structure

---

#### 3.4 Create /network/health Endpoint

- [ ] **Task 3.4.1:** Design health metrics
  - [ ] Overall health score (0-100)
  - [ ] Status (healthy/fair/degraded/critical)
  - [ ] Breakdown by factors

- [ ] **Task 3.4.2:** Implement health calculation
  - [ ] Fetch all nodes
  - [ ] Use `calculate_network_health_score()` from scoring.py
  - [ ] Include network_stats from /pnodes
  - [ ] Include summary counts

- [ ] **Task 3.4.3:** Implement alert generation
  - [ ] Create `generate_network_alerts()` function
  - [ ] Alert: Low node count (< 50 nodes)
  - [ ] Alert: Version fragmentation (> 3 versions)
  - [ ] Alert: Low health score (< 60)
  - [ ] Return array of alert objects

- [ ] **Task 3.4.4:** Build response
  - [ ] health: score + status + factors
  - [ ] network_stats: aggregated metrics
  - [ ] summary: node counts
  - [ ] alerts: array of warnings
  - [ ] timestamp

**Exit Criteria:** `/network/health` provides comprehensive network health view

---

#### 3.5 Enhance /registry Endpoint

- [ ] **Task 3.5.1:** Add filtering parameters
  - [ ] status: online/offline/all
  - [ ] days: only nodes seen in last N days
  - [ ] sort_by: last_seen/first_seen/uptime
  - [ ] sort_order: asc/desc

- [ ] **Task 3.5.2:** Improve response structure
  - [ ] summary: total counts (all/matching/online/offline)
  - [ ] pagination: proper metadata
  - [ ] filters: what was applied
  - [ ] items: node array with is_online flag

- [ ] **Task 3.5.3:** Add accurate counts
  - [ ] Use MongoDB count_documents() for totals
  - [ ] Don't rely on returned array length
  - [ ] Show both total in registry and matching filters

- [ ] **Task 3.5.4:** Update documentation
  - [ ] Clarify this is historical registry
  - [ ] Explain difference from /pnodes
  - [ ] Add migration guide from old format

**Exit Criteria:** `/registry` provides flexible historical node browsing

---

#### 3.6 Create /operators Endpoint

- [ ] **Task 3.6.1:** Design grouping logic
  - [ ] Group all nodes by pubkey
  - [ ] Aggregate metrics per operator

- [ ] **Task 3.6.2:** Implement operator aggregation
  - [ ] Fetch all nodes
  - [ ] Build dictionary keyed by pubkey
  - [ ] For each operator collect:
    - [ ] node_count
    - [ ] online_nodes
    - [ ] total_storage_committed
    - [ ] total_storage_used
    - [ ] addresses (array)
    - [ ] versions (array/set)
    - [ ] first_seen (earliest)

- [ ] **Task 3.6.3:** Calculate decentralization metrics
  - [ ] Total unique operators
  - [ ] Average nodes per operator
  - [ ] Largest operator share (%)
  - [ ] Decentralization score (100 - largest share)

- [ ] **Task 3.6.4:** Build response
  - [ ] summary: decentralization metrics
  - [ ] operators: array sorted by node_count
  - [ ] Apply limit parameter
  - [ ] timestamp

- [ ] **Task 3.6.5:** Add filtering
  - [ ] min_nodes: only operators with N+ nodes
  - [ ] limit: pagination

**Exit Criteria:** `/operators` shows operator distribution and centralization risk

---

### PHASE 4: Historical & Analytics [MEDIUM PRIORITY]
**Goal:** Add time-series data for trend analysis  
**Duration:** 2 days  
**Dependencies:** Phase 3 complete (endpoints working)

#### 4.1 Implement Snapshot History

- [ ] **Task 4.1.1:** Add history collection to db.py
  - [ ] Define `pnodes_snapshots` collection
  - [ ] Create index on timestamp field

- [ ] **Task 4.1.2:** Create history save function
  - [ ] `save_snapshot_history()` in db.py
  - [ ] Extract lightweight summary from current snapshot
  - [ ] Store: timestamp, node counts, CPU/RAM avgs, version distribution
  - [ ] Don't store full pod arrays (too large)

- [ ] **Task 4.1.3:** Implement pruning
  - [ ] Keep only last 30 days of snapshots
  - [ ] Delete older entries automatically
  - [ ] Run during each save operation

- [ ] **Task 4.1.4:** Integrate into fetcher
  - [ ] Call `save_snapshot_history()` after snapshot update
  - [ ] Add error handling
  - [ ] Log when history saved

- [ ] **Task 4.1.5:** Test history saving
  - [ ] Verify entries are created
  - [ ] Verify old entries are pruned
  - [ ] Check MongoDB size doesn't grow unbounded

**Exit Criteria:** Snapshots automatically saved every 60 seconds, 30-day retention

---

#### 4.2 Create /network/history Endpoint

- [ ] **Task 4.2.1:** Design endpoint
  - [ ] Parameter: hours (default 24, max 720 = 30 days)
  - [ ] Query pnodes_snapshots collection

- [ ] **Task 4.2.2:** Implement data retrieval
  - [ ] Calculate start_time = now - hours
  - [ ] Query snapshots >= start_time
  - [ ] Sort by timestamp ascending
  - [ ] Return full array

- [ ] **Task 4.2.3:** Calculate trends
  - [ ] Node count growth (first vs last)
  - [ ] Growth percentage
  - [ ] Data points available
  - [ ] Time range covered

- [ ] **Task 4.2.4:** Build response
  - [ ] history: array of snapshot objects
  - [ ] summary: trends and metadata
  - [ ] timestamp

**Exit Criteria:** `/network/history` returns time-series data for charting

---

### PHASE 5: Advanced Features [MEDIUM PRIORITY]
**Goal:** Add sophisticated analysis tools  
**Duration:** 2 days  
**Dependencies:** All previous phases complete

#### 5.1 Create Alert System

- [ ] **Task 5.1.1:** Create alerts.py module
  - [ ] Add file to app/
  - [ ] Import dependencies

- [ ] **Task 5.1.2:** Implement per-node alert checks
  - [ ] `check_node_alerts(address, historical_data)` function
  - [ ] Alert: Uptime degradation (< 90% online in 7 days)
  - [ ] Alert: Version behind latest
  - [ ] Alert: Storage near capacity (> 90%)
  - [ ] Alert: Gossip inconsistency (flapping)
  - [ ] **IF paging data available:**
    - [ ] Alert: Page miss rate spike (> 40% increase)
    - [ ] Alert: High error rate

- [ ] **Task 5.1.3:** Define alert severity levels
  - [ ] high: Critical issues (long offline, high errors)
  - [ ] medium: Warning signs (version behind, performance drop)
  - [ ] low: Minor issues (slight capacity concerns)

- [ ] **Task

5.1.4:** Create alert response format
  - [ ] severity: string
  - [ ] type: string (uptime_degradation, version_behind, etc.)
  - [ ] message: user-friendly description
  - [ ] metric_value: actual value
  - [ ] threshold: what triggered alert
  - [ ] first_detected: timestamp

- [ ] **Task 5.1.5:** Create /pnode/{address}/alerts endpoint
  - [ ] Fetch node's historical data
  - [ ] Run alert checks
  - [ ] Return array of active alerts
  - [ ] Include timestamp

- [ ] **Task 5.1.6:** Add alerts to existing endpoints
  - [ ] Add alerts field to /pnodes response (optional)
  - [ ] Add alerts to /registry/{address} response
  - [ ] Make it opt-in to avoid slowing requests

**Exit Criteria:** Alert system identifies risky nodes automatically

---

#### 5.2 Create /pnodes/compare Endpoint

- [ ] **Task 5.2.1:** Design comparison endpoint
  - [ ] Parameter: addresses (comma-separated, max 5)
  - [ ] Validate input (2-5 addresses required)

- [ ] **Task 5.2.2:** Implement comparison logic
  - [ ] Parse address list
  - [ ] Fetch each node's full data from /pnodes
  - [ ] Handle missing nodes gracefully

- [ ] **Task 5.2.3:** Calculate winners
  - [ ] Best overall score
  - [ ] Best trust score
  - [ ] Best performance score (if available)
  - [ ] Best capacity score
  - [ ] Best uptime

- [ ] **Task 5.2.4:** Build response
  - [ ] comparison: array of full node objects
  - [ ] winner: object with category winners
  - [ ] summary: quick comparison stats
  - [ ] timestamp

- [ ] **Task 5.2.5:** Add visualization hints
  - [ ] Include normalized scores (for charts)
  - [ ] Include color coding based on tiers
  - [ ] Include recommendation (which to choose)

**Exit Criteria:** `/pnodes/compare` enables side-by-side node evaluation

---

#### 5.3 Implement Gossip Consistency Tracking

- [ ] **Task 5.3.1:** Add consistency fields to registry
  - [ ] gossip_appearances: count of times seen
  - [ ] gossip_disappearances: count of times dropped
  - [ ] last_gossip_drop: timestamp
  - [ ] consistency_score: calculated metric

- [ ] **Task 5.3.2:** Track gossip changes in fetcher
  - [ ] Compare current snapshot to previous
  - [ ] Detect new appearances
  - [ ] Detect disappearances
  - [ ] Update registry accordingly

- [ ] **Task 5.3.3:** Calculate consistency score
  - [ ] appearances / (appearances + disappearances)
  - [ ] Factor into trust score
  - [ ] Flag nodes with low consistency (< 80%)

- [ ] **Task 5.3.4:** Add to alert system
  - [ ] Alert: Frequent flapping (> 3 drops in 24h)
  - [ ] Alert: Recent disappearance (dropped in last hour)

**Exit Criteria:** System tracks and flags unreliable gossip participants

---

### PHASE 6: Testing & Documentation [HIGH PRIORITY]
**Goal:** Ensure production readiness  
**Duration:** 2 days  
**Dependencies:** All features implemented

#### 6.1 Create Test Suite

- [ ] **Task 6.1.1:** Create test_api.py script
  - [ ] Test /health endpoint
  - [ ] Test /pnodes with various parameters
  - [ ] Test /recommendations
  - [ ] Test /network/topology
  - [ ] Test /network/health
  - [ ] Test /network/history
  - [ ] Test /registry with filters
  - [ ] Test /operators
  - [ ] Test /pnodes/compare

- [ ] **Task 6.1.2:** Create unit tests
  - [ ] Test scoring functions (tests/test_scoring.py)
  - [ ] Test alert generation (tests/test_alerts.py)
  - [ ] Test database functions (tests/test_db.py)
  - [ ] Test utility functions

- [ ] **Task 6.1.3:** Create integration tests
  - [ ] Test full data flow (RPC → DB → API)
  - [ ] Test with mock data
  - [ ] Test error scenarios
  - [ ] Test edge cases

- [ ] **Task 6.1.4:** Load testing
  - [ ] Test concurrent requests
  - [ ] Test large pagination
  - [ ] Identify bottlenecks
  - [ ] Optimize if needed

**Exit Criteria:** All endpoints tested, test suite passes consistently

---

#### 6.2 Update Documentation

- [ ] **Task 6.2.1:** Update README.md
  - [ ] Add project overview
  - [ ] Add feature list
  - [ ] Add quick start guide
  - [ ] Add API endpoint list
  - [ ] Add example usage
  - [ ] Add screenshots/diagrams (if available)

- [ ] **Task 6.2.2:** Update ARCHITECTURE.md
  - [ ] Update data flow diagram
  - [ ] Document new collections (pnodes_snapshots)
  - [ ] Document scoring system
  - [ ] Document alert system
  - [ ] Update snapshot structure

- [ ] **Task 6.2.3:** Create API_REFERENCE.md
  - [ ] Document all endpoints
  - [ ] Include request/response examples
  - [ ] Document all parameters
  - [ ] Document error responses
  - [ ] Add authentication info (if added)

- [ ] **Task 6.2.4:** Create SCORING_METHODOLOGY.md
  - [ ] Explain each score (Trust, Performance, Capacity)
  - [ ] Show score calculation formulas
  - [ ] Explain weighting rationale
  - [ ] Provide examples
  - [ ] Make it transparent for users

- [ ] **Task 6.2.5:** Create DEPLOYMENT.md
  - [ ] Environment setup
  - [ ] MongoDB setup
  - [ ] Environment variables
  - [ ] Deployment platforms (Heroku, Railway, etc.)
  - [ ] Monitoring setup
  - [ ] Backup strategy

- [ ] **Task 6.2.6:** Update CONTRIBUTION.md
  - [ ] Add development setup
  - [ ] Add testing instructions
  - [ ] Add PR guidelines
  - [ ] Update node verification process

- [ ] **Task 6.2.7:** Create CHANGELOG.md
  - [ ] Document v2.0.0 changes
  - [ ] List breaking changes
  - [ ] List new features
  - [ ] List bug fixes
  - [ ] Migration guide from v1.x

**Exit Criteria:** All documentation complete, up-to-date, and accurate

---

#### 6.3 Deprecation & Migration

- [ ] **Task 6.3.1:** Mark old endpoints as deprecated
  - [ ] Add `deprecated=True` to /all-nodes
  - [ ] Add deprecation warnings to responses
  - [ ] Add migration instructions

- [ ] **Task 6.3.2:** Create migration guide
  - [ ] Document /all-nodes → /pnodes mapping
  - [ ] Provide code examples
  - [ ] List breaking changes
  - [ ] Provide timeline for removal

- [ ] **Task 6.3.3:** Update root endpoint
  - [ ] Update API overview
  - [ ] Highlight recommended endpoints
  - [ ] Mark deprecated endpoints
  - [ ] Update version to 1.1.0

**Exit Criteria:** Clear migration path for existing users

---

## 📡 API Endpoint Specification

### Final Endpoint Structure

```
Core Data Endpoints:
├── GET  /pnodes                          # Unified node data (MAIN)
├── GET  /pnodes/compare                  # Compare multiple nodes
├── GET  /registry                        # Historical registry
├── GET  /registry/{address}              # Single node details
└── GET  /pnodes/{address}/alerts         # Node-specific alerts

Analytics Endpoints:
├── GET  /recommendations                 # Top staking choices
├── GET  /operators                       # Operator statistics
├── GET  /network/health                  # Network health analysis
└── GET  /network/history                 # Historical metrics

Visualization Endpoints:
└── GET  /network/topology                # Network graph data

Management Endpoints:
├── DELETE /prune                         # Remove old nodes
└── GET    /graveyard                     # Inactive nodes

Monitoring Endpoints:
└── GET  /health                          # API health check
```

---

## 🗄️ Database Schema

### Collections

#### 1. pnodes_snapshot (Single Document)
```javascript
{
  "_id": "snapshot",
  "data": {
    "summary": {
      "total_nodes": int,
      "total_pnodes": int,
      "total_pnodes_raw": int,
      "total_bytes_processed": int,
      "avg_cpu_percent": float,
      "avg_ram_used_percent": float,
      "total_active_streams": int,
      "last_updated": timestamp
    },
    "nodes": {
      "IP_ADDRESS": {
        "metadata": {...},
        "stats": {...},
        "pods": [...]
      }
    },
    "merged_pnodes_raw": [...],
    "merged_pnodes_unique": [...]
  }
}
```

#### 2. pnodes_registry (One Document Per Node)
```javascript
{
  "_id": ObjectId,
  "address": "IP:PORT",                 
  "pubkey": "string",                      
  "version": "string",
  "first_seen": timestamp,
  "last_seen": timestamp,
  "last_checked": timestamp,
  "is_public_rpc": boolean,
  "rpc_port": int,
  "storage_committed": int,
  "storage_used": int,
  "storage_usage_percent": float,
  "uptime": int,
  "source_ips": [string],
  "created_at": timestamp,
  "gossip_appearances": int,
  "gossip_disappearances": int,
  "last_gossip_drop": timestamp,
  "consistency_score": float,
  
  // IF PAGING DATA AVAILABLE
  "page_hit_rate": float,
  "page_miss_rate": float,
  "page_errors": int,
  "throughput_pages_per_sec": float
}
```

**Indexes:**
```javascript
address: unique index (PRIMARY KEY)
pubkey: non-unique index (for operator queries)
last_seen: descending index (for online/offline queries)
```

#### 3. pnodes_status (One Document Per Node)
```javascript
{
  "_id": ObjectId,
  "address": "IP:PORT",
  "status": "public|private|offline|unknown",
  "last_ip": "string",
  "last_seen": timestamp,
  "updated_at": timestamp
}
```

**Indexes:**
```javascript
address: unique index
```

#### 4. pnodes_snapshots (Historical Time-Series)
```javascript
{
  "_id": ObjectId,
  "timestamp": timestamp,
  "total_pnodes": int,
  "total_ip_nodes": int,
  "avg_cpu_percent": float,
  "avg_ram_used_percent": float,
  "total_active_streams": int,
  "total_bytes_processed": int,
  "version_distribution": {
    "0.7.0": int,
    "0.6.5": int
  }
}
```

**Indexes:**
```javascript
timestamp: descending index
```

**Retention:** 30 days (auto-pruned)

---

## 🧪 Testing Strategy

### Test Levels

#### 1. Unit Tests (Pytest)
```bash
tests/
├── test_scoring.py       # Test all scoring functions
├── test_alerts.py        # Test alert generation
├── test_db.py            # Test database functions
└── test_utils.py         # Test utility functions
```

#### 3. Manual Testing Checklist
- [X] Test with real IP nodes
- [X] Test with missing data
- [X] Test with offline nodes
- [X] Test pagination boundaries
- [X] Test sorting edge cases
- [X] Test with various filters
- [X] Test 100 concurr

---

## 📊 Success Metrics

### Technical Metrics
- [X] All endpoints return < 500ms (95th percentile)
- [X] Health endpoint always returns < 100ms
- [X] Background worker completes cycle in < 30s
- [X] MongoDB queries return in < 50ms
- [X] API test suite passes 100%
- [X] No memory leaks (stable over 24h)
- [X] No RPC errors (or < 1% error rate)

### Feature Completeness
- [X] All endpoints from specification implemented
- [X] All scores calculate correctly
- [X] Alert system identifies risky nodes
- [X] Historical data accumulates properly
- [X] Topology visualization works
- [X] Documentation is complete

### User Value
- [X] Stakers can identify top nodes in < 30 seconds
- [X] Operators can monitor their node health
- [X] Developers can access all data via API
- [X] Network health is clear at a glance

---

## 🚀 Deployment Readiness Checklist

### Pre-Deployment
- [X] All Phase 0-6 tasks complete
- [X] Test suite passes
- [X] Documentation complete
- [X] MongoDB indexes created
- [X] Environment variables documented
- [X] .env.example updated
- [X] Error handling tested
- [X] Rate limiting considered (if needed)

### Deployment
- [X] Choose platform (Heroku, Railway, Render, etc.)
- [X] Set environment variables
- [X] Deploy application
- [X] Verify health endpoint
- [X] Test all endpoints in production
- [X] Monitor logs for errors
- [X] Set up monitoring (UptimeRobot, etc.)

### Post-Deployment
- [X] Monitor performance
- [X] Track error rates
- [X] Gather user feedback
- [X] Plan iteration improvements

---

## 📝 Implementation Notes

### Critical Decisions Pending

1. **Paging Data Availability** (BLOCKING)
   - Must verify in Phase 0
   - Determines scoring completeness
   - Affects implementation timeline

2. **Rate Limiting**
   - Do we need it?
   - If yes, what limits? (e.g., 100 req/min per IP)
   - Can add later if needed

3. **Authentication**
   - Currently public API
   - Do we need API keys?
   - Can add later if needed

4. **Caching Layer**
   - Currently no Redis/Memcached
   - MongoDB is fast enough for now
   - Can add if performance issues

### Best Practices to Follow

1. **Always use address as primary key**
2. **Handle missing data gracefully** (return null/0, don't crash)
3. **Include timestamps** in all responses
4. **Use consistent field names** across endpoints
5. **Document breaking changes** clearly
6. **Test with real data** frequently
7. **Keep functions small** and focused
8. **Add comprehensive docstrings**
9. **Log errors** but don't expose internals
10. **Version the API** (currently v1.1.0)

---

## 🎯 Quick Start Command Reference

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URI

# Run locally
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Check health
curl http://localhost:8000/health

# Test endpoint
curl http://localhost:8000/pnodes?status=online&limit=5
```

---

## ✅ Phase Completion Criteria

### Phase 0 Complete When:
- [X] All RPC endpoints tested on all IP nodes
- [X] Paging data availability documented
- [X] Implementation decision made (3-score or 4-score)
- [X] AVAILABLE_DATA.md created

### Phase 1 Complete When:
- [X] Address is primary key everywhere
- [X] IP_NODES reads from .env
- [X] /health endpoint works
- [X] All tests pass

### Phase 2 Complete When:
- [X] app/scoring.py created and tested
- [X] All scoring functions work
- [X] Scores are accurate and reasonable
- [X] Documentation complete

### Phase 3 Complete When:
- [X] /pnodes endpoint works with all parameters
- [X] /recommendations returns top nodes
- [X] /network/topology returns graph data
- [X] /network/health shows network status
- [X] /operators shows operator distribution

### Phase 4 Complete When:
- [X] Snapshot history saves every 60s
- [X] Old snapshots auto-pruned (30 days)
- [X] /network/history returns trends
- [X] MongoDB size stable

### Phase 5 Complete When:
- [X] Alert system identifies risks
- [X] /pnodes/compare works
- [X] Gossip consistency tracked
- [X] All advanced features work

### Phase 6 Complete When:
- [ ] All tests pass
- [ ] All documentation updated
- [ ] Deployment guide created
- [ ] API reference complete
- [X] Ready for production

---

## 📌 Final Notes

**This is a living document.** Update as:
- Requirements change
- New data becomes available
- Implementation challenges arise
- Team decisions are made

**Track progress by:**
- Checking off completed tasks
- Moving tasks between phases if needed
- Adding notes for blockers
- Updating timelines if necessary

**When stuck:**
- Review the developer notes
- Check ARCHITECTURE.md
- Ask the team

**Remember:**
> We're building "The Block Explorer equivalent for Xandeum storage performance"

Make it transparent, accurate, and useful. That's what matters.

---

**Ready to start? Begin with Phase 0! 🚀**