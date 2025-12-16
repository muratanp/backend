# app/scoring.py

def calculate_trust_score(pnode_data: dict) -> dict:
    """
    Trust Score (0-100)
    Based on: uptime, gossip presence, version, consistency
    """
    score = 0
    breakdown = {}
    
    # 1. Uptime (40 points)
    uptime_seconds = pnode_data.get("uptime", 0)
    uptime_days = uptime_seconds / 86400
    uptime_score = min(uptime_days / 30, 1.0) * 40
    breakdown["uptime"] = round(uptime_score, 2)
    score += uptime_score
    
    # 2. Gossip presence (30 points)
    peer_sources = pnode_data.get("peer_sources", [])
    peer_count = len(peer_sources)
    gossip_score = min(peer_count / 3, 1.0) * 30
    breakdown["gossip_presence"] = round(gossip_score, 2)
    score += gossip_score
    
    # 3. Version compliance (20 points)
    version = pnode_data.get("version", "")
    LATEST_VERSION = "0.7.0"
    if version == LATEST_VERSION:
        version_score = 20
    elif version and version.startswith("0.6"):
        version_score = 10
    else:
        version_score = 0
    breakdown["version_compliance"] = version_score
    score += version_score
    
    # 4. Gossip consistency (10 points)
    # If we track gossip_appearances/disappearances
    consistency = pnode_data.get("consistency_score", 1.0)
    consistency_score = consistency * 10
    breakdown["gossip_consistency"] = round(consistency_score, 2)
    score += consistency_score
    
    return {
        "score": round(score, 2),
        "breakdown": breakdown
    }


def calculate_capacity_score(pnode_data: dict) -> dict:
    """
    Capacity Score (0-100)
    Based on: storage committed, usage balance, growth trend
    """
    score = 0
    breakdown = {}
    
    # 1. Storage committed (30 points)
    storage_committed = pnode_data.get("storage_committed", 0)
    # Normalize: 100GB = full points
    committed_gb = storage_committed / (1024**3)
    committed_score = min(committed_gb / 100, 1.0) * 30
    breakdown["storage_committed"] = round(committed_score, 2)
    score += committed_score
    
    # 2. Usage balance (40 points)
    storage_usage = pnode_data.get("storage_usage_percent", 0)
    if 20 <= storage_usage <= 80:
        balance_score = 40
    elif storage_usage < 20:
        balance_score = (storage_usage / 20) * 40
    else:  # > 80%
        balance_score = ((100 - storage_usage) / 20) * 40
    breakdown["usage_balance"] = round(balance_score, 2)
    score += balance_score
    
    # 3. Growth trend (30 points)
    # Requires historical data - default to 15 if unavailable
    growth_trend = pnode_data.get("growth_trend", 0.5)  # 0-1 scale
    growth_score = growth_trend * 30
    breakdown["growth_trend"] = round(growth_score, 2)
    score += growth_score
    
    return {
        "score": round(score, 2),
        "breakdown": breakdown
    }


def calculate_stake_confidence(trust_score: float, capacity_score: float) -> dict:
    """
    Stake Confidence Rating
    Composite of Trust + Capacity
    """
    # Weight: 60% trust, 40% capacity
    composite = (trust_score * 0.6) + (capacity_score * 0.4)
    
    if composite >= 80:
        rating = "low_risk"
        color = "#10b981"  # green
    elif composite >= 60:
        rating = "medium_risk"
        color = "#f59e0b"  # yellow
    else:
        rating = "high_risk"
        color = "#ef4444"  # red
    
    return {
        "composite_score": round(composite, 2),
        "rating": rating,
        "color": color
    }


def calculate_all_scores(pnode_data: dict) -> dict:
    """
    Calculate all available scores for a pNode.
    """
    trust = calculate_trust_score(pnode_data)
    capacity = calculate_capacity_score(pnode_data)
    confidence = calculate_stake_confidence(trust["score"], capacity["score"])
    
    return {
        "trust": trust,
        "capacity": capacity,
        "stake_confidence": confidence,
        "performance": {
            "score": None,
            "status": "unavailable",
            "message": "Performance metrics (paging stats) not available via RPC"
        }
    }

"""
Performance scoring system for Xandeum pNodes.

Calculates quality scores to help stakers make informed decisions.
Based on available RPC data (NO paging stats available).

Implements 3-score system:
1. Trust Score (0-100) - uptime, gossip, version
2. Capacity Score (0-100) - storage metrics
3. Stake Confidence - composite risk rating
"""

import time
from typing import Dict, List

# Update this as new versions release
LATEST_VERSION = "0.8.0"


