"""
Pydantic models for Graph-related API responses.

These models define the exact shape of data the API returns.
Pydantic validates that every response matches these schemas —
if a field is missing or the wrong type, the server returns a clear error.

Interview Q: "What is Pydantic and why is it important in FastAPI?"
Answer: Pydantic provides automatic data validation, serialization,
and OpenAPI schema generation. FastAPI uses it to validate both
incoming requests and outgoing responses at zero extra cost.
"""

from pydantic import BaseModel, Field


class Telemetry(BaseModel):
    """All 24 telemetry metrics for a pipeline node."""

    # Infrastructure metrics
    cpu_usage: int = Field(..., description="CPU utilization percentage (20-100)")
    memory_usage: int = Field(..., description="Memory utilization percentage (20-100)")
    gpu_usage: int = Field(..., description="GPU utilization percentage (0-100)")
    disk_io: int = Field(..., description="Disk I/O in MB/s (5-250)")
    network_latency: int = Field(..., description="Network latency in ms (1-200)")
    temperature: int = Field(..., description="Hardware temperature in °C (30-95)")

    # Execution metrics
    runtime: int = Field(..., description="Task runtime in seconds (1-120)")
    queue_delay: int = Field(..., description="Queue waiting time in seconds (0-45)")
    retry_count: int = Field(..., description="Number of retries (0-5)")
    throughput: int = Field(..., description="Records processed per second (50-2000)")
    batch_size: int = Field(..., description="Batch size (16-512)")

    # Pipeline metadata (encoded as integers)
    node_type: int = Field(..., description="Encoded node type category (0-5)")
    service_name: int = Field(..., description="Encoded service name category (0-5)")
    pipeline_stage: int = Field(..., description="Encoded pipeline stage (0-5)")
    execution_priority: int = Field(..., description="Execution priority (1-5)")

    # Failure signals
    anomaly_score: float = Field(..., description="Anomaly detection score (0.0-1.0)")
    timeout_count: int = Field(..., description="Number of timeouts (0-6)")
    previous_failure_rate: float = Field(
        ..., description="Historical failure rate (0.0-0.6)"
    )
    dependency_failure_count: int = Field(
        ..., description="Failed upstream dependencies (0-5)"
    )

    # Resource & scaling
    pod_restart_count: int = Field(..., description="Kubernetes pod restarts (0-6)")
    container_count: int = Field(..., description="Active containers (1-12)")
    autoscaling_events: int = Field(..., description="Autoscaling triggers (0-6)")

    # Data quality
    missing_value_ratio: float = Field(
        ..., description="Ratio of missing values (0.0-0.25)"
    )
    data_drift_score: float = Field(
        ..., description="Data distribution drift score (0.0-1.0)"
    )
    schema_validation_errors: int = Field(
        ..., description="Schema validation failures (0-6)"
    )


class GraphNode(BaseModel):
    """A single node in the pipeline graph."""

    id: str = Field(..., description="Node identifier (e.g., 'Data_Ingestion')")
    failed: bool = Field(..., description="Whether this node has failed")
    health: str = Field(
        ..., description="Health status: healthy, warning, unstable, failed"
    )
    instability: float = Field(
        ..., description="Instability score based on failure history (0.0-1.0)"
    )
    anomaly_score: float = Field(..., description="Current anomaly score (0.0-1.0)")
    runtime: int = Field(..., description="Current runtime in seconds")
    telemetry: Telemetry = Field(..., description="Full telemetry metrics")


class GraphEdge(BaseModel):
    """A directed edge between two nodes."""

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    propagation_risk: float | None = Field(
        None, description="Risk of failure propagation along this edge"
    )


class PropagationStats(BaseModel):
    """Aggregate failure propagation statistics for a graph snapshot."""

    total_nodes: int
    failed_nodes: int
    warning_nodes: int
    healthy_nodes: int
    failure_rate: float
    avg_anomaly_score: float


class TemporalStats(BaseModel):
    """Temporal metadata for a graph snapshot."""

    current_timestep: int
    total_timesteps: int
    timestep_range: list[int]
    avg_instability: float


class GraphResponse(BaseModel):
    """Full response for a single graph at a specific timestep."""

    graph_id: int
    timestep: int
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    propagation_stats: PropagationStats
    temporal_stats: TemporalStats


class GraphListItem(BaseModel):
    """Summary item for the graph listing endpoint."""

    graph_id: int
    total_nodes: int
    total_edges: int
    total_timesteps: int
    failure_rate: float
    avg_anomaly_score: float
    health_summary: dict[str, int] = Field(
        ..., description="Count of nodes by health status"
    )


class GraphListResponse(BaseModel):
    """Response for GET /api/graph — list of all graphs."""

    total_graphs: int
    graphs: list[GraphListItem]


class NodeDetailResponse(BaseModel):
    """Detailed node information including dependency context."""

    node: GraphNode
    graph_id: int
    timestep: int
    incoming_dependencies: list[str] = Field(
        ..., description="Nodes that feed into this node"
    )
    outgoing_dependencies: list[str] = Field(
        ..., description="Nodes that this node feeds into"
    )


class TimelineTimestep(BaseModel):
    """A single timestep in a timeline response."""

    timestep: int
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    propagation_stats: PropagationStats


class TimelineResponse(BaseModel):
    """Full timeline for temporal replay of a graph."""

    graph_id: int
    total_timesteps: int
    timesteps: list[TimelineTimestep]
