import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { format } from 'date-fns';
import type { NetworkSnapshot } from '@/lib/types';

interface NetworkGrowthChartProps {
  data: NetworkSnapshot[];
  isLoading?: boolean;
}

export function NetworkGrowthChart({ data, isLoading }: NetworkGrowthChartProps) {
  if (isLoading) {
    return (
      <div className="glass-card p-5">
        <h3 className="font-semibold mb-4">Network Growth (24h)</h3>
        <div className="h-[300px] flex items-center justify-center">
          <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        </div>
      </div>
    );
  }

  const chartData = data.map((snapshot) => ({
    timestamp: snapshot.timestamp * 1000,
    nodes: snapshot.total_pnodes,
    online: snapshot.online_pnodes,
    peers: snapshot.avg_peer_count,
  }));

  return (
    <div className="glass-card p-5">
      <h3 className="font-semibold mb-4">Network Growth (24h)</h3>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(ts) => format(ts, 'HH:mm')}
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
            />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
            />
            <Tooltip
              labelFormatter={(ts) => format(ts as number, 'MMM d, HH:mm')}
              contentStyle={{
                backgroundColor: 'hsl(var(--popover))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                color: 'hsl(var(--popover-foreground))',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="nodes"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
              name="Total Nodes"
            />
            <Line
              type="monotone"
              dataKey="online"
              stroke="hsl(var(--accent))"
              strokeWidth={2}
              dot={false}
              name="Online"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
