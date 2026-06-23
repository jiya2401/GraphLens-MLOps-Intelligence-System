/**
 * Temporal Replay Page — timeline playback of graph evolution.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, SkipBack, SkipForward, Clock, Gauge } from 'lucide-react';
import { useTimeline } from '../hooks/useTimeline';
import { useTimelineStore } from '../stores/timelineStore';
import { GraphCanvas } from '../components/graph/GraphCanvas';
import { NodeDetailsPanel } from '../components/graph/NodeDetailsPanel';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { useGraphStore } from '../stores/graphStore';
import type { GraphData } from '../types/graph';

export function TemporalReplay() {
  const [graphId, setGraphId] = useState(0);
  const { timelineData } = useTimeline(graphId);
  const { currentTimestep, isPlaying, playbackSpeed, setIsPlaying, setPlaybackSpeed, nextTimestep, prevTimestep, setCurrentTimestep } = useTimelineStore();
  const { selectedNode } = useGraphStore();

  if (!timelineData) return <LoadingSpinner message="Loading timeline..." />;

  const currentData = timelineData.timesteps[currentTimestep];
  if (!currentData) return <LoadingSpinner message="Loading timestep..." />;

  // Construct a GraphData object for GraphCanvas
  const graphData: GraphData = {
    graph_id: graphId,
    timestep: currentTimestep,
    nodes: currentData.nodes,
    edges: currentData.edges,
    propagation_stats: currentData.propagation_stats,
    temporal_stats: { current_timestep: currentTimestep, total_timesteps: timelineData.total_timesteps, timestep_range: [0, timelineData.total_timesteps - 1], avg_instability: 0 },
  };

  const ps = currentData.propagation_stats;

  return (
    <div className="h-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <motion.h1 initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="text-xl font-bold gradient-text">
          Temporal Replay Engine
        </motion.h1>
        <select
          value={graphId}
          onChange={(e) => setGraphId(Number(e.target.value))}
          className="px-3 py-2 rounded-lg text-sm outline-none"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
        >
          {Array.from({ length: 100 }, (_, i) => (
            <option key={i} value={i}>Graph #{i}</option>
          ))}
        </select>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-4 gap-3">
        <MetricCard title="Timestep" value={`${currentTimestep + 1} / ${timelineData.total_timesteps}`} icon={<Clock size={16} />} color="#6366f1" />
        <MetricCard title="Failed Nodes" value={ps.failed_nodes} icon={<Gauge size={16} />} color="#ef4444" />
        <MetricCard title="Warning" value={ps.warning_nodes} color="#f59e0b" />
        <MetricCard title="Healthy" value={ps.healthy_nodes} color="#10b981" />
      </div>

      {/* Timeline Scrubber */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          {/* Controls */}
          <div className="flex items-center gap-2">
            <button onClick={prevTimestep} className="p-2 rounded-lg hover:bg-white/5 transition-colors" style={{ color: 'var(--text-secondary)' }}><SkipBack size={18} /></button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-3 rounded-xl transition-all"
              style={{ background: 'var(--accent-gradient)', color: 'white', boxShadow: 'var(--shadow-glow)' }}
            >
              {isPlaying ? <Pause size={18} /> : <Play size={18} />}
            </button>
            <button onClick={nextTimestep} className="p-2 rounded-lg hover:bg-white/5 transition-colors" style={{ color: 'var(--text-secondary)' }}><SkipForward size={18} /></button>
          </div>

          {/* Scrubber */}
          <div className="flex-1">
            <div className="flex justify-between mb-2">
              {timelineData.timesteps.map((ts, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentTimestep(i)}
                  className="flex flex-col items-center gap-1 group"
                >
                  <span className={`w-3 h-3 rounded-full transition-all ${i === currentTimestep ? 'scale-125' : 'scale-100 opacity-50 group-hover:opacity-100'}`}
                    style={{ background: i <= currentTimestep ? 'var(--accent-primary)' : 'var(--text-muted)', boxShadow: i === currentTimestep ? 'var(--shadow-glow)' : 'none' }}
                  />
                  <span className="text-[10px] font-mono" style={{ color: i === currentTimestep ? 'var(--text-primary)' : 'var(--text-muted)' }}>T{i}</span>
                  {ts.propagation_stats.failed_nodes > 0 && (
                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--status-failed)' }} />
                  )}
                </button>
              ))}
            </div>
            <div className="h-1 rounded-full overflow-hidden" style={{ background: 'var(--bg-card)' }}>
              <motion.div
                className="h-full rounded-full"
                style={{ background: 'var(--accent-gradient)' }}
                animate={{ width: `${((currentTimestep + 1) / timelineData.total_timesteps) * 100}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>

          {/* Speed Control */}
          <select
            value={playbackSpeed}
            onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
            className="px-2 py-1.5 rounded-lg text-xs outline-none"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}
          >
            <option value={0.5}>0.5×</option>
            <option value={1}>1×</option>
            <option value={2}>2×</option>
            <option value={4}>4×</option>
          </select>
        </div>

        {/* Node status indicators */}
        <div className="flex gap-2 mt-3 flex-wrap">
          {currentData.nodes.map((node) => (
            <StatusBadge key={node.id} status={node.health} size="sm" />
          ))}
        </div>
      </div>

      {/* Graph View */}
      <div className="flex-1 flex min-h-0 rounded-xl overflow-hidden" style={{ border: '1px solid var(--border-subtle)' }}>
        <div className="flex-1"><GraphCanvas graphData={graphData} /></div>
        {selectedNode && <NodeDetailsPanel />}
      </div>
    </div>
  );
}
