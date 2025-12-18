# Xandeum PNode Aggregation API – System Architecture

This document gives developers a full understanding of how the backend works: the data flow, components, background processes, snapshot logic, and RPC aggregation system.

---

# 1. High-Level Architecture (Simple & Visual)

                 ┌────────────────────────────┐
                 │    Frontend Dashboard      │
                 │  (Next.js / React / Vite)  │
                 └───────────────┬────────────┘
                                 │  HTTP (GET)
                                 ▼
                     ┌─────────────────────┐
                     │       FastAPI       │
                     │     `/pndes`        │
                     └────────────┬────────┘
                                  │ Reads snapshot
                                  ▼
                      ┌──────────────────────────┐
                      │      MongoDB Atlas       │
                      │  nodes_current(snapshot) │
                      └─────────────┬────────────┘
                                    │ Writes snapshot
                                    ▼
           ┌────────────────────────────────────────────────┐
           │     Background Worker (fetcher.py)              │
           │────────────────────────────────────────────────│
           │ • Runs every CACHE_TTL seconds                 │
           │ • Makes RPC requests to all configured IPs     │
           │ • Uses Joblib caching per RPC method           │
           │ • Merges & deduplicates pNodes                 │
           │ • Builds snapshot (summary + nodes + pnodes)  │
           │ • Saves it to MongoDB                          │
           └──────────────────────────┬─────────────────────┘
                                       │ Concurrent RPC calls
                                       ▼
                 ┌─────────────────────────────────────────────┐
                 │             Xandeum IP Nodes                │
                 │ get-version / get-stats / get-pods /        │
                 │ (Multiple distributed node IPs)             │
                 └─────────────────────────────────────────────┘


---

# 2. Architecture Explanation

### Why this design?
- The frontend never talks directly to IP nodes  
- FastAPI never makes RPC calls during user requests  
- MongoDB always stores the latest known valid snapshot  
- A background worker does all heavy lifting away from API routes  
- Joblib ensures we don’t spam nodes with duplicate RPC calls  

---

# 3. Data Flow (Step-by-Step)

### Startup
- FastAPI starts
- MongoDB client connects
- Background worker begins recurring loop

### Background Worker Loop
Runs every `CACHE_TTL` seconds:

1. For each node IP:
   - Fetches `get-version`
   - Fetches `get-stats`
   - Fetches `get-pods`
   - Fetches `get-pods-with-stats`
   - All via cached RPC calls
2. Merges all pod lists
3. Deduplicates pNodes by `address`
4. Computes summary metrics
5. Creates final snapshot object
6. Saves snapshot into MongoDB under `nodes_current._id = "snapshot"`

### API Request
Frontend calls:

GET /pnodes


FastAPI:
- Reads from `nodes_current`
- Returns the latest snapshot
- Responds in milliseconds

---

# 4. Folder Structure

### What each file does

**config.py**
- Loads environment variables: `MONGO_URI`, `MONGO_DB`, `CACHE_TTL`
- Exposes configuration used throughout the app

**db.py**
- Initializes MongoDB client and collection
- Exposes `nodes_current` (snapshot storage)

**fetcher.py**
- RPC calling (`get-version`, `get-stats`, `get-pods`, `get-pods-with-stats`)
- Joblib caching
- Concurrent node polling
- Pod merging & deduplication
- Summary calculation
- Snapshot saving

**main.py**
- FastAPI app creation
- CORS configuration
- `/pnodes` endpoint
- Startup event that initializes background worker

**utils/jsonrpc.py**
- Creates JSON-RPC success/error dictionaries
- Ensures consistent response formatting

---

# 5. Snapshot Structure

Every snapshot has:

```json
{
  "summary": {
    "total_nodes": 9,
    "total_pnodes": 117,
    "avg_cpu_percent": 2.12,
    "avg_ram_used_percent": 16.77,
    "total_active_streams": 16,
    "last_updated": 1765052199
  },
  "nodes": {
    "173.212.203.145": {
      "metadata": {...},
      "stats": {...},
      "pods": [...]
    }
  },
  "merged_pnodes": [
    {
      "address": "0xABC...",
      "version": "0.6.0",
      "last_seen_timestamp": 1765052040
    }
  ]
}
```

---

# 6. Why This Architecture Works
Ultra-fast: MongoDB → FastAPI → Frontend, no RPC bottlenecks

Safe & Resilient: Temporary node failures won’t break frontend responses

Easy to Deploy: Single process, no message queues needed

Scalable: Adding more node IPs is automatic