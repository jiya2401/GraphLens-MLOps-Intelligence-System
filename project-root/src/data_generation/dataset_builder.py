from datetime import datetime
from pathlib import Path

import pandas as pd

from graph_generator import generate_pipeline_graph
from feature_generator import generate_node_features
from failure_simulator import simulate_failure


node_rows = []
edge_rows = []

NUM_GRAPHS = 50


for graph_id in range(NUM_GRAPHS):

    G = generate_pipeline_graph()

    for node in G.nodes():

        features = generate_node_features()

        failed = simulate_failure(features)

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

output_dir = Path(__file__).resolve().parents[2] / "data" / "synthetic"
output_dir.mkdir(parents=True, exist_ok=True)

nodes_path = output_dir / "nodes.csv"
edges_path = output_dir / "edges.csv"

nodes_path = _write_csv_with_fallback(nodes_df, nodes_path)
edges_path = _write_csv_with_fallback(edges_df, edges_path)

print("\nGraph-Aware Datasets Generated Successfully!\n")
_print_dataset_summary("Nodes", nodes_df)
_print_dataset_summary("Edges", edges_df)