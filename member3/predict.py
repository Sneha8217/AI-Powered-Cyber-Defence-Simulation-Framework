import torch
import os
import numpy as np
from graph_dataset import SCADAGraphDataset
from graph_model import ICSGraphDetector
from graph_utils import visualize_scada_graph

def run_inference(model_path="models/gnn_detector.pt", threshold=0.15):
    print("Running ICS Graph anomaly detection inference...")
    
    # Load dataset
    dataset = SCADAGraphDataset()
    data = dataset.get_data()
    
    if isinstance(data, dict):
        x = data["x"]
        edge_index = data["edge_index"]
    else:
        x = data.x
        edge_index = data.edge_index

    # Instantiate model
    model = ICSGraphDetector(node_features=5, hidden=32)
    
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
        print(f"Loaded trained GNN weights from {model_path}")
    else:
        print("[Warning] Model weights file not found. Running inference with random initialized weights.")
        
    model.eval()
    with torch.no_grad():
        anomaly_scores = model.anomaly_score(x, edge_index).numpy()
        
    # Classify anomalies
    print("\n--- Detection Results ---")
    anomalies_detected = 0
    for idx, score in enumerate(anomaly_scores):
        is_anomaly = score > threshold
        node_role = "HMI/MTU" if idx < 5 else "PLC"
        status = "ANOMALY DETECTED" if is_anomaly else "NORMAL"
        print(f"Node {idx:2d} ({node_role:7s}) | Anomaly Score: {score:.5f} | Status: {status}")
        if is_anomaly:
            anomalies_detected += 1
            
    print(f"\nSummary: Identified {anomalies_detected} anomalies across {len(anomaly_scores)} nodes.")
    
    # Draw graph
    edge_index_np = edge_index.numpy()
    visualize_scada_graph(edge_index_np, num_nodes=len(anomaly_scores))
    
    return anomaly_scores

if __name__ == "__main__":
    run_inference()
