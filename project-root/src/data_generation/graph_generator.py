import networkx as nx
G = nx.DiGraph()
G.add_nodes_from(["Data_Ingestion", "Data_Cleaning", "Model_Training"])
G.add_edge("Data_Ingestion", "Data_Cleaning")
G.add_edge("Data_Cleaning", "Model_Training")
print("nodes:" + str(list(G.nodes())))
print("edges:" + str(list(G.edges())))