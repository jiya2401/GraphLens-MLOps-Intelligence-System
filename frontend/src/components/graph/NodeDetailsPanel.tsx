/**
 * Node Details Panel — slide-out panel showing full node information.
 */

import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowDownToLine, ArrowUpFromLine } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar } from 'recharts';
import { useGraphStore } from '../../stores/graphStore';
import { StatusBadge } from '../common/StatusBadge';
import { NODE_TYPE_LABELS, SERVICE_NAME_LABELS } from '../../types/graph';

export function NodeDetailsPanel() {
  const { selectedNode, setSelectedNode, currentGraph } = useGraphStore();

  if (!selectedNode || !currentGraph) return null;

  const t = selectedNode.telemetry;
  const edges = currentGraph.edges;
  const incoming = edges.filter((e) => e.target === selectedNode.id).map((e) => e.source);
  const outgoing = edges.filter((e) => e.source === selectedNode.id).map((e) => e.target);

  const resourceData = [
    { name: 'CPU', value: t.cpu_usage, fill: t.cpu_usage > 80 ? '#ef4444' : '#6366f1' },
    { name: 'Memory', value: t.memory_usage, fill: t.memory_usage > 80 ? '#ef4444' : '#8b5cf6' },
    { name: 'GPU', value: t.gpu_usage, fill: '#a78bfa' },
  ];

  const gaugeData = [{ name: 'Anomaly', value: selectedNode.anomaly_score * 100, fill: selectedNode.anomaly_score > 0.7 ? '#ef4444' : selectedNode.anomaly_score > 0.4 ? '#f59e0b' : '#10b981' }];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: 400, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 400, opacity: 0 }}
        transition={{ type: 'spring', damping: 25 }}
        className="w-[380px] h-full overflow-y-auto border-l shrink-0"
        style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)' }}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between p-4 border-b" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border-subtle)' }}>
          <div>
            <h3 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>{selectedNode.id.replace(/_/g, ' ')}</h3>
            <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Node Details</p>
          </div>
          <button onClick={() => setSelectedNode(null)} className="p-1.5 rounded-lg hover:bg-white/5 transition-colors">
            <X size={16} style={{ color: 'var(--text-muted)' }} />
          </button>
        </div>

        <div className="p-4 space-y-5">
          {/* Status */}
          <div className="card p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Status</span>
              <StatusBadge status={selectedNode.health} />
            </div>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div><span style={{ color: 'var(--text-muted)' }}>Node Type</span><p className="font-medium mt-0.5" style={{ color: 'var(--text-primary)' }}>{NODE_TYPE_LABELS[t.node_type] || `Type ${t.node_type}`}</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Service</span><p className="font-medium mt-0.5" style={{ color: 'var(--text-primary)' }}>{SERVICE_NAME_LABELS[t.service_name] || `Service ${t.service_name}`}</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Runtime</span><p className="font-mono font-medium mt-0.5" style={{ color: 'var(--text-primary)' }}>{t.runtime}s</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Throughput</span><p className="font-mono font-medium mt-0.5" style={{ color: 'var(--text-primary)' }}>{t.throughput}/s</p></div>
            </div>
          </div>

          {/* Resource Usage Chart */}
          <div className="card p-4">
            <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Resource Usage</span>
            <div className="mt-3 h-28">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={resourceData} layout="vertical" margin={{ left: 0, right: 10 }}>
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis type="category" dataKey="name" width={55} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                  <Tooltip contentStyle={{ background: '#1a1f35', border: '1px solid rgba(148,163,184,0.1)', borderRadius: 8, fontSize: 12 }} />
                  <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={16} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Anomaly Score Gauge */}
          <div className="card p-4">
            <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Anomaly Score</span>
            <div className="mt-2 h-32 flex items-center justify-center">
              <ResponsiveContainer width={140} height={140}>
                <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" startAngle={180} endAngle={0} data={gaugeData}>
                  <RadialBar dataKey="value" cornerRadius={10} />
                </RadialBarChart>
              </ResponsiveContainer>
              <span className="absolute text-2xl font-bold" style={{ color: gaugeData[0].fill }}>{selectedNode.anomaly_score.toFixed(2)}</span>
            </div>
          </div>

          {/* Failure Metrics */}
          <div className="card p-4">
            <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Failure Metrics</span>
            <div className="grid grid-cols-2 gap-3 mt-3 text-xs">
              <div><span style={{ color: 'var(--text-muted)' }}>Timeouts</span><p className="font-mono text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{t.timeout_count}</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Retries</span><p className="font-mono text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{t.retry_count}</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Failure Rate</span><p className="font-mono text-lg font-bold" style={{ color: t.previous_failure_rate > 0.3 ? 'var(--status-failed)' : 'var(--text-primary)' }}>{(t.previous_failure_rate * 100).toFixed(1)}%</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Dep. Failures</span><p className="font-mono text-lg font-bold" style={{ color: 'var(--text-primary)' }}>{t.dependency_failure_count}</p></div>
            </div>
          </div>

          {/* Dependencies */}
          <div className="card p-4">
            <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Dependencies</span>
            <div className="mt-3 space-y-2">
              {incoming.length > 0 && (
                <div>
                  <div className="flex items-center gap-1.5 mb-1.5"><ArrowDownToLine size={12} className="text-blue-400" /><span className="text-xs font-medium text-blue-400">Incoming ({incoming.length})</span></div>
                  <div className="flex flex-wrap gap-1.5">{incoming.map((n) => (<span key={n} className="text-xs px-2 py-1 rounded-md" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>{n.replace(/_/g, ' ')}</span>))}</div>
                </div>
              )}
              {outgoing.length > 0 && (
                <div className="mt-2">
                  <div className="flex items-center gap-1.5 mb-1.5"><ArrowUpFromLine size={12} className="text-purple-400" /><span className="text-xs font-medium text-purple-400">Outgoing ({outgoing.length})</span></div>
                  <div className="flex flex-wrap gap-1.5">{outgoing.map((n) => (<span key={n} className="text-xs px-2 py-1 rounded-md" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>{n.replace(/_/g, ' ')}</span>))}</div>
                </div>
              )}
              {incoming.length === 0 && outgoing.length === 0 && (
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>No dependencies</p>
              )}
            </div>
          </div>

          {/* Infrastructure */}
          <div className="card p-4">
            <span className="text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>Infrastructure</span>
            <div className="grid grid-cols-2 gap-3 mt-3 text-xs">
              <div><span style={{ color: 'var(--text-muted)' }}>Pod Restarts</span><p className="font-mono font-medium" style={{ color: 'var(--text-primary)' }}>{t.pod_restart_count}</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Containers</span><p className="font-mono font-medium" style={{ color: 'var(--text-primary)' }}>{t.container_count}</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Disk I/O</span><p className="font-mono font-medium" style={{ color: 'var(--text-primary)' }}>{t.disk_io} MB/s</p></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Temperature</span><p className="font-mono font-medium" style={{ color: t.temperature > 85 ? 'var(--status-failed)' : 'var(--text-primary)' }}>{t.temperature}°C</p></div>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
