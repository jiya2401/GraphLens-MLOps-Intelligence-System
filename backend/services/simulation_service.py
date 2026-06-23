"""
Simulation Service — wraps the existing failure simulator for on-demand use.

This service imports your existing Python engine modules and exposes them
through the API. The existing code is NOT modified — we just call it.

Interview Q: "How do you integrate legacy code into a new system?"
Answer: Create an adapter/wrapper layer. The service layer acts as a
bridge between the new FastAPI API and the existing Python modules.
This follows the Adapter Pattern from Design Patterns.
"""

import sys
import logging
import uuid
from pathlib import Path

from backend.config import settings

logger = logging.getLogger(__name__)

# Add the existing engine source to the Python path so we can import it
ENGINE_SRC = Path(settings.config_path).resolve().parent.parent / "project-root" / "src" / "data_generation"
if str(ENGINE_SRC) not in sys.path:
    sys.path.insert(0, str(ENGINE_SRC))

try:
    from graph_generator import generate_pipeline_graph
    from feature_generator import generate_node_features, DEFAULT_CONFIG
    from failure_simulator import simulate_graph_failures
    from temporal_simulator import simulate_temporal_graph

    ENGINE_AVAILABLE = True
    logger.info("Engine modules loaded successfully")
except ImportError as e:
    ENGINE_AVAILABLE = False
    logger.warning(f"Engine modules not available: {e}")


def run_simulation(
    num_nodes: int = 6,
    failure_threshold_cpu: int = 85,
    failure_threshold_runtime: int = 15,
    propagation_enabled: bool = True,
    propagation_strength: float = 0.35,
    num_timesteps: int = 5,
) -> dict:
    """
    Run a new failure simulation using the existing engine.
    Returns summary statistics about the simulation.
    """
    if not ENGINE_AVAILABLE:
        return {
            "graph_id": "error",
            "num_nodes": 0,
            "num_edges": 0,
            "num_timesteps": 0,
            "total_failures": 0,
            "failure_rate": 0.0,
            "propagated_failures": 0,
            "recovery_events": 0,
            "message": "Engine modules not available. Check Python path.",
        }

    # Generate a new graph
    graph = generate_pipeline_graph(min_nodes=num_nodes, max_nodes=num_nodes)

    # Generate features for each node
    initial_features = {
        node: generate_node_features(config=DEFAULT_CONFIG) for node in graph.nodes()
    }

    # Configure simulation parameters
    thresholds = {"cpu": failure_threshold_cpu, "runtime": failure_threshold_runtime}
    prop_config = {
        "propagation_enabled": propagation_enabled,
        "propagation_strength": propagation_strength,
        "propagation_decay": 0.6,
        "max_propagation_depth": 3,
    }
    temp_config = {
        "num_timesteps": num_timesteps,
        "temporal_drift_strength": 0.05,
        "recovery_probability": 0.1,
        "instability_accumulation_rate": 0.15,
    }

    # Run temporal simulation
    sim_id = str(uuid.uuid4())[:8]
    rows, prop_stats, temp_stats = simulate_temporal_graph(
        graph,
        sim_id,
        initial_features,
        thresholds=thresholds,
        propagation_config=prop_config,
        temporal_config=temp_config,
        feature_config=DEFAULT_CONFIG,
    )

    total_failures = sum(1 for r in rows if r.get("failed", 0) == 1)
    total_node_steps = len(rows)

    return {
        "graph_id": f"sim_{sim_id}",
        "num_nodes": graph.number_of_nodes(),
        "num_edges": graph.number_of_edges(),
        "num_timesteps": num_timesteps,
        "total_failures": total_failures,
        "failure_rate": round(total_failures / max(1, total_node_steps), 3),
        "propagated_failures": prop_stats.get("propagated_failures", 0),
        "recovery_events": temp_stats.get("recovery_events", 0),
        "message": "Simulation completed successfully",
    }


