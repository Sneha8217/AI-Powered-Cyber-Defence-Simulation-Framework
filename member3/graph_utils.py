import networkx as nx
import matplotlib.pyplot as plt
import os

def visualize_scada_graph(edge_index_np, num_nodes, save_path="logs/scada_graph.png"):
    """
    Renders the ICS SCADA network layout and saves it as a PNG file.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    
    # Add edges
    edges = edge_index_np.T
    for edge in edges:
        G.add_edge(int(edge[0]), int(edge[1]))

    # Plot
    plt.figure(figsize=(8, 6))
    
    # Custom colors
    node_colors = []
    for node in G.nodes():
        if node < 5:
            node_colors.append("skyblue")  # MTU/HMI
        else:
            node_colors.append("orange")   # PLCs
            
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, edgecolors="black")
    nx.draw_networkx_edges(G, pos, width=1.5, edge_color="gray")
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
    
    plt.title("ICS/OT SCADA Network Communication Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(save_path, dpi=100)
    plt.close()
    print(f"Saved SCADA graph visualization plot to {save_path}")

if __name__ == "__main__":
    import numpy as np
    dummy_edges = np.array([[0, 1, 2, 0], [5, 6, 7, 8]])
    visualize_scada_graph(dummy_edges, 10, "logs/test_scada.png")
