import { AlertTriangle, X } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { AlertsResponse } from '@/lib/types';

interface AlertBannerProps {
  alerts: AlertsResponse | null;
}

export function AlertBanner({ alerts }: AlertBannerProps) {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed || !alerts || alerts.critical_nodes.length === 0) {
    return null;
  }

  return (
    <div className="relative rounded-lg border border-destructive/50 bg-destructive/10 p-4">
      <button
        onClick={() => setDismissed(true)}
        className="absolute right-3 top-3 text-muted-foreground hover:text-foreground transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-destructive mt-0.5" />
        <div>
          <h4 className="font-semibold text-destructive">Critical Issues Detected</h4>
          <p className="text-sm text-muted-foreground mt-1">
            {alerts.critical_nodes.length} node{alerts.critical_nodes.length !== 1 ? 's' : ''} need immediate attention.
            Total of {alerts.summary.critical} critical and {alerts.summary.warning} warning alerts.
          </p>
          <Link
            to="/nodes?status=all"
            className="inline-flex items-center text-sm font-medium text-destructive hover:underline mt-2"
          >
            View affected nodes →
          </Link>
        </div>
      </div>
    </div>
  );
}
