import { cn, shortenAddress, getTierEmoji, getTierLabel, formatUptime, getTierClass } from '@/lib/utils';
import { Trophy, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { PNode } from '@/lib/types';

interface TopPerformersProps {
  nodes: PNode[];
  isLoading?: boolean;
}

export function TopPerformers({ nodes, isLoading }: TopPerformersProps) {
  if (isLoading) {
    return (
      <div className="glass-card p-5">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="h-5 w-5 text-xand-amber" />
          <h3 className="font-semibold">Top Performers</h3>
        </div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-muted/50 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-xand-amber" />
          <h3 className="font-semibold">Top Performers</h3>
        </div>
        <Link
          to="/recommendations"
          className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1 transition-colors"
        >
          View all <ArrowRight className="h-3 w-3" />
        </Link>
      </div>
      <div className="space-y-3">
        {nodes.map((node, index) => (
          <Link
            key={node.address}
            to={`/nodes/${node.address}`}
            className="block rounded-lg bg-muted/30 p-3 transition-all hover:bg-muted/50 hover:border-l-2 hover:border-primary"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs font-bold">
                  {index + 1}
                </span>
                <div>
                  <p className="font-mono text-sm">{shortenAddress(node.address)}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatUptime(node.uptime)} uptime
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className={cn('inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium border', getTierClass(node.tier))}>
                  {getTierEmoji(node.tier)} {node.score.toFixed(1)}
                </span>
                <p className="text-xs text-muted-foreground mt-1">{getTierLabel(node.tier)}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
