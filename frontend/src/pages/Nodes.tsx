import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { NodeTable } from '@/components/nodes/NodeTable';
import { NodeFilters } from '@/components/nodes/NodeFilters';
import { useNodes } from '@/hooks/useNodes';
import { formatBytes, timeAgo } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, Server, Wifi, WifiOff, HardDrive, Clock, RefreshCw } from 'lucide-react';

export default function Nodes() {
  const [status, setStatus] = useState<'online' | 'offline' | 'all'>('online');
  const [sortBy, setSortBy] = useState<'score' | 'uptime' | 'last_seen' | 'storage_used'>('score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [skip, setSkip] = useState(0);
  const limit = 20;

  const { data, isLoading, error, refetch, isFetching } = useNodes({
    status,
    sortBy,
    sortOrder,
    skip,
    limit,
  });

  const handleStatusChange = (value: string) => {
    setStatus(value as typeof status);
    setSkip(0);
  };

  const handleSortByChange = (value: string) => {
    setSortBy(value as typeof sortBy);
    setSkip(0);
  };

  const handleSortOrderChange = (value: string) => {
    setSortOrder(value as typeof sortOrder);
    setSkip(0);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">Node Explorer</h1>
            <p className="text-muted-foreground mt-1">
              Browse and filter all nodes in the Xandeum network
            </p>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Summary Stats */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <div className="glass-card p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-primary/10 p-2">
                <Server className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {data?.summary?.total_pnodes ?? '—'}
                </p>
                <p className="text-xs text-muted-foreground">Total Nodes</p>
              </div>
            </div>
          </div>
          <div className="glass-card p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-success/10 p-2">
                <Wifi className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {data?.summary?.online_pnodes ?? '—'}
                </p>
                <p className="text-xs text-muted-foreground">Online</p>
              </div>
            </div>
          </div>
          <div className="glass-card p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-muted p-2">
                <WifiOff className="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {data?.summary?.offline_pnodes ?? '—'}
                </p>
                <p className="text-xs text-muted-foreground">Offline</p>
              </div>
            </div>
          </div>
          <div className="glass-card p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-accent/10 p-2">
                <HardDrive className="h-5 w-5 text-accent" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {formatBytes(data?.network_stats?.total_storage_committed ?? 0)}
                </p>
                <p className="text-xs text-muted-foreground">Total Storage</p>
              </div>
            </div>
          </div>
          <div className="glass-card p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-warning/10 p-2">
                <Clock className="h-5 w-5 text-warning" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {data?.network_stats?.avg_uptime_hours 
                    ? `${Math.round(data.network_stats.avg_uptime_hours)}h`
                    : '—'}
                </p>
                <p className="text-xs text-muted-foreground">Avg Uptime</p>
              </div>
            </div>
          </div>
        </div>

        {/* Data freshness indicator */}
        {data?.summary && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
            <span>
              Data updated {timeAgo(data.summary.last_updated)} • 
              Snapshot age: {data.summary.snapshot_age_seconds}s
            </span>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <NodeFilters
            status={status}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onStatusChange={handleStatusChange}
            onSortByChange={handleSortByChange}
            onSortOrderChange={handleSortOrderChange}
          />
        </div>

        {/* Table */}
        <NodeTable 
          nodes={data?.pnodes ?? []} 
          isLoading={isLoading} 
          error={error as Error | null}
        />

        {/* Pagination */}
        {data && (
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              Showing {data.pagination.returned} of {data.pagination.total} nodes
              {data.filters && (
                <span className="ml-2">
                  (filtered: {data.filters.status}, sorted by: {data.filters.sort_by})
                </span>
              )}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={skip === 0}
                onClick={() => setSkip(Math.max(0, skip - limit))}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={skip + limit >= data.pagination.total}
                onClick={() => setSkip(skip + limit)}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
