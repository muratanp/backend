import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  trendUp?: boolean;
  status?: string;
  className?: string;
}

export function StatsCard({
  label,
  value,
  icon: Icon,
  trend,
  trendUp,
  status,
  className,
}: StatsCardProps) {
  return (
    <div className={cn('glass-card p-5 transition-all hover:border-primary/30', className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          <p className="text-3xl font-bold tracking-tight">{value}</p>
          {trend && (
            <p
              className={cn(
                'text-xs font-medium',
                trendUp ? 'text-success' : trendUp === false ? 'text-destructive' : 'text-muted-foreground'
              )}
            >
              {trend}
            </p>
          )}
          {status && (
            <p className="text-xs font-medium capitalize text-muted-foreground">
              Status: <span className="text-foreground">{status}</span>
            </p>
          )}
        </div>
        <div className="rounded-lg bg-primary/10 p-3">
          <Icon className="h-6 w-6 text-primary" />
        </div>
      </div>
    </div>
  );
}
