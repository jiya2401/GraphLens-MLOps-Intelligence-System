"""
Timeline Router — endpoint for temporal replay data.
"""

from fastapi import APIRouter, HTTPException

from backend.models.graph import TimelineResponse
from backend.services import timeline_service

router = APIRouter(prefix="/api", tags=["timeline"])


@router.get("/timeline/{graph_id}", response_model=TimelineResponse)
async def get_timeline(graph_id: int):
    """
    Get all timesteps for a graph, ordered for temporal replay.
    Returns the full timeline with nodes/edges at each timestep.
    """
    result = timeline_service.get_timeline(graph_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Timeline for graph {graph_id} not found",
        )
    return result
