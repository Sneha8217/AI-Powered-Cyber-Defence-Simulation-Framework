import os

# Port settings
MOCK_SDN_PORT = 8000
MOCK_TTP_PORT = 8001
MOCK_KG_PORT = 8002
MOCK_DITTO_PORT = 8080
MOCK_INFLUX_PORT = 8086

EXPORTER_PORT = 8020
DASHBOARD_BACKEND_PORT = 8030
XAI_API_PORT = 8010

# API URLs
SDN_URL = f"http://localhost:{MOCK_SDN_PORT}"
DITTO_URL = f"http://localhost:{MOCK_DITTO_PORT}"
TTP_API_URL = f"http://localhost:{MOCK_TTP_PORT}"
KG_API_URL = f"http://localhost:{MOCK_KG_PORT}"
INFLUX_URL = f"http://localhost:{MOCK_INFLUX_PORT}"

# Security tokens
INFLUX_TOKEN = "acdsf2024"
INFLUX_ORG = "acdssf"
INFLUX_BUCKET = "acdssf_metrics"
THEHIVE_API_KEY = "soar_secret_key"
