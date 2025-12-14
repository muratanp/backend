# app/db.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .config import MONGO_URI, MONGO_DB, CACHE_TTL
import time
import logging

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client[MONGO_DB]

# Collections
nodes_current = db["pnodes_snapshot"]        # Single snapshot document
pnodes_registry = db["pnodes_registry"]      # Persistent registry (one doc per ADDRESS)
pnodes_status = db["pnodes_status"]          # Lightweight status store (ADDRESS -> status)
pnodes_snapshots = db["pnodes_snapshots"]    # Historical snapshots (time-series)


# Optional ping
try:
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print("❌ MongoDB connection error:", e)


# -----------------------------
# Database Indexes Setup
# -----------------------------
def setup_indexes():
    """
    Create proper indexes for performance.
    Call this once on startup.
    """
    try:
        # Registry: PRIMARY KEY is address (unique)
        pnodes_registry.create_index([("address", 1)], unique=True)
        logger.info("✅ Created unique index on pnodes_registry.address")
        
        # Registry: Secondary index on pubkey (for operator queries)
        pnodes_registry.create_index([("pubkey", 1)])
        logger.info("✅ Created index on pnodes_registry.pubkey")
        
        # Registry: Index on last_seen for online/offline queries
        pnodes_registry.create_index([("last_seen", -1)])
        logger.info("✅ Created index on pnodes_registry.last_seen")
        
        # Status: PRIMARY KEY is address (unique)
        pnodes_status.create_index([("address", 1)], unique=True)
        logger.info("✅ Created unique index on pnodes_status.address")
        
        # Snapshots: Index on timestamp for time-series queries
        pnodes_snapshots.create_index([("timestamp", -1)])
        logger.info("✅ Created index on pnodes_snapshots.timestamp")
        
        logger.info("✅ All database indexes created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")


# -----------------------------
# Mongo Sanitizer
# -----------------------------
def sanitize_mongo(doc: dict):
    """Convert MongoDB documents into JSON-safe dictionaries."""
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# -----------------------------
# Registry helpers (FIXED - Use ADDRESS as primary key)
# -----------------------------
def upsert_registry(address: str, entry: dict):
    """
    Insert or update a persistent registry entry for a pNode.
    Uses ADDRESS (IP:port) as unique key, NOT pubkey.
    
    Args:
        address: IP:port string (e.g., "109.199.96.218:9001")
        entry: dict with node data
    """
    now = int(time.time())
    entry.setdefault("last_checked", now)
    entry.setdefault("last_seen", entry.get("last_seen", now))
    entry.setdefault("first_seen", entry.get("first_seen", entry.get("last_seen", now)))
    entry.setdefault("source_ips", entry.get("source_ips", []))

    update_doc = {
        "$set": {k: v for k, v in entry.items() if k not in ("source_ips", "first_seen")},
        "$min": {"first_seen": entry["first_seen"]},
        "$setOnInsert": {"created_at": now},
    }

    if entry.get("source_ips"):
        update_doc["$addToSet"] = {"source_ips": {"$each": entry.get("source_ips", [])}}

    # KEY CHANGE: Use address as unique identifier
    pnodes_registry.update_one({"address": address}, update_doc, upsert=True)


def mark_node_status(address: str, status: str, details: dict = None):
    """
    Mark a node's lightweight status.
    Uses ADDRESS as key.
    
    Args:
        address: IP:port string
        status: one of 'public', 'private', 'offline', 'unknown'
        details: optional dict with extra fields (last_checked, last_ip, reason)
    """
    if details is None:
        details = {}

    now = int(time.time())
    doc = {
        "address": address,  # Changed from pubkey
        "status": status,
        "updated_at": now
    }
    doc.update(details)
    pnodes_status.update_one({"address": address}, {"$set": doc}, upsert=True)


# -----------------------------
# SAFE JSON GETTERS (FIXED - Use ADDRESS)
# -----------------------------
def get_registry(limit: int = 100, skip: int = 0):
    """
    Return JSON-safe registry entries (paged).
    """
    cursor = (
        pnodes_registry
        .find()
        .sort("last_seen", -1)
        .skip(skip)
        .limit(limit)
    )

    items = []
    now = int(time.time())
    for doc in cursor:
        doc = sanitize_mongo(doc)
        # Consider online if seen within last 2 * CACHE_TTL seconds
        doc["is_online"] = (now - doc.get("last_seen", 0)) <= 2 * CACHE_TTL
        items.append(doc)

    return {
        "count": len(items),
        "items": items
    }


