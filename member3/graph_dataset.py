import numpy as np
import torch

try:
    from torch_geometric.data import Data
    PYG_AVAILABLE = True
except ImportError:
    PYG_AVAILABLE = False

class SCADAGraphDataset:
    """
    Constructs graph datasets from simulated Zeek network logs.
    Represents SCADA nodes (Master Terminal Unit, Programmable Logic Controllers) and links.
    """
    def __init__(self, num_nodes=20):
        self.num_nodes = num_nodes
        # Node features: [Connection Count, Bytes Sent/Received, Protocol Type, Is SCADA, Criticality]
        self.features = np.random.rand(num_nodes, 5).astype(np.float32)
        # Force some features to represent SCADA nodes
        self.features[0:5, 3] = 1.0  # MTU/HMI
        self.features[5:15, 3] = 0.8  # PLCs using Modbus/DNP3
        
        # Build edges (hierarchical SCADA topology)
        self.edges = []
        for i in range(5):
            for j in range(5, 15):
                self.edges.append([i, j])  # HMI connects to PLCs
                
        self.edge_index = np.array(self.edges, dtype=np.int64).T

    def get_data(self):
        """
        Returns PyTorch Geometric Data object or dictionary fallback.
        """
        x_tensor = torch.tensor(self.features, dtype=torch.float32)
        edge_tensor = torch.tensor(self.edge_index, dtype=torch.long)
        
        if PYG_AVAILABLE:
            return Data(x=x_tensor, edge_index=edge_tensor)
        else:
            return {
                "x": x_tensor,
                "edge_index": edge_tensor,
                "note": "PyTorch Geometric not installed. Using raw tensor dict fallback."
            }

if __name__ == "__main__":
    dataset = SCADAGraphDataset()
    data = dataset.get_data()
    print("Dataset generated successfully.")
    if isinstance(data, dict):
        print(f"Fallback Mode: Keys={data.keys()}")
    else:
        print(f"PyG Mode: Node features shape={data.x.shape}, Edge index shape={data.edge_index.shape}")
