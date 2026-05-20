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
                "cpu_usage": features["cpu_usage"],
                "memory_usage": features["memory_usage"],
                "runtime": features["runtime"],
                "queue_delay": features["queue_delay"],
                "retry_count": features["retry_count"],
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

output_dir = Path(__file__).resolve().parents[2] / "data" / "synthetic"
output_dir.mkdir(parents=True, exist_ok=True)

nodes_path = output_dir / "nodes.csv"
edges_path = output_dir / "edges.csv"

nodes_df.to_csv(nodes_path, index=False)
edges_df.to_csv(edges_path, index=False)

print("\nGraph-Aware Datasets Generated Successfully!\n")
print("Nodes preview:")
print(nodes_df.head())
print("\nEdges preview:")
print(edges_df.head())