import { HEALTH_COLORS } from '../../types/graph';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
  showDot?: boolean;
}

export function StatusBadge({ status, size = 'md', showDot = true }: StatusBadgeProps) {
  const color = HEALTH_COLORS[status] || HEALTH_COLORS.unknown;
  const sizes = { sm: 'text-xs px-2 py-0.5', md: 'text-xs px-2.5 py-1', lg: 'text-sm px-3 py-1.5' };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizes[size]}`}
      style={{ background: `${color}18`, color, border: `1px solid ${color}30` }}
    >
      {showDot && <span className="w-1.5 h-1.5 rounded-full" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
