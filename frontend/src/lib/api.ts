import axios from 'axios';
import type {
  HealthResponse,
  NetworkHealthResponse,
  PNodesResponse,
  NetworkHistoryResponse,
  AlertsResponse,
  NodeAlertsResponse,
  RegistryEntryResponse,
  ConsistencyResponse,
  RecommendationsResponse,
  NetworkAnalyticsResponse,
  ComparisonResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-b4440.up.railway.app';

// const API_BASE_URL = 'https://friendly-parakeet-r45gprv47562x95p-8000.app.github.dev';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Functions
export const fetchHealth = async (): Promise<HealthResponse> => {
  const { data } = await api.get('/health');
  return data;
};

export const fetchNetworkHealth = async (): Promise<NetworkHealthResponse> => {
  const { data } = await api.get('/network/health');
  return data;
};

export const fetchPNodes = async (params: {
  status?: 'online' | 'offline' | 'all';
  limit?: number;
  skip?: number;
  sort_by?: 'score' | 'uptime' | 'last_seen' | 'storage_used';
  sort_order?: 'asc' | 'desc';
}): Promise<PNodesResponse> => {
  const { data } = await api.get('/pnodes', { params });
  return data;
};

export const fetchNetworkHistory = async (hours: number): Promise<NetworkHistoryResponse> => {
  const { data } = await api.get('/network/history', { params: { hours } });
  return data;
};

export const fetchNetworkGrowth = async (hours: number) => {
  const { data } = await api.get('/network/growth', { params: { hours } });
  return data;
};

export const fetchCriticalAlerts = async (): Promise<AlertsResponse> => {
  const { data } = await api.get('/alerts/critical');
  return data;
};

export const fetchNodeAlerts = async (address: string): Promise<NodeAlertsResponse> => {
  const { data } = await api.get(`/pnodes/${address}/alerts`);
  return data;
};

export const fetchRegistryEntry = async (address: string): Promise<RegistryEntryResponse> => {
  const { data } = await api.get(`/registry/${address}`);
  return data;
};

export const fetchNodeConsistency = async (address: string): Promise<ConsistencyResponse> => {
  const { data } = await api.get(`/node/${address}/consistency`);
  return data;
};

export const fetchRecommendations = async (params: {
  limit?: number;
  min_uptime_days?: number;
  require_public?: boolean;
}): Promise<RecommendationsResponse> => {
  const { data } = await api.get('/recommendations', { params });
  return data;
};

export const fetchNetworkAnalytics = async (): Promise<NetworkAnalyticsResponse> => {
  const { data } = await api.get('/network/analytics');
  return data;
};

export const fetchComparison = async (addresses: string[]): Promise<ComparisonResponse> => {
  const { data } = await api.get('/pnodes/compare', {
    params: { addresses: addresses.join(',') },
  });
  return data;
};
