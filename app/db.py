# app/db.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .config import MONGO_URI, MONGO_DB, CACHE_TTL
import time

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client[MONGO_DB]

# existing snapshot collection (single document snapshot)
nodes_current = db["pnodes_snapshot"]

# new registry + status collections
pnodes_registry = db["pnodes_registry"]        # persistent registry (one doc per pubkey)
pnodes_status = db["pnodes_status"]            # lightweight status store (pubkey -> status/info)


# Optional ping
try:
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print("❌ MongoDB connection error:", e)


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
# Registry helpers
# -----------------------------
def upsert_registry(pubkey: str, entry: dict):
    """
    Insert or update a persistent registry entry for a pNode.
    Uses pubkey as unique key.
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

    pnodes_registry.update_one({"pubkey": pubkey}, update_doc, upsert=True)


def mark_node_status(pubkey: str, status: str, details: dict = None):
    """
    Mark a node's lightweight status.
    status: one of 'public', 'private', 'offline', 'unknown'
    details: optional dict with extra fields (last_checked, last_ip, reason)
    """
    if details is None:
        details = {}

    now = int(time.time())
    doc = {
        "pubkey": pubkey,
        "status": status,
        "updated_at": now
    }
    doc.update(details)
    pnodes_status.update_one({"pubkey": pubkey}, {"$set": doc}, upsert=True)


# -----------------------------
# SAFE JSON GETTERS
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


def get_registry_entry(pubkey: str):
    """
    Return a single sanitized registry entry for pubkey.
    """
    doc = pnodes_registry.find_one({"pubkey": pubkey})
    return sanitize_mongo(doc)


def get_status(pubkey: str):
    """
    Return sanitized status entry.
    """
    doc = pnodes_status.find_one({"pubkey": pubkey})
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
