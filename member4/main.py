import os
import sys
import time
import threading
import uvicorn
import logging

# Ensure project root is in python path to resolve modules correctly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from member4.config import EXPORTER_PORT, DASHBOARD_BACKEND_PORT, XAI_API_PORT
from shared.mock_services import start_all_mocks

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (Framework-Main) %(message)s")
logger = logging.getLogger("ACDSF-Core-Integration")

# ----------------- Step 1: Start XAI Server (Port 8010) -----------------
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app_xai = FastAPI(title="ACDSF XAI API Service")

class XaiRequest(BaseModel):
    alert_id: str
    features: List[float]

@app_xai.post("/explain/alert")
def explain_alert_api(req: XaiRequest):
    try:
        from member4.shap_explainer import AlertShapExplainer
        from member4.visualization import generate_waterfall_base64
        
        explainer = AlertShapExplainer()
        res = explainer.explain_instance(req.features)
        b64_chart = generate_waterfall_base64(res["shap_values"])
        
        return {
            "alert_id": req.alert_id,
            "decision": res["prediction"],
            "confidence": f"{res['confidence'] * 100:.1f}%",
            "explanation": f"Primary indicators: {list(res['shap_values'].keys())[0]} heavily influenced this alert.",
            "chart_base64": b64_chart
        }
    except Exception as e:
        logger.error(f"XAI calculation failed: {e}")
        return {"error": str(e)}

@app_xai.get("/health")
def xai_health():
    return {"status": "XAI API running"}

def run_xai_server():
    uvicorn.run(app_xai, host="0.0.0.0", port=XAI_API_PORT, log_level="warning")

# ----------------- Step 2: Start Prometheus Exporter (Port 8020) -----------------
def run_prometheus_exporter():
    from member4.exporter import start_exporter
    start_exporter(port=EXPORTER_PORT)

# ----------------- Step 3: Start Dashboard API Server (Port 8030) -----------------
def run_dashboard_backend():
    # Dynamic import to ensure paths are loaded
    from member4.backend.api import app as dashboard_app
    uvicorn.run(dashboard_app, host="0.0.0.0", port=DASHBOARD_BACKEND_PORT, log_level="info")

def main():
    logger.info("Initializing AI-Powered Cyber Defence Simulation Framework (ACDSF)...")
    
    # 1. Boot up simulated mocks (SDN, Ditto, InfluxDB, TTP, KG)
    start_all_mocks()
    time.sleep(1) # Allow server sockets to bind
    
    # 2. Spin up XAI service
    t_xai = threading.Thread(target=run_xai_server, daemon=True)
    t_xai.start()
    logger.info(f"XAI explanation service launched on port {XAI_API_PORT}")

    # 3. Spin up Prometheus metric exporter
    t_prom = threading.Thread(target=run_prometheus_exporter, daemon=True)
    t_prom.start()
    logger.info(f"Prometheus metrics exporter server launched on port {EXPORTER_PORT}")
    
    # 4. Start main FastAPI Dashboard Backend (blocks thread)
    logger.info(f"Starting human interface dashboard server on port {DASHBOARD_BACKEND_PORT}...")
    run_dashboard_backend()

if __name__ == "__main__":
    main()