def get_registry_entry(address: str):
    """
    Return a single sanitized registry entry for ADDRESS.
    
    Args:
        address: IP:port string (e.g., "109.199.96.218:9001")
    """
    doc = pnodes_registry.find_one({"address": address})
    return sanitize_mongo(doc)


def get_registry_entries_by_pubkey(pubkey: str):
    """
    Get all nodes operated by the same pubkey.
    Useful for operator analytics.
    
    Args:
        pubkey: Operator's public key
        
    Returns:
        List of sanitized registry entries
    """
    cursor = pnodes_registry.find({"pubkey": pubkey})
    return [sanitize_mongo(doc) for doc in cursor]


def get_status(address: str):
    """
    Return sanitized status entry for ADDRESS.
    
    Args:
        address: IP:port string
    """
    doc = pnodes_status.find_one({"address": address})
    return sanitize_mongo(doc)


# -----------------------------
# Prune old nodes
# -----------------------------
def prune_old_nodes(days: int = 90):
    """
    Delete registry entries not seen in `days` days.
    Returns dict with deleted_count.
    """
    threshold = int(time.time()) - days * 24 * 3600
    res = pnodes_registry.delete_many({"last_seen": {"$lt": threshold}})
    return {"deleted_count": res.deleted_count}


# -----------------------------
# Historical Snapshot Tracking
# -----------------------------
def save_snapshot_history():
    """
    Enhanced snapshot history with more detailed metrics.
    Saves lightweight summary every CACHE_TTL seconds.
    Keeps 30 days of data for trend analysis.
    """
    snapshot = nodes_current.find_one({"_id": "snapshot"})
    if not snapshot or "data" not in snapshot:
        return
    
    data = snapshot["data"]
    timestamp = int(time.time())
    
    # Extract summary
    summary = data.get("summary", {})
    
    # Calculate version distribution
    version_counts = {}
    online_by_version = {}
    public_count = 0
    private_count = 0
    
    for pnode in data.get("merged_pnodes_unique", []):
        v = pnode.get("version") or "unknown"
        version_counts[v] = version_counts.get(v, 0) + 1
        
        # Track online status by version (for health analysis)
        if v not in online_by_version:
            online_by_version[v] = {"total": 0, "online": 0}
        online_by_version[v]["total"] += 1
        
        # Count public vs private
        if pnode.get("is_public"):
            public_count += 1
        else:
            private_count += 1
    
    # Calculate storage metrics
    total_storage_committed = 0
    total_storage_used = 0
    storage_usage_samples = []
    
    for pnode in data.get("merged_pnodes_unique", []):
        committed = pnode.get("storage_committed") or 0
        used = pnode.get("storage_used") or 0
        usage_pct = pnode.get("storage_usage_percent") or 0
        
        total_storage_committed += committed
        total_storage_used += used
        if usage_pct > 0:
            storage_usage_samples.append(usage_pct)
    
    # Calculate average storage usage
    avg_storage_usage = (
        sum(storage_usage_samples) / len(storage_usage_samples) 
        if storage_usage_samples else 0
    )
    
    # Calculate peer connectivity stats
    peer_count_samples = []
    for pnode in data.get("merged_pnodes_unique", []):
        peer_sources = pnode.get("peer_sources") or []
        peer_count_samples.append(len(peer_sources))
    
    avg_peer_count = (
        sum(peer_count_samples) / len(peer_count_samples)
        if peer_count_samples else 0
    )
    
    # Build enhanced history entry
    history_entry = {
        "timestamp": timestamp,
        
        # Node counts
        "total_pnodes": summary.get("total_pnodes", 0),
        "total_ip_nodes": len(data.get("nodes", {})),
        "public_pnodes": public_count,
        "private_pnodes": private_count,
        
        # System metrics
        "avg_cpu_percent": summary.get("avg_cpu_percent", 0),
        "avg_ram_used_percent": summary.get("avg_ram_used_percent", 0),
        "total_active_streams": summary.get("total_active_streams", 0),
        "total_bytes_processed": summary.get("total_bytes_processed", 0),
        
        # Storage metrics
        "total_storage_committed": total_storage_committed,
        "total_storage_used": total_storage_used,
        "avg_storage_usage_percent": round(avg_storage_usage, 2),
        "storage_utilization_ratio": round(
            (total_storage_used / total_storage_committed * 100) 
            if total_storage_committed > 0 else 0, 
            2
        ),
        
        # Network metrics
        "avg_peer_count": round(avg_peer_count, 2),
        "version_distribution": version_counts,
        "version_diversity_index": len(version_counts),  # Higher = more fragmented
        
        # Growth indicators (will be calculated by comparing to previous)
        "timestamp_readable": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    }
    
    try:
        pnodes_snapshots.insert_one(history_entry)
        logger.info(f"✅ Enhanced snapshot history saved (timestamp: {timestamp})")
    except Exception as e:
        logger.error(f"❌ Failed to save snapshot history: {e}")
    
    # Prune old snapshots (keep 30 days)
    thirty_days_ago = timestamp - (30 * 86400)
    try:
        result = pnodes_snapshots.delete_many({"timestamp": {"$lt": thirty_days_ago}})
        if result.deleted_count > 0:
            logger.info(f"🗑️  Pruned {result.deleted_count} old snapshot(s)")
    except Exception as e:
        logger.error(f"❌ Failed to prune old snapshots: {e}")


