import torch
import torch.optim as optim
import torch.nn as nn
import os
from graph_dataset import SCADAGraphDataset
from graph_model import ICSGraphDetector

def train_detector(epochs=100, save_path="models/gnn_detector.pt"):
    print("Initializing training for ICS GNN anomaly detector...")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Load dataset
    dataset = SCADAGraphDataset()
    data = dataset.get_data()
    
    # Instantiate GNN Autoencoder
    model = ICSGraphDetector(node_features=5, hidden=32)
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()
    
    # Extract tensors
    if isinstance(data, dict):
        x = data["x"]
        edge_index = data["edge_index"]
    else:
        x = data.x
        edge_index = data.edge_index
        
    model.train()
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        
        # Forward pass
        reconstructed = model(x, edge_index)
        
        # Calculate loss (reconstruction error)
        loss = criterion(reconstructed, x)
        loss.backward()
        optimizer.step()
        
        if epoch % 20 == 0:
            print(f"Epoch {epoch:3d}/{epochs} | Reconstruction Loss: {loss.item():.6f}")
            
    # Save model weights
    torch.save(model.state_dict(), save_path)
    print(f"Training completed. Model saved to {save_path}")

if __name__ == "__main__":
    train_detector(epochs=100)
