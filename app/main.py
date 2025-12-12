from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.utils.jsonrpc import jsonrpc_error, INTERNAL_ERROR
from app.fetcher import fetch_all_nodes_background
from .db import nodes_current, get_registry, get_registry_entry, get_status, prune_old_nodes, sanitize_mongo, CACHE_TTL, pnodes_registry
import asyncio, time


app = FastAPI(
    title="PNode Aggregation API",
    description="Aggregates version, stats, and PNode lists from multiple IP nodes with caching.",
    version="2.0.0"
)

# --- CORS setup ---
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup background task ---
@app.on_event("startup")
async def startup_event():
    # Start the background fetch task to regularly update MongoDB
    fetch_all_nodes_background()

# --- API endpoints ---
@app.get("/all-nodes", summary="Aggregated PNode data from MongoDB")
async def get_all_nodes(version: str = None ):
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


@app.get("/", summary="API Overview and Endpoints")
async def root():
    """
    PNode Aggregation API Root

    This API aggregates data from multiple Xandeum PNodes via their PRPC endpoints.
    The `/all-nodes` endpoint returns RAW node data including:
    - Version information
    - Stats
    - Pod lists

    The background worker updates the snapshot in MongoDB every configured interval.

    Available Endpoints:
    - `/all-nodes` : Returns the latest raw snapshot of all nodes
    - `/docs`      : FastAPI interactive Swagger docs
    - `/redoc`     : ReDoc documentation
    """
    return {
        "api_name": "PNode Aggregation API",
        "description": (
            "Aggregates version, stats, and PNode lists from multiple Xandeum IP nodes "
            "using PRPC. All data returned from `/all-nodes` is RAW as received from the nodes."
        ),
        "endpoints": {
            "/all-nodes": "Latest snapshot of all IP nodes",
            "/registry": "Paged list of all known pNodes (persistent registry)",
            "/registry/{pubkey}": "Fetch a single pNode's registry data and status",
            "/prune": "Remove old inactive nodes from the registry",
            "/docs": "Swagger UI",
            "/redoc": "ReDoc documentation"
        },
        "note": "Data is updated in the background every CACHE_TTL=30 seconds and stored in MongoDB."
    }

@app.get("/registry", summary="List persistent pNode registry")
async def registry_list(limit: int = Query(100, ge=1, le=1000), skip: int = 0):
    """
    Returns the pnodes registry (paged).
    """
    try:
        items = get_registry(limit=limit, skip=skip)
        return items
    except Exception as e:
        return JSONResponse(jsonrpc_error(f"Failed to read registry: {str(e)}", INTERNAL_ERROR), status_code=500)


@app.get("/registry/{pubkey}", summary="Get single registry entry")
async def registry_get(pubkey: str):
    try:
        entry = get_registry_entry(pubkey)
        if not entry:
            return JSONResponse(jsonrpc_error("Registry entry not found", INTERNAL_ERROR), status_code=404)
        status = get_status(pubkey)
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

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(jsonrpc_error("Internal server error", INTERNAL_ERROR))