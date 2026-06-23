"""
Graph Router — endpoints for graph data access.

FastAPI routers group related endpoints together.
Think of them like Express.js Router or Django URL patterns.

Interview Q: "What is an APIRouter in FastAPI?"
Answer: A way to organize endpoints into logical groups.
Each router can have its own prefix, tags, and dependencies.
The main app includes them via app.include_router().
"""

from fastapi import APIRouter, HTTPException, Query

from backend.models.graph import (
    GraphResponse,
    GraphListResponse,
    NodeDetailResponse,
)
from backend.services import graph_service

router = APIRouter(prefix="/api", tags=["graphs"])


@router.get("/graph", response_model=GraphListResponse)
async def list_graphs():
    """
    List all available graphs with summary metadata.

    Returns a list of all 100 graphs with node counts,
    failure rates, and health summaries.
    """
    summaries = graph_service.get_all_graphs_summary()
    return GraphListResponse(total_graphs=len(summaries), graphs=summaries)


@router.get("/graph/{graph_id}", response_model=GraphResponse)
async def get_graph(
    graph_id: int,
    timestep: int = Query(default=0, ge=0, description="Timestep to retrieve"),
):
    """
    Get a specific graph at a given timestep.

    Returns the full graph with nodes, edges, and statistics.
    If timestep is not specified, returns t=0 (initial state).
    """
    data = graph_service.get_graph(graph_id, timestep)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Graph {graph_id} at timestep {timestep} not found",
        )
    return data
