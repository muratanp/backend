"""
Alert System for Xandeum pNode Analytics

Generates alerts based on node metrics and thresholds.
Identifies problematic nodes automatically.
"""

import time
from typing import Dict, List
from .config import CACHE_TTL

# Alert thresholds (configurable)
THRESHOLDS = {
    "uptime": {
        "critical": 3600,        # < 1 hour uptime
        "warning": 86400,        # < 1 day uptime
    },
    "storage_usage": {
        "critical": 95.0,        # > 95% full
        "warning": 85.0,         # > 85% full
    },
    "version_behind": {
        "critical": 2,           # 2+ versions behind
        "warning": 1,            # 1 version behind
    },
    "peer_count": {
        "critical": 1,           # ≤ 1 peer (isolated)
        "warning": 2,            # = 2 peers (weak)
    },
    "offline_duration": {
        "critical": 86400 * 7,   # Offline > 7 days
        "warning": 86400 * 3,    # Offline > 3 days
    }
}

LATEST_VERSION = "0.7.0"


def check_node_alerts(node_data: Dict, historical_data: List[Dict] = None) -> List[Dict]:
    """
    Check for alert conditions on a specific node.
    
    Args:
        node_data: Current node data with all metrics
        historical_data: Optional historical data for trend analysis
        
    Returns:
        List of alert dictionaries
    """
    alerts = []
    now = int(time.time())
    
    # Get node info
    address = node_data.get("address", "unknown")
    is_online = node_data.get("is_online", False)
    
    # Alert 1: Node Offline
    if not is_online:
        offline_duration = node_data.get("offline_duration", 0)
        last_seen = node_data.get("last_seen", 0)
        
        if offline_duration > THRESHOLDS["offline_duration"]["critical"]:
            alerts.append({
                "severity": "critical",
                "type": "offline",
                "message": f"Node offline for {offline_duration // 86400} days",
                "metric": "offline_duration",
                "value": offline_duration,
                "threshold": THRESHOLDS["offline_duration"]["critical"],
                "last_seen": last_seen,
                "recommendation": "Check if node is permanently down or needs restart"
            })
        elif offline_duration > THRESHOLDS["offline_duration"]["warning"]:
            alerts.append({
                "severity": "warning",
                "type": "offline",
                "message": f"Node offline for {offline_duration // 86400} days",
                "metric": "offline_duration",
                "value": offline_duration,
                "threshold": THRESHOLDS["offline_duration"]["warning"],
                "last_seen": last_seen,
                "recommendation": "Monitor node closely"
            })
        
        # Return early if offline (other checks not relevant)
        return alerts
    
    # Alert 2: Low Uptime
    uptime = node_data.get("uptime", 0)
    if uptime < THRESHOLDS["uptime"]["critical"]:
        alerts.append({
            "severity": "critical",
            "type": "low_uptime",
            "message": f"Very low uptime: {uptime // 60} minutes",
            "metric": "uptime",
            "value": uptime,
            "threshold": THRESHOLDS["uptime"]["critical"],
            "recommendation": "Node may be restarting frequently"
        })
    elif uptime < THRESHOLDS["uptime"]["warning"]:
        alerts.append({
            "severity": "warning",
            "type": "low_uptime",
            "message": f"Low uptime: {uptime // 3600} hours",
            "metric": "uptime",
            "value": uptime,
            "threshold": THRESHOLDS["uptime"]["warning"],
            "recommendation": "Monitor for stability issues"
        })
    
    # Alert 3: Storage Near Capacity
    storage_usage = node_data.get("storage_usage_percent", 0)
    if storage_usage > THRESHOLDS["storage_usage"]["critical"]:
        alerts.append({
            "severity": "critical",
            "type": "storage_critical",
            "message": f"Storage critically full: {storage_usage:.1f}%",
            "metric": "storage_usage_percent",
            "value": storage_usage,
            "threshold": THRESHOLDS["storage_usage"]["critical"],
            "recommendation": "Increase storage capacity immediately or risk data loss"
        })
    elif storage_usage > THRESHOLDS["storage_usage"]["warning"]:
        alerts.append({
            "severity": "warning",
            "type": "storage_warning",
            "message": f"Storage filling up: {storage_usage:.1f}%",
            "metric": "storage_usage_percent",
            "value": storage_usage,
            "threshold": THRESHOLDS["storage_usage"]["warning"],
            "recommendation": "Plan to increase storage capacity soon"
        })
    
    # Alert 4: Version Behind
    version = node_data.get("version", "")
    if version:
        version_diff = calculate_version_difference(version, LATEST_VERSION)
        if version_diff >= THRESHOLDS["version_behind"]["critical"]:
            alerts.append({
                "severity": "critical",
                "type": "version_outdated",
                "message": f"Running very old version: {version} (latest: {LATEST_VERSION})",
                "metric": "version",
                "value": version,
                "threshold": LATEST_VERSION,
                "recommendation": "Upgrade to latest version immediately for security and features"
            })
        elif version_diff >= THRESHOLDS["version_behind"]["warning"]:
            alerts.append({
                "severity": "warning",
                "type": "version_behind",
                "message": f"Running old version: {version} (latest: {LATEST_VERSION})",
                "metric": "version",
                "value": version,
                "threshold": LATEST_VERSION,
                "recommendation": "Upgrade to latest version soon"
            })
    
    # Alert 5: Poor Network Connectivity
    peer_count = len(node_data.get("peer_sources", []))
    if peer_count <= THRESHOLDS["peer_count"]["critical"]:
        alerts.append({
            "severity": "critical",
            "type": "isolated",
            "message": f"Node isolated with only {peer_count} peer(s)",
            "metric": "peer_count",
            "value": peer_count,
            "threshold": THRESHOLDS["peer_count"]["critical"],
            "recommendation": "Check network configuration and firewall settings"
        })
    elif peer_count <= THRESHOLDS["peer_count"]["warning"]:
        alerts.append({
            "severity": "warning",
            "type": "weak_connectivity",
            "message": f"Weak connectivity with only {peer_count} peers",
            "metric": "peer_count",
            "value": peer_count,
            "threshold": THRESHOLDS["peer_count"]["warning"],
            "recommendation": "Improve network connectivity for better reliability"
        })
    
    # Alert 6: Underutilized Storage (Info only)
    if storage_usage < 5.0:
        alerts.append({
            "severity": "info",
            "type": "underutilized",
            "message": f"Storage underutilized: {storage_usage:.1f}%",
            "metric": "storage_usage_percent",
            "value": storage_usage,
            "threshold": 5.0,
            "recommendation": "Node may need more network usage or has excess capacity"
        })
    
    # Alert 7: Gossip Flapping (if historical data available)
    if historical_data:
        flapping_detected = detect_flapping(historical_data)
        if flapping_detected:
            alerts.append({
                "severity": "warning",
                "type": "gossip_flapping",
                "message": "Node frequently appears/disappears from gossip",
                "metric": "gossip_consistency",
                "value": flapping_detected.get("flap_count", 0),
                "threshold": 3,  # More than 3 flaps
                "recommendation": "Check for network instability or node restarts"
            })
    
    return alerts


