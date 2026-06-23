import argparse
import json
from pathlib import Path

import pandas as pd

BASE_DIR   = Path(__file__).resolve().parents[2]   # project-root/
NODES_CSV  = BASE_DIR / "data" / "synthetic" / "nodes.csv"
EDGES_CSV  = BASE_DIR / "data" / "synthetic" / "edges.csv"
OUTPUT_DIR = BASE_DIR / "data" / "synthetic" / "json"


INFRA_METRICS = [
    "cpu_usage", "memory_usage", "gpu_usage",
    "disk_io", "network_latency", "temperature",
]
EXEC_METRICS = [
    "runtime", "queue_delay", "retry_count",
    "throughput", "batch_size",
]
METADATA_FIELDS = [
    "node_type", "service_name", "pipeline_stage", "execution_priority",
]
FAILURE_METRICS = [
    "anomaly_score", "timeout_count",
    "previous_failure_rate", "dependency_failure_count",
]
RESOURCE_METRICS = [
    "pod_restart_count", "container_count", "autoscaling_events",
]
DATA_QUALITY_METRICS = [
    "missing_value_ratio", "data_drift_score", "schema_validation_errors",
]

ALL_TELEMETRY = (
    INFRA_METRICS + EXEC_METRICS + METADATA_FIELDS +
    FAILURE_METRICS + RESOURCE_METRICS + DATA_QUALITY_METRICS
)

def _classify_health(row: pd.Series) -> str:
    if row["failed"] == 1:
        return "failed"
    if row["anomaly_score"] >= 0.7 or row["cpu_usage"] >= 80:
        return "warning"
    if row["previous_failure_rate"] > 0.2:
        return "unstable"
    return "healthy"


# execution_state 
def _execution_state(row: pd.Series) -> str:
    if row["failed"] == 1:
        return "failed"
    if row["retry_count"] > 0:
        return "retrying"
    if row["cpu_usage"] >= 60 or row["runtime"] >= 10:
        return "running"
    if row["previous_failure_rate"] > 0.3:
        return "recovering"
    return "idle"


# Serialize one timestep snapshot
def _serialize_timestep(
    graph_id: int,
    timestep: int,
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
) -> dict:

    node_slice = nodes_df[
        (nodes_df["graph_id"] == graph_id) &
        (nodes_df["timestep"] == timestep)
    ]
    edge_slice = edges_df[edges_df["graph_id"] == graph_id]

    if node_slice.empty:
        raise ValueError(
            f"No node data for graph_id={graph_id}, timestep={timestep}"
        )

    # ---- nodes ----
    nodes = []
    for _, row in node_slice.iterrows():
        telemetry = {f: row[f] for f in ALL_TELEMETRY if f in row}
        nodes.append({
            "id":               row["node_name"],
            "failed":           bool(row["failed"]),
            "health":           _classify_health(row),
            "execution_state":  _execution_state(row),   # Change 2
            "instability":      round(float(row["previous_failure_rate"]), 3),
            "anomaly_score":    round(float(row["anomaly_score"]), 3),
            "runtime":          int(row["runtime"]),
            "telemetry":        telemetry,
        })

    # ---- edges ----
    valid_ids = {n["id"] for n in nodes}
    edges = []
    for _, row in edge_slice.iterrows():
        src, tgt = row["source_node"], row["target_node"]
        if src in valid_ids and tgt in valid_ids:
            edges.append({
                "source":           src,
                "target":           tgt,
                "propagation_risk": None,
            })

    # ---- stats ----
    total   = len(nodes)
    failed  = sum(1 for n in nodes if n["failed"])
    warning = sum(1 for n in nodes if n["health"] == "warning")

    propagation_stats = {
        "total_nodes":       total,
        "failed_nodes":      failed,
        "warning_nodes":     warning,
        "healthy_nodes":     total - failed - warning,
        "failure_rate":      round(failed / max(1, total), 3),
        "avg_anomaly_score": round(
            sum(n["anomaly_score"] for n in nodes) / max(1, total), 3
        ),
    }

    return {
        "timestep":          timestep,
        "nodes":             nodes,
        "edges":             edges,
        "propagation_stats": propagation_stats,
    }


# Serialize one full graph — all timesteps inside one JSON
def serialize_graph(
    graph_id: int,
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
) -> dict:

    timesteps = sorted(
        nodes_df[nodes_df["graph_id"] == graph_id]["timestep"].unique().tolist()
    )

    snapshots = []
    for tid in timesteps:
        try:
            snapshots.append(_serialize_timestep(graph_id, tid, nodes_df, edges_df))
        except ValueError as exc:
            print(f"  [skip] {exc}")

    return {
        "graph_id":  graph_id,
        "timesteps": snapshots,
        "temporal_stats": {
            "total_timesteps": len(snapshots),
            "timestep_range":  [int(timesteps[0]), int(timesteps[-1])],
            "avg_instability": round(
                sum(
                    n["instability"]
                    for s in snapshots
                    for n in s["nodes"]
                ) / max(1, sum(len(s["nodes"]) for s in snapshots)),
                3,
            ),
        },
    }


# Batch — one file per graph
def serialize_all(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    graph_ids: list | None = None,
    output_dir: Path = OUTPUT_DIR,
) -> list:

    output_dir = Path(output_dir).resolve()
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    gids = graph_ids or sorted(nodes_df["graph_id"].unique().tolist())
    written = []

    for gid in gids:
        payload  = serialize_graph(gid, nodes_df, edges_df)
        fname    = output_dir / f"graph_{gid:03d}.json"
        fname.write_text(json.dumps(payload, indent=2))
        written.append(fname)
        n_ts = len(payload["timesteps"])
        n_nodes = len(payload["timesteps"][0]["nodes"]) if payload["timesteps"] else 0
        print(f"  [ok]   {fname.name}  ({n_nodes} nodes, {n_ts} timesteps)")

    return written


# CLI
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="GraphLens DAG → JSON converter")
    p.add_argument("--graph-id",  type=int, default=None)
    p.add_argument("--nodes-csv", type=Path, default=NODES_CSV)
    p.add_argument("--edges-csv", type=Path, default=EDGES_CSV)
    p.add_argument("--output",    type=Path, default=OUTPUT_DIR)
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    print(f"Loading {args.nodes_csv} …")
    nodes_df = pd.read_csv(args.nodes_csv)
    print(f"Loading {args.edges_csv} …")
    edges_df = pd.read_csv(args.edges_csv)

    graph_ids = [args.graph_id] if args.graph_id is not None else None

    print(f"\nSerializing → {args.output}\n")
    written = serialize_all(nodes_df, edges_df, graph_ids, args.output)
    print(f"\nDone. {len(written)} file(s) written.")                       


if __name__ == "__main__":
    main()