def get_growth_metrics(hours: int = 24):
    """
    Calculate growth metrics by comparing current state to N hours ago.
    
    Args:
        hours: How many hours back to compare
        
    Returns:
        dict with growth metrics
    """
    now = int(time.time())
    past_time = now - (hours * 3600)
    
    # Get current snapshot
    current = pnodes_snapshots.find_one({"timestamp": {"$lte": now}}, sort=[("timestamp", -1)])
    
    # Get snapshot from N hours ago (closest match)
    past = pnodes_snapshots.find_one({"timestamp": {"$lte": past_time}}, sort=[("timestamp", -1)])
    
    if not current or not past:
        return {
            "available": False,
            "message": "Insufficient historical data for growth calculation"
        }
    
    # Calculate changes
    node_growth = current.get("total_pnodes", 0) - past.get("total_pnodes", 0)
    storage_growth = current.get("total_storage_committed", 0) - past.get("total_storage_committed", 0)
    
    # Calculate percentage changes
    node_growth_pct = (
        (node_growth / past.get("total_pnodes", 1) * 100)
        if past.get("total_pnodes", 0) > 0 else 0
    )
    
    storage_growth_pct = (
        (storage_growth / past.get("total_storage_committed", 1) * 100)
        if past.get("total_storage_committed", 0) > 0 else 0
    )
    
    return {
        "available": True,
        "period_hours": hours,
        "comparison": {
            "start_time": past.get("timestamp"),
            "end_time": current.get("timestamp"),
            "start_time_readable": past.get("timestamp_readable"),
            "end_time_readable": current.get("timestamp_readable")
        },
        "nodes": {
            "start_count": past.get("total_pnodes", 0),
            "end_count": current.get("total_pnodes", 0),
            "growth": node_growth,
            "growth_percent": round(node_growth_pct, 2)
        },
        "storage": {
            "start_committed": past.get("total_storage_committed", 0),
            "end_committed": current.get("total_storage_committed", 0),
            "growth": storage_growth,
            "growth_percent": round(storage_growth_pct, 2)
        },
        "network_health": {
            "start_peer_count": past.get("avg_peer_count", 0),
            "end_peer_count": current.get("avg_peer_count", 0),
            "peer_count_change": round(
                current.get("avg_peer_count", 0) - past.get("avg_peer_count", 0), 
                2
            )
        }
    }


def get_node_history(address: str, days: int = 30):
    """
    Get historical data for a specific node.
    
    NOTE: This requires per-node historical tracking which isn't implemented yet.
    This is a placeholder for Phase 5.
    
    Args:
        address: Node address
        days: How many days of history
        
    Returns:
        dict with node history or placeholder message
    """
    return {
        "address": address,
        "available": False,
        "message": "Per-node historical tracking not yet implemented",
        "note": "Currently only network-wide snapshots are tracked. Per-node history is planned for Phase 5."
    }