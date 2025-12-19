# Xandeum PNode Analytics API - Complete Reference

**Version:** 2.0.0  
**Base URL:** `https://web-production-b4440.up.railway.app`  
**Protocol:** REST API with JSON responses  
**Authentication:** None required (public API)

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Response Format](#response-format)
3. [Core Data Endpoints](#core-data-endpoints)
4. [Network Analytics](#network-analytics)
5. [Historical Data](#historical-data)
6. [Alert System](#alert-system)
7. [Operator Intelligence](#operator-intelligence)
8. [Advanced Features](#advanced-features)
9. [System Health](#system-health)
10. [Error Handling](#error-handling)
11. [Rate Limits](#rate-limits)
12. [Code Examples](#code-examples)

---

## 🚀 Getting Started

### Base URL

```
Production:  https://web-production-b4440.up.railway.app
Development: http://localhost:8000
```

### Quick Test

```bash
# Test API health
curl https://web-production-b4440.up.railway.app/health

# Get top 3 nodes
curl "https://web-production-b4440.up.railway.app/recommendations?limit=3"
```

### Interactive Documentation

Visit the **auto-generated Swagger UI**:
- Production: https://web-production-b4440.up.railway.app/docs
- Includes: Try-it-out functionality, request/response examples

---

## 📦 Response Format

### Standard Success Response

All successful responses follow this structure:

```json
{
  "data": { /* endpoint-specific data */ },
  "summary": { /* optional summary metadata */ },
  "pagination": { /* if paginated */ },
  "timestamp": 1703001234
}
```

### Common Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | integer | Unix timestamp of response generation |
| `summary` | object | Aggregate counts and metadata |
| `pagination` | object | Page info (total, limit, skip, returned) |

---

## 🎯 Core Data Endpoints

### GET `/pnodes`

**The primary endpoint** - Get unified node data with performance scoring.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | `online` | Filter: `online`, `offline`, `all` |
| `limit` | integer | `100` | Results per page (1-1000) |
| `skip` | integer | `0` | Pagination offset |
| `sort_by` | string | `last_seen` | Sort field: `last_seen`, `uptime`, `score`, `storage_used` |
| `sort_order` | string | `desc` | Sort direction: `asc`, `desc` |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/pnodes?status=online&limit=5&sort_by=score&sort_order=desc"
```

#### Response Structure

```json
{
  "summary": {
    "total_pnodes": 120,
    "online_pnodes": 98,
    "offline_pnodes": 22,
    "snapshot_age_seconds": 45,
    "last_updated": 1703001234
  },
  "network_stats": {
    "total_storage_committed": 12247563264,
    "total_storage_used": 3042394,
    "avg_uptime_hours": 720.5,
    "version_distribution": {
      "0.8.0": 98,
      "0.7.0": 22
    }
  },
  "pagination": {
    "total": 98,
    "limit": 5,
    "skip": 0,
    "returned": 5
  },
  "pnodes": [
    {
      "address": "109.199.96.218:9001",
      "pubkey": "0x1234...abcd",
      "is_online": true,
      "last_seen": 1703001234,
      "version": "0.8.0",
      "uptime": 2592000,
      "uptime_days": 30.0,
      
      "storage_committed": 107374182400,
      "storage_used": 26041344,
      "storage_usage_percent": 24.25,
      
      "peer_sources": ["192.168.1.1", "10.0.0.5"],
      "peer_count": 2,
      
      "scores": {
        "trust": {
          "score": 85.5,
          "breakdown": {
            "uptime": 40.0,
            "gossip_presence": 20.0,
            "version_compliance": 20.0,
            "gossip_consistency": 5.5
          }
        },
        "capacity": {
          "score": 75.0,
          "breakdown": {
            "storage_committed": 25.0,
            "usage_balance": 35.0,
            "growth_trend": 15.0
          }
        },
        "stake_confidence": {
          "composite_score": 81.3,
          "rating": "low_risk",
          "color": "#10b981",
          "emoji": "🟢"
        }
      },
      
      "score": 81.3,
      "tier": "low_risk",
      "first_seen": 1700000000,
      "is_public": false
    }
  ],
  "timestamp": 1703001234
}
```

#### Node Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | Unique identifier (IP:port) |
| `pubkey` | string | Operator's public key |
| `is_online` | boolean | Current online status |
| `last_seen` | integer | Last gossip appearance (Unix timestamp) |
| `version` | string | Software version |
| `uptime` | integer | Uptime in seconds |
| `storage_committed` | integer | Committed storage (bytes) |
| `storage_used` | integer | Used storage (bytes) |
| `storage_usage_percent` | float | Usage percentage (0-100) |
| `peer_sources` | array | IPs that reported this node |
| `peer_count` | integer | Number of gossip peers |
| `scores` | object | Performance scores |
| `score` | float | Composite score (0-100) |
| `tier` | string | Risk tier: `low_risk`, `medium_risk`, `high_risk` |

#### Use Cases

✅ **Build node explorer dashboard**  
✅ **Filter nodes by performance tier**  
✅ **Sort by any metric**  
✅ **Paginate through large node lists**

---

### GET `/recommendations`

Get top-performing nodes for staking, pre-filtered and sorted.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | `10` | Max recommendations (1-50) |
| `min_uptime_days` | integer | `7` | Minimum uptime required (days) |
| `require_public` | boolean | `false` | Only public RPC nodes |
| `min_score` | float | `null` | Minimum composite score |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/recommendations?limit=5&min_uptime_days=30"
```

#### Response Structure

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
        "breakdown": {
          "trust": { /* ... */ },
          "capacity": { /* ... */ }
        }
      },
      "uptime_days": 45.2,
      "version": "0.8.0",
      "storage_usage_percent": 35.5,
      "is_public": false,
      "peer_count": 4,
      "first_seen": 1700000000,
      "last_seen": 1703001234
    }
  ],
  "total_evaluated": 98,
  "filters": {
    "min_uptime_days": 30,
    "require_public": false
  },
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **Find best nodes for staking**  
✅ **Filter by uptime requirements**  
✅ **Only show public RPC nodes**  
✅ **Set minimum score threshold**

---

### GET `/registry/{address}`

Get detailed information for a specific node.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | string | Node address (IP:port format) |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/registry/109.199.96.218:9001"
```

#### Response Structure

```json
{
  "entry": {
    "address": "109.199.96.218:9001",
    "pubkey": "0x1234...abcd",
    "version": "0.8.0",
    "first_seen": 1700000000,
    "last_seen": 1703001234,
    "is_online": true,
    "uptime": 2592000,
    "storage_committed": 107374182400,
    "storage_used": 26041344,
    "storage_usage_percent": 24.25,
    "source_ips": ["192.168.1.1", "10.0.0.5"]
  },
  "status": {
    "status": "public",
    "last_ip": "192.168.1.1",
    "updated_at": 1703001234
  }
}
```

#### Use Cases

✅ **Deep dive into specific node**  
✅ **Check detailed status**  
✅ **Verify node configuration**

---

## 📊 Network Analytics

### GET `/network/health`

Get overall network health metrics and alerts.

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/network/health"
```

#### Response Structure

```json
{
  "health": {
    "health_score": 87.3,
    "status": "healthy",
    "factors": {
      "availability": 29.0,
      "version_consistency": 22.5,
      "node_quality": 20.8,
      "connectivity": 18.0
    }
  },
  "network_stats": {
    "total_storage_committed": 12247563264,
    "total_storage_used": 3042394,
    "avg_uptime_hours": 720.5,
    "version_distribution": {
      "0.8.0": 98,
      "0.7.0": 22
    }
  },
  "summary": {
    "total_pnodes": 120,
    "online_pnodes": 98,
    "offline_pnodes": 22
  },
  "alerts": [
    {
      "severity": "medium",
      "type": "version_fragmentation",
      "message": "Network running 2 different versions",
      "recommendation": "Consider coordinating version upgrades"
    }
  ],
  "timestamp": 1703001234
}
```

#### Health Status Values

| Status | Score Range | Description |
|--------|-------------|-------------|
| `healthy` | 80-100 | Network operating normally |
| `fair` | 60-79 | Minor issues detected |
| `degraded` | 40-59 | Significant concerns |
| `critical` | 0-39 | Major problems |

#### Use Cases

✅ **Dashboard health indicator**  
✅ **Monitor network stability**  
✅ **Detect degradation early**

---

### GET `/network/topology`

Get network graph structure for visualization.

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/network/topology"
```

#### Response Structure

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
        "cpu_percent": 2.5,
        "total_pods_reported": 15
      }
    },
    {
      "id": "109.199.96.218:9001",
      "type": "pnode",
      "label": "109.199.96.218",
      "group": "public",
      "properties": {
        "version": "0.8.0",
        "uptime": 2592000,
        "storage_committed": 107374182400,
        "peer_count": 2
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

#### Use Cases

✅ **Render network graph (D3.js, Three.js)**  
✅ **Visualize gossip protocol**  
✅ **Analyze network topology**

---

### GET `/network/analytics`

Comprehensive analytics dashboard data.

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/network/analytics"
```

#### Response Structure

```json
{
  "current_state": {
    "total_pnodes": 120,
    "public_nodes": 68,
    "private_nodes": 52,
    "public_ratio_percent": 56.67
  },
  "growth": {
    "24_hours": {
      "nodes": {
        "start_count": 115,
        "end_count": 120,
        "growth": 5,
        "growth_percent": 4.35
      },
      "storage": {
        "growth": 503512064,
        "growth_percent": 4.29
      }
    },
    "7_days": { /* similar structure */ }
  },
  "version_analysis": {
    "distribution": {"0.8.0": 98, "0.7.0": 22},
    "latest_version": "0.8.0",
    "compliance_percent": 81.67,
    "fragmentation_index": 2,
    "health": "good"
  },
  "storage_analysis": {
    "distribution": {
      "empty": 5,
      "low": 20,
      "optimal": 70,
      "high": 20,
      "critical": 5
    },
    "optimal_percent": 58.33,
    "health": "good"
  },
  "connectivity_analysis": {
    "distribution": {
      "isolated": 2,
      "weak": 10,
      "good": 80,
      "excellent": 28
    },
    "well_connected_percent": 90.0,
    "health": "excellent"
  },
  "recommendations": [
    {
      "category": "version",
      "severity": "medium",
      "message": "18% of nodes need version upgrade",
      "action": "Encourage operators to upgrade to v0.8.0"
    }
  ],
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **Build analytics dashboard**  
✅ **Monitor growth trends**  
✅ **Version compliance tracking**  
✅ **Storage utilization analysis**

---

## 📈 Historical Data

### GET `/network/history`

Get time-series network metrics.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | integer | `24` | Time range (1-720 = 30 days) |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/network/history?hours=168"
```

#### Response Structure

```json
{
  "history": [
    {
      "timestamp": 1702915200,
      "timestamp_readable": "2024-12-18 12:00:00",
      "total_pnodes": 115,
      "total_ip_nodes": 9,
      "public_pnodes": 65,
      "private_pnodes": 50,
      "avg_cpu_percent": 2.3,
      "avg_ram_used_percent": 16.2,
      "total_storage_committed": 11744051200,
      "avg_peer_count": 3.0,
      "version_distribution": {"0.8.0": 90, "0.7.0": 25}
    }
  ],
  "summary": {
    "data_points": 168,
    "time_range_hours": 168,
    "node_growth": {
      "start_count": 115,
      "end_count": 120,
      "growth": 5,
      "growth_percent": 4.35,
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
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **Chart network growth over time**  
✅ **Track storage utilization trends**  
✅ **Monitor version adoption**

---

### GET `/network/growth`

Quick growth snapshot (no full history).

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | integer | `24` | Compare to N hours ago (1-720) |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/network/growth?hours=24"
```

#### Response Structure

```json
{
  "growth_metrics": {
    "available": true,
    "period_hours": 24,
    "comparison": {
      "start_time": 1702914800,
      "end_time": 1703001200,
      "start_time_readable": "2024-12-17 12:00:00",
      "end_time_readable": "2024-12-18 12:00:00"
    },
    "nodes": {
      "start_count": 115,
      "end_count": 120,
      "growth": 5,
      "growth_percent": 4.35
    },
    "storage": {
      "start_committed": 11744051200,
      "end_committed": 12247563264,
      "growth": 503512064,
      "growth_percent": 4.29
    },
    "network_health": {
      "start_peer_count": 2.9,
      "end_peer_count": 3.1,
      "peer_count_change": 0.2
    }
  },
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **Quick growth comparison**  
✅ **Dashboard metrics**  
✅ **Trend indicators**

---

### GET `/node/{address}/history`

Get historical data for a specific node.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | string | Node address (IP:port) |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | `30` | Days of history (1-90) |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/node/109.199.96.218:9001/history?days=30"
```

#### Response Structure

```json
{
  "address": "109.199.96.218:9001",
  "available": true,
  "data_points": 720,
  "time_range": {
    "start": 1700409600,
    "end": 1703001600,
    "days": 30
  },
  "history": [
    {
      "timestamp": 1700409600,
      "is_online": true,
      "score": 85.6,
      "uptime": 2592000,
      "storage_used": 26041344,
      "storage_usage_percent": 24.25,
      "peer_count": 2
    }
  ],
  "trends": {
    "uptime_change_hours": 720.0,
    "storage_used_change_gb": 24.5,
    "score_change": 5.2,
    "score_trend": "improving"
  },
  "availability": {
    "online_snapshots": 718,
    "offline_snapshots": 2,
    "availability_percent": 99.72
  },
  "current_status": {
    "is_online": true,
    "score": 85.6,
    "uptime": 2592000
  }
}
```

#### Use Cases

✅ **Track node performance over time**  
✅ **Detect performance degradation**  
✅ **Calculate availability percentage**

---

## 🚨 Alert System

### GET `/pnodes/{address}/alerts`

Get alerts for a specific node.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | string | Node address (IP:port) |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `severity` | string | `null` | Filter: `critical`, `warning`, `info` |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/pnodes/109.199.96.218:9001/alerts"
```

#### Response Structure

```json
{
  "address": "109.199.96.218:9001",
  "alerts": [
    {
      "severity": "warning",
      "type": "version_behind",
      "message": "Running old version: 0.7.0 (latest: 0.8.0)",
      "metric": "version",
      "value": "0.7.0",
      "threshold": "0.8.0",
      "recommendation": "Upgrade to latest version soon"
    },
    {
      "severity": "info",
      "type": "underutilized",
      "message": "Storage underutilized: 4.5%",
      "metric": "storage_usage_percent",
      "value": 4.5,
      "threshold": 5.0,
      "recommendation": "Node may need more network usage"
    }
  ],
  "summary": {
    "total": 2,
    "critical": 0,
    "warning": 1,
    "info": 1,
    "by_type": {
      "version_behind": 1,
      "underutilized": 1
    }
  },
  "node_info": {
    "is_online": true,
    "uptime": 2592000,
    "version": "0.7.0"
  },
  "timestamp": 1703001234
}
```

#### Alert Types

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

#### Use Cases

✅ **Monitor specific node health**  
✅ **Get actionable recommendations**  
✅ **Early issue detection**

---

### GET `/alerts`

Get network-wide alerts.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `severity` | string | `null` | Filter: `critical`, `warning`, `info` |
| `alert_type` | string | `null` | Filter by alert type |
| `limit` | integer | `100` | Max nodes to check (1-500) |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/alerts?severity=critical"
```

#### Response Structure

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
      "critical_alerts": [
        {
          "severity": "critical",
          "type": "storage_critical",
          "message": "Storage critically full: 96.5%"
        }
      ]
    }
  ],
  "nodes_checked": 120,
  "nodes_with_alerts": 25,
  "filters": {
    "severity": "critical",
    "alert_type": null
  },
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **Identify all problematic nodes**  
✅ **Prioritize critical issues**  
✅ **Network-wide health monitoring**

---

### GET `/alerts/critical`

Quick endpoint for critical alerts only.

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/alerts/critical"
```

#### Use Cases

✅ **Emergency monitoring dashboard**  
✅ **Critical issue alerting**  
✅ **Automated monitoring systems**

---

## 👥 Operator Intelligence

### GET `/operators`

Group nodes by operator (pubkey).

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | `100` | Max operators (1-500) |
| `min_nodes` | integer | `1` | Only operators with N+ nodes |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/operators?min_nodes=2&limit=20"
```

#### Response Structure

```json
{
  "summary": {
    "total_operators": 45,
    "total_nodes": 120,
    "avg_nodes_per_operator": 2.67,
    "largest_operator_share_percent": 8.33,
    "decentralization_score": 91.67
  },
  "operators": [
    {
      "pubkey": "0x1234...abcd",
      "node_count": 10,
      "online_nodes": 9,
      "total_storage_committed": 1073741824000,
      "total_storage_used": 260413440,
      "addresses": [
        "109.199.96.218:9001",
        "10.0.0.5:9001"
      ],
      "versions": ["0.8.0"],
      "first_seen": 1700000000
    }
  ],
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **Identify large operators**  
✅ **Analyze network decentralization**  
✅ **Detect centralization risks**

---

## 🔬 Advanced Features

### GET `/pnodes/compare`

Compare 2-5 nodes side-by-side.

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `addresses` | string | Comma-separated addresses (required) |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/pnodes/compare?addresses=109.199.96.218:9001,10.0.0.5:9001"
```

#### Response Structure

```json
{
  "comparison": [
    { /* full node object */ },
    { /* full node object */ }
  ],
  "winners": {
    "overall_score": {
      "address": "109.199.96.218:9001",
      "score": 85.6,
      "category": "Best overall performance"
    },
    "trust_score": {
      "address": "109.199.96.218:9001",
      "score": 88.0,
      "category": "Most reliable/trustworthy"
    },
    "capacity_score": {
      "address": "10.0.0.5:9001",
      "score": 82.0,
      "category": "Best storage capacity management"
    },
    "best_uptime": {
      "address": "109.199.96.218:9001",
      "uptime": 2592000,
      "uptime_days": 30.0,
      "category": "Longest uptime"
    }
  },
  "recommendation": {
    "recommended_node": "109.199.96.218:9001",
    "reason": "Highest overall score (85.6/100)",
    "considerations": [
      "Node 10.0.0.5:9001 has better storage management"
    ]
  },
  "summary": {
    "nodes_compared": 2,
    "all_online": true,
    "avg_score": 82.5
  },
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **Choose between staking options**  
✅ **Side-by-side performance comparison**  
✅ **Evaluate node trade-offs**

---

### GET `/network/consistency`

Analyze gossip consistency across the network.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_consistency` | float | `0.0` | Filter nodes with score >= this (0.0-1.0) |
| `sort_by` | string | `consistency_score` | Sort field |
| `limit` | integer | `100` | Max results (1-500) |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/network/consistency?min_consistency=0.8"
```

#### Response Structure

```json
{
  "nodes": [
    {
      "address": "109.199.96.218:9001",
      "consistency_score": 0.98,
      "gossip_appearances": 100,
      "gossip_disappearances": 2,
      "last_drop": 1702800000,
      "time_since_last_drop_seconds": 201234,
      "status": "stable",
      "is_online": true
    }
  ],
  "summary": {
    "total_nodes": 120,
    "flapping_nodes": 3,
    "stable_nodes": 117,
    "avg_consistency_score": 0.94,
    "network_health": "good"
  },
  "flapping_nodes": [
    {
      "address": "10.0.0.99:9001",
      "consistency_score": 0.65,
      "gossip_appearances": 65,
      "gossip_disappearances": 35
    }
  ],
  "timestamp": 1703001234
}
```

#### Consistency Score Formula

```
consistency_score = appearances / (appearances + disappearances)
```

**Interpretation:**
- **1.0** = Perfect (never dropped)
- **0.8+** = Good (occasionally drops)
- **< 0.8** = Flapping (unreliable)

#### Use Cases

✅ **Identify unreliable nodes**  
✅ **Track gossip stability**  
✅ **Detect flapping issues**

---

### GET `/node/{address}/consistency`

Get detailed consistency for a specific node.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | string | Node address (IP:port) |

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/node/109.199.96.218:9001/consistency"
```

#### Response Structure

```json
{
  "address": "109.199.96.218:9001",
  "consistency": {
    "score": 0.98,
    "status": "stable",
    "status_emoji": "🟢",
    "appearances": 100,
    "disappearances": 2,
    "ratio": "100:2",
    "total_events": 102
  },
  "recent_activity": {
    "last_drop": 1702800000,
    "last_drop_readable": "2024-12-17 04:26:40 UTC",
    "time_since_drop_hours": 55.9,
    "last_appearance": 1703001200,
    "last_appearance_readable": "2024-12-19 12:20:00 UTC",
    "time_since_appearance_hours": 0.01
  },
  "recommendations": [
    {
      "severity": "info",
      "issue": "No issues detected",
      "recommendation": "Node has stable gossip presence",
      "action": "Continue normal operations"
    }
  ],
  "node_info": {
    "is_online": true,
    "version": "0.8.0",
    "first_seen": 1700000000,
    "last_seen": 1703001234
  },
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **Deep dive into node reliability**  
✅ **Track gossip drops**  
✅ **Get actionable recommendations**

---

## 🏥 System Health

### GET `/health`

Check API health and data freshness.

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/health"
```

#### Response Structure

```json
{
  "status": "healthy",
  "message": "All systems operational",
  "snapshot_age_seconds": 45,
  "last_updated": 1703001234,
  "cache_ttl": 60,
  "total_pnodes": 120,
  "total_ip_nodes": 9,
  "timestamp": 1703001289
}
```

#### Status Values

| Status | Condition | Description |
|--------|-----------|-------------|
| `healthy` | age < 2×TTL | System operational |
| `degraded` | age 2-5×TTL | System functional but slow |
| `unhealthy` | age > 5×TTL | System issues |

#### Use Cases

✅ **Monitoring & uptime checks**  
✅ **Load balancer health endpoint**  
✅ **Verify data freshness**

---

### GET `/`

API overview and endpoint discovery.

#### Request Example

```bash
curl "https://web-production-b4440.up.railway.app/"
```

#### Response Structure

```json
{
  "api_name": "Xandeum PNode Analytics API",
  "version": "2.0.0",
  "description": "Analytics platform for Xandeum pNode network",
  "core_endpoints": {
    "/health": "API health check",
    "/pnodes": "Unified node data",
    "/recommendations": "Top staking nodes",
    "/network/health": "Network health metrics"
  },
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc"
  },
  "data_refresh": "Background worker updates every 60 seconds",
  "timestamp": 1703001234
}
```

#### Use Cases

✅ **API discovery**  
✅ **Verify API is running**  
✅ **Check available endpoints**

---

## ⚠️ Error Handling

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

| Code | Meaning | Example |
|------|---------|---------|
| `200` | Success | Request processed successfully |
| `400` | Bad Request | Invalid parameters |
| `404` | Not Found | Node/resource doesn't exist |
| `500` | Internal Server Error | Server-side error |
| `503` | Service Unavailable | Snapshot not ready |

### Common Errors

#### 404 - Node Not Found

```json
{
  "error": "Node not found: 10.0.0.99:9001",
  "suggestion": "Check /registry for valid addresses"
}
```

#### 400 - Invalid Parameters

```json
{
  "error": "Must provide at least 2 addresses to compare",
  "example": "?addresses=addr1:9001,addr2:9001"
}
```

#### 503 - Snapshot Not Available

```json
{
  "status": "unhealthy",
  "reason": "No snapshot available",
  "message": "Background worker may not have run yet"
}
```

---

## 🔒 Rate Limits

**Current Status:** No rate limits enforced

**Best Practices:**
- ✅ Avoid excessive polling (< 1 request/second)
- ✅ Cache responses when appropriate
- ✅ Use webhooks for real-time updates (coming soon)

**Future:** Rate limiting will be added based on usage patterns.

---

## 💻 Code Examples

### Python

#### Example 1: Get Top Staking Nodes

```python
import requests

response = requests.get(
    "https://web-production-b4440.up.railway.app/recommendations",
    params={"limit": 5, "min_uptime_days": 30}
)

nodes = response.json()["recommendations"]

for node in nodes:
    print(f"Node: {node['address']}")
    print(f"  Score: {node['score']}/100")
    print(f"  Tier: {node['tier']}")
    print(f"  Uptime: {node['uptime_days']} days")
    print()
```

#### Example 2: Monitor Network Health

```python
import requests
import time

def check_network_health():
    response = requests.get(
        "https://web-production-b4440.up.railway.app/network/health"
    )
    data = response.json()
    
    health = data["health"]
    print(f"Network Health: {health['status']}")
    print(f"Score: {health['health_score']}/100")
    
    if health["status"] != "healthy":
        print("⚠️ Network issues detected:")
        for alert in data["alerts"]:
            print(f"  - {alert['message']}")

# Check every 5 minutes
while True:
    check_network_health()
    time.sleep(300)
```

#### Example 3: Track Node Performance

```python
import requests
import pandas as pd

# Get node history
response = requests.get(
    "https://web-production-b4440.up.railway.app/node/109.199.96.218:9001/history",
    params={"days": 30}
)

data = response.json()

if data["available"]:
    # Convert to DataFrame
    df = pd.DataFrame(data["history"])
    
    # Calculate metrics
    avg_score = df["score"].mean()
    availability = data["availability"]["availability_percent"]
    
    print(f"30-Day Performance:")
    print(f"  Average Score: {avg_score:.2f}")
    print(f"  Availability: {availability}%")
    print(f"  Trend: {data['trends']['score_trend']}")
```

---

### JavaScript/TypeScript

#### Example 1: React Hook

```typescript
import { useEffect, useState } from 'react';

interface NetworkHealth {
  health_score: number;
  status: string;
  factors: Record<string, number>;
}

function useNetworkHealth() {
  const [health, setHealth] = useState<NetworkHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      const response = await fetch(
        'https://web-production-b4440.up.railway.app/network/health'
      );
      const data = await response.json();
      setHealth(data.health);
      setLoading(false);
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  return { health, loading };
}

// Usage
function HealthDashboard() {
  const { health, loading } = useNetworkHealth();

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Network Health: {health?.status}</h2>
      <p>Score: {health?.health_score}/100</p>
    </div>
  );
}
```

#### Example 2: Compare Nodes

```javascript
async function compareNodes(address1, address2) {
  const response = await fetch(
    `https://web-production-b4440.up.railway.app/pnodes/compare?addresses=${address1},${address2}`
  );
  
  const data = await response.json();
  
  console.log('Winner:', data.winners.overall_score.address);
  console.log('Score:', data.winners.overall_score.score);
  console.log('Recommendation:', data.recommendation.reason);
  
  return data;
}

// Usage
compareNodes('109.199.96.218:9001', '10.0.0.5:9001')
  .then(result => console.log(result));
```

---

### cURL Examples

#### Get Critical Alerts

```bash
curl "https://web-production-b4440.up.railway.app/alerts/critical" | jq '.critical_nodes'
```

#### Monitor Specific Node

```bash
# Get alerts
curl "https://web-production-b4440.up.railway.app/pnodes/109.199.96.218:9001/alerts" | jq '.summary'

# Get consistency
curl "https://web-production-b4440.up.railway.app/node/109.199.96.218:9001/consistency" | jq '.consistency'

# Get history
curl "https://web-production-b4440.up.railway.app/node/109.199.96.218:9001/history?days=7" | jq '.trends'
```

#### Network Growth Tracking

```bash
# 24h growth
curl "https://web-production-b4440.up.railway.app/network/growth?hours=24" | jq '.growth_metrics.nodes'

# 7d growth
curl "https://web-production-b4440.up.railway.app/network/growth?hours=168" | jq '.growth_metrics'
```

---

## 🔍 Advanced Queries

### Pagination Example

```bash
# Get first 50 nodes
curl "https://web-production-b4440.up.railway.app/pnodes?limit=50&skip=0"

# Get next 50 nodes
curl "https://web-production-b4440.up.railway.app/pnodes?limit=50&skip=50"
```

### Filtering & Sorting

```bash
# Get top 10 by score
curl "https://web-production-b4440.up.railway.app/pnodes?status=online&sort_by=score&sort_order=desc&limit=10"

# Get nodes with low storage usage
curl "https://web-production-b4440.up.railway.app/pnodes?status=online&sort_by=storage_usage_percent&sort_order=asc&limit=20"

# Get newest nodes
curl "https://web-production-b4440.up.railway.app/pnodes?status=all&sort_by=first_seen&sort_order=desc&limit=10"
```

### Combining Multiple Endpoints

```python
import requests

# Get recommendations
recs = requests.get(
    "https://web-production-b4440.up.railway.app/recommendations?limit=5"
).json()

# Get alerts for each recommendation
for node in recs["recommendations"]:
    address = node["address"]
    alerts_response = requests.get(
        f"https://web-production-b4440.up.railway.app/pnodes/{address}/alerts"
    )
    alerts = alerts_response.json()
    
    print(f"{address}: {alerts['summary']['total']} alerts")
```

---

## 📊 Response Time Expectations

| Endpoint | Expected | Acceptable | Notes |
|----------|----------|------------|-------|
| `/health` | 20-50ms | < 100ms | Fastest endpoint |
| `/pnodes` (10) | 100-200ms | < 300ms | Small pagination |
| `/pnodes` (100) | 200-300ms | < 500ms | Moderate pagination |
| `/pnodes` (1000) | 400-600ms | < 1000ms | Large pagination |
| `/recommendations` | 250-350ms | < 600ms | Pre-sorted data |
| `/network/topology` | 100-200ms | < 400ms | Graph structure |
| `/network/health` | 300-500ms | < 800ms | Complex calculations |
| `/network/analytics` | 400-600ms | < 900ms | Most comprehensive |
| `/network/history` | 100-150ms | < 400ms | Time-series query |
| `/alerts` | 300-500ms | < 800ms | Checks all nodes |
| `/pnodes/compare` | 150-250ms | < 500ms | 2-5 nodes |

**Note:** Times measured on Railway Basic with MongoDB Atlas M0 (free tier)

---

## 🌍 CORS Support

**Allowed Origins:**
```
http://localhost:3000
http://localhost:3001
http://localhost:8000
http://localhost:8080
https://*.vercel.app
https://*.github.dev
```

**Credentials:** Allowed  
**Methods:** All  
**Headers:** All

---

## 📝 Changelog

### v1.1.0 (December 2024)

**Added:**
- ✨ Per-node historical tracking
- ✨ Gossip consistency monitoring
- ✨ Advanced alert system
- ✨ Node comparison tool
- ✨ Network analytics dashboard

**Changed:**
- 🔄 Primary key changed from `pubkey` to `address`
- 🔄 Field name: `is_public_rpc` → `is_public`
- 🔄 Scoring system enhanced (null-safe)

**Fixed:**
- 🐛 Null-safety across all endpoints
- 🐛 IP_NODES configuration from .env
- 🐛 Database indexing

---

## 🆘 Support

### Documentation

- **GitHub**: [github.com/lucadavid075/pnode-aggregation-api](https://github.com/lucadavid075/pnode-aggregation-api)
- **Issues**: [Report bugs/features](https://github.com/lucadavid075/pnode-aggregation-api/issues)

### Community

- **Discord**: [Join Community](https://discord.gg/uqRSmmM5m)
- **Twitter/X**: [@Xandeum](https://twitter.com/Xandeum)

### Response Time

- **Community**: 24-48 hours
- **Critical bugs**: < 24 hours
- **Feature requests**: Tracked in roadmap

---

## 🎯 Quick Reference Card

### Most Important Endpoints

```bash
# Get top nodes for staking
GET /recommendations?limit=5&min_uptime_days=30

# Check network health
GET /network/health

# Monitor specific node
GET /pnodes/{address}/alerts

# Compare nodes
GET /pnodes/compare?addresses=addr1,addr2

# Get network growth
GET /network/growth?hours=24
```

### Key Parameters

- `status`: `online`, `offline`, `all`
- `limit`: Results per page (1-1000)
- `sort_by`: `score`, `uptime`, `last_seen`
- `min_uptime_days`: Minimum uptime filter
- `severity`: `critical`, `warning`, `info`

---

## 📚 Additional Resources

- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Testing**: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Contributing**: [CONTRIBUTION.md](CONTRIBUTION.md)

---

<div align="center">

**Xandeum PNode Analytics API v1.1.0**

[Live Demo](https://web-production-b4440.up.railway.app) • [Interactive Docs](https://web-production-b4440.up.railway.app/docs) • [GitHub](https://github.com/lucadavid075/pnode-aggregation-api)

*Built with ❤️ for the Xandeum Community*

</div>