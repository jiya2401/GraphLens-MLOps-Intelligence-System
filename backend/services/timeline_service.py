"""
Timeline Service — assembles temporal replay data for a graph.

Loads all timesteps for a given graph and returns them as an ordered
sequence for the Temporal Replay Engine in the frontend.
"""

import logging

from backend.services.graph_service import (
    get_graph,
    get_timesteps_for_graph,
)

logger = logging.getLogger(__name__)


def get_timeline(graph_id: int) -> dict | None:
    """
    Load all timesteps for a graph and assemble into a timeline.

    Returns:
        {
            "graph_id": 0,
            "total_timesteps": 5,
            "timesteps": [
                { "timestep": 0, "nodes": [...], "edges": [...], "propagation_stats": {...} },
                { "timestep": 1, ... },
                ...
            ]
        }
    """
    timestep_ids = get_timesteps_for_graph(graph_id)
    if not timestep_ids:
        return None

    timesteps = []
    for t in timestep_ids:
        data = get_graph(graph_id, t)
        if data:
            timesteps.append(
                {
                    "timestep": t,
                    "nodes": data.get("nodes", []),
                    "edges": data.get("edges", []),
                    "propagation_stats": data.get("propagation_stats", {}),
                }
            )

    if not timesteps:
        return None

    return {
        "graph_id": graph_id,
        "total_timesteps": len(timesteps),
        "timesteps": timesteps,
    }
