import requests
import uuid
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (IncidentManager) %(message)s")
logger = logging.getLogger("ACDSF-IncidentManager")

class IncidentManager:
    """
    Manages incidents lifecycle.
    Binds alerts to incident cases and replicates updates to TheHive REST API.
    """
    def __init__(self, thehive_url="http://localhost:9000", api_key="mock_api_key"):
        self.thehive_url = thehive_url
        self.api_key = api_key
        self.incidents = {}

    def create_incident(self, alert: dict) -> str:
        """
        Creates an incident case.
        First tries to sync to TheHive, then saves locally.
        """
        case_id = str(uuid.uuid4())
        incident_case = {
            "case_id": case_id,
            "title": f"Incident: {alert['title']}",
            "description": alert["description"],
            "severity": self._map_severity(alert["severity"]),
            "status": "New",
            "ioc": alert["ioc"],
            "assigned_to": "SOC_Auto_Responder",
            "tasks": []
        }
        
        # Try REST sync to TheHive
        success = self._api_create_case(incident_case)
        if success:
            logger.info(f"Sync complete: Case created in TheHive for {alert['title']}.")
        else:
            logger.info(f"Local storage fallback: Case created internally ID: {case_id}")
            
        self.incidents[case_id] = incident_case
        return case_id

    def update_status(self, case_id: str, new_status: str):
        """Updates case resolution state."""
        if case_id in self.incidents:
            self.incidents[case_id]["status"] = new_status
            logger.info(f"Incident Case {case_id} status updated to: {new_status}")
            self._api_update_case(case_id, {"status": new_status})
        else:
            logger.warning(f"Failed to update status. Incident case {case_id} not found.")

    def add_task(self, case_id: str, task_title: str, task_status: str = "Waiting"):
        """Appends sub-actions as review checklist items inside tickets."""
        if case_id in self.incidents:
            task = {"task_id": str(uuid.uuid4()), "title": task_title, "status": task_status}
            self.incidents[case_id]["tasks"].append(task)
            logger.info(f"Task '{task_title}' added to Case {case_id}")
        else:
            logger.warning(f"Case {case_id} not found for appending task.")

    def _map_severity(self, raw_severity: str) -> int:
        mapping = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        return mapping.get(raw_severity, 2)

    def _api_create_case(self, case_data: dict) -> bool:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            r = requests.post(f"{self.thehive_url}/api/v1/case", json=case_data, headers=headers, timeout=0.5)
            if r.status_code in [200, 201]:
                return True
        except requests.exceptions.RequestException:
            pass
        return False

    def _api_update_case(self, case_id: str, updates: dict) -> bool:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            r = requests.patch(f"{self.thehive_url}/api/v1/case/{case_id}", json=updates, headers=headers, timeout=0.5)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        return False
