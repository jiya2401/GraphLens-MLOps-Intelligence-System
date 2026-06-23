/**
 * Graph Explorer Page — the main graph visualization dashboard.
 */

import { motion } from 'framer-motion';
import { Network, AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';
import { useGraphData } from '../hooks/useGraphData';
import { useGraphStore } from '../stores/graphStore';
import { GraphCanvas } from '../components/graph/GraphCanvas';
import { NodeDetailsPanel } from '../components/graph/NodeDetailsPanel';
import { MetricCard } from '../components/common/MetricCard';
import { SearchBar } from '../components/common/SearchBar';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export function GraphExplorer() {
  const { currentGraph, isLoading, error } = useGraphData();
  const { graphs, selectedGraphId, setSelectedGraphId, searchQuery, setSearchQuery, healthFilter, toggleHealthFilter, selectedNode } = useGraphStore();

  if (error) return <div className="flex items-center justify-center h-full text-red-400">{error}</div>;

  const ps = currentGraph?.propagation_stats;
  const healthFilters = ['healthy', 'warning', 'unstable', 'failed'];
  const healthColors: Record<string, string> = { healthy: '#10b981', warning: '#f59e0b', unstable: '#f97316', failed: '#ef4444' };

  return (
    <div className="h-full flex flex-col gap-4">
      {/* Header + Controls */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <motion.h1 initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="text-xl font-bold gradient-text">
          Graph Explorer
        </motion.h1>
        <div className="flex items-center gap-3">
          {/* Graph Selector */}
          <select
            value={selectedGraphId}
            onChange={(e) => setSelectedGraphId(Number(e.target.value))}
            className="px-3 py-2 rounded-lg text-sm outline-none cursor-pointer"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
          >
            {graphs.map((g) => (
              <option key={g.graph_id} value={g.graph_id}>Graph #{g.graph_id} ({g.total_nodes} nodes)</option>
            ))}
          </select>
          <div className="w-56">
            <SearchBar value={searchQuery} onChange={setSearchQuery} placeholder="Search nodes..." />
          </div>
          {/* Health Filters */}
          <div className="flex gap-1.5">
            {healthFilters.map((h) => (
              <button
                key={h}
                onClick={() => toggleHealthFilter(h)}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all"
                style={{
                  background: healthFilter.includes(h) ? `${healthColors[h]}20` : 'var(--bg-card)',
                  border: `1px solid ${healthFilter.includes(h) ? healthColors[h] : 'var(--border-subtle)'}`,
                  color: healthFilter.includes(h) ? healthColors[h] : 'var(--text-muted)',
                }}
              >
                {h}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      {ps && (
        <div className="grid grid-cols-4 gap-3">
          <MetricCard title="Total Nodes" value={ps.total_nodes} icon={<Network size={16} />} color="#6366f1" />
          <MetricCard title="Healthy" value={ps.healthy_nodes} icon={<CheckCircle size={16} />} color="#10b981" />
          <MetricCard title="Warnings" value={ps.warning_nodes} icon={<AlertCircle size={16} />} color="#f59e0b" />
          <MetricCard title="Failed" value={ps.failed_nodes} icon={<AlertTriangle size={16} />} color="#ef4444" />
        </div>
      )}

      {/* Graph + Details Panel */}
      <div className="flex-1 flex gap-0 min-h-0 rounded-xl overflow-hidden" style={{ border: '1px solid var(--border-subtle)' }}>
        {isLoading ? (
          <div className="flex-1"><LoadingSpinner message="Loading graph..." /></div>
        ) : currentGraph ? (
          <div className="flex-1"><GraphCanvas graphData={currentGraph} /></div>
        ) : (
          <div className="flex-1 flex items-center justify-center" style={{ color: 'var(--text-muted)' }}>Select a graph</div>
        )}
        {selectedNode && <NodeDetailsPanel />}
      </div>
    </div>
  );
}
