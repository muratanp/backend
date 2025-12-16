import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { NodeTier } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function shortenAddress(address: string, chars = 6): string {
  if (!address) return '';
  if (address.length <= chars * 2 + 3) return address;
  return `${address.slice(0, chars)}...${address.slice(-chars)}`;
}

export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}

export function formatUptimeSeconds(seconds: number): string {
  const hours = seconds / 3600;
  if (hours < 24) return `${Math.round(hours)}h`;
  const days = Math.floor(hours / 24);
  const remainingHours = Math.round(hours % 24);
  if (days >= 30) {
    const months = Math.floor(days / 30);
    return `${months}mo ${days % 30}d`;
  }
  return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
}

export function formatUptime(hours: number): string {
  if (hours < 24) return `${Math.round(hours)}h`;
  const days = Math.floor(hours / 24);
  const remainingHours = Math.round(hours % 24);
  if (days >= 30) {
    const months = Math.floor(days / 30);
    return `${months}mo ${days % 30}d`;
  }
  return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toFixed(0);
}

export function getTierEmoji(tier: NodeTier): string {
  const emojis: Record<string, string> = {
    low_risk: '🟢',
    medium_risk: '🟡',
    high_risk: '🔴',
    legendary: '🏆',
    elite: '⭐',
    reliable: '✓',
    standard: '•',
    new: '🆕',
  };
  return emojis[tier] || '•';
}

export function getTierLabel(tier: NodeTier): string {
  const labels: Record<string, string> = {
    low_risk: 'Low Risk',
    medium_risk: 'Medium Risk',
    high_risk: 'High Risk',
    legendary: 'Legendary',
    elite: 'Elite',
    reliable: 'Reliable',
    standard: 'Standard',
    new: 'New',
  };
  return labels[tier] || 'Unknown';
}

export function getTierClass(tier: NodeTier): string {
  const classes: Record<string, string> = {
    low_risk: 'tier-low-risk',
    medium_risk: 'tier-medium-risk',
    high_risk: 'tier-high-risk',
    legendary: 'tier-legendary',
    elite: 'tier-elite',
    reliable: 'tier-reliable',
    standard: 'tier-standard',
    new: 'tier-new',
  };
  return classes[tier] || '';
}

export function getScoreColor(score: number): string {
  if (score >= 90) return 'text-success';
  if (score >= 75) return 'text-primary';
  if (score >= 50) return 'text-warning';
  return 'text-destructive';
}

export function getScoreBgClass(score: number): string {
  if (score >= 90) return 'score-excellent';
  if (score >= 75) return 'score-good';
  if (score >= 50) return 'score-fair';
  return 'score-poor';
}

export function getHealthStatusColor(status: string): string {
  const colors: Record<string, string> = {
    healthy: 'text-success',
    fair: 'text-primary',
    degraded: 'text-warning',
    critical: 'text-destructive',
  };
  return colors[status] || 'text-muted-foreground';
}

export function getHealthStatusEmoji(status: string): string {
  const emojis: Record<string, string> = {
    healthy: '🟢',
    fair: '🟡',
    degraded: '🟠',
    critical: '🔴',
  };
  return emojis[status] || '⚪';
}

export function timeAgo(timestamp: number): string {
  const seconds = Math.floor((Date.now() / 1000) - timestamp);
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

// Helper to extract score from either number or ScoreBreakdown
export function getScoreValue(score: number | { score: number; breakdown?: Record<string, number> }): number {
  if (typeof score === 'number') {
    return score;
  }
  return score.score;
}

// Helper to extract breakdown from ScoreBreakdown
export function getScoreBreakdown(score: number | { score: number; breakdown?: Record<string, number> }): Record<string, number> | null {
  if (typeof score === 'number') {
    return null;
  }
  return score.breakdown || null;
}
