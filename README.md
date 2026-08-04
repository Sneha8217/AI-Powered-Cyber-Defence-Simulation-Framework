# AI-Powered Cyber Defence Simulation Framework (ACDSF)

This project contains the implementation of **Member 3 (Blue Team AI & Multi-Agent Defence)** and **Member 4 (Evaluation, XAI Dashboard & Integration)**.

To allow independent verification and integration, a shared mock-engine simulates APIs for Member 1 (SDN controller, Eclipse Ditto, InfluxDB) and Member 2 (TTP API, Knowledge Graph API) so that Member 3 and Member 4 run successfully.

---

## Directory and File Map

The codebase must be structured as follows:

```text
acdssf/
├── requirements.txt         # Dependencies manifest
├── Dockerfile               # Production Docker container manifest
├── docker-compose.yml       # Production services composition
├── README.md                # Development instructions manual
├── shared/
│   └── mock_services.py     # Local HTTP mocks emulating Member 1 & 2 ports (8000, 8001, 8002, 8080, 8086)
├── member3/
│   ├── blue_env.py          # Custom Gymnasium cyber env wrapping controls
│   ├── train_blue.py        # RL training scripts (DQN, PPO, Curriculum learning)
│   ├── evaluate_blue.py     # Evaluation comparator for DQN/PPO models
│   ├── mappo_agent.py       # MAPPO PPO update wrapper
│   ├── actor.py             # Actor network configuration
│   ├── critic.py            # Critic network configuration
│   ├── replay_buffer.py     # Shared experience replay buffer
│   ├── multi_agent.py       # Cooperative MAPPO defender simulation
│   ├── alert_engine.py      # Rule-based threat alerts and IOC extractor
│   ├── incident_manager.py  # Ticketing engine (emulating TheHive REST)
│   ├── playbooks.py         # SOAR playbook steps (DDoS, Ransomware)
│   ├── automation.py        # SDN REST controller execution triggers
│   ├── soc.py               # SOC coordinator matching alerts to playbooks
│   ├── graph_dataset.py     # Graph GNN network topology loader
│   ├── graph_model.py       # GCN Autoencoder anomaly model
│   ├── train_gnn.py         # GNN Autoencoder model optimizer
│   ├── predict.py           # GNN live anomaly detection inference
│   ├── graph_utils.py       # NetworkX SCADA graph visualization utility
│   ├── self_play.py         # Competitive Red vs Blue environment
│   └── train_self_play.py   # Nash Equilibrium self-play trainer
└── member4/
    ├── metrics.py           # Operational KPIs (MTTD, MTTR, Detection Rate) calculator
    ├── evaluation.py        # Performance reports and ROC AUC generator
    ├── exporter.py          # Prometheus telemetry exporter (port 8020)
    ├── dashboard.json       # Grafana dashboard panels structure
    ├── shap_explainer.py    # SHAP feature attribution calculator
    ├── lime_explainer.py    # LIME local perturbation explainer
    ├── visualization.py     # SHAP attribution waterfall chart renderer (base64)
    ├── asset_mapper.py      # Enterprise subnets asset and CVE index mapper
    ├── threat_sync.py       # MISP IOC synchronizer
    ├── situational_awareness.py # Weighted global risk calculator
    ├── config.py            # Port mapping specifications configuration
    ├── main.py              # Framework startup orchestrator (starts all background tasks)
    ├── backend/
    │   ├── api.py           # FastAPI dashboard server (port 8030)
    │   └── router.py        # Role-based API route endpoints (Analyst, Admin, Executive)
    └── frontend/            # React Client Application
        ├── package.json
        ├── tailwind.config.js
        ├── postcss.config.js
        ├── public/
        │   └── index.html
        └── src/
            ├── index.js
            ├── index.css
            └── App.js
```

---

## Getting Started

### 1. Requirements Setup

Ensure Python 3.9+ is installed. Install all dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run All-in-One Framework

Start the entire system using the main integration script. This automatically launches all simulated external databases/APIs (Member 1 & 2 mocks), the Prometheus metrics server, the XAI API, and the FastAPI dashboard backend:
```bash
python member4/main.py
```

### 3. Run Individual Components

#### Train Single RL Blue Agent
```bash
python member3/train_blue.py --algorithm ppo --steps 10000
```

#### Run Multi-Agent Cooperative Training (MAPPO)
```bash
python member3/multi_agent.py
```

#### Run Competitive Self-Play Training (Nash Equilibrium)
```bash
python member3/train_self_play.py
```

#### Train & Run GNN ICS Anomaly Detector
```bash
python member3/train_gnn.py
python member3/predict.py
```

#### Run KPIs Operational Metrics Evaluator
```bash
python member4/metrics.py
```

#### Run Dashboard Frontend Client
Navigate to the frontend folder, install dependencies and start React:
```bash
cd member4/frontend
npm install
npm start
```
Go to `http://localhost:3000` to interact with the Administrator, Analyst, Incident Manager, and Executive views!
