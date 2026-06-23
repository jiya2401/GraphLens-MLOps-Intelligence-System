/**
 * TypeScript types for Analytics data.
 */

export interface FailureDistribution {
  healthy: number;
  warning: number;
  unstable: number;
  failed: number;
}

export interface GraphFailureFrequency {
  graph_id: number;
  total_failures: number;
  failure_rate: number;
}

export interface ResourceUtilization {
  avg_cpu: number;
  avg_memory: number;
  avg_gpu: number;
  avg_disk_io: number;
  avg_network_latency: number;
  avg_temperature: number;
}

export interface TemporalTrend {
  timestep: number;
  avg_failure_rate: number;
  avg_anomaly_score: number;
  avg_cpu_usage: number;
  avg_latency: number;
  total_failures: number;
  total_nodes: number;
}

export interface LatencyTrendPoint {
  graph_id: number;
  timestep: number;
  avg_latency: number;
  max_latency: number;
  min_latency: number;
}

export interface AnalyticsData {
  total_graphs: number;
  total_nodes: number;
  total_edges: number;
  total_timesteps: number;
  overall_failure_rate: number;
  overall_avg_anomaly: number;
  failure_distribution: FailureDistribution;
  failure_frequency: GraphFailureFrequency[];
  resource_utilization: ResourceUtilization;
  temporal_trends: TemporalTrend[];
  latency_trends: LatencyTrendPoint[];
}

export interface NodePrediction {
  node_id: string;
  failure_probability: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  contributing_factors: string[];
}

export interface PredictionData {
  graph_id: number;
  timestep: number;
  predictions: NodePrediction[];
  model_type: string;
  confidence: number;
}

export interface RootCauseNode {
  node_id: string;
  root_cause_score: number;
  evidence: string[];
  affected_nodes: string[];
}

export interface RootCauseData {
  graph_id: number;
  timestep: number;
  root_causes: RootCauseNode[];
  analysis_method: string;
}
