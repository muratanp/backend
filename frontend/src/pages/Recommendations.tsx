import { Link } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { useRecommendations } from '@/hooks/useNetworkHealth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  cn,
  shortenAddress,
  getTierEmoji,
  getTierLabel,
  getTierClass,
  formatPercent,
} from '@/lib/utils';
import { Trophy, Star, CheckCircle, ArrowRight, AlertTriangle, RefreshCw, Globe, Lock } from 'lucide-react';

export default function Recommendations() {
  const { data, isLoading, error, refetch, isFetching } = useRecommendations({ 
    limit: 10, 
    min_uptime_days: 7 
  });

  if (isLoading) {
    return (
      <MainLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">Top Staking Recommendations</h1>
            <p className="text-muted-foreground mt-1">
              Best nodes for staking your XAND tokens
            </p>
          </div>
          <div className="grid gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="glass-card h-48 animate-pulse" />
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
              <Trophy className="h-8 w-8 text-xand-amber" />
              Top Staking Recommendations
            </h1>
          </div>
          <div className="glass-card p-8 text-center">
            <AlertTriangle className="h-12 w-12 text-warning mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-warning mb-2">Failed to Load Recommendations</h3>
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

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Trophy className="h-8 w-8 text-xand-amber" />
              Top Staking Recommendations
            </h1>
            <p className="text-muted-foreground mt-1">
              Best nodes for staking your XAND tokens based on reliability, performance, and trust scores
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

        {/* Criteria */}
        <div className="glass-card p-4 flex flex-wrap gap-4 text-sm">
          <span className="text-muted-foreground">Selection criteria:</span>
          <span className="flex items-center gap-1.5">
            <CheckCircle className="h-4 w-4 text-success" />
            Min {data?.filters?.min_uptime_days ?? 7} days uptime
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle className="h-4 w-4 text-success" />
            Evaluated {data?.total_evaluated ?? 0} nodes
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle className="h-4 w-4 text-success" />
            Sorted by overall score
          </span>
        </div>

        {/* Recommendations List */}
        <div className="grid gap-6">
          {data?.recommendations?.map((node, index) => (
            <Card key={node.address} className="glass-card border-border overflow-hidden">
              <CardHeader className="pb-4">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  <div className="flex items-center gap-4">
                    {/* Rank Badge */}
                    <div
                      className={cn(
                        'flex h-12 w-12 items-center justify-center rounded-xl text-xl font-bold',
                        index === 0
                          ? 'bg-gradient-to-br from-amber-500 to-yellow-500 text-amber-950'
                          : index === 1
                          ? 'bg-gradient-to-br from-gray-300 to-gray-400 text-gray-800'
                          : index === 2
                          ? 'bg-gradient-to-br from-amber-700 to-amber-800 text-amber-100'
                          : 'bg-muted text-muted-foreground'
                      )}
                    >
                      #{index + 1}
                    </div>
                    <div>
                      <CardTitle className="font-mono text-lg">
                        {node.address}
                      </CardTitle>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mt-0.5">
                        <span>{node.uptime_days.toFixed(1)} days uptime</span>
                        <span>•</span>
                        <span>v{node.version}</span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          {node.is_public ? (
                            <><Globe className="h-3 w-3" /> Public</>
                          ) : (
                            <><Lock className="h-3 w-3" /> Private</>
                          )}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-4xl font-bold">{node.score.toFixed(1)}</div>
                      <div
                        className={cn(
                          'inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 mt-1 text-xs font-medium border',
                          getTierClass(node.tier)
                        )}
                      >
                        {getTierEmoji(node.tier)} {getTierLabel(node.tier)}
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Score Breakdown */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Trust Score</p>
                    <p className="text-xl font-bold">{node.scores.trust.toFixed(1)}</p>
                    <Progress value={node.scores.trust} className="h-1.5" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Capacity Score</p>
                    <p className="text-xl font-bold">{node.scores.capacity.toFixed(1)}</p>
                    <Progress value={node.scores.capacity} className="h-1.5" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Storage Usage</p>
                    <p className="text-xl font-bold">{formatPercent(node.storage_usage_percent)}</p>
                    <Progress value={node.storage_usage_percent} className="h-1.5" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Peer Count</p>
                    <p className="text-xl font-bold">{node.peer_count}</p>
                  </div>
                </div>

                {/* Why recommended (for top 3) */}
                {index < 3 && (
                  <div className="rounded-lg bg-muted/50 p-4">
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <Star className="h-4 w-4 text-xand-amber" />
                      Why this node is #{index + 1}:
                    </h4>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-3.5 w-3.5 text-success" />
                        {index === 0 ? 'Highest overall score' : `Top ${index + 1} overall score`} ({node.score.toFixed(1)})
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-3.5 w-3.5 text-success" />
                        Excellent version compliance (v{node.version})
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-3.5 w-3.5 text-success" />
                        {node.storage_usage_percent < 70 ? 'Optimal' : 'Good'} storage utilization ({formatPercent(node.storage_usage_percent)})
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-3.5 w-3.5 text-success" />
                        {node.uptime_days.toFixed(1)} days of proven uptime
                      </li>
                    </ul>
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-wrap gap-3">
                  <Link to={`/nodes/${encodeURIComponent(node.address)}`} className="flex-1">
                    <Button variant="outline" className="w-full">
                      View Details
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                  <Button className="flex-1 bg-success hover:bg-success/90 text-success-foreground">
                    🎯 Stake XAND
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {data?.recommendations?.length === 0 && (
          <div className="glass-card p-8 text-center">
            <p className="text-muted-foreground">No recommendations available at this time.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
