import time
import random
import logging
from prometheus_client import start_http_server, Gauge

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (PromExporter) %(message)s")
logger = logging.getLogger("ACDSF-PromExporter")

# Define prometheus metrics
CPU_USAGE = Gauge("acdssf_system_cpu_usage", "Current CPU Usage percentage")
MEMORY_USAGE = Gauge("acdssf_system_memory_usage", "Current Memory Usage percentage")
ACTIVE_INCIDENTS = Gauge("acdssf_soc_active_incidents", "Number of active incidents in SOAR")
RL_AVERAGE_REWARD = Gauge("acdssf_rl_average_reward", "Mean episodic reward of RL agent")
THREAT_LEVEL = Gauge("acdssf_global_threat_level", "Calculated global risk threat level [0-100]")

def start_exporter(port=8020):
    start_http_server(port)
    logger.info(f"Prometheus metrics exporter started on port {port}")
    
    # Infinite loop to update metrics periodically
    try:
        while True:
            # Simulate metrics gathering
            CPU_USAGE.set(random.uniform(15.0, 45.0))
            MEMORY_USAGE.set(random.uniform(40.0, 65.0))
            ACTIVE_INCIDENTS.set(random.randint(0, 5))
            RL_AVERAGE_REWARD.set(random.uniform(180.0, 220.0))
            THREAT_LEVEL.set(random.uniform(10.0, 35.0))
            
            time.sleep(15)
    except KeyboardInterrupt:
        logger.info("Shutting down exporter daemon.")

if __name__ == "__main__":
    # Start in daemon mode or block
    start_exporter()
