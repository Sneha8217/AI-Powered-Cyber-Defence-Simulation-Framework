from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import requests

router = APIRouter()

# Simple mock database
INCIDENTS_DB = [
    {
        "id": "1",
        "title": "Unidentified Port Sweep",
        "severity": "Medium",
        "status": "Investigating",
        "sector": "Government",
        "timestamp": "2026-08-04 12:45:00"
    },
    {
        "id": "2",
        "title": "SCADA Protocol Anomaly",
        "severity": "Critical",
        "status": "Contained",
        "sector": "Energy",
        "timestamp": "2026-08-04 12:48:12"
    }
]

# Request validation schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class PlaybookRequest(BaseModel):
    playbook_name: str
    target_ip: str

# ----------------- Role: Administrator Endpoints -----------------
@router.post("/admin/sdn/block", tags=["Administrator"])
def admin_block_ip(ip: str):
    """
    Commands the SDN controller to block an IP.
    """
    try:
        r = requests.post("http://localhost:8000/block-host", json={"ip": ip}, timeout=0.5)
        return r.json()
    except requests.exceptions.RequestException:
        # Fallback simulation
        return {"status": "blocked (simulated)", "ip": ip}

@router.get("/admin/system-health", tags=["Administrator"])
def get_system_health():
    return {
        "services": {
            "SDN_Gateway": "Healthy",
            "Ditto_Twin": "Healthy",
            "InfluxDB": "Healthy",
            "TTP_Extractor": "Healthy",
            "SOAR_Playbooks": "Healthy",
            "GNN_Anomaly_Detector": "Healthy"
        },
        "system": {"cpu": "24%", "memory": "48%"}
    }

# ----------------- Role: Analyst Endpoints -----------------
@router.get("/analyst/alerts", tags=["Analyst"], response_model=List[Dict[str, Any]])
def get_alerts():
    """
    Returns lists of active alerts.
    """
    return INCIDENTS_DB

@router.post("/analyst/xai/explain", tags=["Analyst"])
def get_xai_explanation(features: List[float]):
    """
    Generates explanation plot for a given set of features.
    """
    try:
        r = requests.post("http://localhost:8010/explain/alert", json={"alert_id": "test", "features": features}, timeout=0.5)
        return r.json()
    except requests.exceptions.RequestException:
        # Generate inline fallback base64 diagram details
        from shap_explainer import AlertShapExplainer
        from visualization import generate_waterfall_base64
        explainer = AlertShapExplainer()
        res = explainer.explain_instance(features)
        b64 = generate_waterfall_base64(res["shap_values"])
        return {
            "alert_id": "test",
            "decision": res["prediction"],
            "confidence": f"{res['confidence'] * 100:.1f}%",
            "explanation": "High src_ip_reputation combined with protocol_anomaly triggered alert.",
            "chart_base64": b64
        }

# ----------------- Role: Incident Manager Endpoints -----------------
@router.post("/manager/playbook/trigger", tags=["Incident Manager"])
def trigger_playbook(req: PlaybookRequest):
    """
    Triggers automated playbook workflow commands.
    """
    if "ddos" in req.playbook_name.lower():
        from playbooks import run_ddos_playbook
        actions = run_ddos_playbook(req.target_ip)
    elif "ransomware" in req.playbook_name.lower():
        from playbooks import run_ransomware_playbook
        actions = run_ransomware_playbook(req.target_ip)
    else:
        raise HTTPException(status_code=400, detail="Unknown playbook type")
        
    return {"status": "Execution Complete", "actions_taken": actions}

@router.get("/manager/tickets", tags=["Incident Manager"])
def list_tickets():
    return INCIDENTS_DB

# ----------------- Role: Executive Endpoints -----------------
@router.get("/executive/security-score", tags=["Executive"])
def get_security_score():
    from metrics import KPICalculator
    calc = KPICalculator()
    return {
        "security_score": calc.get_overall_security_score(),
        "threat_level": "LOW-MEDIUM",
        "risk_by_sector": {
            "Energy": 15.0,
            "Government": 8.0,
            "Finance": 5.0,
            "Water": 10.0,
            "Telecom": 12.0,
            "Transport": 9.0
        }
    }