def predict_failures(graph_id: int, timestep: int = 0) -> dict:
    """
    Heuristic-based failure prediction.
    Uses telemetry thresholds to estimate failure probability.

    In the future, this will be replaced by a GNN model.
    """
    from backend.services.graph_service import get_graph

    data = get_graph(graph_id, timestep)
    if not data:
        return {"graph_id": graph_id, "timestep": timestep, "predictions": [],
                "model_type": "heuristic", "confidence": 0.0}

    predictions = []
    for node in data.get("nodes", []):
        telemetry = node.get("telemetry", {})

        # Heuristic: combine multiple signals into a failure probability
        cpu_risk = max(0, (telemetry.get("cpu_usage", 0) - 70)) / 30
        anomaly_risk = node.get("anomaly_score", 0)
        instability_risk = node.get("instability", 0)
        retry_risk = telemetry.get("retry_count", 0) / 5
        timeout_risk = telemetry.get("timeout_count", 0) / 6

        # Weighted combination
        prob = min(1.0, round(
            0.30 * cpu_risk
            + 0.25 * anomaly_risk
            + 0.20 * instability_risk
            + 0.15 * retry_risk
            + 0.10 * timeout_risk,
            3,
        ))

        # Determine risk level
        if prob >= 0.7:
            risk_level = "critical"
        elif prob >= 0.5:
            risk_level = "high"
        elif prob >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Top contributing factors
        factors = []
        if cpu_risk > 0.3:
            factors.append(f"High CPU usage ({telemetry.get('cpu_usage', 0)}%)")
        if anomaly_risk > 0.5:
            factors.append(f"High anomaly score ({anomaly_risk:.2f})")
        if instability_risk > 0.3:
            factors.append(f"Historical instability ({instability_risk:.2f})")
        if retry_risk > 0.4:
            factors.append(f"Frequent retries ({telemetry.get('retry_count', 0)})")
        if timeout_risk > 0.3:
            factors.append(f"Timeout events ({telemetry.get('timeout_count', 0)})")
        if not factors:
            factors.append("No significant risk factors detected")

        predictions.append(
            {
                "node_id": node["id"],
                "failure_probability": prob,
                "risk_level": risk_level,
                "contributing_factors": factors,
            }
        )

    # Sort by highest risk
    predictions.sort(key=lambda p: p["failure_probability"], reverse=True)

    return {
        "graph_id": graph_id,
        "timestep": timestep,
        "predictions": predictions,
        "model_type": "heuristic",
        "confidence": 0.65,
    }


def analyze_root_cause(graph_id: int, timestep: int = 0) -> dict:
    """
    Heuristic root cause analysis.
    Identifies nodes most likely to be the origin of failures
    based on their position in the DAG and telemetry signals.
    """
    from backend.services.graph_service import get_graph

    data = get_graph(graph_id, timestep)
    if not data:
        return {"graph_id": graph_id, "timestep": timestep, "root_causes": [],
                "analysis_method": "heuristic"}

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Build adjacency info
    outgoing: dict[str, list[str]] = {}
    incoming: dict[str, list[str]] = {}
    for edge in edges:
        outgoing.setdefault(edge["source"], []).append(edge["target"])
        incoming.setdefault(edge["target"], []).append(edge["source"])

    root_causes = []
    for node in nodes:
        nid = node["id"]
        telemetry = node.get("telemetry", {})

        # Root cause score: upstream nodes with high anomaly + failures
        # have higher root cause likelihood
        is_source_node = nid not in incoming or len(incoming.get(nid, [])) == 0
        has_downstream = len(outgoing.get(nid, [])) > 0
        is_failed = node.get("failed", False)
        anomaly = node.get("anomaly_score", 0)

        # Score components
        position_score = 0.3 if is_source_node else 0.1
        failure_score = 0.4 if is_failed else 0.0
        anomaly_score_val = anomaly * 0.3
        downstream_impact = min(0.2, len(outgoing.get(nid, [])) * 0.1)

        total_score = round(
            min(1.0, position_score + failure_score + anomaly_score_val + downstream_impact),
            3,
        )

        if total_score < 0.2:
            continue

        # Build evidence
        evidence = []
        if is_failed:
            evidence.append("Node is in failed state")
        if is_source_node:
            evidence.append("Upstream source node — failures here propagate downstream")
        if anomaly > 0.7:
            evidence.append(f"Very high anomaly score: {anomaly:.3f}")
        if telemetry.get("cpu_usage", 0) > 85:
            evidence.append(f"CPU overloaded: {telemetry.get('cpu_usage', 0)}%")
        if has_downstream:
            evidence.append(
                f"Has {len(outgoing.get(nid, []))} downstream dependencies"
            )
        if not evidence:
            evidence.append("Moderate risk indicators detected")

        affected = outgoing.get(nid, [])

        root_causes.append(
            {
                "node_id": nid,
                "root_cause_score": total_score,
                "evidence": evidence,
                "affected_nodes": affected,
            }
        )

    root_causes.sort(key=lambda r: r["root_cause_score"], reverse=True)

    return {
        "graph_id": graph_id,
        "timestep": timestep,
        "root_causes": root_causes,
        "analysis_method": "heuristic",
    }
