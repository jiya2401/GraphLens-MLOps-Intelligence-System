/**
 * Custom React Flow Node — the visual representation of each pipeline node.
 *
 * This is a key React Flow concept: Custom Nodes.
 * Instead of using the default rectangle, we create a rich component
 * showing service name, health status, and key metrics.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { motion } from 'framer-motion';
import { HEALTH_COLORS } from '../../types/graph';
import { Cpu, MemoryStick, Timer, Activity } from 'lucide-react';

interface CustomNodeData {
  label: string;
  health: string;
  failed: boolean;
  cpu_usage: number;
  memory_usage: number;
  latency: number;
  anomaly_score: number;
  isSelected: boolean;
  isSearchMatch: boolean;
  isFiltered: boolean;
  [key: string]: unknown;
}

function CustomNodeComponent({ data }: NodeProps) {
  const d = data as unknown as CustomNodeData;
  const color = HEALTH_COLORS[d.health] || HEALTH_COLORS.unknown;
  const dimmed = d.isFiltered ? 0.3 : 1;

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: dimmed }}
      whileHover={{ scale: 1.05 }}
      className={`relative rounded-2xl p-4 cursor-pointer transition-all duration-200 ${d.failed ? 'animate-pulse-red' : ''}`}
      style={{
        background: 'var(--bg-card)',
        border: `2px solid ${d.isSelected ? 'var(--accent-primary)' : color}`,
        boxShadow: d.isSelected
          ? `0 0 24px var(--accent-primary), var(--shadow-card)`
          : d.isSearchMatch
          ? `0 0 16px ${color}`
          : 'var(--shadow-card)',
        minWidth: 180,
      }}
    >
      {/* Connection handles */}
      <Handle type="target" position={Position.Left} className="!w-2.5 !h-2.5 !rounded-full !border-2" style={{ background: color, borderColor: 'var(--bg-primary)' }} />
      <Handle type="source" position={Position.Right} className="!w-2.5 !h-2.5 !rounded-full !border-2" style={{ background: color, borderColor: 'var(--bg-primary)' }} />

      {/* Status indicator */}
      <div className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full border-2" style={{ background: color, borderColor: 'var(--bg-primary)', boxShadow: `0 0 8px ${color}` }} />

      {/* Node name */}
      <div className="flex items-center gap-2 mb-3">
        <Activity size={14} style={{ color }} />
        <span className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>
          {d.label?.replace(/_/g, ' ')}
        </span>
      </div>

      {/* Mini metrics grid */}
      <div className="grid grid-cols-2 gap-2">
        <div className="flex items-center gap-1.5">
          <Cpu size={11} style={{ color: 'var(--text-muted)' }} />
          <span className="text-[11px] font-mono" style={{ color: d.cpu_usage > 80 ? 'var(--status-warning)' : 'var(--text-secondary)' }}>
            {d.cpu_usage}%
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <MemoryStick size={11} style={{ color: 'var(--text-muted)' }} />
          <span className="text-[11px] font-mono" style={{ color: 'var(--text-secondary)' }}>
            {d.memory_usage}%
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <Timer size={11} style={{ color: 'var(--text-muted)' }} />
          <span className="text-[11px] font-mono" style={{ color: 'var(--text-secondary)' }}>
            {d.latency}ms
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <Activity size={11} style={{ color: 'var(--text-muted)' }} />
          <span className="text-[11px] font-mono" style={{ color: d.anomaly_score > 0.7 ? 'var(--status-failed)' : 'var(--text-secondary)' }}>
            {d.anomaly_score?.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Health label */}
      <div className="mt-3 pt-2 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
        <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color }}>
          {d.health}
        </span>
      </div>
    </motion.div>
  );
}

export const CustomNode = memo(CustomNodeComponent);
