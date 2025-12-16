import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { useNodes } from '@/hooks/useNodes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn, shortenAddress, formatUptime, formatPercent, getTierEmoji, getTierLabel, getTierClass, getScoreValue } from '@/lib/utils';
import { GitCompare, Trophy, Star, X } from 'lucide-react';
import type { PNode } from '@/lib/types';

export default function Compare() {
  const [selectedNodes, setSelectedNodes] = useState<PNode[]>([]);
  const { data: nodesData, isLoading } = useNodes({ limit: 50, sortBy: 'score' });

  const toggleNode = (node: PNode) => {
    if (selectedNodes.find((n) => n.address === node.address)) {
      setSelectedNodes(selectedNodes.filter((n) => n.address !== node.address));
    } else if (selectedNodes.length < 5) {
      setSelectedNodes([...selectedNodes, node]);
    }
  };

  const clearSelection = () => setSelectedNodes([]);

  const getBestValue = (key: 'score' | 'trust' | 'capacity' | 'uptime') => {
    if (selectedNodes.length === 0) return null;
    return selectedNodes.reduce((best, node) => {
      const value =
        key === 'score'
          ? node.score
          : key === 'trust'
          ? getScoreValue(node.scores.trust)
          : key === 'capacity'
          ? getScoreValue(node.scores.capacity)
          : node.uptime;
      const bestValue =
        key === 'score'
          ? best.score
          : key === 'trust'
          ? getScoreValue(best.scores.trust)
          : key === 'capacity'
          ? getScoreValue(best.scores.capacity)
          : best.uptime;
      return value > bestValue ? node : best;
    }, selectedNodes[0]).address;
  };

  const overallWinner = selectedNodes.length > 0 ? selectedNodes.reduce((best, node) => 
    node.score > best.score ? node : best, selectedNodes[0]) : null;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <GitCompare className="h-8 w-8 text-accent" />
            Compare Nodes
          </h1>
          <p className="text-muted-foreground mt-1">
            Select up to 5 nodes to compare side-by-side
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Node Selection */}
          <Card className="glass-card border-border lg:col-span-1">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Select Nodes ({selectedNodes.length}/5)</CardTitle>
                {selectedNodes.length > 0 && (
                  <Button variant="ghost" size="sm" onClick={clearSelection}>
                    <X className="h-4 w-4 mr-1" />
                    Clear
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="max-h-[500px] overflow-y-auto scrollbar-thin">
              {isLoading ? (
                <div className="space-y-2">
                  {[...Array(10)].map((_, i) => (
                    <div key={i} className="h-12 bg-muted/50 rounded animate-pulse" />
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {nodesData?.pnodes?.map((node) => {
                    const isSelected = selectedNodes.some((n) => n.address === node.address);
                    const isDisabled = !isSelected && selectedNodes.length >= 5;
                    return (
                      <label
                        key={node.address}
                        className={cn(
                          'flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors',
                          isSelected ? 'bg-primary/10 border border-primary/30' : 'hover:bg-muted/50',
                          isDisabled && 'opacity-50 cursor-not-allowed'
                        )}
                      >
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={() => !isDisabled && toggleNode(node)}
                          disabled={isDisabled}
                        />
                        <div className="flex-1 min-w-0">
                          <p className="font-mono text-sm truncate">{shortenAddress(node.address)}</p>
                          <p className="text-xs text-muted-foreground">
                            Score: {node.score.toFixed(1)} • {getTierLabel(node.tier)}
                          </p>
                        </div>
                      </label>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Comparison Table */}
          <Card className="glass-card border-border lg:col-span-2">
            <CardHeader>
              <CardTitle>Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedNodes.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  Select nodes from the list to compare
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="hover:bg-transparent border-border">
                        <TableHead className="text-muted-foreground">Metric</TableHead>
                        {selectedNodes.map((node) => (
                          <TableHead key={node.address} className="text-center min-w-[120px]">
                            <div className="font-mono text-xs">{shortenAddress(node.address, 4)}</div>
                          </TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow className="border-border">
                        <TableCell className="font-medium">Overall Score</TableCell>
                        {selectedNodes.map((node) => (
                          <TableCell key={node.address} className="text-center">
                            <span className={cn(
                              'inline-flex items-center gap-1 px-2 py-1 rounded text-sm font-medium border',
                              getTierClass(node.tier)
                            )}>
                              {node.address === getBestValue('score') && <Star className="h-3 w-3" />}
                              {node.score.toFixed(1)}
                            </span>
                          </TableCell>
                        ))}
                      </TableRow>
                      <TableRow className="border-border">
                        <TableCell className="font-medium">Tier</TableCell>
                        {selectedNodes.map((node) => (
                          <TableCell key={node.address} className="text-center">
                            {getTierEmoji(node.tier)} {getTierLabel(node.tier)}
                          </TableCell>
                        ))}
                      </TableRow>
                      <TableRow className="border-border">
                        <TableCell className="font-medium">Trust Score</TableCell>
                        {selectedNodes.map((node) => (
                          <TableCell key={node.address} className="text-center">
                            {node.address === getBestValue('trust') && <Star className="h-3 w-3 inline mr-1 text-xand-amber" />}
                            {getScoreValue(node.scores.trust).toFixed(1)}
                          </TableCell>
                        ))}
                      </TableRow>
                      <TableRow className="border-border">
                        <TableCell className="font-medium">Capacity Score</TableCell>
                        {selectedNodes.map((node) => (
                          <TableCell key={node.address} className="text-center">
                            {node.address === getBestValue('capacity') && <Star className="h-3 w-3 inline mr-1 text-xand-amber" />}
                            {getScoreValue(node.scores.capacity).toFixed(1)}
                          </TableCell>
                        ))}
                      </TableRow>
                      <TableRow className="border-border">
                        <TableCell className="font-medium">Uptime</TableCell>
                        {selectedNodes.map((node) => (
                          <TableCell key={node.address} className="text-center">
                            {node.address === getBestValue('uptime') && <Star className="h-3 w-3 inline mr-1 text-xand-amber" />}
                            {formatUptime(node.uptime / 3600)}
                          </TableCell>
                        ))}
                      </TableRow>
                      <TableRow className="border-border">
                        <TableCell className="font-medium">Storage Usage</TableCell>
                        {selectedNodes.map((node) => (
                          <TableCell key={node.address} className="text-center">
                            {formatPercent(node.storage_usage_percent)}
                          </TableCell>
                        ))}
                      </TableRow>
                      <TableRow className="border-border">
                        <TableCell className="font-medium">Peer Count</TableCell>
                        {selectedNodes.map((node) => (
                          <TableCell key={node.address} className="text-center">
                            {node.peer_count}
                          </TableCell>
                        ))}
                      </TableRow>
                      <TableRow className="border-border">
                        <TableCell className="font-medium">Version</TableCell>
                        {selectedNodes.map((node) => (
                          <TableCell key={node.address} className="text-center">
                            v{node.version}
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Winner Card */}
        {overallWinner && selectedNodes.length >= 2 && (
          <Card className="glass-card border-success/30 bg-success/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-success">
                <Trophy className="h-6 w-6" />
                Recommended: {shortenAddress(overallWinner.address)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Based on the comparison, <span className="font-mono text-foreground">{shortenAddress(overallWinner.address)}</span> has 
                the highest overall score ({overallWinner.score.toFixed(1)}) with {getTierLabel(overallWinner.tier)} tier status.
                This node demonstrates strong performance across trust, capacity, and uptime metrics.
              </p>
              <div className="flex gap-3 mt-4">
                <Button className="bg-success hover:bg-success/90 text-success-foreground">
                  🎯 Stake on This Node
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
