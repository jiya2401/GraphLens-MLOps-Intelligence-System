"""
Simulation Router — endpoints for running simulations.
"""

from fastapi import APIRouter

from backend.models.simulation import (
    SimulationRequest,
    SimulationResponse,
    ReplayRequest,
)
from backend.models.graph import TimelineResponse
from backend.services import simulation_service, timeline_service

router = APIRouter(prefix="/api", tags=["simulation"])


@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """
    Run a new failure simulation with custom parameters.
    Uses the existing Python engine to generate a fresh graph,
    simulate failures, and return results.
    """
    result = simulation_service.run_simulation(
        num_nodes=request.num_nodes,
        failure_threshold_cpu=request.failure_threshold_cpu,
        failure_threshold_runtime=request.failure_threshold_runtime,
        propagation_enabled=request.propagation_enabled,
        propagation_strength=request.propagation_strength,
        num_timesteps=request.num_timesteps,
    )
    return result


@router.post("/replay", response_model=TimelineResponse)
async def replay_graph(request: ReplayRequest):
    """
    Get timeline data for replaying an existing graph.
    Same as GET /timeline/{graph_id} but using POST for
    additional configuration like playback speed.
    """
    from fastapi import HTTPException

    result = timeline_service.get_timeline(request.graph_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Graph {request.graph_id} not found for replay",
        )
    return result
