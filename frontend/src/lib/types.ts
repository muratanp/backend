// Node Types
export interface PNode {
  address: string;
  pubkey: string;
  version: string;
  is_online: boolean;
  is_public: boolean;
  last_seen: number;
  uptime: number; // in seconds
  peer_count: number;
  peer_sources?: string[];
  storage_committed: number;
  storage_used: number;
  storage_usage_percent: number;
  score: number;
  tier: NodeTier;
  scores: NodeScores;
}

export type NodeTier = 'low_risk' | 'medium_risk' | 'high_risk' | 'legendary' | 'elite' | 'reliable' | 'standard' | 'new';

export interface NodeScores {
  trust: ScoreBreakdown | number;
  capacity: ScoreBreakdown | number;
  stake_confidence?: StakeConfidence;
  breakdown?: Record<string, number>;
}

export interface ScoreBreakdown {
  score: number;
  breakdown: Record<string, number>;
}

export interface StakeConfidence {
  composite_score: number;
  rating: string;
  color?: string;
}

// API Response Types
export interface HealthResponse {
  status: string;
  total_pnodes: number;
  last_gossip_fetch: number;
  uptime: number;
}

export interface NetworkHealthResponse {
  health: {
    health_score: number;
    status: 'healthy' | 'fair' | 'degraded' | 'critical';
  };
  summary: {
    online_pnodes: number;
    offline_pnodes: number;
    total_storage: number;
  };
}

export interface PNodesResponse {
  pnodes: PNode[];
  summary: {
    total_pnodes: number;
    online_pnodes: number;
    offline_pnodes: number;
    snapshot_age_seconds: number;
    last_updated: number;
  };
  network_stats: {
    total_storage_committed: number;
    total_storage_used: number;
    avg_uptime_hours: number;
    version_distribution: Record<string, number>;
  };
  pagination: {
    total: number;
    returned: number;
    skip: number;
    limit: number;
  };
  filters: {
    status: string;
    sort_by: string;
    sort_order: string;
  };
  timestamp: number;
}

export interface NetworkHistoryResponse {
  history: NetworkSnapshot[];
  summary: {
    node_growth: {
      growth: number;
      growth_percent: number;
      trend: 'growing' | 'stable' | 'declining';
    };
  };
}

export interface NetworkSnapshot {
  timestamp: number;
  total_pnodes: number;
  online_pnodes: number;
  total_storage_committed: number;
  avg_peer_count: number;
}

export interface AlertsResponse {
  critical_nodes: CriticalNode[];
  summary: {
    total: number;
    critical: number;
    warning: number;
  };
}

export interface CriticalNode {
  address: string;
  alerts: NodeAlert[];
}

export interface NodeAlert {
  type: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  recommendation?: string;
}

export interface NodeAlertsResponse {
  address: string;
  alerts: NodeAlert[];
  summary: {
    total: number;
    critical: number;
    warning: number;
  };
}

export interface RegistryEntryResponse {
  entry: PNode;
  last_updated: number;
}

export interface ConsistencyResponse {
  consistency: {
    score: number;
    status: string;
    status_emoji: string;
    appearances: number;
    disappearances: number;
  };
}

// Recommendations Types
export interface RecommendedNode {
  address: string;
  pubkey: string;
  score: number;
  tier: NodeTier;
  scores: {
    trust: number;
    capacity: number;
    breakdown?: Record<string, number>;
  };
  uptime_days: number;
  version: string;
  storage_usage_percent: number;
  is_public: boolean;
  peer_count: number;
}

export interface RecommendationsResponse {
  recommendations: RecommendedNode[];
  total_evaluated: number;
  filters: {
    min_uptime_days: number;
    require_public: boolean;
  };
  timestamp: number;
}

// Analytics Types
export interface NetworkAnalyticsResponse {
  current_state: {
    total_pnodes: number;
    public_nodes: number;
    private_nodes: number;
    public_ratio_percent: number;
  };
  growth?: {
    '24_hours'?: GrowthPeriod;
    '7_days'?: GrowthPeriod;
  };
  version_analysis: {
    distribution: Record<string, number>;
    latest_version: string;
    compliance_percent: number;
    fragmentation_index?: number;
    health: string;
  };
  storage_analysis: {
    distribution: {
      empty: number;
      low: number;
      optimal: number;
      high: number;
      critical: number;
    };
    optimal_percent?: number;
    total_committed?: number;
    total_used?: number;
    utilization_percent?: number;
    health: string;
  };
  connectivity_analysis?: {
    distribution: {
      isolated: number;
      weak: number;
      good: number;
      excellent: number;
    };
    well_connected_percent: number;
    health: string;
  };
  recommendations?: NetworkRecommendation[];
}

export interface GrowthPeriod {
  start_count?: number;
  end_count?: number;
  change?: number;
  percent_change?: number;
}

export interface NetworkRecommendation {
  category: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  action: string;
}

export interface ComparisonResponse {
  comparison: PNode[];
  winners: {
    overall_score: { address: string; value: number };
    trust_score: { address: string; value: number };
    capacity_score: { address: string; value: number };
    uptime: { address: string; value: number };
  };
  recommendation: {
    recommended_node: string;
    reason: string;
    considerations: string[];
  };
}
