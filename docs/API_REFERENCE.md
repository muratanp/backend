# Xandeum pNode Analytics API - Complete Reference

**Version:** 1.1.0  
**Base URL:** `https://web-production-b4440.up.railway.app` in prod or `http://localhost:8000` for dev.
**Protocol:** REST API with JSON responses

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Endpoints](#core-endpoints)
3. [Analytics Endpoints](#analytics-endpoints)
4. [Historical Endpoints](#historical-endpoints)
5. [Alert Endpoints](#alert-endpoints)
6. [Advanced Endpoints](#advanced-endpoints)
7. [Error Handling](#error-handling)
8. [Rate Limits](#rate-limits)
9. [Examples](#examples)

---

## Getting Started

### Authentication

Currently **no authentication required**. All endpoints are publicly accessible.

### Base Response Format

All endpoints return JSON with this structure:

```json
{
  "data": {...},
  "timestamp": 1735920000
}
```

### Common Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Max results to return | 100 |
| `skip` | integer | Pagination offset | 0 |
| `status` | string | Filter by status (online/offline/all) | online |
| `sort_by` | string | Field to sort by | last_seen |
| `sort_order` | string | Sort direction (asc/desc) | desc |

---

## Core Endpoints

### GET `/health`

Check API health and data freshness.

**Response:**
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "snapshot_age_seconds": 45,
  "last_updated": 1735920000,
  "cache_ttl": 60,
  "total_pnodes": 117,
  "total_ip_nodes": 9,
  "timestamp": 1735920045
}
```

**Status Values:**
- `healthy` - System operating normally (snapshot < 2x cache_ttl)
- `degraded` - System functional but snapshot stale
- `unhealthy` - Snapshot missing or very old

---

### GET `/pnodes`

**Main endpoint** - Get unified pNode data with scoring and filters.

**Parameters:**
- `status` - Filter by status (online/offline/all) [default: online]
- `limit` - Results per page (1-1000) [default: 100]
- `skip` - Pagination offset [default: 0]
- `sort_by` - Sort field (last_seen, uptime, score, storage_used, etc.)
- `sort_order` - Sort direction (asc/desc) [default: desc]

**Example Request:**
```bash
GET /pnodes?status=online&limit=10&sort_by=score&sort_order=desc
```

**Response:**
```json
{
  "summary": {
    "total_pnodes": 117,
    "online_pnodes": 98,
    "offline_pnodes": 19,
    "snapshot_age_seconds": 45,
    "last_updated": 1735920000
  },
  "network_stats": {
    "total_storage_committed": 12247563264,
    "total_storage_used": 3042394,
    "avg_uptime_hours": 720.5,
    "version_distribution": {
      "0.7.0": 98,
      "0.6.5": 19
    }
  },
  "pagination": {
    "total": 98,
    "limit": 10,
    "skip": 0,
    "returned": 10
  },
  "filters": {
    "status": "online",
    "sort_by": "score",
    "sort_order": "desc"
  },
  "pnodes": [
    {
      "address": "109.199.96.218:9001",
      "pubkey": "0x1234...abcd",
      "is_online": true,
      "last_seen": 1735920000,
      "version": "0.7.0",
      "uptime": 2592000,
      "is_public": false,
      "storage_committed": 107374182400,
      "storage_used": 26041344,
      "storage_usage_percent": 24.25,
      "peer_sources": ["192.168.1.1", "10.0.0.5"],
      "peer_count": 2,
      "scores": {
        "trust": {
          "score": 85.5,
          "breakdown": {
            "uptime": 40,
            "gossip_presence": 20,
            "version_compliance": 20,
            "gossip_consistency": 5.5
          }
        },
        "capacity": {
          "score": 75.0,
          "breakdown": {
            "storage_committed": 25,
            "usage_balance": 35,
            "growth_trend": 15
          }
        },
        "stake_confidence": {
          "composite_score": 81.3,
          "rating": "low_risk",
          "color": "#10b981"
        }
      },
      "score": 81.3,
      "tier": "low_risk"
    }
  ],
  "timestamp": 1735920000
}
```

**Node Object Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | IP:port identifier |
| `pubkey` | string | Operator's public key |
| `is_online` | boolean | Current online status |
| `last_seen` | integer | Unix timestamp of last gossip appearance |
| `version` | string | pNode software version |
| `uptime` | integer | Uptime in seconds |
| `is_public` | boolean | Whether RPC is public |
| `storage_committed` | integer | Committed storage in bytes |
| `storage_used` | integer | Used storage in bytes |
| `storage_usage_percent` | float | Usage percentage |
| `peer_sources` | array | IPs that reported this node |
| `peer_count` | integer | Number of gossip peers |
| `scores` | object | Performance scores |
| `score` | float | Composite score (0-100) |
| `tier` | string | Risk tier (low_risk, medium_risk, high_risk) |

---

### GET `/recommendations`

Get top nodes for staking.

**Parameters:**
- `limit` - Max recommendations (1-50) [default: 10]
- `min_uptime_days` - Minimum uptime in days [default: 7]
- `require_public` - Only public RPC nodes [default: false]

**Example Request:**
```bash
GET /recommendations?limit=5&min_uptime_days=30
```

**Response:**
```json
{
  "recommendations": [
    {
      "address": "109.199.96.218:9001",
      "pubkey": "0x1234...abcd",
      "score": 85.6,
      "tier": "low_risk",
      "scores": {
        "trust": 88.0,
        "capacity": 82.0,
        "breakdown": {...}
      },
      "uptime_days": 45.2,
      "version": "0.7.0",
      "storage_usage_percent": 35.5,
      "is_public": false,
      "peer_count": 4
    }
  ],
  "total_evaluated": 98,
  "filters": {
    "min_uptime_days": 30,
    "require_public": false
  },
  "timestamp": 1735920000
}
```

---

### GET `/network/topology`

Get network graph data for visualization.

**Response:**
```json
{
  "nodes": [
    {
      "id": "192.168.1.1",
      "type": "ip_node",
      "label": "192.168.1.1",
      "group": "ip",
      "properties": {
        "active_streams": 5,
        "uptime": 86400,
        "cpu_percent": 2.5
      }
    },
    {
      "id": "109.199.96.218:9001",
      "type": "pnode",
      "label": "109.199.96.218",
      "group": "public",
      "properties": {
        "version": "0.7.0",
        "uptime": 2592000,
        "storage_committed": 107374182400
      }
    }
  ],
  "edges": [
    {
      "source": "192.168.1.1",
      "target": "109.199.96.218:9001",
      "type": "gossip_connection"
    }
  ],
  "stats": {
    "total_nodes": 107,
    "ip_nodes": 9,
    "pnodes": 98,
    "total_connections": 294,
    "avg_connections_per_pnode": 3.0
  }
}
```

---

### GET `/network/health`

Get overall network health metrics.

**Response:**
```json
{
  "health": {
    "health_score": 85.5,
    "status": "healthy",
    "factors": {
      "availability": 29.0,
      "version_consistency": 22.5,
      "node_quality": 20.8,
      "connectivity": 18.0
    }
  },
  "network_stats": {...},
  "summary": {...},
  "alerts": [
    {
      "severity": "medium",
      "type": "version_fragmentation",
      "message": "Network running 2 different versions",
      "recommendation": "Consider coordinating version upgrades"
    }
  ],
  "timestamp": 1735920000
}
```

---

### GET `/operators`

Group nodes by operator (pubkey).

**Parameters:**
- `limit` - Max operators to return (1-500) [default: 100]
- `min_nodes` - Only operators with N+ nodes [default: 1]

**Response:**
```json
{
  "summary": {
    "total_operators": 45,
    "total_nodes": 98,
    "avg_nodes_per_operator": 2.18,
    "largest_operator_share_percent": 8.16,
    "decentralization_score": 91.84
  },
  "operators": [
    {
      "pubkey": "0x1234...abcd",
      "node_count": 8,
      "online_nodes": 7,
      "total_storage_committed": 858993459200,
      "total_storage_used": 208330752,
      "addresses": ["109.199.96.218:9001", ...],
      "versions": ["0.7.0"],
      "first_seen": 1730000000
    }
  ],
  "timestamp": 1735920000
}
```

---

## Historical Endpoints

### GET `/network/history`

Get network metrics over time.

**Parameters:**
- `hours` - How many hours of history (1-720 = 30 days) [default: 24]

**Response:**
```json
{
  "history": [
    {
      "timestamp": 1735833600,
      "timestamp_readable": "2025-01-02 12:00:00",
      "total_pnodes": 95,
      "total_ip_nodes": 9,
      "public_pnodes": 68,
      "private_pnodes": 27,
      "avg_cpu_percent": 2.3,
      "avg_ram_used_percent": 16.2,
      "total_storage_committed": 11744051200,
      "avg_peer_count": 3.0,
      "version_distribution": {"0.7.0": 90, "0.6.5": 5}
    }
  ],
  "summary": {
    "data_points": 24,
    "time_range_hours": 24,
    "node_growth": {
      "start_count": 95,
      "end_count": 98,
      "growth": 3,
      "growth_percent": 3.16,
      "trend": "growing"
    },
    "storage_growth": {
      "start_committed": 11744051200,
      "end_committed": 12247563264,
      "growth": 503512064,
      "growth_percent": 4.29,
      "trend": "growing"
    }
  },
  "timestamp": 1735920000
}
```

---

### GET `/network/growth`

Quick growth snapshot.

**Parameters:**
- `hours` - Compare to N hours ago (1-720) [default: 24]

**Response:**
```json
{
  "growth_metrics": {
    "available": true,
    "period_hours": 24,
    "comparison": {
      "start_time": 1735833600,
      "end_time": 1735920000
    },
    "nodes": {
      "start_count": 95,
      "end_count": 98,
      "growth": 3,
      "growth_percent": 3.16
    },
    "storage": {
      "start_committed": 11744051200,
      "end_committed": 12247563264,
      "growth": 503512064,
      "growth_percent": 4.29
    },
    "network_health": {
      "start_peer_count": 3.0,
      "end_peer_count": 3.2,
      "peer_count_change": 0.2
    }
  },
  "timestamp": 1735920000
}
```

---

### GET `/network/analytics`

Comprehensive analytics dashboard.

**Response:**
```json
{
  "current_state": {
    "total_pnodes": 98,
    "public_nodes": 68,
    "private_nodes": 30,
    "public_ratio_percent": 69.39
  },
  "growth": {
    "24_hours": {...},
    "7_days": {...}
  },
  "version_analysis": {
    "distribution": {"0.7.0": 93, "0.6.5": 5},
    "latest_version": "0.7.0",
    "compliance_percent": 94.90,
    "fragmentation_index": 2,
    "health": "good"
  },
  "storage_analysis": {
    "distribution": {
      "empty": 5,
      "low": 20,
      "optimal": 60,
      "high": 10,
      "critical": 3
    },
    "optimal_percent": 61.22,
    "health": "good"
  },
  "connectivity_analysis": {
    "distribution": {
      "isolated": 2,
      "weak": 10,
      "good": 70,
      "excellent": 16
    },
    "well_connected_percent": 87.76,
    "health": "good"
  },
  "recommendations": [...]
}
```

---

## Alert Endpoints

### GET `/pnodes/{address}/alerts`

Get alerts for specific node.

**Parameters:**
- `severity` - Filter by severity (critical, warning, info)

**Response:**
```json
{
  "address": "109.199.96.218:9001",
  "alerts": [
    {
      "severity": "warning",
      "type": "version_behind",
      "message": "Running old version: 0.6.5 (latest: 0.7.0)",
      "metric": "version",
      "value": "0.6.5",
      "threshold": "0.7.0",
      "recommendation": "Upgrade to latest version soon"
    }
  ],
  "summary": {
    "total": 1,
    "critical": 0,
    "warning": 1,
    "info": 0,
    "by_type": {
      "version_behind": 1
    }
  },
  "node_info": {
    "is_online": true,
    "uptime": 2592000,
    "version": "0.6.5"
  },
  "timestamp": 1735920000
}
```

**Alert Types:**

| Type | Severity | Description |
|------|----------|-------------|
| `offline` | critical/warning | Node offline for extended period |
| `low_uptime` | critical/warning | Low uptime (< 1 day) |
| `storage_critical` | critical | Storage > 95% full |
| `storage_warning` | warning | Storage > 85% full |
| `version_outdated` | critical | 2+ versions behind |
| `version_behind` | warning | 1 version behind |
| `isolated` | critical | ≤ 1 peer |
| `weak_connectivity` | warning | 2 peers |
| `underutilized` | info | Storage < 5% used |
| `gossip_flapping` | warning | Frequently appearing/disappearing |

---

### GET `/alerts`

Get network-wide alerts.

**Parameters:**
- `severity` - Filter by severity
- `alert_type` - Filter by alert type
- `limit` - Max nodes to check (1-500) [default: 100]

**Response:**
```json
{
  "summary": {
    "total": 25,
    "critical": 3,
    "warning": 18,
    "info": 4,
    "by_type": {
      "version_behind": 15,
      "storage_warning": 8,
      "weak_connectivity": 2
    }
  },
  "critical_nodes": [
    {
      "address": "10.0.0.5:9001",
      "alert_count": 2,
      "critical_alerts": [...]
    }
  ],
  "nodes_checked": 98,
  "nodes_with_alerts": 25,
  "timestamp": 1735920000
}
```

---

### GET `/alerts/critical`

Quick endpoint for monitoring critical issues only.

---

## Advanced Endpoints

### GET `/pnodes/compare`

Compare 2-5 nodes side-by-side.

**Parameters:**
- `addresses` - Comma-separated addresses (required)

**Example:**
```bash
GET /pnodes/compare?addresses=109.199.96.218:9001,10.0.0.5:9001
```

**Response:**
```json
{
  "comparison": [...],
  "winners": {
    "overall_score": {
      "address": "109.199.96.218:9001",
      "score": 85.6,
      "category": "Best overall performance"
    },
    "trust_score": {...},
    "capacity_score": {...},
    "best_uptime": {...},
    "most_storage": {...},
    "best_connectivity": {...}
  },
  "recommendation": {
    "recommended_node": "109.199.96.218:9001",
    "reason": "Highest overall score (85.6/100)",
    "considerations": [...]
  },
  "summary": {
    "nodes_compared": 2,
    "all_online": true,
    "avg_score": 82.5
  }
}
```

---

### GET `/network/consistency`

Gossip consistency metrics.

**Parameters:**
- `min_consistency` - Only nodes with score >= this (0.0-1.0)
- `sort_by` - Sort field [default: consistency_score]
- `limit` - Max results [default: 100]

**Response:**
```json
{
  "nodes": [
    {
      "address": "109.199.96.218:9001",
      "consistency_score": 0.98,
      "gossip_appearances": 100,
      "gossip_disappearances": 2,
      "last_drop": 1735800000,
      "time_since_last_drop": 120000,
      "status": "stable",
      "is_online": true
    }
  ],
  "summary": {
    "total_nodes": 98,
    "flapping_nodes": 3,
    "stable_nodes": 95,
    "avg_consistency_score": 0.94,
    "network_health": "good"
  },
  "flapping_nodes": [...]
}
```

---

### GET `/node/{address}/consistency`

Detailed consistency for specific node.

### GET `/registry`

Historical registry (use `/pnodes` instead).

### GET `/registry/{address}`

Single node from registry.

### GET `/pnodes`

All pnode in the network

---

## Error Handling

### Standard Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Error description"
  },
  "id": 1
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (node/resource doesn't exist) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (snapshot not ready) |

---

## Rate Limits

Currently **no rate limits** enforced. Please be considerate:
- Avoid excessive polling (< 1 request/second)
- Use webhooks/subscriptions for real-time updates (coming soon)
- Cache responses when appropriate

---

## Examples

### Python

```python
import requests

# Get top nodes for staking
response = requests.get("http://localhost:8000/recommendations?limit=5")
nodes = response.json()["recommendations"]

for node in nodes:
    print(f"{node['address']}: Score {node['score']}")
```

### JavaScript

```javascript
// Get network health
const response = await fetch('http://localhost:8000/network/health');
const health = await response.json();

console.log(`Network health: ${health.health.status}`);
console.log(`Score: ${health.health.health_score}`);
```

### cURL

```bash
# Compare two nodes
curl "http://localhost:8000/pnodes/compare?addresses=addr1:9001,addr2:9001" | jq '.winners'

# Get critical alerts
curl "http://localhost:8000/alerts/critical" | jq '.critical_nodes'
```

---

## Support

- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Discord:** [Community Server](https://discord.gg/uqRSmmM5m)

---

**API Version:** 1.1.0  
**Last Updated:** December 2025 
**License:** MIT