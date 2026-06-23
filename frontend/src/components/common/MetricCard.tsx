import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
}

export function MetricCard({ title, value, subtitle, icon, trend, color = 'var(--accent-primary)' }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-5"
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
          {title}
        </span>
        {icon && (
          <div className="p-2 rounded-lg" style={{ background: `${color}15`, color }}>
            {icon}
          </div>
        )}
      </div>
      <div className="flex items-end gap-2">
        <span className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
          {value}
        </span>
        {trend && (
          <span className={`text-sm font-medium mb-1 ${trend === 'up' ? 'text-red-400' : trend === 'down' ? 'text-emerald-400' : 'text-gray-400'}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>{subtitle}</p>
      )}
    </motion.div>
  );
}
