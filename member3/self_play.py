import gymnasium as gym
import numpy as np

class SelfPlayEnv(gym.Env):
    """
    Competitive environment for Self-Play simulation.
    Combines both the Red Team (attack) action space and Blue Team (defense) action space.
    """
    def __init__(self):
        super(SelfPlayEnv, self).__init__()

        # State size = 100 features
        # [0-59]: Host compromise flags (0.0=compromised, 1.0=secure)
        # [60-79]: Active alert levels
        # [80-99]: Security enforcement status
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(100,), dtype=np.float32
        )

        # Red actions (10): scan, exploit, lateral-move, exfiltrate...
        self.red_action_space = gym.spaces.Discrete(10)
        self.RED_ACTIONS = [
            'scan_ports', 'exploit_ssh', 'exploit_smb',
            'exploit_web', 'dump_credentials', 'create_persistence',
            'lateral_move', 'install_backdoor', 'exfiltrate', 'cover_tracks'
        ]

        # Blue actions (12): monitor, block IP, isolate, patch...
        self.blue_action_space = gym.spaces.Discrete(12)
        self.BLUE_ACTIONS = [
            'Monitor', 'Block_IP', 'Isolate_Host', 'Deploy_Honeypot',
            'Reset_Host', 'Patch_Vuln', 'Enable_IDS_Rule', 'Collect_Forensics',
            'Alert_Human', 'Restore_Service', 'Clear_FalsePos', 'Escalate'
        ]

        self.max_steps = 200
        self.reset()

    def reset(self, seed=None, options=None):
        self.current_step = 0
        self.compromised_hosts = set()
        self.blocked_ips = set()
        self.patched_hosts = set()
        self.alerts_triggered = 0

        self.state = np.ones(100, dtype=np.float32)
        self.state[60:100] = 0.0  # Reset alerts and metrics to zero
        
        return self.state, {}

    def step(self, red_action, blue_action):
        """
        Executes actions from both agents in a single time step.
        """
        self.current_step += 1
        
        red_name = self.RED_ACTIONS[red_action]
        blue_name = self.BLUE_ACTIONS[blue_action]

        red_reward = 0
        blue_reward = 0

        # --- Phase 1: Attack Execution ---
        if red_name == 'scan_ports':
            red_reward += 1.0
            self.state[60] = 0.2  # Trigger minor telemetry alert
        elif red_name == 'exploit_ssh' or red_name == 'exploit_smb':
            target = (self.current_step * 3) % 60
            if target not in self.patched_hosts and target not in self.blocked_ips:
                self.compromised_hosts.add(target)
                self.state[target] = 0.0  # Node compromised
                red_reward += 15.0
                self.alerts_triggered += 1
            else:
                red_reward -= 5.0  # exploit failed
        elif red_name == 'exfiltrate':
            if len(self.compromised_hosts) > 0:
                red_reward += 100.0  # Goal achieved
            else:
                red_reward -= 20.0

        # --- Phase 2: Defense Execution ---
        if blue_name == 'Block_IP':
            # Simulates blocking
            if self.alerts_triggered > 0:
                self.blocked_ips.add(self.current_step % 60)
                blue_reward += 30.0
                self.alerts_triggered = max(0, self.alerts_triggered - 1)
        elif blue_name == 'Isolate_Host':
            if self.compromised_hosts:
                isolated = self.compromised_hosts.pop()
                self.state[isolated] = 0.5  # Isolated state
                blue_reward += 40.0
        elif blue_name == 'Patch_Vuln':
            self.patched_hosts.add(self.current_step % 60)
            blue_reward += 15.0

        # Calculate joint observation updates
        self.state[60:80] = np.clip(self.alerts_triggered / 10.0, 0.0, 1.0)
        self.state[80:100] = len(self.compromised_hosts) / 20.0

        # Check episode termination
        terminated = len(self.compromised_hosts) >= 15 or len(self.compromised_hosts) == 0
        truncated = self.current_step >= self.max_steps
        done = terminated or truncated

        info = {
            "compromised_count": len(self.compromised_hosts),
            "blocked_count": len(self.blocked_ips),
            "alerts": self.alerts_triggered
        }

        return self.state, red_reward, blue_reward, done, info
