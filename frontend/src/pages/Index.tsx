import { MainLayout } from '@/components/layout/MainLayout';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { NetworkHealthCard } from '@/components/dashboard/NetworkHealthCard';
import { TopPerformers } from '@/components/dashboard/TopPerformers';
import { AlertBanner } from '@/components/dashboard/AlertBanner';
import { NetworkGrowthChart } from '@/components/charts/NetworkGrowthChart';
import { useHealth, useNetworkHealth, useNetworkHistory, useCriticalAlerts } from '@/hooks/useNetworkHealth';
import { useNodes } from '@/hooks/useNodes';
import { Server, Wifi, HardDrive, Users, Clock } from 'lucide-react';
import { formatBytes, formatUptime } from '@/lib/utils';

export default function Index() {
  const { data: health, isLoading: healthLoading } = useHealth();
  const { data: networkHealth, isLoading: networkHealthLoading } = useNetworkHealth();
  const { data: historyData, isLoading: historyLoading } = useNetworkHistory(24);
  const { data: topNodes, isLoading: topNodesLoading } = useNodes({ limit: 5, sortBy: 'score' });
  const { data: alerts } = useCriticalAlerts();

  const isLoading = healthLoading || networkHealthLoading;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Real-time overview of the Xandeum network
          </p>
        </div>

        {/* Alert Banner */}
        <AlertBanner alerts={alerts ?? null} />

        {/* Stats Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            label="Total Nodes"
            value={isLoading ? '—' : health?.total_pnodes ?? 0}
            icon={Server}
            trend={historyData?.summary?.node_growth ? 
              `${historyData.summary.node_growth.growth >= 0 ? '+' : ''}${historyData.summary.node_growth.growth} (24h)` : 
              undefined
            }
            trendUp={historyData?.summary?.node_growth?.growth ? historyData.summary.node_growth.growth >= 0 : undefined}
          />
          <StatsCard
            label="Online"
            value={networkHealthLoading ? '—' : networkHealth?.summary?.online_pnodes ?? 0}
            icon={Wifi}
            trend={`${networkHealth?.summary?.offline_pnodes ?? 0} offline`}
          />
          {networkHealth && (
            <NetworkHealthCard
              score={networkHealth.health.health_score}
              status={networkHealth.health.status}
            />
          )}
          <StatsCard
            label="Total Storage"
            value={networkHealthLoading ? '—' : formatBytes(networkHealth?.summary?.total_storage ?? 0)}
            icon={HardDrive}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Chart - Takes 2 columns */}
          <div className="lg:col-span-2">
            <NetworkGrowthChart
              data={historyData?.history ?? []}
              isLoading={historyLoading}
            />
          </div>

          {/* Top Performers - Takes 1 column */}
          <div>
            <TopPerformers
              nodes={topNodes?.pnodes ?? []}
              isLoading={topNodesLoading}
            />
          </div>
        </div>

        {/* Additional Stats */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            label="Online Nodes"
            value={topNodes?.summary?.online_pnodes ?? '—'}
            icon={Users}
          />
          <StatsCard
            label="Avg Uptime"
            value={topNodes?.network_stats?.avg_uptime_hours ? formatUptime(topNodes.network_stats.avg_uptime_hours) : '—'}
            icon={Clock}
          />
          <StatsCard
            label="Network Storage"
            value={formatBytes(topNodes?.network_stats?.total_storage_committed ?? 0)}
            icon={HardDrive}
          />
          <StatsCard
            label="System Uptime"
            value={health?.uptime ? formatUptime(health.uptime / 3600) : '—'}
            icon={Server}
            status={health?.status}
          />
        </div>
      </div>
    </MainLayout>
  );
}
