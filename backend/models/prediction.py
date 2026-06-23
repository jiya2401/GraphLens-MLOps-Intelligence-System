"""
Pydantic models for Prediction and Root Cause Analysis.

These are placeholders prepared for future GNN model integration.
Currently they return heuristic-based predictions using telemetry data.

Interview Q: "How would you prepare a web app for ML model integration?"
Answer: Define clear API contracts (request/response schemas) first,
serve heuristic baselines, then swap in the ML model later.
The frontend doesn't change — only the backend prediction logic does.
"""

from pydantic import BaseModel, Field


class NodePrediction(BaseModel):
    """Failure prediction for a single node."""

    node_id: str
    failure_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Predicted failure probability"
    )
    risk_level: str = Field(
        ..., description="Risk level: low, medium, high, critical"
    )
    contributing_factors: list[str] = Field(
        ..., description="Top features driving the prediction"
    )


class PredictionRequest(BaseModel):
    """Request body for POST /api/predict."""

    graph_id: int = Field(..., ge=0, description="Graph ID to predict on")
    timestep: int = Field(default=0, ge=0, description="Timestep to predict from")


class PredictionResponse(BaseModel):
    """Response from POST /api/predict."""

    graph_id: int
    timestep: int
    predictions: list[NodePrediction]
    model_type: str = Field(
        default="heuristic", description="Model type: heuristic or gnn"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall model confidence"
    )


class RootCauseNode(BaseModel):
    """A node identified as a potential root cause."""

    node_id: str
    root_cause_score: float = Field(
        ..., ge=0.0, le=1.0, description="Root cause likelihood score"
    )
    evidence: list[str] = Field(
        ..., description="Evidence supporting this root cause"
    )
    affected_nodes: list[str] = Field(
        ..., description="Downstream nodes affected by this root cause"
    )


class RootCauseRequest(BaseModel):
    """Request body for POST /api/root-cause."""

    graph_id: int = Field(..., ge=0, description="Graph ID to analyze")
    timestep: int = Field(default=0, ge=0, description="Timestep to analyze")


class RootCauseResponse(BaseModel):
    """Response from POST /api/root-cause."""

    graph_id: int
    timestep: int
    root_causes: list[RootCauseNode]
    analysis_method: str = Field(
        default="heuristic", description="Analysis method used"
    )
