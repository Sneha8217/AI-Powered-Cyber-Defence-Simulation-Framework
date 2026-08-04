import torch
import torch.optim as optim
import torch.nn as nn
from actor import Actor
from critic import Critic

class MAPPOAgent:
    """
    MAPPO Agent wrapper containing actor and critic networks.
    Responsible for local policy updates and advantage estimation.
    """
    def __init__(self, obs_dim, share_obs_dim, act_dim, lr=3e-4, clip_param=0.2, ppo_epoch=10, batch_size=32, device="cpu"):
        self.device = torch.device(device)
        self.clip_param = clip_param
        self.ppo_epoch = ppo_epoch
        self.batch_size = batch_size

        self.actor = Actor(obs_dim, act_dim).to(self.device)
        self.critic = Critic(share_obs_dim).to(self.device)

        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr)
        
        self.value_loss_fn = nn.MSELoss()

    def train_on_buffer(self, buffer, gamma=0.99, gae_lambda=0.95):
        """
        Computes targets, advantages, and runs policy update epochs.
        """
        if buffer.size < self.batch_size:
            return 0.0, 0.0

        # Run multiple optimization epochs
        actor_losses = []
        critic_losses = []

        for _ in range(self.ppo_epoch):
            for batch in buffer.get_batches(self.batch_size):
                obs, share_obs, actions, old_log_probs, rewards, values, masks = batch
                
                obs = obs.to(self.device)
                share_obs = share_obs.to(self.device)
                actions = actions.to(self.device)
                old_log_probs = old_log_probs.to(self.device)
                rewards = rewards.to(self.device)
                values = values.to(self.device)
                masks = masks.to(self.device)

                # Compute value targets and GAE advantages
                # Calculate returns and advantages using GAE
                returns = torch.zeros_like(rewards)
                advantages = torch.zeros_like(rewards)
                
                # Dynamic GAE calculation
                gae = 0
                for step in reversed(range(rewards.size(0))):
                    next_value = values[step + 1] if step < rewards.size(0) - 1 else 0.0
                    delta = rewards[step] + gamma * next_value * masks[step] - values[step]
                    gae = delta + gamma * gae_lambda * masks[step] * gae
                    returns[step] = gae + values[step]
                    advantages[step] = gae

                # Normalize advantages
                advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-5)

                # Update Actor
                # For each agent, calculate current log probabilities
                for agent_idx in range(buffer.num_agents):
                    agent_obs = obs[:, agent_idx]
                    agent_actions = actions[:, agent_idx]
                    agent_old_log_probs = old_log_probs[:, agent_idx]

                    _, new_log_probs, entropy = self.actor.get_action(agent_obs, agent_actions)
                    
                    # Policy ratio
                    ratio = torch.exp(new_log_probs - agent_old_log_probs)
                    
                    # Clipped surrogate objective
                    surr1 = ratio * advantages[:, 0]
                    surr2 = torch.clamp(ratio, 1.0 - self.clip_param, 1.0 + self.clip_param) * advantages[:, 0]
                    actor_loss = -torch.min(surr1, surr2).mean() - 0.01 * entropy.mean()

                    self.actor_optimizer.zero_grad()
                    actor_loss.backward()
                    self.actor_optimizer.step()
                    actor_losses.append(actor_loss.item())

                # Update Critic
                estimated_values = self.critic(share_obs)
                critic_loss = self.value_loss_fn(estimated_values, returns)
                
                self.critic_optimizer.zero_grad()
                critic_loss.backward()
                self.critic_optimizer.step()
                critic_losses.append(critic_loss.item())

        mean_actor_loss = sum(actor_losses) / len(actor_losses) if actor_losses else 0.0
        mean_critic_loss = sum(critic_losses) / len(critic_losses) if critic_losses else 0.0
        return mean_actor_loss, mean_critic_loss
