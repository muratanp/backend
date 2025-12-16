import { MainLayout } from '@/components/layout/MainLayout';
import { useNetworkAnalytics } from '@/hooks/useNetworkHealth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { formatPercent } from '@/lib/utils';
import { BarChart3, AlertTriangle, CheckCircle, RefreshCw, Globe, Lock, Server, Users } from 'lucide-react';

const COLORS = {
  emerald: 'hsl(160, 84%, 39%)',
  cyan: 'hsl(199, 89%, 48%)',
  amber: 'hsl(38, 92%, 50%)',
  red: 'hsl(0, 72%, 51%)',
  gray: 'hsl(215, 20%, 55%)',
  purple: 'hsl(270, 76%, 60%)',
  blue: 'hsl(217, 91%, 60%)',
};

export default function Analytics() {
  const { data: analytics, isLoading, error, refetch, isFetching } = useNetworkAnalytics();

  if (isLoading) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">Network Analytics</h1>
            <p className="text-muted-foreground mt-1">Deep dive into network metrics and trends</p>
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="glass-card h-[400px] animate-pulse" />
            ))}
          </div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-accent" />
              Network Analytics
            </h1>
          </div>
          <div className="glass-card p-8 text-center">
            <AlertTriangle className="h-12 w-12 text-warning mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-warning mb-2">Failed to Load Analytics</h3>
            <p className="text-muted-foreground mb-4 max-w-md mx-auto">
              {(error as Error).message?.includes('Network Error') 
                ? 'Unable to connect to the API. This may be due to CORS restrictions.'
                : (error as Error).message}
            </p>
            <Button onClick={() => refetch()} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Version distribution data
  const versionData = analytics?.version_analysis?.distribution
    ? Object.entries(analytics.version_analysis.distribution).map(([version, count]) => ({
        name: version,
        value: count,
        fill: version === analytics.version_analysis.latest_version ? COLORS.emerald : COLORS.amber,
      }))
    : [];

  // Storage distribution data
  const storageData = analytics?.storage_analysis?.distribution
    ? [
        { name: 'Empty (0-10%)', count: analytics.storage_analysis.distribution.empty, fill: COLORS.gray },
        { name: 'Low (10-30%)', count: analytics.storage_analysis.distribution.low, fill: COLORS.cyan },
        { name: 'Optimal (30-70%)', count: analytics.storage_analysis.distribution.optimal, fill: COLORS.emerald },
        { name: 'High (70-90%)', count: analytics.storage_analysis.distribution.high, fill: COLORS.amber },
        { name: 'Critical (90-100%)', count: analytics.storage_analysis.distribution.critical, fill: COLORS.red },
      ]
    : [];

  // Connectivity distribution data
  const connectivityData = analytics?.connectivity_analysis?.distribution
    ? [
        { name: 'Isolated', count: analytics.connectivity_analysis.distribution.isolated, fill: COLORS.red },
        { name: 'Weak', count: analytics.connectivity_analysis.distribution.weak, fill: COLORS.amber },
        { name: 'Good', count: analytics.connectivity_analysis.distribution.good, fill: COLORS.cyan },
        { name: 'Excellent', count: analytics.connectivity_analysis.distribution.excellent, fill: COLORS.emerald },
      ]
    : [];

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'good': return 'text-success';
      case 'fair': return 'text-warning';
      case 'poor': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  const getHealthEmoji = (health: string) => {
    switch (health) {
      case 'good': return '🟢';
      case 'fair': return '🟡';
      case 'poor': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-accent" />
              Network Analytics
            </h1>
            <p className="text-muted-foreground mt-1">
              Comprehensive overview of network health, distributions, and trends
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

        {/* Current State Overview */}
        {analytics?.current_state && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="glass-card p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-primary/10 p-2">
                  <Server className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{analytics.current_state.total_pnodes}</p>
                  <p className="text-xs text-muted-foreground">Total Nodes</p>
                </div>
              </div>
            </div>
            <div className="glass-card p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-success/10 p-2">
                  <Globe className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{analytics.current_state.public_nodes}</p>
                  <p className="text-xs text-muted-foreground">Public Nodes</p>
                </div>
              </div>
            </div>
            <div className="glass-card p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-muted p-2">
                  <Lock className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{analytics.current_state.private_nodes}</p>
                  <p className="text-xs text-muted-foreground">Private Nodes</p>
                </div>
              </div>
            </div>
            <div className="glass-card p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-accent/10 p-2">
                  <Users className="h-5 w-5 text-accent" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{formatPercent(analytics.current_state.public_ratio_percent)}</p>
                  <p className="text-xs text-muted-foreground">Public Ratio</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Charts Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Version Distribution */}
          <Card className="glass-card border-border">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Version Distribution</CardTitle>
                {analytics?.version_analysis && (
                  <span className={`text-sm ${getHealthColor(analytics.version_analysis.health)}`}>
                    {getHealthEmoji(analytics.version_analysis.health)} {analytics.version_analysis.health}
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={versionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {versionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--popover))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                        color: 'hsl(var(--popover-foreground))',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="text-center mt-4 space-y-1">
                <div className="text-2xl font-bold text-success">
                  {formatPercent(analytics?.version_analysis?.compliance_percent ?? 0)}
                </div>
                <div className="text-sm text-muted-foreground">
                  on latest version ({analytics?.version_analysis?.latest_version})
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Storage Distribution */}
          <Card className="glass-card border-border">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Storage Distribution</CardTitle>
                {analytics?.storage_analysis && (
                  <span className={`text-sm ${getHealthColor(analytics.storage_analysis.health)}`}>
                    {getHealthEmoji(analytics.storage_analysis.health)} {analytics.storage_analysis.health}
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={storageData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                      dataKey="name"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={10}
                      angle={-20}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--popover))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                        color: 'hsl(var(--popover-foreground))',
                      }}
                    />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {storageData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {analytics?.storage_analysis?.optimal_percent && (
                <div className="text-center mt-4">
                  <div className="text-sm text-muted-foreground">
                    {formatPercent(analytics.storage_analysis.optimal_percent)} in optimal range
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Connectivity Distribution */}
          {analytics?.connectivity_analysis && (
            <Card className="glass-card border-border">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Connectivity Distribution</CardTitle>
                  <span className={`text-sm ${getHealthColor(analytics.connectivity_analysis.health)}`}>
                    {getHealthEmoji(analytics.connectivity_analysis.health)} {analytics.connectivity_analysis.health}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={connectivityData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <YAxis 
                        type="category" 
                        dataKey="name" 
                        stroke="hsl(var(--muted-foreground))" 
                        fontSize={12}
                        width={80}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--popover))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          color: 'hsl(var(--popover-foreground))',
                        }}
                      />
                      <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                        {connectivityData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="text-center mt-4">
                  <div className="text-2xl font-bold text-success">
                    {formatPercent(analytics.connectivity_analysis.well_connected_percent)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    well connected (good + excellent)
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Health Summary */}
          <Card className="glass-card border-border">
            <CardHeader>
              <CardTitle>Health Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Version Health */}
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                  <div>
                    <p className="font-medium">Version Compliance</p>
                    <p className="text-sm text-muted-foreground">
                      {formatPercent(analytics?.version_analysis?.compliance_percent ?? 0)} on latest
                    </p>
                  </div>
                  <div className={`text-2xl ${getHealthColor(analytics?.version_analysis?.health ?? '')}`}>
                    {getHealthEmoji(analytics?.version_analysis?.health ?? '')}
                  </div>
                </div>

                {/* Storage Health */}
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                  <div>
                    <p className="font-medium">Storage Utilization</p>
                    <p className="text-sm text-muted-foreground">
                      {formatPercent(analytics?.storage_analysis?.optimal_percent ?? 0)} optimal
                    </p>
                  </div>
                  <div className={`text-2xl ${getHealthColor(analytics?.storage_analysis?.health ?? '')}`}>
                    {getHealthEmoji(analytics?.storage_analysis?.health ?? '')}
                  </div>
                </div>

                {/* Connectivity Health */}
                {analytics?.connectivity_analysis && (
                  <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                    <div>
                      <p className="font-medium">Network Connectivity</p>
                      <p className="text-sm text-muted-foreground">
                        {formatPercent(analytics.connectivity_analysis.well_connected_percent)} connected
                      </p>
                    </div>
                    <div className={`text-2xl ${getHealthColor(analytics.connectivity_analysis.health)}`}>
                      {getHealthEmoji(analytics.connectivity_analysis.health)}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recommendations */}
        {analytics?.recommendations && analytics.recommendations.length > 0 && (
          <Card className="glass-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                Network Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.recommendations.map((rec, idx) => (
                  <div
                    key={idx}
                    className={`rounded-lg p-4 border ${
                      rec.severity === 'high'
                        ? 'bg-destructive/10 border-destructive/30'
                        : rec.severity === 'medium'
                        ? 'bg-warning/10 border-warning/30'
                        : 'bg-muted border-border'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {rec.severity === 'high' ? (
                        <AlertTriangle className="h-5 w-5 text-destructive mt-0.5" />
                      ) : rec.severity === 'medium' ? (
                        <AlertTriangle className="h-5 w-5 text-warning mt-0.5" />
                      ) : (
                        <CheckCircle className="h-5 w-5 text-muted-foreground mt-0.5" />
                      )}
                      <div>
                        <h4 className="font-semibold capitalize">{rec.category}</h4>
                        <p className="text-sm text-muted-foreground mt-1">{rec.message}</p>
                        <p className="text-sm mt-2">
                          <strong>Action:</strong> {rec.action}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
