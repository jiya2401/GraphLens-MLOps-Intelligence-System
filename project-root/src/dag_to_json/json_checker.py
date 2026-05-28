import json
import sys
from pathlib import Path
 
TOP_LEVEL_KEYS = {"graph_id", "timestep", "nodes", "edges",
                  "propagation_stats", "temporal_stats"}
 
NODE_KEYS = {"id", "failed", "health", "instability",
             "anomaly_score", "runtime", "telemetry"}
 
TELEMETRY_SPOT_CHECK = {
    "cpu_usage", "memory_usage", "anomaly_score",
    "runtime", "queue_delay", "retry_count",
}
 
VALID_HEALTH_VALUES = {"healthy", "warning", "unstable", "failed"}
 
PROP_STATS_KEYS = {"total_nodes", "failed_nodes", "healthy_nodes",
                   "failure_rate", "avg_anomaly_score"}
 
TEMPORAL_STATS_KEYS = {"current_timestep", "total_timesteps",
                       "timestep_range", "avg_instability"}
 

class ValidationError(Exception):
    pass
 
 
def _check_keys(obj: dict, required: set, label: str) -> None:
    missing = required - obj.keys()
    if missing:
        raise ValidationError(f"{label} is missing keys: {missing}")
 
 
def validate_graph(data: dict) -> list[str]:
    """
    Returns a list of warning strings (non-fatal issues).
    Raises ValidationError on fatal problems.
    """
    warnings: list[str] = []
 
    # ---- top-level structure ----
    _check_keys(data, TOP_LEVEL_KEYS, "Top-level JSON")
 
    if not isinstance(data["nodes"], list) or len(data["nodes"]) == 0:
        raise ValidationError("'nodes' must be a non-empty list")
 
    if not isinstance(data["edges"], list):
        raise ValidationError("'edges' must be a list")
 
    _check_keys(data["propagation_stats"], PROP_STATS_KEYS, "propagation_stats")
    _check_keys(data["temporal_stats"], TEMPORAL_STATS_KEYS, "temporal_stats")
 
    # ---- node validation ----
    node_ids: set[str] = set()
    for i, node in enumerate(data["nodes"]):
        label = f"nodes[{i}]"
        _check_keys(node, NODE_KEYS, label)
 
        if node["id"] in node_ids:
            raise ValidationError(f"Duplicate node id '{node['id']}'")
        node_ids.add(node["id"])
 
        if node["health"] not in VALID_HEALTH_VALUES:
            raise ValidationError(
                f"{label}: invalid health '{node['health']}' "
                f"(expected one of {VALID_HEALTH_VALUES})"
            )
 
        if not (0.0 <= node["anomaly_score"] <= 1.0):
            warnings.append(
                f"{label}: anomaly_score {node['anomaly_score']} out of [0,1]"
            )
 
        if not (0.0 <= node["instability"] <= 1.0):
            warnings.append(
                f"{label}: instability {node['instability']} out of [0,1]"
            )
 
        # spot-check telemetry keys
        telemetry = node.get("telemetry", {})
        missing_tel = TELEMETRY_SPOT_CHECK - telemetry.keys()
        if missing_tel:
            warnings.append(f"{label}: telemetry missing fields {missing_tel}")
 
    # ---- edge validation ----
    for i, edge in enumerate(data["edges"]):
        label = f"edges[{i}]"
        if "source" not in edge or "target" not in edge:
            raise ValidationError(f"{label} missing 'source' or 'target'")
        if edge["source"] not in node_ids:
            raise ValidationError(
                f"{label}: source '{edge['source']}' not in node list"
            )
        if edge["target"] not in node_ids:
            raise ValidationError(
                f"{label}: target '{edge['target']}' not in node list"
            )
 
    # ---- propagation_stats consistency ----
    ps = data["propagation_stats"]
    expected_total = ps["failed_nodes"] + ps["warning_nodes"] + ps["healthy_nodes"]
    if expected_total != ps["total_nodes"]:
        warnings.append(
            f"propagation_stats: failed+warning+healthy={expected_total} "
            f"!= total_nodes={ps['total_nodes']}"
        )
 
    return warnings
 

def validate_file(path: Path) -> bool:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"  [FAIL]  {path.name}  →  Invalid JSON: {exc}") 
        return False
 
    try:
        warnings = validate_graph(data)
    except ValidationError as exc:
        print(f"  [FAIL]  {path.name}  →  {exc}")
        return False
 
    node_count = len(data["nodes"])
    edge_count = len(data["edges"])
    status = f"graph={data['graph_id']}  t={data['timestep']}  " \
             f"{node_count} nodes  {edge_count} edges"
 
    if warnings:
        for w in warnings:
            print(f"  [WARN]  {path.name}  →  {w}")
        print(f"  [PASS]  {path.name}  →  {status}  ({len(warnings)} warning(s))")
    else:
        print(f"  [PASS]  {path.name}  →  {status}")
 
    return True
 
 
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python json_checker.py <file.json | directory>")
        sys.exit(1)
 
    target = Path(sys.argv[1])
    files = sorted(target.glob("*.json")) if target.is_dir() else [target]
 
    if not files:
        print("No JSON files found.")
        sys.exit(1)
 
    print(f"\nValidating {len(files)} file(s) …\n")
    passed = sum(validate_file(f) for f in files)
    failed = len(files) - passed
 
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(files)}")
    if failed:
        sys.exit(1)
 
 
if __name__ == "__main__":
    main() 