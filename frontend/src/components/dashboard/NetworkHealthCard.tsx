import { cn, getHealthStatusColor, getHealthStatusEmoji } from '@/lib/utils';
import { Activity } from 'lucide-react';

interface NetworkHealthCardProps {
  score: number;
  status: string;
}

export function NetworkHealthCard({ score, status }: NetworkHealthCardProps) {
  return (
    <div className="glass-card p-5 transition-all hover:border-primary/30">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">Network Health</p>
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-bold tracking-tight">{score}</p>
            <span className="text-lg text-muted-foreground">/100</span>
          </div>
          <p className={cn('text-sm font-medium capitalize flex items-center gap-1.5', getHealthStatusColor(status))}>
            {getHealthStatusEmoji(status)} {status}
          </p>
        </div>
        <div className={cn('rounded-lg p-3', 
          score >= 80 ? 'bg-success/10' : 
          score >= 60 ? 'bg-warning/10' : 
          'bg-destructive/10'
        )}>
          <Activity className={cn('h-6 w-6',
            score >= 80 ? 'text-success' : 
            score >= 60 ? 'text-warning' : 
            'text-destructive'
          )} />
        </div>
      </div>
    </div>
  );
}
