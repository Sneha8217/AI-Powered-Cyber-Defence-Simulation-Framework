import os
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from self_play import SelfPlayEnv

# Simple PyTorch policy structure for self-play training
class SimplePolicy(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(SimplePolicy, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim),
            nn.Softmax(dim=-1)
        )
    def act(self, state):
        state_t = torch.tensor(state, dtype=torch.float32)
        probs = self.forward(state_t)
        action = torch.multinomial(probs, 1).item()
        return action, torch.log(probs[action])

def train_self_play(rounds=5, steps_per_round=100):
    print("Initializing competitive self-play training loop...")
    env = SelfPlayEnv()
    
    # Initialize policies for both players
    red_policy = SimplePolicy(100, 10)
    blue_policy = SimplePolicy(100, 12)
    
    red_optimizer = optim.Adam(red_policy.parameters(), lr=0.01)
    blue_optimizer = optim.Adam(blue_policy.parameters(), lr=0.01)
    
    red_wins = 0
    blue_wins = 0
    
    print("\nStarting Self-Play Competition...")
    print("Round | Red Total Reward | Blue Total Reward | Round Winner")
    print("-" * 60)
    
    for r in range(1, rounds + 1):
        state, _ = env.reset()
        done = False
        
        red_log_probs = []
        blue_log_probs = []
        red_rewards = []
        blue_rewards = []
        
        step_count = 0
        while not done and step_count < steps_per_round:
            step_count += 1
            
            # Agents choose action
            red_action, red_lp = red_policy.act(state)
            blue_action, blue_lp = blue_policy.act(state)
            
            # Step environment
            next_state, red_r, blue_r, done, info = env.step(red_action, blue_action)
            
            # Accumulate records
            red_log_probs.append(red_lp)
            blue_log_probs.append(blue_lp)
            red_rewards.append(red_r)
            blue_rewards.append(blue_r)
            
            state = next_state
            
        # Determine winner
        red_total = sum(red_rewards)
        blue_total = sum(blue_rewards)
        
        winner = "RED" if red_total > blue_total else "BLUE"
        if winner == "RED":
            red_wins += 1
            # Retrain BLUE (loser)
            # Standard reinforcement policy gradient update
            loss = -torch.stack(blue_log_probs).mean() * (blue_total - red_total)
            blue_optimizer.zero_grad()
            loss.backward()
            blue_optimizer.step()
        else:
            blue_wins += 1
            # Retrain RED (loser)
            loss = -torch.stack(red_log_probs).mean() * (red_total - blue_total)
            red_optimizer.zero_grad()
            loss.backward()
            red_optimizer.step()

        print(f" {r:3d}  | {red_total:16.2f} | {blue_total:17.2f} | {winner}")

    print("-" * 60)
    print("\nSelf-Play completed.")
    print(f"Red Wins: {red_wins}/{rounds} ({100 * red_wins // rounds}%)")
    print(f"Blue Wins: {blue_wins}/{rounds} ({100 * blue_wins // rounds}%)")

    # Save policies
    os.makedirs("models/selfplay", exist_ok=True)
    torch.save(red_policy.state_dict(), "models/selfplay/red_selfplay_final.pt")
    torch.save(blue_policy.state_dict(), "models/selfplay/blue_selfplay_final.pt")
    print("Policies saved successfully.")

if __name__ == "__main__":
    train_self_play(rounds=5, steps_per_round=50)
