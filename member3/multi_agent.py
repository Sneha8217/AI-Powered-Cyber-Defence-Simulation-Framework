import numpy as np
import torch
import logging
from replay_buffer import ReplayBuffer
from mappo_agent import MAPPOAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (MultiAgent) %(message)s")
logger = logging.getLogger("ACDSF-MultiAgent")

class SharedBus:
    """Thread-safe communication channel for agents."""
    def __init__(self):
        self.data = {}
        
    def publish(self, agent_name, key, value):
        self.data[f"{agent_name}:{key}"] = value

    def read(self, agent_name, key, default=None):
        return self.data.get(f"{agent_name}:{key}", default)

class MultiAgentDefenseSystem:
    """
    Cooperative defense engine utilizing MAPPO for coordination.
    """
    def __init__(self, num_episodes=50, episode_length=100):
        self.num_episodes = num_episodes
        self.episode_length = episode_length
        self.bus = SharedBus()

        # Define sizes matching Member 3 configuration details
        self.agents_config = {
            "NetworkDefender": {"obs_dim": 30, "act_dim": 4},
            "IncidentResponder": {"obs_dim": 25, "act_dim": 4},
            "ThreatIntelAgent": {"obs_dim": 20, "act_dim": 4},
            "PatchManager": {"obs_dim": 25, "act_dim": 4}
        }
        
        self.num_agents = len(self.agents_config)
        self.global_obs_dim = 100 # Sum of all individual observations (30 + 25 + 20 + 25)

        # Setup MAPPO agents
        self.mappo_agents = {}
        self.buffers = {}
        
        for name, config in self.agents_config.items():
            self.mappo_agents[name] = MAPPOAgent(
                obs_dim=config["obs_dim"],
                share_obs_dim=self.global_obs_dim,
                act_dim=config["act_dim"]
            )
            self.buffers[name] = ReplayBuffer(
                limit=self.episode_length,
                num_agents=self.num_agents,
                obs_dim=config["obs_dim"],
                share_obs_dim=self.global_obs_dim,
                act_dim=config["act_dim"]
            )

    def run_training(self):
        logger.info("Starting Multi-Agent Cooperative Training (MAPPO)...")
        
        for ep in range(self.num_episodes):
            # Reset episode
            local_obs = {
                "NetworkDefender": np.random.rand(30).astype(np.float32),
                "IncidentResponder": np.random.rand(25).astype(np.float32),
                "ThreatIntelAgent": np.random.rand(20).astype(np.float32),
                "PatchManager": np.random.rand(25).astype(np.float32)
            }
            
            # Reset buffers
            for name in self.agents_config:
                self.buffers[name].reset()

            total_reward = 0
            
            for step in range(self.episode_length):
                # 1. Shared communication phase
                self.bus.publish("NetworkDefender", "suspicious_ip", "10.1.0.99")
                self.bus.publish("ThreatIntelAgent", "threat_level", "HIGH")
                
                # Agents read communication details
                intel_msg = self.bus.read("ThreatIntelAgent", "threat_level", "LOW")
                
                # 2. Get joint observations
                # Shared observation is the concatenation of all local observations
                shared_obs = np.concatenate([
                    local_obs["NetworkDefender"],
                    local_obs["IncidentResponder"],
                    local_obs["ThreatIntelAgent"],
                    local_obs["PatchManager"]
                ])

                actions = {}
                log_probs = {}
                values = {}
                
                # 3. Action selection
                for name, agent in self.mappo_agents.items():
                    obs_t = torch.tensor(local_obs[name], dtype=torch.float32)
                    shared_obs_t = torch.tensor(shared_obs, dtype=torch.float32)
                    
                    with torch.no_grad():
                        action, log_prob, _ = agent.actor.get_action(obs_t)
                        value = agent.critic(shared_obs_t)
                        
                    actions[name] = action.item()
                    log_probs[name] = log_prob.item()
                    values[name] = value.item()

                # 4. Environment step simulation (Cooperative Shared Reward)
                # Compute a shared reward based on collective action correctness
                # If IncidentResponder patches while ThreatIntel reports high threat, reward increases
                reward = 1.0
                if intel_msg == "HIGH" and actions["IncidentResponder"] == 2:  # index 2 corresponds to patch
                    reward += 10.0
                if actions["NetworkDefender"] == 1:  # index 1 corresponds to block IP
                    reward += 5.0
                    
                total_reward += reward

                # 5. Populate next step observations
                next_local_obs = {
                    "NetworkDefender": np.random.rand(30).astype(np.float32),
                    "IncidentResponder": np.random.rand(25).astype(np.float32),
                    "ThreatIntelAgent": np.random.rand(20).astype(np.float32),
                    "PatchManager": np.random.rand(25).astype(np.float32)
                }

                # 6. Store transitions in replay buffers
                # Convert action dict to array format for storage
                action_array = np.array([actions[n] for n in self.agents_config])
                log_prob_array = np.array([log_probs[n] for n in self.agents_config])
                value_array = np.array([values[n] for n in self.agents_config])
                
                for name in self.agents_config:
                    self.buffers[name].insert(
                        obs=local_obs[name],
                        share_obs=shared_obs,
                        actions=action_array,
                        log_probs=log_prob_array,
                        reward=np.array([reward], dtype=np.float32),
                        values=value_array,
                        mask=np.array([1.0], dtype=np.float32)
                    )

                local_obs = next_local_obs

            # 7. Optimize agents
            actor_l_list = []
            critic_l_list = []
            for name, agent in self.mappo_agents.items():
                al, cl = agent.train_on_buffer(self.buffers[name])
                actor_l_list.append(al)
                critic_l_list.append(cl)
                
            logger.info(f"Episode {ep + 1}/{self.num_episodes} | Total Shared Reward: {total_reward:.2f} | Mean Actor Loss: {np.mean(actor_l_list):.4f} | Mean Critic Loss: {np.mean(critic_l_list):.4f}")

        logger.info("Cooperative Multi-Agent training run completed.")
        
        # Save policies
        import os
        os.makedirs("models/mappo", exist_ok=True)
        for name, agent in self.mappo_agents.items():
            torch.save(agent.actor.state_dict(), f"models/mappo/{name}_actor.pt")
            torch.save(agent.critic.state_dict(), f"models/mappo/{name}_critic.pt")
        logger.info("Saved MAPPO checkpoint files.")

if __name__ == "__main__":
    mads = MultiAgentDefenseSystem(num_episodes=5, episode_length=50)
    mads.run_training()
