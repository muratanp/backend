# app/fetcher.py
import httpx
import time
import asyncio
import ipaddress
import logging
from joblib import Memory
from .db import (
    nodes_current, 
    upsert_registry, 
    mark_node_status, 
    save_snapshot_history, 
    track_gossip_changes,
    save_node_snapshot,
    prune_old_node_history  
)
from .config import CACHE_TTL, IP_NODES  # FIXED: Import from config

# -------------------------------
# Logging setup
# -------------------------------
logger = logging.getLogger("fetcher")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


memory = Memory(location=".cache", verbose=0)

# -------------------------------
# Unified RPC error formatter
# -------------------------------
def rpc_error(message: str, ip: str, method: str):
    """
    Returns a standard RPC error response dictionary.
    """
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32000,
            "message": "RPC Request Failed",
            "details": {
                "ip": ip,
                "method": method,
                "reason": message
            }
        }
    }

# -------------------------------
# Synchronous RPC caller (IP or host:port)
# -------------------------------
def prpc_sync(ip_or_addr: str, method: str, timeout: float = 3.0):
    """
    Perform a synchronous RPC call to a node.

    ip_or_addr may be '1.2.3.4' or '1.2.3.4:9001'.
    Returns JSON response or rpc_error dict.
    """
    if ":" in str(ip_or_addr):
        host, port = str(ip_or_addr).rsplit(":", 1)
    else:
        host, port = str(ip_or_addr), "6000"

    try:
        ipaddress.ip_address(host)
    except Exception:
        # allow hostnames; skip strict IP validation
        pass

    url = f"http://{host}:{port}/rpc"
    payload = {"jsonrpc": "2.0", "method": method, "id": 1}

    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            try:
                return r.json()
            except ValueError:
                logger.warning(f"Invalid JSON from {host}:{port} method {method}")
                return rpc_error("Invalid JSON response", f"{host}:{port}", method)
    except httpx.RequestError as e:
        logger.warning(f"HTTP request failed for {host}:{port} method {method}: {e}")
        return rpc_error(f"HTTP request failed: {str(e)}", f"{host}:{port}", method)
    except Exception as e:
        logger.exception(f"Unexpected error for {host}:{port} method {method}")
        return rpc_error(f"Unexpected error: {str(e)}", f"{host}:{port}", method)

# -------------------------------
# Cache wrapper
# -------------------------------
@memory.cache
def cached_call(ip: str, method: str, timestamp: int):
    """
    Cache RPC calls using joblib.

    Keeps the cache key stable with timestamp to avoid stale results.
    """
    return prpc_sync(ip, method)

