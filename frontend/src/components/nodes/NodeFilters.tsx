import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface NodeFiltersProps {
  status: string;
  sortBy: string;
  sortOrder: string;
  onStatusChange: (value: string) => void;
  onSortByChange: (value: string) => void;
  onSortOrderChange: (value: string) => void;
}

export function NodeFilters({
  status,
  sortBy,
  sortOrder,
  onStatusChange,
  onSortByChange,
  onSortOrderChange,
}: NodeFiltersProps) {
  return (
    <div className="flex flex-wrap gap-3">
      <Select value={status} onValueChange={onStatusChange}>
        <SelectTrigger className="w-[140px] bg-card border-border">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="online">Online Only</SelectItem>
          <SelectItem value="all">All Nodes</SelectItem>
          <SelectItem value="offline">Offline Only</SelectItem>
        </SelectContent>
      </Select>

      <Select value={sortBy} onValueChange={onSortByChange}>
        <SelectTrigger className="w-[140px] bg-card border-border">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="score">Score</SelectItem>
          <SelectItem value="uptime">Uptime</SelectItem>
          <SelectItem value="storage_used">Storage Used</SelectItem>
          <SelectItem value="last_seen">Last Seen</SelectItem>
        </SelectContent>
      </Select>

      <Select value={sortOrder} onValueChange={onSortOrderChange}>
        <SelectTrigger className="w-[140px] bg-card border-border">
          <SelectValue placeholder="Order" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="desc">Descending</SelectItem>
          <SelectItem value="asc">Ascending</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
