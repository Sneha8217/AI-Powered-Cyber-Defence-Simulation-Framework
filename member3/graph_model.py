import torch
import torch.nn as nn

try:
    from torch_geometric.nn import GCNConv
    PYG_AVAILABLE = True
except ImportError:
    PYG_AVAILABLE = False

class ICSGraphDetector(nn.Module):
    """
    Graph Convolutional Network (GCN) Autoencoder for anomaly detection.
    Compresses graph attributes and flags high reconstruction errors as anomalies.
    """
    def __init__(self, node_features=5, hidden=32):
        super(ICSGraphDetector, self).__init__()
        self.pyg_available = PYG_AVAILABLE
        
        if self.pyg_available:
            self.conv1 = GCNConv(node_features, hidden)
            self.conv2 = GCNConv(hidden, hidden)
        else:
            # Fallback linear layer encoder
            self.linear_enc1 = nn.Linear(node_features, hidden)
            self.linear_enc2 = nn.Linear(hidden, hidden)
            
        self.decoder = nn.Sequential(
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, node_features)
        )

    def forward(self, x, edge_index):
        """
        Runs graph convolutions and reconstructs node attributes.
        """
        if self.pyg_available:
            # Graph encoding
            h = torch.relu(self.conv1(x, edge_index))
            h = self.conv2(h, edge_index)
        else:
            # MLP encoding (simulates node convolution)
            h = torch.relu(self.linear_enc1(x))
            h = self.linear_enc2(h)
            
        # Reconstruct node features
        reconstructed = self.decoder(h)
        return reconstructed

    def anomaly_score(self, x, edge_index):
        """
        Calculates mean squared reconstruction error for each node.
        """
        reconstructed = self.forward(x, edge_index)
        # MSE per node
        score = torch.mean((x - reconstructed) ** 2, dim=1)
        return score
