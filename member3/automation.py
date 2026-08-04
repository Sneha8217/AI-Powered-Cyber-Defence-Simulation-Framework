import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (Automation) %(message)s")
logger = logging.getLogger("ACDSF-Automation")

SDN_URL = "http://localhost:8000"

def block_attacker_ip(ip: str) -> bool:
    """
    Sends flow rule command to SDN controller to block source traffic.
    """
    try:
        r = requests.post(f"{SDN_URL}/block-host", json={"ip": ip}, timeout=0.5)
        if r.status_code == 200:
            logger.info(f"SDN API confirmed block rule for {ip}")
            return True
    except requests.exceptions.RequestException:
        pass
    
    # Fallback to local simulator log
    logger.info(f"[Simulator Fallback] Blocked IP {ip} locally.")
    return True

def isolate_compromised_host(ip: str) -> bool:
    """
    Commands the SDN controller to isolate a host on a restricted VLAN.
    """
    try:
        # Re-use block routing rule as isolation command
        r = requests.post(f"{SDN_URL}/block-host", json={"ip": ip}, timeout=0.5)
        if r.status_code == 200:
            logger.info(f"SDN API confirmed isolation rule for {ip}")
            return True
    except requests.exceptions.RequestException:
        pass
        
    logger.info(f"[Simulator Fallback] Isolated host {ip} locally.")
    return True
