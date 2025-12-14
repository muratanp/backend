from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.utils.jsonrpc import jsonrpc_error, INTERNAL_ERROR
from app.fetcher import fetch_all_nodes_background
from .db import (
    nodes_current, get_registry, get_registry_entry, get_status, 
    prune_old_nodes, sanitize_mongo, CACHE_TTL, pnodes_registry,
    setup_indexes, get_growth_metrics, get_node_history  # ADDED
)
import time


app = FastAPI(
    title="Xandeum PNode Analytics API",
    description="Production-ready analytics platform for Xandeum pNode network monitoring and staking",
    version="2.0.0"
)

# --- CORS setup ---
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup: Initialize indexes and background task ---
@app.on_event("startup")
async def startup_event():
    """Initialize database indexes and start background worker."""
    setup_indexes()  # ADDED: Create indexes on startup
    fetch_all_nodes_background()


# --- NEW: Health Check Endpoint ---
@app.get("/health", summary="API Health Check")
async def health_check():
    """
    Check if API and background worker are functioning.
    
    Returns:
        - status: "healthy" | "degraded" | "unhealthy"
        - snapshot_age_seconds: How old the snapshot is
        - last_updated: Timestamp of last snapshot
        - cache_ttl: Expected refresh interval
        - total_pnodes: Count from snapshot
    """
    snapshot = nodes_current.find_one({"_id": "snapshot"})
    
    if not snapshot:
        return JSONResponse(
            {
                "status": "unhealthy",
                "reason": "No snapshot available",
                "message": "Background worker may not have run yet",
                "timestamp": int(time.time())
            },
            status_code=503
        )
    
    data = snapshot.get("data", {})
    summary = data.get("summary", {})
    last_updated = summary.get("last_updated", 0)
    now = int(time.time())
    age_seconds = now - last_updated
    
    # If snapshot is older than 2x CACHE_TTL, something is wrong
    is_healthy = age_seconds < (2 * CACHE_TTL)
    
    if not is_healthy:
        status = "degraded"
        message = f"Snapshot is {age_seconds}s old (expected < {2 * CACHE_TTL}s)"
    else:
        status = "healthy"
        message = "All systems operational"
    
    return {
        "status": status,
        "message": message,
        "snapshot_age_seconds": age_seconds,
        "last_updated": last_updated,
        "cache_ttl": CACHE_TTL,
        "total_pnodes": summary.get("total_pnodes", 0),
        "total_ip_nodes": len(data.get("nodes", {})),
        "timestamp": now
    }


# --- API endpoints ---
@app.get("/all-nodes", summary="Aggregated PNode data from MongoDB")
async def get_all_nodes(version: str = None):
    """
    Returns the latest snapshot of all IP nodes aggregated by the background worker.

    Parameters:
    - version: "unique" (default) returns deduplicated nodes (merged_pnodes_unique)
               "raw" returns all nodes including duplicates (merged_pnodes_raw)
    """
    snapshot = nodes_current.find_one({"_id": "snapshot"})
    if not snapshot or "data" not in snapshot:
        return JSONResponse(jsonrpc_error("Snapshot not yet available", INTERNAL_ERROR))

    data = snapshot["data"]

    if version == "raw":
        return {"version": "raw", "nodes": data.get("merged_pnodes_raw", [])}
    elif version == "unique":
        # default to unique
        return {"version": "unique", "nodes": data.get("merged_pnodes_unique", [])}
    else:
        return data


@app.get("/", summary="API Overview")
async def root():
    """
    Xandeum PNode Analytics API Root
    
    A comprehensive analytics platform for the Xandeum storage network.
    Track node performance, network health, and make informed staking decisions.
    """
    return {
        "api_name": "Xandeum PNode Analytics API",
        "version": "2.0.0",
        "description": "Production-ready analytics platform for Xandeum pNode network",
        
        "core_endpoints": {
            "/health": "API health check",
            "/all-nodes": "Current snapshot of all nodes",
            "/registry": "Historical node registry (paged)",
            "/registry/{address}": "Individual node details",
        },
        
        "management_endpoints": {
            "/prune": "Remove old inactive nodes",
            "/graveyard": "List inactive nodes"
        },
        
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        
        "data_refresh": f"Background worker updates every {CACHE_TTL} seconds",
        "timestamp": int(time.time())
    }


@app.get("/registry", summary="List persistent pNode registry")
async def registry_list(limit: int = Query(100, ge=1, le=1000), skip: int = 0):
    """
    Returns the pnodes registry (paged).
    
    This is a PERSISTENT DATABASE - nodes stay here even when offline.
    For real-time active nodes only, use /all-nodes instead.
    """
    try:
        items = get_registry(limit=limit, skip=skip)
        return items
    except Exception as e:
        return JSONResponse(jsonrpc_error(f"Failed to read registry: {str(e)}", INTERNAL_ERROR), status_code=500)