def calculate_trust_score(pnode_data: Dict) -> Dict:
    """
    Calculate Trust Score (0-100).
    
    Factors:
    - Uptime consistency (40 points)
    - Gossip presence (30 points) - based on peer_sources
    - Version compliance (20 points)
    - Gossip consistency (10 points)
    
    Args:
        pnode_data: Node data dict with fields:
            - uptime: seconds
            - peer_sources: list of IPs that see this node
            - version: string
            - consistency_score: float 0-1 (optional)
    
    Returns:
        dict with score and breakdown
    """
    score = 0
    breakdown = {}
    
    # 1. Uptime score (40 points max)
    uptime_seconds = pnode_data.get("uptime", 0)
    uptime_days = uptime_seconds / 86400
    # Full points if uptime > 30 days
    uptime_score = min(uptime_days / 30, 1.0) * 40
    breakdown["uptime"] = round(uptime_score, 2)
    score += uptime_score
    
    # 2. Gossip presence (30 points max)
    # peer_sources = list of IP nodes that reported seeing this pNode
    peer_sources = pnode_data.get("peer_sources", [])
    peer_count = len(peer_sources) if peer_sources else 0
    # Full points if seen by 3+ IP nodes
    gossip_score = min(peer_count / 3, 1.0) * 30
    breakdown["gossip_presence"] = round(gossip_score, 2)
    score += gossip_score
    
    # 3. Version compliance (20 points max)
    version = pnode_data.get("version", "")
    if version == LATEST_VERSION:
        version_score = 20
    elif version and version.startswith("0.6"):  # One version behind
        version_score = 10
    else:
        version_score = 0
    breakdown["version_compliance"] = version_score
    score += version_score
    
    # 4. Gossip consistency (10 points max)
    # Future: track gossip_appearances/disappearances
    # For now, default to full points if online
    consistency = pnode_data.get("consistency_score", 1.0)
    consistency_score = consistency * 10
    breakdown["gossip_consistency"] = round(consistency_score, 2)
    score += consistency_score
    
    return {
        "score": round(score, 2),
        "breakdown": breakdown
    }


def calculate_capacity_score(pnode_data: Dict) -> Dict:
    """
    Calculate Capacity Score (0-100).
    
    Factors:
    - Storage committed (30 points) - larger = more capacity
    - Usage balance (40 points) - optimal 20-80%
    - Growth trend (30 points) - requires historical data
    
    Args:
        pnode_data: Node data dict with fields:
            - storage_committed: bytes
            - storage_usage_percent: float
            - growth_trend: float 0-1 (optional, from historical)
    
    Returns:
        dict with score and breakdown
    """
    score = 0
    breakdown = {}
    
    # 1. Storage committed (30 points max)
    storage_committed = pnode_data.get("storage_committed", 0)
    # Normalize: 100GB = full points
    committed_gb = storage_committed / (1024**3)
    committed_score = min(committed_gb / 100, 1.0) * 30
    breakdown["storage_committed"] = round(committed_score, 2)
    score += committed_score
    
    # 2. Usage balance (40 points max)
    storage_usage = pnode_data.get("storage_usage_percent", 0)
    # Optimal range: 20-80% usage
    # Too low = underutilized, too high = risky/full
    if 20 <= storage_usage <= 80:
        balance_score = 40
    elif storage_usage < 20:
        # Penalize underutilization
        balance_score = (storage_usage / 20) * 40
    else:  # > 80%
        # Penalize being too full
        balance_score = ((100 - storage_usage) / 20) * 40
    breakdown["usage_balance"] = round(balance_score, 2)
    score += balance_score
    
    # 3. Growth trend (30 points max)
    # Requires historical data - default to 15 if unavailable
    growth_trend = pnode_data.get("growth_trend", 0.5)  # 0-1 scale
    growth_score = growth_trend * 30
    breakdown["growth_trend"] = round(growth_score, 2)
    score += growth_score
    
    return {
        "score": round(score, 2),
        "breakdown": breakdown
    }


def calculate_stake_confidence(trust_score: float, capacity_score: float) -> Dict:
    """
    Calculate Stake Confidence Rating.
    
    Composite of Trust + Capacity scores.
    Weight: 60% trust, 40% capacity
    
    Args:
        trust_score: Trust score 0-100
        capacity_score: Capacity score 0-100
    
    Returns:
        dict with composite_score, rating, and color
    """
    # Weight: 60% trust, 40% capacity
    composite = (trust_score * 0.6) + (capacity_score * 0.4)
    
    if composite >= 80:
        rating = "low_risk"
        color = "#10b981"  # green
        emoji = "🟢"
    elif composite >= 60:
        rating = "medium_risk"
        color = "#f59e0b"  # yellow
        emoji = "🟡"
    else:
        rating = "high_risk"
        color = "#ef4444"  # red
        emoji = "🔴"
    
    return {
        "composite_score": round(composite, 2),
        "rating": rating,
        "color": color,
        "emoji": emoji
    }