def calculate_version_difference(current: str, latest: str) -> int:
    """
    Calculate how many versions behind a node is.
    
    Args:
        current: Current version (e.g., "0.6.5")
        latest: Latest version (e.g., "0.7.0")
        
    Returns:
        Number of minor versions behind
    """
    try:
        current_parts = [int(x) for x in current.split(".")]
        latest_parts = [int(x) for x in latest.split(".")]
        
        # Compare major.minor (ignore patch)
        if len(current_parts) >= 2 and len(latest_parts) >= 2:
            current_minor = current_parts[0] * 10 + current_parts[1]
            latest_minor = latest_parts[0] * 10 + latest_parts[1]
            return max(0, latest_minor - current_minor)
    except:
        pass
    
    return 0  # Can't calculate, assume up to date


def detect_flapping(historical_data: List[Dict]) -> Dict:
    """
    Detect if a node is flapping (appearing/disappearing frequently).
    
    Args:
        historical_data: List of historical states for this node
        
    Returns:
        Dict with flapping info or None if no flapping detected
    """
    if not historical_data or len(historical_data) < 5:
        return None
    
    # Count state changes (online -> offline -> online)
    state_changes = 0
    prev_state = None
    
    for entry in historical_data:
        current_state = entry.get("is_online", False)
        if prev_state is not None and current_state != prev_state:
            state_changes += 1
        prev_state = current_state
    
    # If more than 3 state changes in the historical window, it's flapping
    if state_changes > 3:
        return {
            "flap_count": state_changes,
            "severity": "warning",
            "detected_at": int(time.time())
        }
    
    return None


def get_alerts_summary(all_alerts: List[Dict]) -> Dict:
    """
    Summarize all alerts by severity.
    
    Args:
        all_alerts: List of all alert dictionaries
        
    Returns:
        Summary dictionary
    """
    summary = {
        "total": len(all_alerts),
        "critical": 0,
        "warning": 0,
        "info": 0,
        "by_type": {}
    }
    
    for alert in all_alerts:
        severity = alert.get("severity", "info")
        alert_type = alert.get("type", "unknown")
        
        # Count by severity
        if severity in summary:
            summary[severity] += 1
        
        # Count by type
        if alert_type not in summary["by_type"]:
            summary["by_type"][alert_type] = 0
        summary["by_type"][alert_type] += 1
    
    return summary


def filter_alerts(alerts: List[Dict], severity: str = None, alert_type: str = None) -> List[Dict]:
    """
    Filter alerts by severity and/or type.
    
    Args:
        alerts: List of alert dictionaries
        severity: Filter by severity (critical, warning, info)
        alert_type: Filter by type (offline, low_uptime, etc.)
        
    Returns:
        Filtered list of alerts
    """
    filtered = alerts
    
    if severity:
        filtered = [a for a in filtered if a.get("severity") == severity]
    
    if alert_type:
        filtered = [a for a in filtered if a.get("type") == alert_type]
    
    return filtered