import { useParams, Link } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { useNodeDetails, useNodeAlerts, useNodeConsistency } from '@/hooks/useNodes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  cn,
  getTierEmoji,
  getTierLabel,
  getTierClass,
  formatBytes,
  formatUptimeSeconds,
  formatPercent,
  timeAgo,
  shortenAddress,
  getScoreValue,
  getScoreBreakdown,
} from '@/lib/utils';
import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle,
  Copy,
  Shield,
  HardDrive,
  Target,
  Activity,
  Globe,
  Lock,
} from 'lucide-react';
import { toast } from 'sonner';

export default function NodeDetails() {
  const { address } = useParams<{ address: string }>();
  const decodedAddress = address ? decodeURIComponent(address) : '';
  const { data: nodeData, isLoading } = useNodeDetails(decodedAddress);
  const { data: alertsData } = useNodeAlerts(decodedAddress);
  const { data: consistencyData } = useNodeConsistency(decodedAddress);

  const copyAddress = () => {
    if (decodedAddress) {
      navigator.clipboard.writeText(decodedAddress);
      toast.success('Address copied to clipboard');
    }
  };

  if (isLoading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="h-10 w-10 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </MainLayout>
    );
  }

  if (!nodeData) {
    return (
      <MainLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold">Node Not Found</h2>
          <p className="text-muted-foreground mt-2">The requested node could not be found.</p>
          <Link to="/nodes">
            <Button variant="outline" className="mt-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Nodes
            </Button>
          </Link>
        </div>
      </MainLayout>
    );
  }

  const node = nodeData.entry;
  const trustScore = getScoreValue(node.scores.trust);
  const capacityScore = getScoreValue(node.scores.capacity);
  const trustBreakdown = getScoreBreakdown(node.scores.trust);
  const capacityBreakdown = getScoreBreakdown(node.scores.capacity);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Back Button */}
        <Link to="/nodes">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Nodes
          </Button>
        </Link>

        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl lg:text-3xl font-bold font-mono break-all">
                {node.address}
              </h1>
              <button
                onClick={copyAddress}
                className="p-2 rounded-lg hover:bg-muted transition-colors"
              >
                <Copy className="h-4 w-4 text-muted-foreground" />
              </button>
            </div>
            <p className="text-muted-foreground mt-1">
              Operator: {shortenAddress(node.pubkey)}
            </p>
            <div className="flex items-center gap-3 mt-2 flex-wrap">
              <span
                className={cn(
                  'inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium',
                  node.is_online ? 'status-online' : 'status-offline'
                )}
              >
                <span className={cn('h-2 w-2 rounded-full', node.is_online ? 'bg-success animate-pulse' : 'bg-muted-foreground')} />
                {node.is_online ? 'Online' : 'Offline'}
              </span>
              <span className="flex items-center gap-1 text-sm text-muted-foreground">
                {node.is_public ? (
                  <><Globe className="h-4 w-4" /> Public RPC</>
                ) : (
                  <><Lock className="h-4 w-4" /> Private</>
                )}
              </span>
              <span className="text-sm text-muted-foreground">
                Last seen: {timeAgo(node.last_seen)}
              </span>
            </div>
          </div>
          <div className="text-left lg:text-right">
            <div className="text-5xl font-bold">{node.score.toFixed(1)}</div>
            <div
              className={cn(
                'inline-flex items-center gap-2 rounded-lg px-3 py-1.5 mt-2 text-sm font-medium border',
                getTierClass(node.tier)
              )}
            >
              {getTierEmoji(node.tier)} {getTierLabel(node.tier)}
            </div>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="grid gap-4 md:grid-cols-3">
          {/* Trust Score */}
          <Card className="glass-card border-border">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Shield className="h-5 w-5 text-primary" />
                Trust Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-primary">
                {trustScore.toFixed(1)}
              </div>
              {trustBreakdown && (
                <div className="space-y-3 mt-4">
                  {Object.entries(trustBreakdown).map(([key, value]) => (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-muted-foreground capitalize">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="font-medium">{(value as number).toFixed(1)}</span>
                      </div>
                      <Progress value={(value as number) * 2.5} className="h-1.5" />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Capacity Score */}
          <Card className="glass-card border-border">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <HardDrive className="h-5 w-5 text-accent" />
                Capacity Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-accent">
                {capacityScore.toFixed(1)}
              </div>
              {capacityBreakdown && (
                <div className="space-y-3 mt-4">
                  {Object.entries(capacityBreakdown).map(([key, value]) => (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-muted-foreground capitalize">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="font-medium">{(value as number).toFixed(1)}</span>
                      </div>
                      <Progress value={(value as number) * 2.5} className="h-1.5" />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Stake Confidence */}
          <Card className={cn('glass-card border-border', getTierClass(node.tier))}>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Target className="h-5 w-5" />
                Stake Confidence
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">
                {node.scores.stake_confidence?.composite_score?.toFixed(1) ?? node.score.toFixed(1)}
              </div>
              <div className="text-lg mt-2">
                {getTierEmoji(node.tier)} {node.scores.stake_confidence?.rating ?? getTierLabel(node.tier)}
              </div>
              <Button className="w-full mt-4 bg-primary hover:bg-primary/90">
                Stake XAND Here
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Alerts & Consistency */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Alerts */}
          <Card className="glass-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                Active Alerts ({alertsData?.summary?.total ?? 0})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {alertsData?.alerts && alertsData.alerts.length > 0 ? (
                <div className="space-y-3">
                  {alertsData.alerts.map((alert, idx) => (
                    <div
                      key={idx}
                      className={cn(
                        'rounded-lg p-3 border',
                        alert.severity === 'critical'
                          ? 'bg-destructive/10 border-destructive/30'
                          : alert.severity === 'warning'
                          ? 'bg-warning/10 border-warning/30'
                          : 'bg-muted border-border'
                      )}
                    >
                      <div className="font-medium capitalize">
                        {alert.type.replace(/_/g, ' ')}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {alert.message}
                      </p>
                      {alert.recommendation && (
                        <p className="text-sm mt-2">
                          💡 <strong>Tip:</strong> {alert.recommendation}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center gap-3 text-success">
                  <CheckCircle className="h-5 w-5" />
                  <span>No active alerts - node operating normally</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Consistency */}
          <Card className="glass-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                Gossip Consistency
              </CardTitle>
            </CardHeader>
            <CardContent>
              {consistencyData ? (
                <div>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-4xl font-bold">
                        {consistencyData.consistency.status_emoji}{' '}
                        {(consistencyData.consistency.score * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-muted-foreground capitalize mt-1">
                        {consistencyData.consistency.status}
                      </div>
                    </div>
                    <div className="text-right text-sm space-y-1">
                      <div>Appearances: {consistencyData.consistency.appearances}</div>
                      <div>Drops: {consistencyData.consistency.disappearances}</div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-muted-foreground">Loading consistency data...</div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Node Details */}
        <Card className="glass-card border-border">
          <CardHeader>
            <CardTitle>Node Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <p className="text-sm text-muted-foreground">Version</p>
                <p className="font-medium">v{node.version}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Peer Count</p>
                <p className="font-medium">{node.peer_count}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Uptime</p>
                <p className="font-medium">{formatUptimeSeconds(node.uptime)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Storage Used</p>
                <p className="font-medium">
                  {formatBytes(node.storage_used)} / {formatBytes(node.storage_committed)}
                </p>
              </div>
              <div className="sm:col-span-2">
                <p className="text-sm text-muted-foreground">Storage Usage</p>
                <div className="flex items-center gap-2 mt-1">
                  <Progress value={node.storage_usage_percent} className="h-2 flex-1" />
                  <span className="text-sm font-medium">{formatPercent(node.storage_usage_percent)}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
