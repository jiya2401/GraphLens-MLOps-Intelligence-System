/**
 * TypeScript type definitions for Graph data.
 *
 * These types mirror the Pydantic models on the backend.
 * When the API returns data, TypeScript uses these to ensure
 * we handle it correctly — catching typos and missing fields.
 *
 * Interview Q: "Why define types for API responses?"
 * Answer: Type safety at the boundary between frontend and backend.
 * Without types, a backend field rename silently breaks the UI.
 * With types, TypeScript catches it at compile time.
 */

export interface Telemetry {
  cpu_usage: number;
  memory_usage: number;
  gpu_usage: number;
  disk_io: number;
  network_latency: number;
  temperature: number;
  runtime: number;
  queue_delay: number;
  retry_count: number;
  throughput: number;
  batch_size: number;
  node_type: number;
  service_name: number;
  pipeline_stage: number;
  execution_priority: number;
  anomaly_score: number;
  timeout_count: number;
  previous_failure_rate: number;
  dependency_failure_count: number;
  pod_restart_count: number;
  container_count: number;
  autoscaling_events: number;
  missing_value_ratio: number;
  data_drift_score: number;
  schema_validation_errors: number;
}

export interface GraphNode {
  id: string;
  failed: boolean;
  health: 'healthy' | 'warning' | 'unstable' | 'failed';
  instability: number;
  anomaly_score: number;
  runtime: number;
  telemetry: Telemetry;
}

export interface GraphEdge {
  source: string;
  target: string;
  propagation_risk: number | null;
}

export interface PropagationStats {
  total_nodes: number;
  failed_nodes: number;
  warning_nodes: number;
  healthy_nodes: number;
  failure_rate: number;
  avg_anomaly_score: number;
}

export interface TemporalStats {
  current_timestep: number;
  total_timesteps: number;
  timestep_range: number[];
  avg_instability: number;
}

export interface GraphData {
  graph_id: number;
  timestep: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
  propagation_stats: PropagationStats;
  temporal_stats: TemporalStats;
}

export interface GraphListItem {
  graph_id: number;
  total_nodes: number;
  total_edges: number;
  total_timesteps: number;
  failure_rate: number;
  avg_anomaly_score: number;
  health_summary: Record<string, number>;
}

export interface GraphListResponse {
  total_graphs: number;
  graphs: GraphListItem[];
}

export interface NodeDetail {
  node: GraphNode;
  graph_id: number;
  timestep: number;
  incoming_dependencies: string[];
  outgoing_dependencies: string[];
}

export interface TimelineTimestep {
  timestep: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
  propagation_stats: PropagationStats;
}

export interface TimelineData {
  graph_id: number;
  total_timesteps: number;
  timesteps: TimelineTimestep[];
}

// Node type labels for display
export const NODE_TYPE_LABELS: Record<number, string> = {
  0: 'Data Ingestion',
  1: 'Data Cleaning',
  2: 'Feature Engineering',
  3: 'Model Training',
  4: 'Evaluation',
  5: 'Deployment',
};

export const SERVICE_NAME_LABELS: Record<number, string> = {
  0: 'Ingestion Service',
  1: 'Cleaning Service',
  2: 'Feature Store',
  3: 'Training Service',
  4: 'Evaluation Service',
  5: 'Deployment Service',
};

export const HEALTH_COLORS: Record<string, string> = {
  healthy: '#10b981',
  warning: '#f59e0b',
  failed: '#ef4444',
  unstable: '#f97316',
  unknown: '#6b7280',
  root_cause: '#3b82f6',
};
