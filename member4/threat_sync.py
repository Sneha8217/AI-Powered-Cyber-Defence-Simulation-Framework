import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (ThreatSync) %(message)s")
logger = logging.getLogger("ACDSF-ThreatSync")

class ThreatIntelligenceSynchronizer:
    """
    Threat intelligence feeds synchronization (MISP).
    Pulls Indicators of Compromise (IOCs) such as malicious IPs and hashes.
    """
    def __init__(self, misp_url="http://localhost:80", api_key="misp_auth_key"):
        self.misp_url = misp_url
        self.api_key = api_key
        self.ioc_cache = []

    def sync_feeds(self) -> int:
        """
        Synchronizes threat data. Falls back to static seed if MISP server is offline.
        """
        logger.info("Synchronizing threat feeds from MISP...")
        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        try:
            r = requests.get(f"{self.misp_url}/events/index", headers=headers, timeout=0.5)
            if r.status_code == 200:
                data = r.json()
                # Parse IOCs
                self.ioc_cache = self._parse_misp_events(data)
                logger.info(f"Successfully synchronized {len(self.ioc_cache)} active IOCs from MISP.")
                return len(self.ioc_cache)
        except requests.exceptions.RequestException:
            pass

        # Simulator fallback sync
        logger.info("MISP server offline. Loading local intelligence cache database...")
        self.ioc_cache = [
            {"type": "ip", "value": "198.51.100.42", "description": "DDoS Attacker Botnet Node"},
            {"type": "ip", "value": "203.0.113.15", "description": "Ransomware Command and Control Server"},
            {"type": "domain", "value": "phish-portal.acdsf.com", "description": "Credential Harvester Landing Site"}
        ]
        return len(self.ioc_cache)

    def _parse_misp_events(self, events) -> list:
        parsed = []
        for ev in events:
            # dummy parsing structure
            parsed.append({"type": "ip", "value": "198.51.100.42", "description": ev.get("info", "Unknown threat")})
        return parsed
        
if __name__ == "__main__":
    sync = ThreatIntelligenceSynchronizer()
    count = sync.sync_feeds()
    print(f"Synchronized {count} indicators.")