@app.get("/registry/{address:path}", summary="Get single registry entry")
async def registry_get(address: str):
    """
    Get registry entry by ADDRESS (IP:port format).
    
    Example: /registry/109.199.96.218:9001
    
    Args:
        address: IP:port string (e.g., "109.199.96.218:9001")
    """
    try:
        entry = get_registry_entry(address)
        if not entry:
            return JSONResponse(
                jsonrpc_error(f"Registry entry not found for address: {address}", INTERNAL_ERROR),
                status_code=404
            )
        status = get_status(address)
        
        # Add online status
        now = int(time.time())
        entry["is_online"] = (now - entry.get("last_seen", 0)) <= 2 * CACHE_TTL
        
        return {"entry": entry, "status": status}
    except Exception as e:
        return JSONResponse(jsonrpc_error(f"Failed to read registry entry: {str(e)}", INTERNAL_ERROR), status_code=500)


@app.delete("/prune", summary="Prune inactive nodes from registry")
async def prune_registry(days: int = 90):
    """
    Remove registry entries that haven't been seen in `days` days.
    """
    try:
        result = prune_old_nodes(days=days)
        return {
            "status": "ok",
            "threshold_days": days,
            "deleted_count": result.get("deleted_count", 0)
        }
    except Exception as e:
        return JSONResponse(
            jsonrpc_error(f"Failed to prune registry: {str(e)}", INTERNAL_ERROR),
            status_code=500
        )


@app.get("/graveyard", summary="List inactive nodes (graveyard)")
async def graveyard_nodes(days: int = 90, skip: int = 0, limit: int = 100):
    """
    Returns nodes not seen in `days` days.
    """
    try:
        threshold = int(time.time()) - days * 24 * 3600
        cursor = pnodes_registry.find({"last_seen": {"$lt": threshold}}).sort("last_seen", -1).skip(skip).limit(limit)
        items = [sanitize_mongo(doc) for doc in cursor]
        return {
            "count": len(items),
            "threshold_days": days,
            "items": items
        }
    except Exception as e:
        return JSONResponse(
            jsonrpc_error(f"Failed to fetch graveyard nodes: {str(e)}", INTERNAL_ERROR),
            status_code=500
        )

# Add this to app/main.py (after existing endpoints)

from .scoring import calculate_all_scores

# Helper function to safely get values with defaults
def safe_get(data: dict, key: str, default=0):
    """Safely get value from dict, handling None."""
    value = data.get(key, default)
    return default if value is None else value


def safe_get_list(data: dict, key: str):
    """Safely get list from dict, handling None."""
    value = data.get(key, [])
    return [] if value is None else value


