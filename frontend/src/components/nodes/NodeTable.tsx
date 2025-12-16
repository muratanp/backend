import { Link } from 'react-router-dom';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import {
  cn,
  shortenAddress,
  formatUptimeSeconds,
  formatPercent,
  getTierEmoji,
  getTierClass,
  getTierLabel,
  timeAgo,
  getScoreValue,
} from '@/lib/utils';
import type { PNode } from '@/lib/types';
import { ExternalLink, Globe, Lock, AlertTriangle } from 'lucide-react';

interface NodeTableProps {
  nodes: PNode[];
  isLoading?: boolean;
  error?: Error | null;
}

export function NodeTable({ nodes, isLoading, error }: NodeTableProps) {
  if (isLoading) {
    return (
      <div className="glass-card overflow-hidden">
        <div className="p-8 text-center">
          <div className="h-8 w-8 mx-auto rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <p className="text-sm text-muted-foreground mt-4">Loading nodes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-8 text-center">
        <AlertTriangle className="h-12 w-12 text-warning mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-warning mb-2">Failed to Load Nodes</h3>
        <p className="text-muted-foreground mb-4 max-w-md mx-auto">
          {error.message.includes('Network Error') || error.message.includes('CORS') 
            ? 'Unable to connect to the API. This may be due to CORS restrictions. The API needs to allow requests from this domain.'
            : error.message}
        </p>
        <p className="text-xs text-muted-foreground">
          API: https://web-production-b4440.up.railway.app/pnodes
        </p>
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div className="glass-card p-8 text-center">
        <p className="text-muted-foreground">No nodes found matching your criteria.</p>
      </div>
    );
  }

  return (
    <div className="glass-card overflow-hidden overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent border-border">
            <TableHead className="text-muted-foreground">Address</TableHead>
            <TableHead className="text-muted-foreground">Score</TableHead>
            <TableHead className="text-muted-foreground">Trust</TableHead>
            <TableHead className="text-muted-foreground">Capacity</TableHead>
            <TableHead className="text-muted-foreground">Uptime</TableHead>
            <TableHead className="text-muted-foreground">Storage</TableHead>
            <TableHead className="text-muted-foreground">Peers</TableHead>
            <TableHead className="text-muted-foreground">Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {nodes.map((node) => (
            <TableRow
              key={node.address}
              className="hover:bg-muted/30 border-border cursor-pointer group"
            >
              <TableCell>
                <Link to={`/nodes/${encodeURIComponent(node.address)}`} className="block">
                  <div className="font-mono text-sm flex items-center gap-2">
                    {node.address}
                    <ExternalLink className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <div className="text-xs text-muted-foreground mt-0.5 flex items-center gap-2">
                    <span>v{node.version}</span>
                    <span className="flex items-center gap-1">
                      {node.is_public ? (
                        <><Globe className="h-3 w-3" /> Public</>
                      ) : (
                        <><Lock className="h-3 w-3" /> Private</>
                      )}
                    </span>
                  </div>
                </Link>
              </TableCell>
              <TableCell>
                <Link to={`/nodes/${encodeURIComponent(node.address)}`}>
                  <span
                    className={cn(
                      'inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium border',
                      getTierClass(node.tier)
                    )}
                  >
                    {getTierEmoji(node.tier)} {node.score.toFixed(1)}
                  </span>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    {getTierLabel(node.tier)}
                  </div>
                </Link>
              </TableCell>
              <TableCell>
                <span className="text-sm font-medium">{getScoreValue(node.scores.trust).toFixed(1)}</span>
              </TableCell>
              <TableCell>
                <span className="text-sm font-medium">{getScoreValue(node.scores.capacity).toFixed(1)}</span>
              </TableCell>
              <TableCell>
                <span className="text-sm">{formatUptimeSeconds(node.uptime)}</span>
                <div className="text-xs text-muted-foreground">
                  Last: {timeAgo(node.last_seen)}
                </div>
              </TableCell>
              <TableCell>
                <div className="space-y-1 w-24">
                  <span className="text-xs font-medium">{formatPercent(node.storage_usage_percent)}</span>
                  <Progress value={node.storage_usage_percent} className="h-1.5" />
                </div>
              </TableCell>
              <TableCell>
                <span className="text-sm">{node.peer_count}</span>
              </TableCell>
              <TableCell>
                <span
                  className={cn(
                    'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium',
                    node.is_online ? 'status-online' : 'status-offline'
                  )}
                >
                  <span className={cn('h-1.5 w-1.5 rounded-full', node.is_online ? 'bg-success animate-pulse' : 'bg-muted-foreground')} />
                  {node.is_online ? 'Online' : 'Offline'}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
