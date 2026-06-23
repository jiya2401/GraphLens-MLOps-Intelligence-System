"""
Analytics Service — computes aggregate analytics across all graphs.

This service reads all graph data and computes statistics that power
the Analytics Dashboard: failure distribution, trends, resource usage, etc.

Interview Q: "How would you optimize analytics computation for large datasets?"
Answer: Pre-compute and cache results. Use background tasks to refresh.
For real-time, use streaming aggregation (e.g., Apache Kafka + Flink).
Here we use @lru_cache since the data is static JSON files.
"""

import logging
from functools import lru_cache

from backend.services.graph_service import (
    get_graph,
    get_available_graph_ids,
    get_timesteps_for_graph,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def compute_analytics() -> dict:
    """
    Compute comprehensive analytics across all graphs and timesteps.
    Cached because the underlying JSON data doesn't change at runtime.
    """
    graph_ids = get_available_graph_ids()

    # Accumulators
    total_nodes = 0
    total_edges = 0
    total_timesteps = 0
    total_failures = 0

    health_counts = {"healthy": 0, "warning": 0, "unstable": 0, "failed": 0}
    failure_frequency = []

    # Resource accumulators
    cpu_sum = 0.0
    memory_sum = 0.0
    gpu_sum = 0.0
    disk_io_sum = 0.0
    latency_sum = 0.0
    temp_sum = 0.0
    resource_count = 0

    # Temporal trends: timestep -> accumulators
    temporal_data: dict[int, dict] = {}

    # Latency trends
    latency_trends = []

    for gid in graph_ids:
        timesteps = get_timesteps_for_graph(gid)
        graph_failures = 0

        for t in timesteps:
            data = get_graph(gid, t)
            if not data:
                continue

            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            total_timesteps += 1

            if t == 0:
                total_edges += len(edges)

            latencies = []

            for node in nodes:
                total_nodes += 1
                health = node.get("health", "unknown")
                if health in health_counts:
                    health_counts[health] += 1

                if node.get("failed", False):
                    total_failures += 1
                    graph_failures += 1

                telemetry = node.get("telemetry", {})
                cpu_sum += telemetry.get("cpu_usage", 0)
                memory_sum += telemetry.get("memory_usage", 0)
                gpu_sum += telemetry.get("gpu_usage", 0)
                disk_io_sum += telemetry.get("disk_io", 0)
                latency_sum += telemetry.get("network_latency", 0)
                temp_sum += telemetry.get("temperature", 0)
                resource_count += 1

                latencies.append(telemetry.get("network_latency", 0))

            # Temporal trend accumulation
            if t not in temporal_data:
                temporal_data[t] = {
                    "failure_count": 0,
                    "anomaly_sum": 0.0,
                    "cpu_sum": 0.0,
                    "latency_sum": 0.0,
                    "node_count": 0,
                    "total_failures": 0,
                }

            td = temporal_data[t]
            prop_stats = data.get("propagation_stats", {})
            td["failure_count"] += prop_stats.get("failed_nodes", 0)
            td["anomaly_sum"] += sum(n.get("anomaly_score", 0) for n in nodes)
            td["cpu_sum"] += sum(
                n.get("telemetry", {}).get("cpu_usage", 0) for n in nodes
            )
            td["latency_sum"] += sum(
                n.get("telemetry", {}).get("network_latency", 0) for n in nodes
            )
            td["node_count"] += len(nodes)
            td["total_failures"] += sum(1 for n in nodes if n.get("failed"))

            # Latency trends per graph-timestep
            if latencies:
                latency_trends.append(
                    {
                        "graph_id": gid,
                        "timestep": t,
                        "avg_latency": round(sum(latencies) / len(latencies), 1),
                        "max_latency": max(latencies),
                        "min_latency": min(latencies),
                    }
                )

        # Per-graph failure stats
        node_count_for_graph = len(
            get_graph(gid, 0).get("nodes", []) if get_graph(gid, 0) else []
        )
        total_node_timesteps = node_count_for_graph * len(timesteps)
        failure_frequency.append(
            {
                "graph_id": gid,
                "total_failures": graph_failures,
                "failure_rate": round(
                    graph_failures / max(1, total_node_timesteps), 3
                ),
            }
        )

    # Build temporal trends
    temporal_trends = []
    for t in sorted(temporal_data.keys()):
        td = temporal_data[t]
        nc = max(1, td["node_count"])
        temporal_trends.append(
            {
                "timestep": t,
                "avg_failure_rate": round(td["failure_count"] / nc, 3),
                "avg_anomaly_score": round(td["anomaly_sum"] / nc, 3),
                "avg_cpu_usage": round(td["cpu_sum"] / nc, 1),
                "avg_latency": round(td["latency_sum"] / nc, 1),
                "total_failures": td["total_failures"],
                "total_nodes": td["node_count"],
            }
        )

    # Build resource utilization
    rc = max(1, resource_count)
    resource_utilization = {
        "avg_cpu": round(cpu_sum / rc, 1),
        "avg_memory": round(memory_sum / rc, 1),
        "avg_gpu": round(gpu_sum / rc, 1),
        "avg_disk_io": round(disk_io_sum / rc, 1),
        "avg_network_latency": round(latency_sum / rc, 1),
        "avg_temperature": round(temp_sum / rc, 1),
    }

    overall_failure_rate = round(total_failures / max(1, total_nodes), 3)
    overall_avg_anomaly = round(
        sum(td["anomaly_sum"] for td in temporal_data.values())
        / max(1, total_nodes),
        3,
    )

    # Limit latency trends to a representative sample (every 10th graph)
    sampled_latency = [lt for lt in latency_trends if lt["graph_id"] % 10 == 0]

    return {
        "total_graphs": len(graph_ids),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "total_timesteps": total_timesteps,
        "overall_failure_rate": overall_failure_rate,
        "overall_avg_anomaly": overall_avg_anomaly,
        "failure_distribution": health_counts,
        "failure_frequency": failure_frequency,
        "resource_utilization": resource_utilization,
        "temporal_trends": temporal_trends,
        "latency_trends": sampled_latency,
    }
