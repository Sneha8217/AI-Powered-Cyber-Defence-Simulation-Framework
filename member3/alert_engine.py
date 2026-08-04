import re
import uuid
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (AlertEngine) %(message)s")
logger = logging.getLogger("ACDSF-AlertEngine")

class AlertEngine:
    """
    Threat detection rules engine.
    Scans logs/events to match signatures, extract IOCs, and generate alert tickets.
    """
    def __init__(self):
        # Known indicators of compromise (blacklisted values)
        self.malicious_ips = {"198.51.100.42", "203.0.113.15", "192.0.2.77"}
        self.malicious_hashes = {"e99a18c428cb38d5f260853678922e03", "4a7d1ed414474e4033ac29ccb8653d9b"}
        
    def analyze_log(self, log_line: str) -> dict:
        """
        Analyzes a single raw log string.
        Extracts IPs, matches against signatures, and triggers alerts.
        """
        alert = None
        
        # Check IP indicators
        ip_matches = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", log_line)
        for ip in ip_matches:
            if ip in self.malicious_ips:
                alert = self._create_alert(
                    title="Malicious IP Connection Attempt",
                    description=f"Connection match to blacklisted threat intel IP: {ip}",
                    severity="High",
                    ioc_type="ip",
                    ioc_value=ip
                )
                break
                
        # Check for DDoS/Flooding patterns
        if not alert and "SYN Flood" in log_line or "packet threshold exceeded" in log_line:
            src_ip = ip_matches[0] if ip_matches else "Unknown"
            alert = self._create_alert(
                title="DDoS Traffic Anomaly",
                description=f"Traffic spike observed from source IP: {src_ip}",
                severity="Critical",
                ioc_type="ip",
                ioc_value=src_ip
            )
            
        # Check for Ransomware/Malware patterns
        if not alert and ("unauthorized encryption" in log_line.lower() or "shadow copy deleted" in log_line.lower()):
            alert = self._create_alert(
                title="Ransomware Activity Detected",
                description="Indicators of volume encryption or volume shadow copy deletion.",
                severity="Critical",
                ioc_type="activity",
                ioc_value="Ransomware execution signature"
            )
            
        return alert

    def _create_alert(self, title, description, severity, ioc_type, ioc_value) -> dict:
        alert_id = str(uuid.uuid4())
        alert_payload = {
            "alert_id": alert_id,
            "title": title,
            "description": description,
            "severity": severity,
            "ioc": {
                "type": ioc_type,
                "value": ioc_value
            },
            "status": "New",
            "timestamp": uuid.uuid4().hex[:8]  # unique execution mark
        }
        logger.info(f"[*] Alert Generated: [{severity}] {title} - IOC: {ioc_value}")
        return alert_payload
