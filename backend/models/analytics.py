"""
Pydantic models for Analytics API responses.

These models define the aggregate analytics computed
across all 100 graphs and their timesteps.
"""

from pydantic import BaseModel, Field


class FailureDistribution(BaseModel):
    """Distribution of node health statuses across all graphs."""

    healthy: int = Field(..., description="Total healthy node-timestep instances")
    warning: int = Field(..., description="Total warning node-timestep instances")
    unstable: int = Field(..., description="Total unstable node-timestep instances")
    failed: int = Field(..., description="Total failed node-timestep instances")


class GraphFailureFrequency(BaseModel):
    """Failure count for a single graph."""

    graph_id: int
    total_failures: int
    failure_rate: float


class ResourceUtilization(BaseModel):
    """Average resource metrics across all nodes."""

    avg_cpu: float
    avg_memory: float
    avg_gpu: float
    avg_disk_io: float
    avg_network_latency: float
    avg_temperature: float


class TemporalTrend(BaseModel):
    """Metrics at a specific timestep, averaged across all graphs."""

    timestep: int
    avg_failure_rate: float
    avg_anomaly_score: float
    avg_cpu_usage: float
    avg_latency: float
    total_failures: int
    total_nodes: int


class LatencyTrendPoint(BaseModel):
    """Latency data point for trend visualization."""

    graph_id: int
    timestep: int
    avg_latency: float
    max_latency: float
    min_latency: float


class AnalyticsResponse(BaseModel):
    """Complete analytics response for the dashboard."""

    total_graphs: int
    total_nodes: int
    total_edges: int
    total_timesteps: int
    overall_failure_rate: float
    overall_avg_anomaly: float

    failure_distribution: FailureDistribution
    failure_frequency: list[GraphFailureFrequency]
    resource_utilization: ResourceUtilization
    temporal_trends: list[TemporalTrend]
    latency_trends: list[LatencyTrendPoint]
