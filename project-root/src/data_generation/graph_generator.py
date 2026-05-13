import networkx as nx
import random


PIPELINE_STAGES = [
    "Data_Ingestion",
    "Data_Cleaning",
    "Feature_Engineering",
    "Model_Training",
    "Evaluation",
    "Deployment"
]


def generate_pipeline_graph(min_nodes=3, max_nodes=6):

    num_nodes = random.randint(min_nodes, max_nodes)

    selected_steps = PIPELINE_STAGES[:num_nodes]

    G = nx.DiGraph()

    # Add nodes
    for step in selected_steps:
        G.add_node(step)

    # Add edges
    for i in range(len(selected_steps) - 1):
        G.add_edge(selected_steps[i], selected_steps[i + 1])

    return G


if __name__ == "__main__":

    graph = generate_pipeline_graph()

    print("\nNodes:\n")
    print(list(graph.nodes()))

    print("\nEdges:\n")
    print(list(graph.edges()))