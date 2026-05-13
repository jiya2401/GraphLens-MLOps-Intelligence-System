import pandas as pd

from graph_generator import generate_pipeline_graph
from feature_generator import generate_node_features
from failure_simulator import simulate_failure


all_rows = []

NUM_GRAPHS = 50


for graph_id in range(NUM_GRAPHS):

    G = generate_pipeline_graph()

    for node in G.nodes():

        features = generate_node_features()

        failed = simulate_failure(features)

        row = {

            "graph_id": graph_id,

            "node_name": node,

            "cpu_usage": features["cpu_usage"],

            "memory_usage": features["memory_usage"],

            "runtime": features["runtime"],

            "queue_delay": features["queue_delay"],

            "retry_count": features["retry_count"],

            "failed": failed
        }

        all_rows.append(row)


df = pd.DataFrame(all_rows)

output_path = "C:\\Code_arena\\GraphLens-MLOps-Intelligence-System\\project-root\\data\\synthetic\\synthetic_pipeline_dataset.csv"

df.to_csv(output_path, index=False)

print("\nDataset Generated Successfully!\n")

print(df.head())