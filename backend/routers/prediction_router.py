"""
Prediction Router — endpoints for failure prediction and root cause analysis.
"""

from fastapi import APIRouter

from backend.models.prediction import (
    PredictionRequest,
    PredictionResponse,
    RootCauseRequest,
    RootCauseResponse,
)
from backend.services import simulation_service

router = APIRouter(prefix="/api", tags=["prediction"])


@router.post("/predict", response_model=PredictionResponse)
async def predict_failures(request: PredictionRequest):
    """
    Predict failure probabilities for nodes in a graph.
    Currently uses heuristic-based prediction.
    Will be upgraded to GNN-based prediction in the future.
    """
    return simulation_service.predict_failures(request.graph_id, request.timestep)


@router.post("/root-cause", response_model=RootCauseResponse)
async def analyze_root_cause(request: RootCauseRequest):
    """
    Analyze potential root causes of failures in a graph.
    Identifies upstream nodes most likely to be the origin of issues.
    """
    return simulation_service.analyze_root_cause(request.graph_id, request.timestep)
