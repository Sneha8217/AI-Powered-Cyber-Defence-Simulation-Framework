import torch
import torch.nn as nn

class Critic(nn.Module):
    """
    MAPPO Critic Network.
    Estimates the state value function based on the shared (global) observation.
    """
    def __init__(self, share_obs_dim, hidden_dim=64):
        super(Critic, self).__init__()
        
        self.net = nn.Sequential(
            nn.Linear(share_obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, share_obs):
        """
        Returns estimated state value V(s).
        """
        return self.net(share_obs)
