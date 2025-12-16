import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Network, Server, Globe, Link2 } from 'lucide-react';

export default function Topology() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Network className="h-8 w-8 text-accent" />
            Network Topology
          </h1>
          <p className="text-muted-foreground mt-1">
            Visualize the network structure and node connections
          </p>
        </div>

        {/* Placeholder for topology visualization */}
        <Card className="glass-card border-border">
          <CardHeader>
            <CardTitle>Network Graph</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[500px] flex flex-col items-center justify-center text-center">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 rounded-full blur-3xl animate-pulse" />
                <Network className="h-24 w-24 text-primary relative" />
              </div>
              <h3 className="text-xl font-semibold mt-6">Coming Soon</h3>
              <p className="text-muted-foreground mt-2 max-w-md">
                Interactive network topology visualization showing node connections, 
                geographic distribution, and real-time network activity.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Placeholder Stats */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="glass-card border-border">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-primary/10 p-3">
                  <Server className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">—</p>
                  <p className="text-xs text-muted-foreground">Total Nodes</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="glass-card border-border">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-accent/10 p-3">
                  <Link2 className="h-5 w-5 text-accent" />
                </div>
                <div>
                  <p className="text-2xl font-bold">—</p>
                  <p className="text-xs text-muted-foreground">Connections</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="glass-card border-border">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-success/10 p-3">
                  <Globe className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="text-2xl font-bold">—</p>
                  <p className="text-xs text-muted-foreground">Regions</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="glass-card border-border">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-warning/10 p-3">
                  <Network className="h-5 w-5 text-warning" />
                </div>
                <div>
                  <p className="text-2xl font-bold">—</p>
                  <p className="text-xs text-muted-foreground">Avg Degree</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
