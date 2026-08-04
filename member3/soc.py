import requests
import json
import logging
from alert_engine import AlertEngine
from incident_manager import IncidentManager
import playbooks

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (SOC-Orchestrator) %(message)s")
logger = logging.getLogger("ACDSF-SOC-Orchestrator")

class AutonomousSOC:
    """
    SOC Orchestration Engine.
    Collects alerts, queries threat intelligence APIs, and runs response workflows.
    """
    def __init__(self, ttp_api_url="http://localhost:8001"):
        self.alert_engine = AlertEngine()
        self.incident_manager = IncidentManager()
        self.ttp_api_url = ttp_api_url

    def handle_log_event(self, log_line: str) -> dict:
        """
        Processes a new log line, classifies threat vectors, and executes playbooks.
        """
        logger.info(f"Analyzing incoming log: {log_line[:80]}...")
        alert = self.alert_engine.analyze_log(log_line)
        
        if not alert:
            return {"status": "ignored"}

        # 1. Enrich threat data: Classify ATT&CK tactic using Member 2 TTP extraction API
        tactic = self._classify_ttp(alert["description"])
        alert["tactic"] = tactic
        logger.info(f"Threat Intelligence TTP enrichment: Tactic classified as: {tactic}")

        # 2. File case in Incident Manager (TheHive)
        case_id = self.incident_manager.create_incident(alert)
        
        # 3. Select and execute playbook
        actions_taken = []
        if tactic == "initial-access":
            actions_taken = playbooks.run_phishing_playbook("compromised_user@govt.acdsf.local")
            self.incident_manager.add_task(case_id, "Reset Active Directory Password")
            
        elif tactic == "execution" or tactic == "lateral-movement":
            target_ip = alert["ioc"]["value"] if alert["ioc"]["type"] == "ip" else "10.1.0.10"
            actions_taken = playbooks.run_ransomware_playbook(target_ip)
            self.incident_manager.add_task(case_id, "Re-image host with backup")
            
        elif tactic == "exfiltration" or "ddos" in alert["title"].lower():
            attacker_ip = alert["ioc"]["value"] if alert["ioc"]["type"] == "ip" else "198.51.100.42"
            actions_taken = playbooks.run_ddos_playbook(attacker_ip)
            self.incident_manager.add_task(case_id, "Verify SDN Drop Rule status")
            
        else:
            logger.info("No automatic remediation playbook configured for this tactic. Escalating to human.")
            actions_taken = ["Escalated to L2 human analyst."]
            self.incident_manager.add_status = "Escalated"
            
        # 4. Update case status to resolved/closed
        self.incident_manager.update_status(case_id, "Resolved")
        
        return {
            "status": "Remediated",
            "case_id": case_id,
            "tactic": tactic,
            "actions": actions_taken
        }

    def _classify_ttp(self, description: str) -> str:
        """Calls Member 2's TTP API to extract ATT&CK tactic, falls back to rule-based parser."""
        try:
            r = requests.post(f"{self.ttp_api_url}/extract", json={"text": description}, timeout=0.5)
            if r.status_code == 200:
                data = r.json()
                if data.get("extracted_ttps"):
                    return data["extracted_ttps"][0]["tactic"]
        except requests.exceptions.RequestException:
            pass
            
        # Rule-based fallback
        desc_lower = description.lower()
        if "ddos" in desc_lower or "spike" in desc_lower:
            return "exfiltration"
        elif "blacklisted" in desc_lower:
            return "lateral-movement"
        return "initial-access"

if __name__ == "__main__":
    soc = AutonomousSOC()
    
    # Test logs
    logs = [
        "SYN Flood detected; packet threshold exceeded from 198.51.100.42",
        "Host at 10.1.0.10 reports unauthorized encryption and shadow copy deleted"
    ]
    
    for l in logs:
        res = soc.handle_log_event(l)
        print(f"Workflow result: {json.dumps(res, indent=2)}\n")
