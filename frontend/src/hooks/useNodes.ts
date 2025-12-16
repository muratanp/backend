import { useQuery } from '@tanstack/react-query';
import { fetchPNodes, fetchRegistryEntry, fetchNodeAlerts, fetchNodeConsistency } from '@/lib/api';

interface UseNodesParams {
  status?: 'online' | 'offline' | 'all';
  limit?: number;
  skip?: number;
  sortBy?: 'score' | 'uptime' | 'last_seen' | 'storage_used';
  sortOrder?: 'asc' | 'desc';
}

export function useNodes({
  status = 'online',
  limit = 20,
  skip = 0,
  sortBy = 'score',
  sortOrder = 'desc',
}: UseNodesParams = {}) {
  return useQuery({
    queryKey: ['pnodes', status, limit, skip, sortBy, sortOrder],
    queryFn: async () => {
      try {
        const result = await fetchPNodes({
          status,
          limit,
          skip,
          sort_by: sortBy,
          sort_order: sortOrder,
        });
        return result;
      } catch (error) {
        console.error('Failed to fetch nodes:', error);
        throw error;
      }
    },
    refetchInterval: 60000,
    staleTime: 30000,
    retry: 2,
  });
}

export function useNodeDetails(address: string) {
  return useQuery({
    queryKey: ['node', address],
    queryFn: () => fetchRegistryEntry(address),
    enabled: !!address,
    refetchInterval: 60000,
  });
}

export function useNodeAlerts(address: string) {
  return useQuery({
    queryKey: ['node-alerts', address],
    queryFn: () => fetchNodeAlerts(address),
    enabled: !!address,
    refetchInterval: 60000,
  });
}

export function useNodeConsistency(address: string) {
  return useQuery({
    queryKey: ['node-consistency', address],
    queryFn: () => fetchNodeConsistency(address),
    enabled: !!address,
    refetchInterval: 60000,
  });
}
