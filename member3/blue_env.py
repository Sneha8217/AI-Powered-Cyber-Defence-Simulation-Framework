import gymnasium as gym
import numpy as np
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (BlueEnv) %(message)s")
logger = logging.getLogger("ACDSF-BlueEnv")

class BlueTeamEnv(gym.Env):
    """
    Custom Gymnasium Environment for the Blue Team Defender.
    Integrates with:
      - Member 1's SDN Gateway for blocking/restoring hosts.
      - Member 1's Eclipse Ditto for status reporting.
    Supports a fully self-contained simulation mode if APIs are unreachable.
    """
    metadata = {"render_modes": ["ansi"]}

    def __init__(self, sdn_url="http://localhost:8000", ditto_url="http://localhost:8080"):
        super(BlueTeamEnv, self).__init__()
        
        self.sdn_url = sdn_url
        self.ditto_url = ditto_url

        # Observation Space: 100 features representing security states of the network
        # [0-59]: Asset status (6 sectors * 10 nodes each)
        # [60-79]: IDS alerts frequency
        # [80-89]: Active compromise flags
        # [90-99]: System metrics (CPU, Memory, Telemetry)
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(100,), dtype=np.float32
        )

        # Action Space: 12 actions the Blue Team defender can perform
        self.action_space = gym.spaces.Discrete(12)

        self.ACTION_NAMES = [
            'Monitor',            # 0: Gather observations
            'Block_IP',           # 1: Block attacker IP via SDN
            'Isolate_Host',       # 2: Cut off host from network
            'Deploy_Honeypot',    # 3: Deploy honeypot on target subnet
            'Reset_Host',         # 4: Re-image and restore host
            'Patch_Vuln',         # 5: Apply security patch
            'Enable_IDS_Rule',    # 6: Add detection signature
            'Collect_Forensics',  # 7: Collect logs/evidence from host
            'Alert_Human',        # 8: Escalate to SOC analyst
            'Restore_Service',    # 9: Bring blocked service back online
            'Clear_FalsePos',     # 10: Mark alert as false positive
            'Escalate'            # 11: Escalate to major incident manager
        ]

        self.max_steps = 500
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.current_step = 0
        self.compromised_hosts = set()
        self.blocked_ips = set()
        self.isolated_hosts = set()
        self.honeypots = set()
        self.patched_hosts = set()
        self.ids_rules_enabled = 0
        self.alerts_triggered = 0
        self.human_escalations = 0
        self.major_escalations = 0
        
        # Initialize observation state vector
        self.state = np.zeros(100, dtype=np.float32)
        # Populate initial assets (default healthy state)
        self.state[0:60] = 1.0  # 1.0 = Clean/Secure
        # Populate metrics
        self.state[90:100] = 0.1  # Normal low load telemetry

        logger.info("BlueTeamEnv reset completed.")
        return self.state, {}

    def step(self, action):
        self.current_step += 1
        action_name = self.ACTION_NAMES[action]
        reward = 0
        
        # Simulate network events (attacks occur dynamically based on steps)
        self._simulate_adversary()

        # Handle action implementation
        if action_name == 'Monitor':
            reward = 1.0  # Reward for scanning/observing without disruption
            
        elif action_name == 'Block_IP':
            # Block suspicious IP
            ip_to_block = self._get_most_suspicious_ip()
            if ip_to_block:
                success = self._api_block_ip(ip_to_block)
                if success:
                    reward = 50.0
                    self.blocked_ips.add(ip_to_block)
                    logger.info(f"Action: Block_IP succeeded for {ip_to_block}")
                else:
                    reward = -5.0
                    logger.warning("Action: Block_IP API request failed")
            else:
                reward = -10.0  # Penalty for false positive / invalid block
                logger.info("Action: Block_IP penalty (No suspicious IP found)")

        elif action_name == 'Isolate_Host':
            # Isolate a compromised host
            host_to_isolate = self._get_compromised_host()
            if host_to_isolate:
                self.isolated_hosts.add(host_to_isolate)
                # Lower compromised state feature
                idx = host_to_isolate % 60
                self.state[idx] = 0.5  # Isolated state value
                reward = 40.0
                logger.info(f"Action: Isolate_Host succeeded for Host {host_to_isolate}")
            else:
                reward = -15.0  # Penalty for unnecessary isolation
                logger.info("Action: Isolate_Host penalty (No compromised host found)")

        elif action_name == 'Deploy_Honeypot':
            # Deploy honeypots to divert traffic
            self.honeypots.add(self.current_step)
            reward = 15.0
            logger.info("Action: Deploy_Honeypot executed")

        elif action_name == 'Reset_Host':
            # Restore isolated/compromised hosts
            host_to_reset = next(iter(self.compromised_hosts), None)
            if host_to_reset:
                self.compromised_hosts.discard(host_to_reset)
                idx = host_to_reset % 60
                self.state[idx] = 1.0  # Secure state restored
                reward = 35.0
                logger.info(f"Action: Reset_Host completed for Host {host_to_reset}")
            else:
                reward = -5.0

        elif action_name == 'Patch_Vuln':
            # Immunize host from future exploits
            host_to_patch = self.current_step % 60
            self.patched_hosts.add(host_to_patch)
            reward = 20.0
            logger.info(f"Action: Patch_Vuln applied to Host {host_to_patch}")

        elif action_name == 'Enable_IDS_Rule':
            self.ids_rules_enabled += 1
            reward = 10.0
            logger.info("Action: Enable_IDS_Rule executed")

        elif action_name == 'Collect_Forensics':
            reward = 5.0
            logger.info("Action: Collect_Forensics completed")

        elif action_name == 'Alert_Human':
            self.human_escalations += 1
            reward = -5.0  # Penalize for unnecessary human escalations
            logger.info("Action: Alert_Human triggered")

        elif action_name == 'Restore_Service':
            # Restore blocked services
            if self.isolated_hosts:
                restored = self.isolated_hosts.pop()
                idx = restored % 60
                self.state[idx] = 1.0
                reward = 20.0
                logger.info(f"Action: Restore_Service succeeded for Host {restored}")
            else:
                reward = -5.0

        elif action_name == 'Clear_FalsePos':
            if self.alerts_triggered > 0:
                self.alerts_triggered = max(0, self.alerts_triggered - 1)
                reward = 15.0
                logger.info("Action: Clear_FalsePos executed")
            else:
                reward = -5.0

        elif action_name == 'Escalate':
            self.major_escalations += 1
            reward = -10.0
            logger.info("Action: Escalate triggered")

        # Sync state with Eclipse Ditto Mock if available
        self._sync_ditto_state()

        # Update metrics in state vector
        self.state[60:80] = np.clip(self.alerts_triggered / 10.0, 0.0, 1.0)
        self.state[80:90] = len(self.compromised_hosts) / 10.0

        # Terminated / Truncated conditions
        terminated = len(self.compromised_hosts) >= 10  # Out of control breach
        truncated = self.current_step >= self.max_steps
        
        info = {
            "compromised_hosts_count": len(self.compromised_hosts),
            "blocked_ips_count": len(self.blocked_ips),
            "alerts_triggered": self.alerts_triggered,
            "steps": self.current_step
        }

        return self.state, reward, terminated, truncated, info

    def _simulate_adversary(self):
        """Simulates attack steps arriving to the environment."""
        # Simple threat injection model
        if self.current_step % 15 == 0:
            target_host = (self.current_step * 7) % 60
            if target_host not in self.patched_hosts and target_host not in self.isolated_hosts:
                self.compromised_hosts.add(target_host)
                self.state[target_host] = 0.0  # 0.0 = Compromised state
                self.alerts_triggered += 1
                logger.info(f"[Threat] Host {target_host} compromised by adversary!")

    def _get_most_suspicious_ip(self):
        """Utility logic to identify suspicious IP."""
        if self.alerts_triggered > 0:
            # Simulated suspicious IP
            return f"10.1.0.{100 + self.current_step % 50}"
        return None

    def _get_compromised_host(self):
        """Utility logic to retrieve active compromised host ID."""
        if self.compromised_hosts:
            return next(iter(self.compromised_hosts))
        return None

    def _api_block_ip(self, ip):
        """Calls Member 1's SDN API to block the IP with fallback to mock simulation."""
        try:
            r = requests.post(f"{self.sdn_url}/block-host", json={"ip": ip}, timeout=0.5)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        # Fallback simulation
        logger.info(f"[Simulation Fallback] Local bypass blocked IP {ip} successfully.")
        return True

    def _sync_ditto_state(self):
        """Pushes current simulation statuses to Eclipse Ditto API."""
        payload = {
            "properties": {
                "cpu_load": int(np.mean(self.state[90:100]) * 100),
                "is_compromised": len(self.compromised_hosts) > 0,
                "alert_count": self.alerts_triggered,
                "blocked_hosts": list(self.blocked_ips)
            }
        }
        try:
            requests.put(
                f"{self.ditto_url}/api/2/things/acdsf:BlueDefender/features/status/properties",
                json=payload,
                timeout=0.5
            )
        except requests.exceptions.RequestException:
            pass # Silent ignore when offline or mock not listening
