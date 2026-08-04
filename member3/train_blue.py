import argparse
import os
import gymnasium as gym
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback, StopTrainingOnNoModelImprovement
from stable_baselines3.common.monitor import Monitor
from blue_env import BlueTeamEnv

# Create folders for models and logs
os.makedirs("models/dqn", exist_ok=True)
os.makedirs("models/ppo", exist_ok=True)
os.makedirs("models/curriculum", exist_ok=True)
os.makedirs("logs", exist_ok=True)

class CurriculumBlueEnv(BlueTeamEnv):
    """
    Subclass of BlueTeamEnv that adjusts difficulty dynamically
    based on training progress (step count).
    """
    def __init__(self, difficulty=1, **kwargs):
        super().__init__(**kwargs)
        self.difficulty = difficulty
        logger = self.observation_space  # reference variables to avoid lints
        
    def _simulate_adversary(self):
        # Adjust threat arrival intervals dynamically based on difficulty
        interval = 25 if self.difficulty == 1 else (15 if self.difficulty == 2 else 8)
        if self.current_step % interval == 0:
            target_host = (self.current_step * 7) % 60
            if target_host not in self.patched_hosts and target_host not in self.isolated_hosts:
                self.compromised_hosts.add(target_host)
                self.state[target_host] = 0.0
                self.alerts_triggered += 1

def train_dqn(timesteps=50000):
    print("\n--- Training DQN Blue Agent ---")
    env = Monitor(BlueTeamEnv())
    eval_env = Monitor(BlueTeamEnv())
    
    # Callbacks
    checkpoint_cb = CheckpointCallback(
        save_freq=10000, save_path="./models/dqn/", name_prefix="blue_dqn"
    )
    stop_cb = StopTrainingOnNoModelImprovement(max_no_improvement_evals=5, min_evals=5, verbose=1)
    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path="./models/dqn/best/",
        log_path="./logs/dqn/",
        eval_freq=5000,
        callback_after_eval=stop_cb,
        verbose=1
    )
    
    model = DQN(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=5e-4,
        buffer_size=10000,
        batch_size=64,
        gamma=0.99,
        exploration_fraction=0.2,
        exploration_final_eps=0.05,
        tensorboard_log="./logs/tb/"
    )
    
    model.learn(total_timesteps=timesteps, callback=[checkpoint_cb, eval_cb])
    model.save("models/dqn/blue_dqn_final")
    print("DQN Training complete.")

def train_ppo(timesteps=50000):
    print("\n--- Training PPO Blue Agent ---")
    env = Monitor(BlueTeamEnv())
    eval_env = Monitor(BlueTeamEnv())
    
    checkpoint_cb = CheckpointCallback(
        save_freq=10000, save_path="./models/ppo/", name_prefix="blue_ppo"
    )
    stop_cb = StopTrainingOnNoModelImprovement(max_no_improvement_evals=5, min_evals=5, verbose=1)
    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path="./models/ppo/best/",
        log_path="./logs/ppo/",
        eval_freq=5000,
        callback_after_eval=stop_cb,
        verbose=1
    )
    
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        tensorboard_log="./logs/tb/"
    )
    
    model.learn(total_timesteps=timesteps, callback=[checkpoint_cb, eval_cb])
    model.save("models/ppo/blue_ppo_final")
    print("PPO Training complete.")

def train_curriculum(timesteps=60000):
    print("\n--- Training Curriculum-Based Blue Agent (PPO) ---")
    
    # Curriculum split into 3 phases: Easy, Medium, Hard
    steps_per_phase = timesteps // 3
    model = None
    
    for phase, difficulty in enumerate([1, 2, 3], start=1):
        print(f"\n>> Phase {phase} - Difficulty level: {difficulty}")
        env = Monitor(CurriculumBlueEnv(difficulty=difficulty))
        
        if model is None:
            model = PPO(
                "MlpPolicy",
                env,
                verbose=1,
                learning_rate=3e-4,
                n_steps=1024,
                batch_size=64,
                n_epochs=5,
                gamma=0.99,
                tensorboard_log="./logs/tb/"
            )
        else:
            model.set_env(env)
            
        model.learn(total_timesteps=steps_per_phase)
        
    model.save("models/curriculum/blue_curriculum_final")
    print("Curriculum Training complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ACDSF Blue Agent Training")
    parser.add_argument("--algorithm", type=str, default="ppo", choices=["dqn", "ppo", "curriculum", "all"], help="Algorithm to train")
    parser.add_argument("--steps", type=int, default=15000, help="Training timesteps")
    args = parser.parse_args()
    
    if args.algorithm == "dqn":
        train_dqn(args.steps)
    elif args.algorithm == "ppo":
        train_ppo(args.steps)
    elif args.algorithm == "curriculum":
        train_curriculum(args.steps)
    elif args.algorithm == "all":
        train_dqn(args.steps)
        train_ppo(args.steps)
        train_curriculum(args.steps)
