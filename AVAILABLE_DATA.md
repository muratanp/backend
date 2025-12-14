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