from copy import deepcopy
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

from graph_generator import generate_pipeline_graph
from feature_generator import DEFAULT_CONFIG, generate_node_features
from failure_simulator import simulate_graph_failures


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "configs" / "dataset_config.yaml"


def _load_dataset_config(path):
    if not path.exists():
        print(f"Config file not found at {path}. Using defaults.")
        return {}

    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _merge_feature_ranges(base_ranges, config):
    merged = deepcopy(base_ranges)
    configured_ranges = config.get("feature_ranges", {})

    for name, bounds in configured_ranges.items():
        if isinstance(bounds, dict) and "min" in bounds and "max" in bounds:
            merged[name] = (bounds["min"], bounds["max"])

    legacy_map = {
        "cpu_range": "cpu_usage",
        "memory_range": "memory_usage",
        "runtime_range": "runtime",
    }

    for legacy_key, feature_key in legacy_map.items():
        bounds = config.get(legacy_key)
        if isinstance(bounds, dict) and "min" in bounds and "max" in bounds:
            merged[feature_key] = (bounds["min"], bounds["max"])

    return merged


def _build_feature_config(config):
    feature_config = deepcopy(DEFAULT_CONFIG)
    feature_config["ranges"] = _merge_feature_ranges(
        DEFAULT_CONFIG["ranges"], config
    )

    if "float_precision" in config:
        feature_config["float_precision"] = config["float_precision"]

    categories = config.get("categories")
    if isinstance(categories, dict):
        for key, values in categories.items():
            if isinstance(values, list) and values:
                feature_config["categories"][key] = values

    return feature_config


node_rows = []
edge_rows = []

dataset_config = _load_dataset_config(CONFIG_PATH)
feature_config = _build_feature_config(dataset_config)

failure_thresholds = dataset_config.get("failure_thresholds", {})
propagation_config = {
    "propagation_enabled": dataset_config.get("propagation_enabled", True),
    "propagation_strength": dataset_config.get("propagation_strength", 0.35),
    "propagation_decay": dataset_config.get("propagation_decay", 0.6),
    "max_propagation_depth": dataset_config.get("max_propagation_depth", 3),
}

num_graphs = dataset_config.get("num_graphs", 50)
min_nodes = dataset_config.get("min_nodes", 3)
max_nodes = dataset_config.get("max_nodes", 6)

propagation_totals = {
    "graphs": 0,
    "base_failures": 0,
    "propagated_failures": 0,
    "impacted_nodes": 0,
    "total_failures": 0,
}


for graph_id in range(num_graphs):

    G = generate_pipeline_graph(min_nodes=min_nodes, max_nodes=max_nodes)

    features_by_node = {
        node: generate_node_features(config=feature_config) for node in G.nodes()
    }

    features_by_node, failures_by_node, graph_stats = simulate_graph_failures(
        G,
        features_by_node,
        thresholds=failure_thresholds,
        propagation_config=propagation_config,
    )

    propagation_totals["graphs"] += 1
    for key in (
        "base_failures",
        "propagated_failures",
        "impacted_nodes",
        "total_failures",
    ):
        propagation_totals[key] += graph_stats.get(key, 0)

    for node in G.nodes():

        features = features_by_node[node]
        failed = failures_by_node[node]

        node_rows.append(
            {
                "graph_id": graph_id,
                "node_name": node,
                **features,
                "failed": failed,
            }
        )

    for source_node, target_node in G.edges():
        edge_rows.append(
            {
                "graph_id": graph_id,
                "source_node": source_node,
                "target_node": target_node,
            }
        )


nodes_df = pd.DataFrame(node_rows)
edges_df = pd.DataFrame(edge_rows)


def _write_csv_with_fallback(df, path):
    try:
        df.to_csv(path, index=False)
        return path
    except PermissionError:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback_path = path.with_stem(f"{path.stem}_{timestamp}")
        df.to_csv(fallback_path, index=False)
        print(
            f"Permission denied for {path}. Wrote to {fallback_path} instead."
        )
        return fallback_path


def _print_dataset_summary(label, df):
    print(f"\n{label} dataset shape: {df.shape}")
    print(f"{label} columns: {list(df.columns)}")
    print(f"{label} preview:")
    print(df.head())


def _print_propagation_summary(stats, total_nodes):
    graphs = stats.get("graphs", 0)
    base_failures = stats.get("base_failures", 0)
    propagated_failures = stats.get("propagated_failures", 0)
    impacted_nodes = stats.get("impacted_nodes", 0)
    total_failures = stats.get("total_failures", 0)
    failure_rate = total_failures / max(1, total_nodes)

    print("\nFailure propagation summary:")
    print(f"Graphs processed: {graphs}")
    print(f"Total nodes: {total_nodes}")
    print(f"Base failures: {base_failures}")
    print(f"Propagated failures: {propagated_failures}")
    print(f"Impacted nodes: {impacted_nodes}")
    print(f"Total failures: {total_failures}")
    print(f"Failure rate: {failure_rate:.3f}")

output_dir = BASE_DIR / "data" / "synthetic"
output_dir.mkdir(parents=True, exist_ok=True)

nodes_path = output_dir / "nodes.csv"
edges_path = output_dir / "edges.csv"

nodes_path = _write_csv_with_fallback(nodes_df, nodes_path)
edges_path = _write_csv_with_fallback(edges_df, edges_path)

print("\nGraph-Aware Datasets Generated Successfully!\n")
_print_propagation_summary(propagation_totals, len(nodes_df))
_print_dataset_summary("Nodes", nodes_df)
_print_dataset_summary("Edges", edges_df)