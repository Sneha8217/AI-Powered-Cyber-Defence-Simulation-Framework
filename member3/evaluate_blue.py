import os
import argparse
import numpy as np
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.evaluation import evaluate_policy
from blue_env import BlueTeamEnv

def evaluate_model(model_path, algo_name, episodes=10):
    print(f"\nEvaluating {algo_name} agent...")
    env = BlueTeamEnv()
    
    # Check if model exists
    if not os.path.exists(model_path) and not model_path.endswith(".zip"):
        zip_path = model_path + ".zip"
        if not os.path.exists(zip_path):
            print(f"[Warning] Model file {model_path} not found. Running random agent instead.")
            run_random_agent(episodes)
            return None, None
            
    # Load model
    try:
        if "dqn" in algo_name.lower():
            model = DQN.load(model_path)
        else:
            model = PPO.load(model_path)
            
        mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=episodes)
        print(f"Results for {algo_name}:")
        print(f"  Mean Reward: {mean_reward:.2f} +/- {std_reward:.2f}")
        return mean_reward, std_reward
    except Exception as e:
        print(f"Failed to load or evaluate model {model_path}: {e}")
        return None, None

def run_random_agent(episodes=5):
    env = BlueTeamEnv()
    rewards = []
    
    for ep in range(episodes):
        obs, _ = env.reset()
        done = False
        total_reward = 0
        while not done:
            action = env.action_space.sample()  # Random Action
            obs, reward, term, trunc, info = env.step(action)
            total_reward += reward
            done = term or trunc
        rewards.append(total_reward)
        print(f"  Episode {ep + 1} Random Reward: {total_reward:.2f}")
        
    print(f"Random Agent Mean Reward: {np.mean(rewards):.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ACDSF Blue Team Model Evaluator")
    parser.add_argument("--dqn_path", type=str, default="models/dqn/blue_dqn_final", help="Path to DQN model")
    parser.add_argument("--ppo_path", type=str, default="models/ppo/blue_ppo_final", help="Path to PPO model")
    parser.add_argument("--curriculum_path", type=str, default="models/curriculum/blue_curriculum_final", help="Path to Curriculum model")
    parser.add_argument("--episodes", type=int, default=5, help="Number of evaluation episodes")
    args = parser.parse_args()

    # Evaluate each if they exist, or show fallback output
    results = {}
    
    r_dqn = evaluate_model(args.dqn_path, "DQN", args.episodes)
    if r_dqn[0] is not None:
        results["DQN"] = r_dqn
        
    r_ppo = evaluate_model(args.ppo_path, "PPO", args.episodes)
    if r_ppo[0] is not None:
        results["PPO"] = r_ppo

    r_curr = evaluate_model(args.curriculum_path, "Curriculum PPO", args.episodes)
    if r_curr[0] is not None:
        results["Curriculum PPO"] = r_curr
        
    if results:
        print("\n--- Comparative Leaderboard ---")
        for k, v in sorted(results.items(), key=lambda item: item[1][0], reverse=True):
            print(f"Agent: {k:20s} | Mean Reward: {v[0]:10.2f} +/- {v[1]:.2f}")
