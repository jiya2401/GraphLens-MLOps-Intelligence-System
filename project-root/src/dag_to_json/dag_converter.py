import argparse
import json
from pathlib import Path
 
import pandas as pd

BASE_DIR   = Path(__file__).resolve().parents[1]   # project-root/
NODES_CSV  = BASE_DIR / "data" / "synthetic" / "nodes.csv"
EDGES_CSV  = BASE_DIR / "data" / "synthetic" / "edges.csv"
OUTPUT_DIR = BASE_DIR / "data" / "json"
 
 
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
 
 
# Core serializer — one JSON per (graph_id, timestep) 
def serialize_graph(
    graph_id: int,
    timestep: int,
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
) -> dict:
    """Return a frontend-ready dict for one (graph_id, timestep) snapshot."""
 
    # ---- filter to this graph + timestep ----
    node_slice = nodes_df[
        (nodes_df["graph_id"] == graph_id) &
        (nodes_df["timestep"] == timestep)
    ]
    edge_slice = edges_df[edges_df["graph_id"] == graph_id]
 
    if node_slice.empty:
        raise ValueError(
            f"No node data found for graph_id={graph_id}, timestep={timestep}"
        )
 
    # ---- build node list ----
    nodes = []
    for _, row in node_slice.iterrows():
        telemetry = {field: row[field] for field in ALL_TELEMETRY if field in row}
        nodes.append({
            "id":              row["node_name"],
            "failed":          bool(row["failed"]),
            "health":          _classify_health(row),
            "instability":     round(float(row["previous_failure_rate"]), 3),
            "anomaly_score":   round(float(row["anomaly_score"]), 3),
            "runtime":         int(row["runtime"]),
            "telemetry":       telemetry,
        })
 
    # ---- build edge list ----
    valid_node_ids = {n["id"] for n in nodes}
    edges = []
    for _, row in edge_slice.iterrows():
        src, tgt = row["source_node"], row["target_node"]
        # only include edges whose endpoints exist in this graph's node set
        if src in valid_node_ids and tgt in valid_node_ids:
            edges.append({
                "source": src,
                "target": tgt,
                "propagation_risk": None,   # placeholder for Phase 3
            })
 
    # ---- propagation stats ----
    total_nodes   = len(nodes)
    failed_nodes  = sum(1 for n in nodes if n["failed"])
    warning_nodes = sum(1 for n in nodes if n["health"] == "warning")
    avg_anomaly   = round(
        sum(n["anomaly_score"] for n in nodes) / max(1, total_nodes), 3
    )
 
    propagation_stats = {
        "total_nodes":    total_nodes,
        "failed_nodes":   failed_nodes,
        "warning_nodes":  warning_nodes,
        "healthy_nodes":  total_nodes - failed_nodes - warning_nodes,
        "failure_rate":   round(failed_nodes / max(1, total_nodes), 3),
        "avg_anomaly_score": avg_anomaly,
    }
 
    # ---- temporal stats ----
    all_timesteps = sorted(
        nodes_df[nodes_df["graph_id"] == graph_id]["timestep"].unique().tolist()
    )
    temporal_stats = {
        "current_timestep": timestep,
        "total_timesteps":  len(all_timesteps),
        "timestep_range":   [int(all_timesteps[0]), int(all_timesteps[-1])],
        "avg_instability":  round(
            sum(n["instability"] for n in nodes) / max(1, total_nodes), 3
        ),
    }
 
    return {
        "graph_id":          graph_id,
        "timestep":          timestep,
        "nodes":             nodes,
        "edges":             edges,
        "propagation_stats": propagation_stats,
        "temporal_stats":    temporal_stats,
    }
 

def serialize_all(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    graph_ids: list[int] | None = None,
    timesteps: list[int] | None = None,
    output_dir: Path = OUTPUT_DIR,
) -> list[Path]:
    output_dir = Path(output_dir).resolve()
    if not output_dir.exists():
      output_dir.mkdir(parents=True)  
 
    gids = graph_ids or sorted(nodes_df["graph_id"].unique().tolist())
    tids = timesteps  # None means all timesteps per graph
 
    written: list[Path] = []
 
    for gid in gids:
        g_timesteps = tids or sorted(
            nodes_df[nodes_df["graph_id"] == gid]["timestep"].unique().tolist()
        )
        for tid in g_timesteps:
            try:
                payload = serialize_graph(gid, tid, nodes_df, edges_df)
            except ValueError as exc:
                print(f"  [skip] {exc}")
                continue
 
            fname = output_dir / f"graph_{gid:03d}_t{tid:02d}.json"
            fname.write_text(json.dumps(payload, indent=2))
            written.append(fname)
            print(f"  [ok]   {fname.name}  "
                  f"({payload['propagation_stats']['total_nodes']} nodes, "
                  f"{len(payload['edges'])} edges)")
 
    return written
 
 
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="GraphLens DAG → JSON converter")
    p.add_argument("--graph-id",  type=int, default=None,
                   help="Single graph ID to export (default: all)")
    p.add_argument("--timestep",  type=int, default=None,
                   help="Single timestep to export (default: all)")
    p.add_argument("--nodes-csv", type=Path, default=NODES_CSV)
    p.add_argument("--edges-csv", type=Path, default=EDGES_CSV)
    p.add_argument("--output",    type=Path, default=OUTPUT_DIR,
                   help="Output directory for JSON files")
    return p.parse_args()
 
 
def main() -> None:
    args = _parse_args()
 
    print(f"Loading {args.nodes_csv} …")
    nodes_df = pd.read_csv(args.nodes_csv)
    print(f"Loading {args.edges_csv} …")
    edges_df = pd.read_csv(args.edges_csv)
 
    graph_ids = [args.graph_id] if args.graph_id is not None else None
    timesteps = [args.timestep] if args.timestep is not None else None
 
    print(f"\nSerializing → {args.output}\n")
    written = serialize_all(nodes_df, edges_df, graph_ids, timesteps, args.output)
 
    print(f"\nDone. {len(written)} file(s) written.")
 
 
if __name__ == "__main__":
    main()
 