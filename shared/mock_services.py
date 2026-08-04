import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
import threading
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ACDSF-MockServices")

# ----------------- PORT 8000: SDN Gateway Mock (Member 1) -----------------
app_sdn = FastAPI(title="ACDSF SDN Gateway Mock")
blocked_ips = set()

class BlockRequest(BaseModel):
    ip: str

@app_sdn.post("/block-host")
def block_host(req: BlockRequest):
    blocked_ips.add(req.ip)
    logger.info(f"SDN Blocked IP: {req.ip}")
    return {"status": "blocked", "ip": req.ip, "code": 200}

@app_sdn.post("/restore-host")
def restore_host(req: BlockRequest):
    blocked_ips.discard(req.ip)
    logger.info(f"SDN Restored IP: {req.ip}")
    return {"status": "restored", "ip": req.ip, "code": 200}

@app_sdn.get("/topology")
def get_topology():
    return {
        "nodes": [
            {"id": "GOVT-CORE-R1", "type": "router", "ip": "10.1.0.1"},
            {"id": "ENERGY-CORE-R1", "type": "router", "ip": "10.2.0.1"},
            {"id": "FINANCE-CORE-R1", "type": "router", "ip": "10.3.0.1"},
            {"id": "GOVT-SRV1", "type": "server", "ip": "10.1.0.10"},
            {"id": "ENERGY-SRV1", "type": "server", "ip": "10.2.0.20"},
            {"id": "FINANCE-DB-01", "type": "server", "ip": "10.3.0.15"}
        ],
        "links": [
            {"source": "GOVT-CORE-R1", "target": "NBR-01"},
            {"source": "ENERGY-CORE-R1", "target": "NBR-01"},
            {"source": "FINANCE-CORE-R1", "target": "NBR-01"}
        ]
    }

# ----------------- PORT 8080: Eclipse Ditto Mock (Member 1) -----------------
app_ditto = FastAPI(title="Eclipse Ditto Mock")
ditto_store = {}

@app_ditto.put("/api/2/things/{thing_id}/features/status/properties")
async def update_ditto_properties(thing_id: str, request: Request):
    data = await request.json()
    ditto_store[thing_id] = data
    logger.info(f"Ditto Updated thing {thing_id}: {data}")
    return {"status": "updated"}

@app_ditto.get("/api/2/things/{thing_id}")
def get_ditto_thing(thing_id: str):
    if thing_id not in ditto_store:
        return {
            "thingId": thing_id,
            "attributes": {"sector": "Unknown", "type": "device", "ip": "0.0.0.0"},
            "features": {"status": {"properties": {"is_alive": True, "cpu_load": 10, "alert_count": 0}}}
        }
    return ditto_store[thing_id]

# ----------------- PORT 8001: TTP Extraction API (Member 2) -----------------
app_ttp = FastAPI(title="TTP Extraction API Mock")

class TtpRequest(BaseModel):
    text: str

@app_ttp.post("/extract")
def extract_ttps(req: TtpRequest):
    logger.info(f"TTP Extracting from text: {req.text[:60]}...")
    # Simple rule-based mock
    text_lower = req.text.lower()
    if "phish" in text_lower or "email" in text_lower:
        tactic, confidence = "initial-access", 0.92
    elif "powershell" in text_lower or "run" in text_lower:
        tactic, confidence = "execution", 0.85
    elif "lsass" in text_lower or "credential" in text_lower:
        tactic, confidence = "credential-access", 0.88
    elif "lateral" in text_lower or "smb" in text_lower:
        tactic, confidence = "lateral-movement", 0.90
    elif "exfiltrat" in text_lower:
        tactic, confidence = "exfiltration", 0.95
    else:
        tactic, confidence = "discovery", 0.70
        
    return {
        "extracted_ttps": [
            {"tactic": tactic, "confidence": confidence},
            {"tactic": "reconnaissance", "confidence": 0.15}
        ]
    }

# ----------------- PORT 8002: Knowledge Graph API Mock (Member 2) -----------------
app_kg = FastAPI(title="Knowledge Graph API Mock")

@app_kg.get("/attack-paths/{sector}")
def get_attack_paths(sector: str):
    return [
        {"actor": "APT28", "technique": "T1566.001", "technique_name": "Spearphishing Attachment", "tactic": "initial-access"},
        {"actor": "APT28", "technique": "T1059.001", "technique_name": "PowerShell Execution", "tactic": "execution"}
    ]

