import { useQuery } from '@tanstack/react-query';
import {
  fetchHealth,
  fetchNetworkHealth,
  fetchNetworkHistory,
  fetchCriticalAlerts,
  fetchRecommendations,
  fetchNetworkAnalytics,
} from '@/lib/api';

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function useNetworkHealth() {
  return useQuery({
    queryKey: ['network-health'],
    queryFn: fetchNetworkHealth,
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function useNetworkHistory(hours: number = 24) {
  return useQuery({
    queryKey: ['network-history', hours],
    queryFn: () => fetchNetworkHistory(hours),
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function useCriticalAlerts() {
  return useQuery({
    queryKey: ['critical-alerts'],
    queryFn: fetchCriticalAlerts,
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function useRecommendations(params?: {
  limit?: number;
  min_uptime_days?: number;
  require_public?: boolean;
}) {
  return useQuery({
    queryKey: ['recommendations', params],
    queryFn: async () => {
      try {
        const result = await fetchRecommendations(params || {});
        return result;
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
        throw error;
      }
    },
    refetchInterval: 60000,
    staleTime: 30000,
    retry: 2,
  });
}

export function useNetworkAnalytics() {
  return useQuery({
    queryKey: ['network-analytics'],
    queryFn: async () => {
      try {
        const result = await fetchNetworkAnalytics();
        return result;
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
        throw error;
      }
    },
    refetchInterval: 60000,
    staleTime: 30000,
    retry: 2,
  });
}