# -------------------------------
# Background aggregation worker
# -------------------------------
def fetch_all_nodes_background():
    """
    Starts a background worker that:
    - Fetches get-version, get-stats and get-pods-with-stats
    - Builds snapshot saved to nodes_current (pnodes_snapshot)
    - Updates persistent registry (pnodes_registry) using ADDRESS as primary key
    - Updates status (pnodes_status) using ADDRESS as primary key
    - Saves historical snapshots

    This function starts the worker and returns immediately.
    """
    async def worker():
        while True:
            logger.info("Starting aggregation loop")
            timestamp = int(time.time() // CACHE_TTL)
            merged_pods = []               # raw concatenation of all pods (duplicates allowed)
            results = {}                   # per-node results (with pods_raw and pods)

            async def fetch_node(ip):
                """
                Fetch data from a single node concurrently:
                - version
                - stats
                - pods (with stats if available, fallback to legacy)
                """
                version_task = asyncio.to_thread(cached_call, ip, "get-version", timestamp)
                stats_task = asyncio.to_thread(cached_call, ip, "get-stats", timestamp)
                pods_with_stats_task = asyncio.to_thread(cached_call, ip, "get-pods-with-stats", timestamp)

                version, stats, pods_with_stats = await asyncio.gather(
                    version_task, stats_task, pods_with_stats_task
                )

                pods_result = pods_with_stats
                if isinstance(pods_with_stats, dict) and pods_with_stats.get("error"):
                    pods_result = await asyncio.to_thread(cached_call, ip, "get-pods", timestamp)

                pods_list = []
                node_total_count = None
                if isinstance(pods_result, dict):
                    node_total_count = pods_result.get("result", {}).get("total_count")
                    pods_list = pods_result.get("result", {}).get("pods", [])
                elif isinstance(pods_result, list):
                    pods_list = pods_result

                # build per-node entry
                results[ip] = {
                    "metadata": {
                        "total_bytes": stats.get("result", {}).get("total_bytes", 0),
                        "total_pages": stats.get("result", {}).get("total_pages", 0),
                        "last_updated": stats.get("result", {}).get("last_updated", int(time.time())),
                        "file_size": stats.get("result", {}).get("file_size", 0)
                    },
                    "stats": {
                        "cpu_percent": stats.get("result", {}).get("cpu_percent", 0),
                        "ram_used": stats.get("result", {}).get("ram_used", 0),
                        "ram_total": stats.get("result", {}).get("ram_total", 0),
                        "uptime": stats.get("result", {}).get("uptime", 0),
                        "packets_received": stats.get("result", {}).get("packets_received", 0),
                        "packets_sent": stats.get("result", {}).get("packets_sent", 0),
                        "active_streams": stats.get("result", {}).get("active_streams", 0)
                    },
                    "pods_raw": pods_result,   # keep original RPC response for debugging
                    "pods_total_count": node_total_count,
                    "pods": [
                        {
                            "address": p.get("address") or p.get("pubkey") or p.get("address"),
                            "pubkey": p.get("pubkey") or p.get("address"),
                            "is_public": p.get("is_public", None),
                            "rpc_port": p.get("rpc_port", None),
                            "storage_committed": p.get("storage_committed"),
                            "storage_used": p.get("storage_used"),
                            "storage_usage_percent": p.get("storage_usage_percent"),
                            "uptime": p.get("uptime") or p.get("uptime_seconds"),
                            "version": p.get("version"),
                            "last_seen": p.get("last_seen"),
                            "last_seen_timestamp": p.get("last_seen_timestamp"),
                            "source_ip": ip
                        }
                        for p in pods_list
                        if p and (p.get("address") or p.get("pubkey"))
                    ]
                }

                
                # add all pods from this node to merged_pods (raw merged list)
                merged_pods.extend(results[ip]["pods"])

            # fetch all nodes concurrently
            await asyncio.gather(*(fetch_node(ip) for ip in IP_NODES))

            # Build merged_pnodes_unique with peer_sources (DEDUP BY ADDRESS)
            unique = {}
            for p in merged_pods:
                key = p.get("address")  # PRIMARY KEY: address
                if not key:
                    continue

                if key not in unique:
                    # initialize unique entry and track peer_sources
                    unique[key] = {
                        **p,
                        "peer_sources": [p.get("source_ip")] if p.get("source_ip") else [],
                    }
                else:
                    # update peer_sources and prefer latest last_seen_timestamp
                    existing = unique[key]
                    src = p.get("source_ip")
                    if src and src not in existing["peer_sources"]:
                        existing["peer_sources"].append(src)

                    # prefer the pod with the latest last_seen_timestamp (if present)
                    if p.get("last_seen_timestamp", 0) > existing.get("last_seen_timestamp", 0):
                        # keep source peer_sources aggregated
                        peer_sources = existing.get("peer_sources", [])
                        unique[key] = {**p, "peer_sources": peer_sources}

            merged_unique = list(unique.values())

            # Update registry for each unique pod using ADDRESS as primary key
            for pod in merged_unique:
                address = pod.get("address")  # PRIMARY KEY
                if not address:
                    continue
                
                pubkey = pod.get("pubkey") or pod.get("address")
                last_seen_ts = pod.get("last_seen_timestamp") or int(time.time())
                peer_sources = pod.get("peer_sources", []) or []
                is_public_flag = pod.get("is_public")
                rpc_port = pod.get("rpc_port") or 6000

                registry_entry = {
                    "address": address,  # PRIMARY KEY
                    "pubkey": pubkey,
                    "last_seen": last_seen_ts,
                    "last_ip": peer_sources[0] if peer_sources else None,
                    "rpc_port": rpc_port,
                    "is_public": bool(is_public_flag) if is_public_flag is not None else False,  # FIXED: Match RPC field name
                    "storage_committed": pod.get("storage_committed"),
                    "storage_used": pod.get("storage_used"),
                    "storage_usage_percent": pod.get("storage_usage_percent"),
                    "uptime": pod.get("uptime"),
                    "version": pod.get("version"),
                    "last_checked": int(time.time()),
                    "source_ips": peer_sources,   # persist sources that reported this pod
                }

                try:
                    upsert_registry(address, registry_entry)  # Use address
                    if registry_entry["is_public"]:
                        mark_node_status(address, "public", {"last_ip": registry_entry["last_ip"], "last_seen": last_seen_ts})
                    else:
                        mark_node_status(address, "private", {"last_ip": registry_entry["last_ip"], "last_seen": last_seen_ts})
                except Exception as e:
                    logger.error(f"Registry write error for {address}: {e}")

            # Snapshot summary and storage
            total_nodes = len(IP_NODES)
            total_pnodes = len(merged_unique)
            total_pnodes_raw = len(merged_pods)
            total_bytes_processed = sum(n["metadata"]["total_bytes"] for n in results.values()) if results else 0
            avg_cpu_percent = (sum(n["stats"]["cpu_percent"] for n in results.values()) / total_nodes) if total_nodes and results else 0
            avg_ram_used_percent = (sum((n["stats"]["ram_used"] / max(n["stats"]["ram_total"], 1) * 100) for n in results.values()) / total_nodes) if total_nodes and results else 0
            total_active_streams = sum(n["stats"]["active_streams"] for n in results.values()) if results else 0
            last_updated = int(time.time())

            snapshot = {
                "summary": {
                    "total_nodes": total_nodes,
                    "total_pnodes": total_pnodes,
                    "total_pnodes_raw": total_pnodes_raw,
                    "total_bytes_processed": total_bytes_processed,
                    "avg_cpu_percent": round(avg_cpu_percent, 2),
                    "avg_ram_used_percent": round(avg_ram_used_percent, 2),
                    "total_active_streams": total_active_streams,
                    "last_updated": last_updated
                },
                "nodes": results,
                "merged_pnodes_raw": merged_pods,
                "merged_pnodes_unique": merged_unique
            }

            # Track gossip consistency BEFORE saving snapshot
            # This compares current merged_unique to previous snapshot
            try:
                gossip_summary = track_gossip_changes(merged_unique)
                logger.info(
                    f"Gossip consistency tracked: "
                    f"+{gossip_summary['new_appearances']} appeared, "
                    f"-{gossip_summary['disappearances']} dropped"
                )
            except Exception as e:
                logger.error(f"❌ Gossip tracking failed: {e}")
                # Don't fail the entire snapshot if gossip tracking fails


            # ============================================================================
            # SAVE PER-NODE HISTORY SNAPSHOTS
            # ============================================================================
            logger.info("💾 Saving per-node history snapshots...")
            for pod in merged_unique:
                address = pod.get("address")
                if not address:
                    continue
                try:
                    # Save individual node snapshot
                    save_node_snapshot(address, pod)
                except Exception as e:
                    logger.error(f"Failed to save node history for {address}: {e}")

                # Prune old node history (once per day, check if it's midnight)
                if time.localtime(last_updated).tm_hour == 0 and time.localtime(last_updated).tm_min < 2:
                    logger.info("🗑️  Running daily node history cleanup...")
                    try:
                        prune_old_node_history(days=30)
                    except Exception as e:
                        logger.error(f"Failed to prune node history: {e}")    


            # Save snapshot to MongoDB
            try:
                nodes_current.replace_one({"_id": "snapshot"}, {"_id": "snapshot", "data": snapshot}, upsert=True)
                logger.info("✅ Snapshot updated successfully")
                
                # Save snapshot history
                save_snapshot_history()
                
            except Exception as e:
                logger.error(f"MongoDB write error: {e}")

            await asyncio.sleep(CACHE_TTL)
            logger.info("Aggregation loop completed, sleeping until next iteration")

    # Start worker
    try:
        loop = asyncio.get_running_loop()
        asyncio.create_task(worker())
    except RuntimeError:
        import threading
        threading.Thread(target=lambda: asyncio.run(worker()), daemon=True).start()