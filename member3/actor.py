import torch
import torch.nn as nn
from torch.distributions import Categorical

class Actor(nn.Module):
    """
    MAPPO Actor Network.
    Maps local observation + communication input to action distribution.
    """
    def __init__(self, obs_dim, act_dim, hidden_dim=64):
        super(Actor, self).__init__()
        
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, act_dim)
        )

    def forward(self, obs):
        """
        Returns action distribution logits.
        """
        logits = self.net(obs)
        return logits

    def get_action(self, obs, action=None):
        """
        Samples an action and returns its log probability and entropy.
        """
        logits = self.forward(obs)
        dist = Categorical(logits=logits)
        
        if action is None:
            action = dist.sample()
            
        log_prob = dist.log_prob(action)
        entropy = dist.entropy()
        
        return action, log_prob, entropy