@app.get("/pnodes", summary="Unified pNode data (RECOMMENDED)")
async def get_pnodes_unified(
    status: str = Query("online", regex="^(all|online|offline)$"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = 0,
    sort_by: str = Query("last_seen", regex="^(last_seen|uptime|score|storage_used|storage_usage_percent|first_seen)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """
    UNIFIED pNode endpoint - single source of truth for frontend.
    
    This endpoint combines:
    - Accurate total count (all known nodes)
    - Real-time online/offline status (from snapshot)
    - Detailed registry data (persistent info, first_seen, etc.)
    - Performance scoring
    
    **NULL-SAFE**: Handles missing/None values gracefully
    
    Parameters:
    - status: "online" (default), "offline", or "all"
    - limit: pagination limit (1-1000)
    - skip: pagination offset
    - sort_by: field to sort by
    - sort_order: "asc" or "desc"
    
    Returns comprehensive data suitable for building rich UI.
    """
    # Get current snapshot for online status
    snapshot = nodes_current.find_one({"_id": "snapshot"})
    if not snapshot or "data" not in snapshot:
        return JSONResponse(
            jsonrpc_error("Snapshot not available", INTERNAL_ERROR),
            status_code=503
        )
    
    snapshot_data = snapshot["data"]
    current_pnodes = snapshot_data.get("merged_pnodes_unique", [])
    
    # Build map of currently online nodes by address
    online_map = {}
    for pnode in current_pnodes:
        addr = pnode.get("address")
        if addr:
            online_map[addr] = pnode
    
    # Get all registry entries
    now = int(time.time())
    all_registry = list(pnodes_registry.find())
    
    # Merge snapshot data with registry data
    merged_pnodes = []
    processed_addresses = set()
    
    # First: Process all online nodes (from snapshot)
    for pnode in current_pnodes:
        address = pnode.get("address")
        if not address:
            continue
        
        processed_addresses.add(address)
        
        # Get corresponding registry entry (if exists)
        registry_entry = pnodes_registry.find_one({"address": address})
        
        # Build unified entry with NULL-SAFE access
        unified_entry = {
            # Identity
            "address": address,
            "pubkey": pnode.get("pubkey") or "",
            
            # Status
            "is_online": True,
            "last_seen": safe_get(pnode, "last_seen_timestamp", now),
            "last_checked": now,
            
            # Network info (from snapshot - most current)
            "version": pnode.get("version") or "unknown",
            "uptime": safe_get(pnode, "uptime", 0),
            "is_public": bool(pnode.get("is_public")) if pnode.get("is_public") is not None else False,
            "rpc_port": safe_get(pnode, "rpc_port", 6000),
            
            # Storage metrics (from snapshot) - NULL-SAFE
            "storage_committed": safe_get(pnode, "storage_committed", 0),
            "storage_used": safe_get(pnode, "storage_used", 0),
            "storage_usage_percent": safe_get(pnode, "storage_usage_percent", 0.0),
            
            # Network topology (from snapshot) - NULL-SAFE
            "peer_sources": safe_get_list(pnode, "peer_sources"),
            "peer_count": len(safe_get_list(pnode, "peer_sources")),
            
            # Historical data (from registry if available) - NULL-SAFE
            "first_seen": (
                safe_get(registry_entry, "first_seen", safe_get(pnode, "last_seen_timestamp", now))
                if registry_entry else safe_get(pnode, "last_seen_timestamp", now)
            ),
            "source_ips": (
                safe_get_list(registry_entry, "source_ips") if registry_entry 
                else safe_get_list(pnode, "peer_sources")
            ),
        }
        
        # Calculate performance score - WRAP IN TRY/CATCH
        try:
            score_data = calculate_all_scores(unified_entry)
            unified_entry["scores"] = score_data
            unified_entry["score"] = score_data["stake_confidence"]["composite_score"]
            unified_entry["tier"] = score_data["stake_confidence"]["rating"]
        except Exception as e:
            # If scoring fails, set defaults
            logger.error(f"Scoring failed for {address}: {e}")
            unified_entry["scores"] = {
                "trust": {"score": 0, "breakdown": {}},
                "capacity": {"score": 0, "breakdown": {}},
                "stake_confidence": {"composite_score": 0, "rating": "unknown"}
            }
            unified_entry["score"] = 0
            unified_entry["tier"] = "unknown"
        
        merged_pnodes.append(unified_entry)
    
    # Second: Add offline nodes from registry (if status is "all" or "offline")
    if status in ["all", "offline"]:
        for reg_entry in all_registry:
            address = reg_entry.get("address")
            if not address or address in processed_addresses:
                continue  # Already added as online
            
            # Check if truly offline (not seen in 2x CACHE_TTL)
            last_seen = safe_get(reg_entry, "last_seen", 0)
            is_offline = (now - last_seen) > 2 * CACHE_TTL
            
            if not is_offline:
                continue  # Still considered online somehow
            
            # Build offline entry - NULL-SAFE
            unified_entry = {
                # Identity
                "address": address,
                "pubkey": reg_entry.get("pubkey") or "",
                
                # Status
                "is_online": False,
                "last_seen": last_seen,
                "last_checked": now,
                "offline_duration": now - last_seen,
                
                # Network info (from last known state) - NULL-SAFE
                "version": reg_entry.get("version") or "unknown",
                "uptime": 0,  # Offline = no uptime
                "is_public": bool(reg_entry.get("is_public")) if reg_entry.get("is_public") is not None else False,
                "rpc_port": safe_get(reg_entry, "rpc_port", 6000),
                
                # Storage metrics (from last known state) - NULL-SAFE
                "storage_committed": safe_get(reg_entry, "storage_committed", 0),
                "storage_used": safe_get(reg_entry, "storage_used", 0),
                "storage_usage_percent": safe_get(reg_entry, "storage_usage_percent", 0.0),
                
                # Network topology
                "peer_sources": [],
                "peer_count": 0,
                
                # Historical data - NULL-SAFE
                "first_seen": safe_get(reg_entry, "first_seen", last_seen),
                "source_ips": safe_get_list(reg_entry, "source_ips"),
            }
            
            # Score is 0 for offline nodes
            unified_entry["scores"] = {
                "trust": {"score": 0, "breakdown": {}},
                "capacity": {"score": 0, "breakdown": {}},
                "stake_confidence": {"composite_score": 0, "rating": "offline"}
            }
            unified_entry["score"] = 0
            unified_entry["tier"] = "offline"
            
            merged_pnodes.append(unified_entry)
    
    # Filter by status
    if status == "online":
        filtered_nodes = [p for p in merged_pnodes if p.get("is_online", False)]
    elif status == "offline":
        filtered_nodes = [p for p in merged_pnodes if not p.get("is_online", True)]
    else:
        filtered_nodes = merged_pnodes
    
    # Sort with NULL-SAFE handling
    reverse = (sort_order == "desc")
    try:
        filtered_nodes.sort(
            key=lambda x: safe_get(x, sort_by, 0),
            reverse=reverse
        )
    except Exception as e:
        logger.error(f"Sort failed: {e}. Using default sort.")
        # Fallback to last_seen sort
        filtered_nodes.sort(
            key=lambda x: safe_get(x, "last_seen", 0),
            reverse=True
        )
    
    # Calculate accurate counts
    total_count = len(merged_pnodes)
    online_count = len([p for p in merged_pnodes if p.get("is_online", False)])
    offline_count = total_count - online_count
    
    # Paginate
    paginated = filtered_nodes[skip:skip + limit]
    
    # Calculate version distribution (online nodes only) - NULL-SAFE
    version_distribution = {}
    for node in merged_pnodes:
        if node.get("is_online", False):
            v = node.get("version") or "unknown"
            version_distribution[v] = version_distribution.get(v, 0) + 1
    
    # Calculate network-wide totals - NULL-SAFE
    total_storage_committed = sum(
        safe_get(p, "storage_committed", 0) for p in merged_pnodes
    )
    total_storage_used = sum(
        safe_get(p, "storage_used", 0) for p in merged_pnodes
    )
    
    # Calculate average uptime (online nodes only) - NULL-SAFE
    if online_count > 0:
        total_uptime_hours = sum(
            safe_get(p, "uptime", 0) / 3600 
            for p in merged_pnodes 
            if p.get("is_online", False)
        )
        avg_uptime_hours = total_uptime_hours / online_count
    else:
        avg_uptime_hours = 0
    
    # Return comprehensive response
    return {
        "summary": {
            "total_pnodes": total_count,
            "online_pnodes": online_count,
            "offline_pnodes": offline_count,
            "snapshot_age_seconds": now - safe_get(snapshot_data.get("summary", {}), "last_updated", now),
            "last_updated": safe_get(snapshot_data.get("summary", {}), "last_updated", now),
        },
        "network_stats": {
            "total_storage_committed": total_storage_committed,
            "total_storage_used": total_storage_used,
            "avg_uptime_hours": round(avg_uptime_hours, 2),
            "version_distribution": version_distribution,
        },
        "pagination": {
            "total": len(filtered_nodes),
            "limit": limit,
            "skip": skip,
            "returned": len(paginated)
        },
        "filters": {
            "status": status,
            "sort_by": sort_by,
            "sort_order": sort_order
        },
        "pnodes": paginated,
        "timestamp": now
    }

# Add these to app/main.py (after /pnodes endpoint)

@app.get("/recommendations", summary="Top pNodes for staking")
async def get_staking_recommendations(
    limit: int = Query(10, ge=1, le=50),
    min_uptime_days: int = Query(7, ge=1, le=365),
    require_public: bool = Query(False)
):
    """
    Returns top-performing pNodes for XAND staking.
    
    Pre-filtered for quality:
    - Only online nodes
    - Minimum uptime threshold
    - Optionally only public RPC nodes
    
    Sorted by performance score (highest first).
    
    **NULL-SAFE**: Handles missing/None values gracefully
    
    Parameters:
    - limit: How many recommendations to return (max 50)
    - min_uptime_days: Minimum uptime in days (default 7)
    - require_public: Only include public RPC nodes
    """
    # Get all online nodes
    response = await get_pnodes_unified(status="online", limit=10000)
    all_nodes = response.get("pnodes", [])
    
    scored = []
    now = int(time.time())
    min_uptime_seconds = min_uptime_days * 86400
    
    for pnode in all_nodes:
        # Filter criteria - NULL-SAFE
        if not pnode.get("is_online", False):
            continue
        if safe_get(pnode, "uptime", 0) < min_uptime_seconds:
            continue
        if require_public and not pnode.get("is_public", False):
            continue
        
        # Extract scores safely
        scores = pnode.get("scores", {})
        stake_confidence = scores.get("stake_confidence", {})
        
        scored.append({
            "address": pnode.get("address") or "",
            "pubkey": pnode.get("pubkey") or "",
            "score": safe_get(stake_confidence, "composite_score", 0),
            "tier": stake_confidence.get("rating") or "unknown",
            "scores": {
                "trust": safe_get(scores.get("trust", {}), "score", 0),
                "capacity": safe_get(scores.get("capacity", {}), "score", 0),
                "breakdown": {
                    "trust": scores.get("trust", {}).get("breakdown", {}),
                    "capacity": scores.get("capacity", {}).get("breakdown", {})
                }
            },
            "uptime_days": round(safe_get(pnode, "uptime", 0) / 86400, 1),
            "version": pnode.get("version") or "unknown",
            "storage_usage_percent": round(safe_get(pnode, "storage_usage_percent", 0), 2),
            "is_public": bool(pnode.get("is_public", False)),
            "peer_count": safe_get(pnode, "peer_count", 0),
            "first_seen": safe_get(pnode, "first_seen", 0),
            "last_seen": safe_get(pnode, "last_seen", 0)
        })
    
    # Sort by score descending
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return {
        "recommendations": scored[:limit],
        "total_evaluated": len(scored),
        "filters": {
            "min_uptime_days": min_uptime_days,
            "require_public": require_public
        },
        "timestamp": now
    }


@app.get("/network/topology", summary="Network topology for visualization")
async def get_network_topology():
    """
    Returns network graph structure for visualization.
    
    Nodes:
    - IP nodes (discovery/gossip hubs)
    - pNodes (storage nodes)
    
    Edges:
    - Gossip connections (which IP nodes see which pNodes)
    
    **NULL-SAFE**: Handles missing/None values gracefully
    
    Perfect for D3.js, Three.js, Cytoscape, etc.
    """
    snapshot = nodes_current.find_one({"_id": "snapshot"})
    if not snapshot or "data" not in snapshot:
        return JSONResponse(
            jsonrpc_error("Snapshot not available", INTERNAL_ERROR),
            status_code=503
        )
    
    data = snapshot["data"]
    nodes = []
    edges = []
    
    # Add IP nodes (discovery nodes) - NULL-SAFE
    for ip, node_data in data.get("nodes", {}).items():
        stats = node_data.get("stats", {})
        ram_total = safe_get(stats, "ram_total", 1)
        ram_used = safe_get(stats, "ram_used", 0)
        ram_percent = (ram_used / ram_total * 100) if ram_total > 0 else 0
        
        nodes.append({
            "id": ip,
            "type": "ip_node",
            "label": ip,
            "group": "ip",
            "properties": {
                "active_streams": safe_get(stats, "active_streams", 0),
                "uptime": safe_get(stats, "uptime", 0),
                "cpu_percent": safe_get(stats, "cpu_percent", 0),
                "ram_used_percent": round(ram_percent, 2),
                "total_pods_reported": len(node_data.get("pods", []))
            }
        })
    
    # Add pNodes with their connections - NULL-SAFE
    for pnode in data.get("merged_pnodes_unique", []):
        address = pnode.get("address")
        if not address:
            continue
        
        peer_sources = safe_get_list(pnode, "peer_sources")
        
        # Create label (shorten if needed)
        label = address.split(":")[0] if ":" in address else address
        if len(label) > 15:
            label = label[:12] + "..."
        
        nodes.append({
            "id": address,
            "type": "pnode",
            "label": label,
            "group": "public" if pnode.get("is_public") else "private",
            "properties": {
                "pubkey": pnode.get("pubkey") or "",
                "version": pnode.get("version") or "unknown",
                "uptime": safe_get(pnode, "uptime", 0),
                "storage_committed": safe_get(pnode, "storage_committed", 0),
                "storage_used": safe_get(pnode, "storage_used", 0),
                "storage_usage_percent": safe_get(pnode, "storage_usage_percent", 0),
                "is_public": bool(pnode.get("is_public", False)),
                "peer_count": len(peer_sources),
                "last_seen": safe_get(pnode, "last_seen_timestamp", 0)
            }
        })
        
        # Create edges: IP node -> pNode (gossip connection)
        for source_ip in peer_sources:
            edges.append({
                "source": source_ip,
                "target": address,
                "type": "gossip_connection"
            })
    
    # Calculate basic network stats - NULL-SAFE
    pnode_count = len([n for n in nodes if n.get("type") == "pnode"])
    ip_node_count = len([n for n in nodes if n.get("type") == "ip_node"])
    avg_connections = len(edges) / pnode_count if pnode_count > 0 else 0
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "ip_nodes": ip_node_count,
            "pnodes": pnode_count,
            "total_connections": len(edges),
            "avg_connections_per_pnode": round(avg_connections, 2),
            "timestamp": int(time.time())
        }
    }


@app.get("/network/health", summary="Overall network health metrics")
async def get_network_health():
    """
    Aggregate network-wide health statistics.
    
    Returns:
    - Overall health score (0-100)
    - Status (healthy/fair/degraded/critical)
    - Breakdown of contributing factors
    - Network statistics
    - Active alerts
    
    **NULL-SAFE**: Handles missing/None values gracefully
    """
    from .scoring import calculate_network_health_score
    
    # Get all nodes
    response = await get_pnodes_unified(status="all", limit=10000)
    all_nodes = response.get("pnodes", [])
    
    # Calculate health score
    health_data = calculate_network_health_score(all_nodes)
    
    # Generate alerts - NULL-SAFE
    alerts = []
    online_count = len([n for n in all_nodes if n.get("is_online", False)])
    
    # Alert: Low node count
    if online_count < 50:
        alerts.append({
            "severity": "high" if online_count < 30 else "medium",
            "type": "low_node_count",
            "message": f"Network has only {online_count} active nodes",
            "recommendation": "Monitor node availability closely"
        })
    
    # Alert: Version fragmentation
    version_counts = response.get("network_stats", {}).get("version_distribution", {})
    if len(version_counts) > 3:
        alerts.append({
            "severity": "medium",
            "type": "version_fragmentation",
            "message": f"Network running {len(version_counts)} different versions",
            "recommendation": "Consider coordinating version upgrades"
        })
    
    # Alert: Low health score
    if health_data.get("health_score", 0) < 60:
        alerts.append({
            "severity": "high",
            "type": "low_health_score",
            "message": f"Network health score is {health_data.get('health_score', 0)}",
            "recommendation": "Review network health factors"
        })
    
    return {
        "health": health_data,
        "network_stats": response.get("network_stats", {}),
        "summary": response.get("summary", {}),
        "alerts": alerts,
        "timestamp": int(time.time())
    }


@app.get("/operators", summary="List operators and their nodes")
async def get_operators(
    limit: int = Query(100, ge=1, le=500),
    min_nodes: int = Query(1, ge=1)
):
    """
    Group nodes by operator (pubkey).
    Shows which operators run multiple nodes.
    
    Useful for:
    - Identifying large operators
    - Analyzing network decentralization
    - Detecting centralization risks
    
    **NULL-SAFE**: Handles missing/None values gracefully
    
    Parameters:
    - limit: Max operators to return
    - min_nodes: Only show operators with at least N nodes
    """
    # Get all nodes
    response = await get_pnodes_unified(status="all", limit=10000)
    all_nodes = response.get("pnodes", [])
    
    operators = {}
    
    for node in all_nodes:
        pubkey = node.get("pubkey") or node.get("address")  # Fallback to address if no pubkey
        if not pubkey:
            continue
        
        if pubkey not in operators:
            operators[pubkey] = {
                "pubkey": pubkey,
                "node_count": 0,
                "online_nodes": 0,
                "total_storage_committed": 0,
                "total_storage_used": 0,
                "addresses": [],
                "versions": set(),
                "first_seen": safe_get(node, "first_seen", 0)
            }
        
        op = operators[pubkey]
        op["node_count"] += 1
        if node.get("is_online", False):
            op["online_nodes"] += 1
        op["total_storage_committed"] += safe_get(node, "storage_committed", 0)
        op["total_storage_used"] += safe_get(node, "storage_used", 0)
        op["addresses"].append(node.get("address") or "")
        version = node.get("version")
        if version:
            op["versions"].add(version)
        
        # Track earliest first_seen
        node_first_seen = safe_get(node, "first_seen", float('inf'))
        if node_first_seen < op["first_seen"]:
            op["first_seen"] = node_first_seen
    
    # Convert versions set to list
    for op in operators.values():
        op["versions"] = list(op["versions"])
    
    # Filter by min_nodes
    filtered_operators = [
        op for op in operators.values()
        if op["node_count"] >= min_nodes
    ]
    
    # Sort by node count descending
    filtered_operators.sort(key=lambda x: x.get("node_count", 0), reverse=True)
    
    # Calculate decentralization metrics - NULL-SAFE
    total_nodes = sum(op.get("node_count", 0) for op in filtered_operators)
    if filtered_operators and total_nodes > 0:
        largest_operator_share = (filtered_operators[0].get("node_count", 0) / total_nodes * 100)
    else:
        largest_operator_share = 0
    
    return {
        "summary": {
            "total_operators": len(filtered_operators),
            "total_nodes": total_nodes,
            "avg_nodes_per_operator": round(total_nodes / len(filtered_operators), 2) if filtered_operators else 0,
            "largest_operator_share_percent": round(largest_operator_share, 2),
            "decentralization_score": round(100 - largest_operator_share, 2)
        },
        "operators": filtered_operators[:limit],
        "timestamp": int(time.time())
    }


@app.get("/network/history", summary="Network metrics over time")
async def get_network_history(
    hours: int = Query(24, ge=1, le=720)  # Up to 30 days
):
    """
    Returns historical network metrics for trend analysis.
    
    **ENHANCED**: Now includes detailed storage, network, and growth metrics
    **NULL-SAFE**: Handles missing/None values gracefully
    
    Parameters:
    - hours: How many hours of history to return (max 720 = 30 days)
    
    Perfect for rendering charts showing network growth over time.
    """
    from .db import pnodes_snapshots
    
    now = int(time.time())
    start_time = now - (hours * 3600)
    
    cursor = pnodes_snapshots.find({
        "timestamp": {"$gte": start_time}
    }).sort("timestamp", 1)
    
    history = []
    for doc in cursor:
        doc = sanitize_mongo(doc)
        history.append(doc)
    
    if not history:
        return {
            "history": [],
            "summary": {
                "data_points": 0,
                "time_range_hours": hours,
                "message": "No historical data available yet. Wait a few minutes for snapshots to accumulate."
            },
            "timestamp": now
        }
    
    # Calculate trends - NULL-SAFE
    first = history[0]
    last = history[-1]
    
    first_count = safe_get(first, "total_pnodes", 0)
    last_count = safe_get(last, "total_pnodes", 0)
    node_growth = last_count - first_count
    node_growth_pct = (node_growth / first_count * 100) if first_count > 0 else 0
    
    # Storage growth
    first_storage = safe_get(first, "total_storage_committed", 0)
    last_storage = safe_get(last, "total_storage_committed", 0)
    storage_growth = last_storage - first_storage
    storage_growth_pct = (storage_growth / first_storage * 100) if first_storage > 0 else 0
    
    # Network health trends
    first_peers = safe_get(first, "avg_peer_count", 0)
    last_peers = safe_get(last, "avg_peer_count", 0)
    peer_change = last_peers - first_peers
    
    # Version stability (fewer versions = more stable)
    first_versions = len(first.get("version_distribution", {}))
    last_versions = len(last.get("version_distribution", {}))
    
    return {
        "history": history,
        "summary": {
            "data_points": len(history),
            "time_range_hours": hours,
            "start_timestamp": safe_get(first, "timestamp", 0),
            "end_timestamp": safe_get(last, "timestamp", 0),
            "start_time_readable": first.get("timestamp_readable", ""),
            "end_time_readable": last.get("timestamp_readable", ""),
            
            "node_growth": {
                "start_count": first_count,
                "end_count": last_count,
                "growth": node_growth,
                "growth_percent": round(node_growth_pct, 2),
                "trend": "growing" if node_growth > 0 else "declining" if node_growth < 0 else "stable"
            },
            
            "storage_growth": {
                "start_committed": first_storage,
                "end_committed": last_storage,
                "growth": storage_growth,
                "growth_percent": round(storage_growth_pct, 2),
                "trend": "growing" if storage_growth > 0 else "declining" if storage_growth < 0 else "stable"
            },
            
            "network_health": {
                "start_avg_peers": round(first_peers, 2),
                "end_avg_peers": round(last_peers, 2),
                "peer_change": round(peer_change, 2),
                "connectivity_trend": "improving" if peer_change > 0 else "declining" if peer_change < 0 else "stable"
            },
            
            "version_stability": {
                "start_version_count": first_versions,
                "end_version_count": last_versions,
                "stability": "improving" if last_versions < first_versions else "fragmenting" if last_versions > first_versions else "stable"
            }
        },
        "timestamp": now
    }


@app.get("/network/growth", summary="Network growth metrics")
async def get_network_growth(
    hours: int = Query(24, ge=1, le=720)
):
    """
    Calculate network growth by comparing current state to N hours ago.
    
    Provides a quick snapshot of network changes without full history.
    
    **NEW ENDPOINT** - Phase 4
    
    Parameters:
    - hours: How many hours back to compare (default 24, max 720)
    """
    growth = get_growth_metrics(hours)
    
    return {
        "growth_metrics": growth,
        "timestamp": int(time.time())
    }


@app.get("/network/analytics", summary="Advanced network analytics")
async def get_network_analytics():
    """
    Comprehensive network analytics combining multiple data sources.
    
    **NEW ENDPOINT** - Phase 4
    
    Provides:
    - Current state summary
    - 24h growth metrics
    - 7-day growth metrics
    - Version distribution analysis
    - Storage utilization trends
    - Network connectivity health
    """
    # Get current snapshot
    snapshot = nodes_current.find_one({"_id": "snapshot"})
    if not snapshot or "data" not in snapshot:
        return JSONResponse(
            jsonrpc_error("Snapshot not available", INTERNAL_ERROR),
            status_code=503
        )
    
    data = snapshot["data"]
    summary = data.get("summary", {})
    
    # Get growth metrics for different time periods
    growth_24h = get_growth_metrics(24)
    growth_7d = get_growth_metrics(168)  # 7 days
    
    # Analyze current state
    pnodes = data.get("merged_pnodes_unique", [])
    
    # Version analysis
    version_dist = {}
    latest_version_count = 0
    outdated_count = 0
    
    for pnode in pnodes:
        v = pnode.get("version") or "unknown"
        version_dist[v] = version_dist.get(v, 0) + 1
        
        if v == "0.7.0":  # Latest version
            latest_version_count += 1
        elif v and v.startswith("0.6"):
            outdated_count += 1
    
    total_nodes = len(pnodes)
    version_compliance_pct = (
        (latest_version_count / total_nodes * 100) 
        if total_nodes > 0 else 0
    )
    
    # Storage analysis
    storage_buckets = {
        "empty": 0,        # 0-10%
        "low": 0,          # 10-30%
        "optimal": 0,      # 30-70%
        "high": 0,         # 70-90%
        "critical": 0      # 90-100%
    }
    
    for pnode in pnodes:
        usage = pnode.get("storage_usage_percent") or 0
        if usage < 10:
            storage_buckets["empty"] += 1
        elif usage < 30:
            storage_buckets["low"] += 1
        elif usage < 70:
            storage_buckets["optimal"] += 1
        elif usage < 90:
            storage_buckets["high"] += 1
        else:
            storage_buckets["critical"] += 1
    
    # Network connectivity analysis
    peer_count_dist = {
        "isolated": 0,     # 0-1 peers
        "weak": 0,         # 2 peers
        "good": 0,         # 3-4 peers
        "excellent": 0     # 5+ peers
    }
    
    for pnode in pnodes:
        peer_count = len(pnode.get("peer_sources") or [])
        if peer_count <= 1:
            peer_count_dist["isolated"] += 1
        elif peer_count == 2:
            peer_count_dist["weak"] += 1
        elif peer_count <= 4:
            peer_count_dist["good"] += 1
        else:
            peer_count_dist["excellent"] += 1
    
    # Public vs Private ratio
    public_count = sum(1 for p in pnodes if p.get("is_public"))
    private_count = total_nodes - public_count
    
    return {
        "current_state": {
            "total_pnodes": total_nodes,
            "public_nodes": public_count,
            "private_nodes": private_count,
            "public_ratio_percent": round((public_count / total_nodes * 100) if total_nodes > 0 else 0, 2)
        },
        
        "growth": {
            "24_hours": growth_24h,
            "7_days": growth_7d
        },
        
        "version_analysis": {
            "distribution": version_dist,
            "latest_version": "0.7.0",
            "latest_version_count": latest_version_count,
            "outdated_count": outdated_count,
            "compliance_percent": round(version_compliance_pct, 2),
            "fragmentation_index": len(version_dist),
            "health": "good" if version_compliance_pct > 70 else "fair" if version_compliance_pct > 50 else "poor"
        },
        
        "storage_analysis": {
            "distribution": storage_buckets,
            "optimal_nodes": storage_buckets["optimal"],
            "optimal_percent": round((storage_buckets["optimal"] / total_nodes * 100) if total_nodes > 0 else 0, 2),
            "critical_nodes": storage_buckets["critical"],
            "health": "good" if storage_buckets["optimal"] > storage_buckets["critical"] else "fair"
        },
        
        "connectivity_analysis": {
            "distribution": peer_count_dist,
            "well_connected": peer_count_dist["good"] + peer_count_dist["excellent"],
            "well_connected_percent": round(
                ((peer_count_dist["good"] + peer_count_dist["excellent"]) / total_nodes * 100) 
                if total_nodes > 0 else 0, 
                2
            ),
            "isolated_nodes": peer_count_dist["isolated"],
            "health": "good" if peer_count_dist["isolated"] < total_nodes * 0.1 else "fair"
        },
        
        "recommendations": generate_network_recommendations(
            version_compliance_pct,
            storage_buckets,
            peer_count_dist,
            total_nodes
        ),
        
        "timestamp": int(time.time())
    }


def generate_network_recommendations(version_compliance, storage_buckets, peer_dist, total_nodes):
    """Generate actionable recommendations based on analytics."""
    recommendations = []
    
    # Version recommendations
    if version_compliance < 70:
        recommendations.append({
            "category": "version",
            "severity": "high" if version_compliance < 50 else "medium",
            "message": f"Only {round(version_compliance, 1)}% of nodes are on the latest version",
            "action": "Encourage operators to upgrade to v0.7.0"
        })
    
    # Storage recommendations
    if storage_buckets.get("critical", 0) > total_nodes * 0.1:
        recommendations.append({
            "category": "storage",
            "severity": "high",
            "message": f"{storage_buckets['critical']} nodes at critical storage capacity (>90%)",
            "action": "Monitor these nodes closely or increase storage allocation"
        })
    
    if storage_buckets.get("empty", 0) > total_nodes * 0.3:
        recommendations.append({
            "category": "storage",
            "severity": "low",
            "message": f"{storage_buckets['empty']} nodes are underutilized (<10% usage)",
            "action": "Network may be over-provisioned or needs more usage"
        })
    
    # Connectivity recommendations
    if peer_dist.get("isolated", 0) > total_nodes * 0.1:
        recommendations.append({
            "category": "connectivity",
            "severity": "high",
            "message": f"{peer_dist['isolated']} nodes have weak connectivity (≤1 peer)",
            "action": "Check network configuration and gossip protocol health"
        })
    
    if not recommendations:
        recommendations.append({
            "category": "general",
            "severity": "info",
            "message": "Network health is good",
            "action": "Continue monitoring"
        })
    
    return recommendations


@app.get("/node/{address:path}/history", summary="Get node historical data")
async def get_node_history_endpoint(address: str, days: int = Query(30, ge=1, le=90)):
    """
    Get historical data for a specific node.
    
    **PLACEHOLDER** - Phase 5 feature
    
    Currently returns placeholder message. Per-node historical tracking
    will be implemented in Phase 5.
    
    Parameters:
    - address: Node address (IP:port)
    - days: How many days of history (max 90)
    """
    result = get_node_history(address, days)
    
    if not result.get("available"):
        return JSONResponse(
            {
                "address": address,
                "available": False,
                "message": result.get("message"),
                "note": result.get("note"),
                "planned_for": "Phase 5",
                "alternative": "Use /network/history for network-wide trends"
            },
            status_code=200  # Not an error, just not implemented yet
        )
    
    return result