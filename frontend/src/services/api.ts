/**
 * API Service Layer — centralized HTTP client.
 *
 * All API calls go through this file. This is the "API service layer" pattern.
 *
 * Benefits:
 * 1. Single place to change base URL, headers, auth tokens
 * 2. Centralized error handling
 * 3. Type-safe responses using generics
 * 4. Easy to mock in tests
 *
 * Interview Q: "Why not call fetch() directly in components?"
 * Answer: Violates DRY (Don't Repeat Yourself). If the API URL changes,
 * you'd have to update every component. With a service layer, you change
 * one file. Also enables centralized error handling and request interceptors.
 */

import type { GraphData, GraphListResponse, NodeDetail, TimelineData } from '../types/graph';
import type { AnalyticsData, PredictionData, RootCauseData } from '../types/analytics';

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling and JSON parsing.
 * The <T> is a TypeScript generic — it means "this function returns
 * whatever type you tell it". So fetchApi<GraphData>('/graph/0')
 * returns a Promise<GraphData>.
 */
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`API Error ${response.status}: ${errorBody}`);
    }

    return await response.json() as T;
  } catch (error) {
    if (error instanceof Error) {
      console.error(`[API] ${endpoint} failed:`, error.message);
      throw error;
    }
    throw new Error(`[API] Unknown error at ${endpoint}`);
  }
}

// ============================================================
// Graph Endpoints
// ============================================================

export async function fetchGraphList(): Promise<GraphListResponse> {
  return fetchApi<GraphListResponse>('/graph');
}

export async function fetchGraph(graphId: number, timestep = 0): Promise<GraphData> {
  return fetchApi<GraphData>(`/graph/${graphId}?timestep=${timestep}`);
}

export async function fetchNodeDetail(
  nodeId: string,
  graphId = 0,
  timestep = 0,
): Promise<NodeDetail> {
  return fetchApi<NodeDetail>(
    `/node/${encodeURIComponent(nodeId)}?graph_id=${graphId}&timestep=${timestep}`,
  );
}

// ============================================================
// Timeline Endpoints
// ============================================================

export async function fetchTimeline(graphId: number): Promise<TimelineData> {
  return fetchApi<TimelineData>(`/timeline/${graphId}`);
}

// ============================================================
// Analytics Endpoints
// ============================================================

export async function fetchAnalytics(): Promise<AnalyticsData> {
  return fetchApi<AnalyticsData>('/analytics');
}

// ============================================================
// Simulation Endpoints
// ============================================================

export interface SimulationRequest {
  num_nodes?: number;
  failure_threshold_cpu?: number;
  failure_threshold_runtime?: number;
  propagation_enabled?: boolean;
  propagation_strength?: number;
  num_timesteps?: number;
}

export interface SimulationResponse {
  graph_id: string;
  num_nodes: number;
  num_edges: number;
  num_timesteps: number;
  total_failures: number;
  failure_rate: number;
  propagated_failures: number;
  recovery_events: number;
  message: string;
}

export async function runSimulation(params: SimulationRequest): Promise<SimulationResponse> {
  return fetchApi<SimulationResponse>('/simulate', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

// ============================================================
// Prediction Endpoints
// ============================================================

export async function fetchPredictions(graphId: number, timestep = 0): Promise<PredictionData> {
  return fetchApi<PredictionData>('/predict', {
    method: 'POST',
    body: JSON.stringify({ graph_id: graphId, timestep }),
  });
}

export async function fetchRootCause(graphId: number, timestep = 0): Promise<RootCauseData> {
  return fetchApi<RootCauseData>('/root-cause', {
    method: 'POST',
    body: JSON.stringify({ graph_id: graphId, timestep }),
  });
}
