"""
Node Router — endpoint for detailed node information.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.models.graph import NodeDetailResponse
from backend.services import graph_service

router = APIRouter(prefix="/api", tags=["nodes"])


@router.get("/node/{node_id}", response_model=NodeDetailResponse)
async def get_node(
    node_id: str,
    graph_id: int = Query(default=0, ge=0, description="Graph ID"),
    timestep: int = Query(default=0, ge=0, description="Timestep"),
):
    """
    Get detailed information about a specific node,
    including its incoming and outgoing dependencies.
    """
    result = graph_service.get_node_detail(node_id, graph_id, timestep)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Node '{node_id}' not found in graph {graph_id} at t={timestep}",
        )
    return result
