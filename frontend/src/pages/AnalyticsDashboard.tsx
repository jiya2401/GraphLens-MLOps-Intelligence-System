/**
 * Analytics Dashboard — charts and metrics overview using Recharts.
 */

import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Cpu, AlertTriangle, PieChart as PieChartIcon, Activity } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  AreaChart, Area,
  LineChart, Line,
  Legend,
} from 'recharts';
import { useAnalytics } from '../hooks/useAnalytics';
import { MetricCard } from '../components/common/MetricCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const COLORS = { healthy: '#10b981', warning: '#f59e0b', unstable: '#f97316', failed: '#ef4444' };
const tooltipStyle = { background: '#1a1f35', border: '1px solid rgba(148,163,184,0.1)', borderRadius: 8, fontSize: 12, color: '#f1f5f9' };

export function AnalyticsDashboard() {
  const { data, isLoading, error } = useAnalytics();

  if (isLoading) return <LoadingSpinner message="Computing analytics..." />;
  if (error) return <div className="text-red-400 text-center">{error}</div>;
  if (!data) return null;

  const pieData = [
    { name: 'Healthy', value: data.failure_distribution.healthy, color: COLORS.healthy },
    { name: 'Warning', value: data.failure_distribution.warning, color: COLORS.warning },
    { name: 'Unstable', value: data.failure_distribution.unstable, color: COLORS.unstable },
    { name: 'Failed', value: data.failure_distribution.failed, color: COLORS.failed },
  ];

  const failureFreqData = data.failure_frequency.slice(0, 30).map((f) => ({
    name: `#${f.graph_id}`,
    failures: f.total_failures,
    rate: f.failure_rate,
  }));

  const ru = data.resource_utilization;
  const resourceData = [
    { name: 'CPU', value: ru.avg_cpu },
    { name: 'Memory', value: ru.avg_memory },
    { name: 'GPU', value: ru.avg_gpu },
    { name: 'Disk I/O', value: Math.min(100, (ru.avg_disk_io / 250) * 100) },
    { name: 'Temp', value: Math.min(100, (ru.avg_temperature / 95) * 100) },
  ];

  return (
    <div className="space-y-6">
      <motion.h1 initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="text-xl font-bold gradient-text">
        Analytics Dashboard
      </motion.h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <MetricCard title="Total Graphs" value={data.total_graphs} icon={<BarChart3 size={16} />} color="#6366f1" />
        <MetricCard title="Total Nodes" value={data.total_nodes.toLocaleString()} icon={<Activity size={16} />} color="#8b5cf6" />
        <MetricCard title="Timesteps" value={data.total_timesteps} icon={<TrendingUp size={16} />} color="#a78bfa" />
        <MetricCard title="Failure Rate" value={`${(data.overall_failure_rate * 100).toFixed(1)}%`} icon={<AlertTriangle size={16} />} color="#ef4444" />
        <MetricCard title="Avg Anomaly" value={data.overall_avg_anomaly.toFixed(3)} icon={<PieChartIcon size={16} />} color="#f59e0b" />
        <MetricCard title="Avg CPU" value={`${ru.avg_cpu.toFixed(0)}%`} icon={<Cpu size={16} />} color="#10b981" />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Failure Distribution Pie */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card p-5">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Health Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={4} dataKey="value">
                  {pieData.map((entry, i) => (<Cell key={i} fill={entry.color} stroke="transparent" />))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Failure Frequency Bar */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card p-5">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Failure Frequency (per graph)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={failureFreqData}>
                <XAxis dataKey="name" tick={{ fontSize: 9 }} interval={2} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="failures" fill="#ef4444" radius={[4, 4, 0, 0]} opacity={0.8} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Temporal Trends */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card p-5">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Temporal Failure Trends</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.temporal_trends}>
                <XAxis dataKey="timestep" tick={{ fontSize: 10 }} tickFormatter={(v) => `T${v}`} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="avg_failure_rate" stroke="#ef4444" fill="#ef444420" strokeWidth={2} name="Failure Rate" />
                <Area type="monotone" dataKey="avg_anomaly_score" stroke="#f59e0b" fill="#f59e0b15" strokeWidth={2} name="Anomaly Score" />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Resource Utilization */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card p-5">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Resource Utilization</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={resourceData} layout="vertical">
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="name" width={60} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => `${v.toFixed(1)}%`} />
                <Bar dataKey="value" fill="#6366f1" radius={[0, 8, 8, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Latency Trends */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="card p-5 lg:col-span-2">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Latency Trends (sampled graphs)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.latency_trends}>
                <XAxis dataKey="timestep" tick={{ fontSize: 10 }} tickFormatter={(v) => `T${v}`} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Line type="monotone" dataKey="avg_latency" stroke="#8b5cf6" strokeWidth={2} dot={false} name="Avg Latency" />
                <Line type="monotone" dataKey="max_latency" stroke="#ef4444" strokeWidth={1} dot={false} name="Max" strokeDasharray="4 4" />
                <Line type="monotone" dataKey="min_latency" stroke="#10b981" strokeWidth={1} dot={false} name="Min" strokeDasharray="4 4" />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