def calculate_all_scores(pnode_data: Dict) -> Dict:
    """
    Calculate all available scores for a pNode.
    
    Args:
        pnode_data: Complete node data with all fields
    
    Returns:
        dict with trust, capacity, stake_confidence, and performance status
    """
    trust = calculate_trust_score(pnode_data)
    capacity = calculate_capacity_score(pnode_data)
    confidence = calculate_stake_confidence(trust["score"], capacity["score"])
    
    return {
        "trust": trust,
        "capacity": capacity,
        "stake_confidence": confidence,
        "performance": {
            "score": None,
            "status": "unavailable",
            "message": "Performance metrics (paging stats) not available via RPC",
            "note": "Paging statistics only accessible via Pod Monitor dashboard (port 80)"
        }
    }


def calculate_network_health_score(all_nodes: List[Dict]) -> Dict:
    """
    Calculate overall network health based on all nodes.
    
    Factors:
    - Node availability (30%)
    - Version consistency (25%)
    - Average node quality (25%)
    - Network connectivity (20%)
    
    Args:
        all_nodes: List of all nodes (online + offline)
    
    Returns:
        dict with health_score, status, and factor breakdown
    """
    if not all_nodes:
        return {
            "health_score": 0,
            "status": "unknown",
            "factors": {}
        }
    
    online_nodes = [n for n in all_nodes if n.get("is_online", False)]
    total_nodes = len(all_nodes)
    online_count = len(online_nodes)
    
    factors = {}
    health_score = 0
    
    # Factor 1: Node availability (30%)
    availability_ratio = online_count / total_nodes if total_nodes > 0 else 0
    availability_score = availability_ratio * 30
    factors["availability"] = round(availability_score, 2)
    health_score += availability_score
    
    # Factor 2: Version consistency (25%)
    version_counts = {}
    for node in online_nodes:
        v = node.get("version", "unknown")
        version_counts[v] = version_counts.get(v, 0) + 1
    
    if version_counts:
        most_common_version_count = max(version_counts.values())
        version_consistency = most_common_version_count / online_count if online_count else 0
        version_score = version_consistency * 25
    else:
        version_score = 0
    factors["version_consistency"] = round(version_score, 2)
    health_score += version_score
    
    # Factor 3: Average node quality (25%)
    if online_nodes:
        total_quality = 0
        for node in online_nodes:
            scores = calculate_all_scores(node)
            node_quality = scores["stake_confidence"]["composite_score"]
            total_quality += node_quality
        avg_node_score = total_quality / online_count
        quality_score = (avg_node_score / 100) * 25
    else:
        quality_score = 0
    factors["node_quality"] = round(quality_score, 2)
    health_score += quality_score
    
    # Factor 4: Network connectivity (20%)
    if online_nodes:
        total_peers = sum(
            len(n.get("peer_sources", [])) for n in online_nodes
        )
        avg_peer_count = total_peers / online_count if online_count else 0
        # Optimal: 3+ peers per node
        connectivity_ratio = min(avg_peer_count / 3, 1.0)
        connectivity_score = connectivity_ratio * 20
    else:
        connectivity_score = 0
    factors["connectivity"] = round(connectivity_score, 2)
    health_score += connectivity_score
    
    # Determine status
    if health_score >= 80:
        status = "healthy"
    elif health_score >= 60:
        status = "fair"
    elif health_score >= 40:
        status = "degraded"
    else:
        status = "critical"
    
    return {
        "health_score": round(health_score, 2),
        "status": status,
        "factors": factors
    }


def get_tier_color(tier: str) -> str:
    """
    Return hex color code for tier (for UI rendering).
    
    Args:
        tier: Tier name
    
    Returns:
        Hex color string
    """
    colors = {
        "low_risk": "#10b981",      # green
        "medium_risk": "#f59e0b",   # yellow
        "high_risk": "#ef4444",     # red
        "Offline": "#6b7280"        # gray
    }
    return colors.get(tier, "#6b7280")


def get_tier_description(tier: str) -> str:
    """
    Return user-friendly description for tier.
    
    Args:
        tier: Tier name
    
    Returns:
        Description string
    """
    descriptions = {
        "low_risk": "Excellent for staking - high reliability and performance",
        "medium_risk": "Good for staking - acceptable metrics with minor concerns",
        "high_risk": "Risky for staking - significant issues detected",
        "Offline": "Node is currently offline"
    }
    return descriptions.get(tier, "Unknown tier")