"""
Pydantic models for Simulation API requests and responses.

POST endpoints use request models to validate incoming data.
This is different from GET endpoints which use query parameters.

Interview Q: "When should you use POST vs GET?"
Answer: GET for reading data (idempotent). POST for actions that
create something or trigger computation (non-idempotent).
Simulation creates new data, so it's POST.
"""

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """Request body for POST /api/simulate."""

    num_nodes: int = Field(
        default=6, ge=3, le=12, description="Number of pipeline nodes (3-12)"
    )
    failure_threshold_cpu: int = Field(
        default=85, ge=50, le=100, description="CPU threshold for failure detection"
    )
    failure_threshold_runtime: int = Field(
        default=15, ge=5, le=60, description="Runtime threshold for failure detection"
    )
    propagation_enabled: bool = Field(
        default=True, description="Enable failure propagation"
    )
    propagation_strength: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Strength of failure propagation",
    )
    num_timesteps: int = Field(
        default=5, ge=1, le=20, description="Number of timesteps to simulate"
    )


class SimulationResponse(BaseModel):
    """Response from POST /api/simulate."""

    graph_id: str = Field(..., description="Generated simulation ID")
    num_nodes: int
    num_edges: int
    num_timesteps: int
    total_failures: int
    failure_rate: float
    propagated_failures: int
    recovery_events: int
    message: str = Field(default="Simulation completed successfully")


class ReplayRequest(BaseModel):
    """Request body for POST /api/replay."""

    graph_id: int = Field(..., ge=0, description="Graph ID to replay")
    speed: float = Field(
        default=1.0, ge=0.25, le=4.0, description="Replay speed multiplier"
    )
