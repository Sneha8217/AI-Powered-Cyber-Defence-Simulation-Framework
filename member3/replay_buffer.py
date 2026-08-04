import numpy as np
import torch

class ReplayBuffer:
    """
    Experience buffer for joint training in MAPPO.
    Tracks shared observations, local observations, actions, rewards, values,
    and log probabilities.
    """
    def __init__(self, limit, num_agents, obs_dim, share_obs_dim, act_dim):
        self.limit = limit
        self.num_agents = num_agents
        self.obs_dim = obs_dim
        self.share_obs_dim = share_obs_dim
        self.act_dim = act_dim

        self.reset()

    def reset(self):
        self.obs = np.zeros((self.limit, self.num_agents, self.obs_dim), dtype=np.float32)
        self.share_obs = np.zeros((self.limit, self.share_obs_dim), dtype=np.float32)
        self.actions = np.zeros((self.limit, self.num_agents), dtype=np.float32)
        self.log_probs = np.zeros((self.limit, self.num_agents), dtype=np.float32)
        self.rewards = np.zeros((self.limit, 1), dtype=np.float32)
        self.values = np.zeros((self.limit, self.num_agents), dtype=np.float32)
        self.masks = np.ones((self.limit, 1), dtype=np.float32)
        
        self.ptr = 0
        self.size = 0

    def insert(self, obs, share_obs, actions, log_probs, reward, values, mask):
        """
        Inserts one environment step transition.
        """
        self.obs[self.ptr] = obs
        self.share_obs[self.ptr] = share_obs
        self.actions[self.ptr] = actions
        self.log_probs[self.ptr] = log_probs
        self.rewards[self.ptr] = reward
        self.values[self.ptr] = values
        self.masks[self.ptr] = mask

        self.ptr = (self.ptr + 1) % self.limit
        self.size = min(self.size + 1, self.limit)

    def get_batches(self, batch_size):
        """
        Yields random mini-batches of size batch_size.
        """
        indices = np.random.permutation(self.size)
        start_idx = 0
        while start_idx < self.size:
            end_idx = min(start_idx + batch_size, self.size)
            batch_indices = indices[start_idx:end_idx]
            
            yield (
                torch.tensor(self.obs[batch_indices], dtype=torch.float32),
                torch.tensor(self.share_obs[batch_indices], dtype=torch.float32),
                torch.tensor(self.actions[batch_indices], dtype=torch.long),
                torch.tensor(self.log_probs[batch_indices], dtype=torch.float32),
                torch.tensor(self.rewards[batch_indices], dtype=torch.float32),
                torch.tensor(self.values[batch_indices], dtype=torch.float32),
                torch.tensor(self.masks[batch_indices], dtype=torch.float32)
            )
            start_idx = end_idx
