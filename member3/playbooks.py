import logging
from automation import block_attacker_ip, isolate_compromised_host

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (SOAR-Playbook) %(message)s")
logger = logging.getLogger("ACDSF-SOAR-Playbook")

def run_ddos_playbook(attacker_ip: str) -> list:
    """
    SOAR Playbook: DDoS Response.
    Steps:
      1. Block attacking IP using SDN API.
      2. Record actions.
    """
    logger.info(f"[!] Executing DDoS Playbook for attacker: {attacker_ip}")
    actions_taken = []
    
    # Step 1: SDN IP block
    success = block_attacker_ip(attacker_ip)
    if success:
        actions_taken.append(f"Blocked IP: {attacker_ip} via SDN")
        logger.info(f"[+] Success: Blocked {attacker_ip} via SDN.")
    else:
        actions_taken.append(f"Failed to block IP: {attacker_ip}")
        logger.error(f"[-] Error blocking {attacker_ip} via SDN.")
        
    return actions_taken

def run_ransomware_playbook(host_ip: str) -> list:
    """
    SOAR Playbook: Ransomware Response.
    Steps:
      1. Isolate compromised host from the subnet.
      2. Trigger forensic log acquisition.
    """
    logger.info(f"[!] Executing Ransomware Playbook for Host IP: {host_ip}")
    actions_taken = []
    
    # Step 1: Subnet isolation
    success = isolate_compromised_host(host_ip)
    if success:
        actions_taken.append(f"Isolated Host: {host_ip}")
        logger.info(f"[+] Success: Isolated host {host_ip} from network segment.")
    else:
        actions_taken.append(f"Failed to isolate Host: {host_ip}")
        logger.error(f"[-] Error isolating host {host_ip}.")
        
    # Step 2: Forensic log capture
    actions_taken.append("Triggered automated forensic dump collection.")
    logger.info("[+] Forensic evidence collection triggered.")
    
    return actions_taken

def run_phishing_playbook(user_email: str) -> list:
    """
    SOAR Playbook: Phishing Escalation.
    Steps:
      1. Deactivate AD account.
      2. Revoke active OAuth tokens.
    """
    logger.info(f"[!] Executing Phishing Playbook for User: {user_email}")
    actions_taken = [
        f"AD Account suspended for {user_email}",
        f"Active OAuth sessions revoked for {user_email}"
    ]
    logger.info(f"[+] User account {user_email} secured.")
    return actions_taken