@app_kg.get("/asset-risk/{hostname}")
def get_asset_risk(hostname: str):
    # Simulated risk
    criticality = 10 if "DB" in hostname or "SRV" in hostname else 5
    vuln_count = 3
    risk_score = criticality * (1 + vuln_count * 0.1)
    return {"hostname": hostname, "risk_score": round(risk_score, 2)}

# ----------------- PORT 8086: InfluxDB Mock (Member 4 / Member 1) -----------------
app_influx = FastAPI(title="InfluxDB API Mock")

@app_influx.post("/api/v2/write")
async def influx_write(request: Request):
    body = await request.body()
    # Log incoming metric lines
    lines = body.decode().splitlines()
    for line in lines:
        logger.info(f"InfluxDB Mock Stored metric: {line}")
    return Response(status_code=204)

@app_influx.post("/api/v2/query")
async def influx_query(request: Request):
    body = await request.body()
    query_str = body.decode()
    logger.info(f"InfluxDB Mock Query received: {query_str[:120]}...")
    
    # Check what we are querying and return dummy CSV lines
    # standard InfluxDB CSV format response:
    # #group,false,false,true,true,false,false,true,true
    # #datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,string,string,string,string,double
    # #default,_result,,,,,,,,
    # ,result,table,_start,_stop,_time,_measurement,sector,_field,_value
    
    now_str = "2026-08-04T12:00:00Z"
    
    if "ids_alert" in query_str:
        csv_response = f"""#group,false,false,true,true,false,false,true,true
#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,string,string,string,string,string
#default,_result,,,,,,,,
,result,table,_start,_stop,_time,_measurement,severity,is_false_positive,_value
,,0,{now_str},{now_str},{now_str},ids_alert,P1,false,10.1.0.99
"""
        return Response(content=csv_response, media_type="text/csv")
        
    elif "detection_rate" in query_str:
        csv_response = f"""#group,false,false,true,true,false,false,true,true
#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,string,string,string,string,double
#default,_result,,,,,,,,
,result,table,_start,_stop,_time,_measurement,sector,_field,_value
,,0,{now_str},{now_str},{now_str},kpi_metrics,all,detection_rate,85.5
"""
        return Response(content=csv_response, media_type="text/csv")

    elif "sector_health" in query_str:
        csv_response = f"""#group,false,false,true,true,false,false,true,true
#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,string,string,string,string,double
#default,_result,,,,,,,,
,result,table,_start,_stop,_time,_measurement,sector,_field,_value
,,0,{now_str},{now_str},{now_str},sector_health,Government,health_score,92.0
,,0,{now_str},{now_str},{now_str},sector_health,Energy,health_score,85.0
,,0,{now_str},{now_str},{now_str},sector_health,Finance,health_score,95.0
,,0,{now_str},{now_str},{now_str},sector_health,Telecom,health_score,88.0
,,0,{now_str},{now_str},{now_str},sector_health,Water,health_score,90.0
,,0,{now_str},{now_str},{now_str},sector_health,Transport,health_score,91.0
"""
        return Response(content=csv_response, media_type="text/csv")
        
    else:
        csv_response = f"""#group,false,false,true,true,false,false,true,true
#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,string,string,string,string,double
#default,_result,,,,,,,,
,result,table,_start,_stop,_time,_measurement,sector,_field,_value
,,0,{now_str},{now_str},{now_str},general_metric,general,value,1.0
"""
        return Response(content=csv_response, media_type="text/csv")

@app_influx.get("/ping")
def influx_ping():
    return Response(status_code=204)

# ----------------- Start Services Helper Functions -----------------
def run_service(app, port):
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
    except Exception as e:
        logger.error(f"Error starting server on port {port}: {e}")

def start_all_mocks():
    ports = {
        8000: app_sdn,
        8001: app_ttp,
        8002: app_kg,
        8080: app_ditto,
        8086: app_influx
    }
    
    threads = []
    for port, app in ports.items():
        t = threading.Thread(target=run_service, args=(app, port), daemon=True)
        t.start()
        threads.append(t)
        logger.info(f"Mock server initialized on port {port}")
    
    logger.info("All mock services running in background threads.")

if __name__ == "__main__":
    start_all_mocks()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down mocks.")
