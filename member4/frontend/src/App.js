import React, { useState, useEffect } from 'react';
import { Shield, Radio, Activity, AlertTriangle, Play, RefreshCw, Cpu, Server, Lock, User, CheckCircle, BarChart2 } from 'lucide-react';

// API root mapping
const API_URL = "http://localhost:8030/api/v1";

function App() {
  const [role, setRole] = useState("analyst"); // administrator, analyst, manager, executive
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [username, setUsername] = useState("admin1");
  const [password, setPassword] = useState("");
  
  // Dashboard states
  const [alerts, setAlerts] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [executiveScore, setExecutiveScore] = useState(null);
  const [xaiResult, setXaiResult] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [playbookTarget, setPlaybookTarget] = useState("10.1.0.99");
  const [playbookName, setPlaybookName] = useState("DDoS Playbook");
  const [playbookLogs, setPlaybookLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Poll metrics on mount
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, [role]);

  const fetchData = async () => {
    try {
      if (role === "analyst") {
        const res = await fetch(`${API_URL}/analyst/alerts`);
        const data = await res.json();
        setAlerts(data);
      } else if (role === "administrator") {
        const res = await fetch(`${API_URL}/admin/system-health`);
        const data = await res.json();
        setSystemHealth(data);
      } else if (role === "executive") {
        const res = await fetch(`${API_URL}/executive/security-score`);
        const data = await res.json();
        setExecutiveScore(data);
      } else if (role === "manager") {
        const res = await fetch(`${API_URL}/manager/tickets`);
        const data = await res.json();
        setAlerts(data);
      }
    } catch (e) {
      console.log("Error contacting API backend. Operating in simulated offline mode.");
      // Fallback state
      setAlerts([
        { id: "1", title: "Unidentified Port Sweep", severity: "Medium", status: "Investigating", sector: "Government", timestamp: "2026-08-04 12:45:00" },
        { id: "2", title: "SCADA Protocol Anomaly", severity: "Critical", status: "Contained", sector: "Energy", timestamp: "2026-08-04 12:48:12" }
      ]);
      setSystemHealth({
        services: { SDN_Gateway: "Healthy", Ditto_Twin: "Healthy", InfluxDB: "Healthy", TTP_Extractor: "Healthy", SOAR_Playbooks: "Healthy", GNN_Anomaly_Detector: "Healthy" },
        system: { cpu: "32%", memory: "54%" }
      });
      setExecutiveScore({
        security_score: 82.5,
        threat_level: "LOW-MEDIUM",
        risk_by_sector: { Energy: 15.0, Government: 8.0, Finance: 5.0, Water: 10.0, Telecom: 12.0, Transport: 9.0 }
      });
    }
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (username && password) {
      setIsLoggedIn(true);
    }
  };

  const handleTriggerPlaybook = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/manager/playbook/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ playbook_name: playbookName, target_ip: playbookTarget })
      });
      const data = await res.json();
      setPlaybookLogs(data.actions_taken || ["Completed playbook block (simulated)"]);
    } catch (e) {
      setPlaybookLogs([`Triggered ${playbookName} on ${playbookTarget}`, "SDN Command sent", "Isolation successful (simulated)"]);
    }
    setIsLoading(false);
  };

  const handleExplainAlert = async (alert) => {
    setSelectedAlert(alert);
    setIsLoading(true);
    // Generate simulated feature list for XAI
    const dummyFeatures = [0.9, 0.2, 15.0, 9.0, 0.1, 0.8, 1.0, 0.05];
    try {
      const res = await fetch(`${API_URL}/analyst/xai/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dummyFeatures)
      });
      const data = await res.json();
      setXaiResult(data);
    } catch (e) {
      setXaiResult({
        decision: "True Positive",
        confidence: "94.5%",
        explanation: "Primary indicators: src_ip_reputation (0.42) and protocol_anomaly (0.35) contributed significantly to this prediction.",
        chart_base64: ""
      });
    }
    setIsLoading(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
        <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
          <div className="flex justify-center mb-6">
            <div className="p-3 bg-cyan-500/10 rounded-full border border-cyan-500/20 text-cyan-400">
              <Shield size={32} />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-center text-white mb-2">ACDSF Command Center</h2>
          <p className="text-slate-400 text-sm text-center mb-8">Access restricted to authorized personnel</p>
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-slate-400 text-xs font-semibold uppercase mb-2">Username</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500"><User size={16} /></span>
                <input type="text" value={username} onChange={e => setUsername(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-850 rounded-xl text-white focus:outline-none focus:border-cyan-500 transition-colors" placeholder="Username" required />
              </div>
            </div>
            <div>
              <label className="block text-slate-400 text-xs font-semibold uppercase mb-2">Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500"><Lock size={16} /></span>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-850 rounded-xl text-white focus:outline-none focus:border-cyan-500 transition-colors" placeholder="••••••••" required />
              </div>
            </div>
            <button type="submit" className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-xl shadow-lg transition-all transform active:scale-95">Sign In</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header bar */}
      <header className="h-16 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="text-cyan-400" size={24} />
          <span className="font-extrabold text-lg tracking-wider text-white">ACDSF</span>
          <span className="px-2 py-0.5 bg-slate-800 text-slate-400 text-xs font-semibold rounded-md border border-slate-700">MEMBER 3 & 4</span>
        </div>
        
        {/* Role Switching Selector */}
        <div className="flex items-center space-x-2 bg-slate-950 border border-slate-850 p-1 rounded-xl">
          {["administrator", "analyst", "manager", "executive"].map((r) => (
            <button key={r} onClick={() => setRole(r)} className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition-all ${role === r ? 'bg-cyan-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}>
              {r}
            </button>
          ))}
        </div>
      </header>

      {/* Main dashboard content container */}
      <main className="flex-1 p-6 overflow-y-auto max-w-7xl w-full mx-auto space-y-6">
        
        {/* ----------------- DASHBOARD VIEW: ADMINISTRATOR ----------------- */}
        {role === "administrator" && systemHealth && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white flex items-center space-x-2">
              <Cpu size={20} className="text-cyan-400" />
              <span>System Health & Infrastructure Topology</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                <h4 className="text-slate-400 text-xs font-bold uppercase">SDN Gateway Status</h4>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-2xl font-bold text-white">{systemHealth.services.SDN_Gateway}</span>
                  <CheckCircle size={24} className="text-emerald-500" />
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                <h4 className="text-slate-400 text-xs font-bold uppercase">Digital Twin States</h4>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-2xl font-bold text-white">{systemHealth.services.Ditto_Twin}</span>
                  <CheckCircle size={24} className="text-emerald-500" />
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                <h4 className="text-slate-400 text-xs font-bold uppercase">CPU load</h4>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-2xl font-bold text-white">{systemHealth.system.cpu}</span>
                  <Cpu size={24} className="text-cyan-400" />
                </div>
              </div>
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                <h4 className="text-slate-400 text-xs font-bold uppercase">Memory Consumption</h4>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-2xl font-bold text-white">{systemHealth.system.memory}</span>
                  <Server size={24} className="text-cyan-400" />
                </div>
              </div>
            </div>

            {/* Network Topology Visualizer (SVG) */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
              <h3 className="text-white font-semibold mb-4">Enterprise CNI Subnets Connectivity Map</h3>
              <div className="bg-slate-950 rounded-lg p-6 border border-slate-850 flex justify-center">
                <svg width="600" height="300" viewBox="0 0 600 300">
                  <line x1="300" y1="150" x2="100" y2="80" stroke="#475569" strokeWidth="2" />
                  <line x1="300" y1="150" x2="100" y2="220" stroke="#475569" strokeWidth="2" />
                  <line x1="300" y1="150" x2="500" y2="80" stroke="#475569" strokeWidth="2" />
                  <line x1="300" y1="150" x2="500" y2="220" stroke="#475569" strokeWidth="2" />
                  
                  <circle cx="300" cy="150" r="30" fill="#0891b2" stroke="#22d3ee" strokeWidth="3" />
                  <text x="300" y="155" fill="white" fontSize="10" textAnchor="middle" fontWeight="bold">NBR-01</text>
                  
                  <circle cx="100" cy="80" r="22" fill="#1e293b" stroke="#e2e8f0" strokeWidth="2" />
                  <text x="100" y="84" fill="white" fontSize="8" textAnchor="middle">GOVT</text>
                  
                  <circle cx="100" cy="220" r="22" fill="#1e293b" stroke="#e2e8f0" strokeWidth="2" />
                  <text x="100" y="224" fill="white" fontSize="8" textAnchor="middle">ENERGY</text>
                  
                  <circle cx="500" cy="80" r="22" fill="#1e293b" stroke="#e2e8f0" strokeWidth="2" />
                  <text x="500" y="84" fill="white" fontSize="8" textAnchor="middle">FINANCE</text>
                  
                  <circle cx="500" cy="220" r="22" fill="#1e293b" stroke="#e2e8f0" strokeWidth="2" />
                  <text x="500" y="224" fill="white" fontSize="8" textAnchor="middle">TELECOM</text>
                </svg>
              </div>
            </div>
          </div>
        )}

        {/* ----------------- DASHBOARD VIEW: ANALYST (ALERTS & XAI) ----------------- */}
        {role === "analyst" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Alerts Table list */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
              <h3 className="text-white font-bold flex items-center space-x-2">
                <AlertTriangle className="text-amber-500" size={18} />
                <span>Live Intrusions Alert Log</span>
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 font-bold">
                      <th className="py-3 px-2">Alert</th>
                      <th className="py-3 px-2">Severity</th>
                      <th className="py-3 px-2">Sector</th>
                      <th className="py-3 px-2">Status</th>
                      <th className="py-3 px-2">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alerts.map((a) => (
                      <tr key={a.id} className="border-b border-slate-850 hover:bg-slate-850/50">
                        <td className="py-4 px-2 font-semibold text-white">{a.title}</td>
                        <td className="py-4 px-2">
                          <span className={`px-2 py-0.5 text-xs font-bold rounded-md ${a.severity === 'Critical' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
                            {a.severity}
                          </span>
                        </td>
                        <td className="py-4 px-2 text-slate-300">{a.sector}</td>
                        <td className="py-4 px-2 text-cyan-400">{a.status}</td>
                        <td className="py-4 px-2">
                          <button onClick={() => handleExplainAlert(a)} className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg text-xs transition-all">
                            Explain AI
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Explainable AI Dashboard Sidebar */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col space-y-4">
              <h3 className="text-white font-bold flex items-center space-x-2">
                <Radio className="text-cyan-400" size={18} />
                <span>Decision Explanation (SHAP)</span>
              </h3>
              {isLoading ? (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
                  <RefreshCw className="animate-spin mb-2" size={24} />
                  <span>Computing Shapley attributions...</span>
                </div>
              ) : xaiResult ? (
                <div className="space-y-4 flex-1 flex flex-col">
                  <div className="bg-slate-950 p-4 border border-slate-850 rounded-xl">
                    <div className="text-xs uppercase text-slate-500 font-bold">Model Decision</div>
                    <div className="text-lg font-bold text-white mt-1">{xaiResult.decision}</div>
                    <div className="text-xs text-slate-400 mt-1">Confidence Score: {xaiResult.confidence}</div>
                  </div>
                  <div className="bg-slate-950 p-4 border border-slate-850 rounded-xl flex-1">
                    <div className="text-xs uppercase text-slate-500 font-bold mb-2">SHAP Explanation Details</div>
                    <p className="text-slate-300 text-xs leading-relaxed">{xaiResult.explanation}</p>
                    
                    {/* Render Base64 Image */}
                    {xaiResult.chart_base64 && (
                      <div className="mt-4 border border-slate-800 rounded-lg overflow-hidden bg-white p-1">
                        <img src={`data:image/png;base64,${xaiResult.chart_base64}`} alt="SHAP Waterfall Plot" className="w-full h-auto" />
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center text-slate-500 text-xs text-center">
                  Select an alert and click "Explain AI" to view decision contributions.
                </div>
              )}
            </div>
          </div>
        )}

        {/* ----------------- DASHBOARD VIEW: INCIDENT MANAGER (SOAR REMEDIATION) ----------------- */}
        {role === "manager" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
              <h3 className="text-white font-bold flex items-center space-x-2">
                <Play className="text-cyan-400" size={18} />
                <span>Execute SOAR Defense Playbook</span>
              </h3>
              <div className="space-y-4 bg-slate-950 p-5 rounded-xl border border-slate-850">
                <div>
                  <label className="block text-slate-400 text-xs font-semibold mb-2">Target Host IP / Attacker Source IP</label>
                  <input type="text" value={playbookTarget} onChange={e => setPlaybookTarget(e.target.value)} className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-cyan-500" />
                </div>
                <div>
                  <label className="block text-slate-400 text-xs font-semibold mb-2">Remediation Playbook</label>
                  <select value={playbookName} onChange={e => setPlaybookName(e.target.value)} className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-cyan-500">
                    <option>DDoS Playbook</option>
                    <option>Ransomware Playbook</option>
                  </select>
                </div>
                <button onClick={handleTriggerPlaybook} className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg text-xs transition-all shadow-md">
                  Trigger Playbook
                </button>
              </div>
            </div>

            {/* Playbook Log Output Console */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col space-y-4">
              <h3 className="text-white font-bold">Playbook Run Logs</h3>
              <div className="flex-1 bg-slate-950 p-4 rounded-xl border border-slate-850 font-mono text-xs text-cyan-400 space-y-2 overflow-y-auto min-h-[200px]">
                {playbookLogs.length > 0 ? (
                  playbookLogs.map((log, idx) => (
                    <div key={idx}>&gt; {log}</div>
                  ))
                ) : (
                  <div className="text-slate-600">Console ready. Trigger a playbook to start log stream.</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ----------------- DASHBOARD VIEW: EXECUTIVE OVERVIEW ----------------- */}
        {role === "executive" && executiveScore && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white flex items-center space-x-2">
              <BarChart2 size={20} className="text-cyan-400" />
              <span>Cyber Risk Situational Awareness</span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Score Display Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg flex flex-col items-center justify-center text-center space-y-3">
                <h3 className="text-slate-400 text-sm font-bold uppercase tracking-wider">ACDSF Security Score</h3>
                <div className="text-6xl font-black text-emerald-400">{executiveScore.security_score}%</div>
                <p className="text-slate-400 text-xs">
                  A comprehensive metric computed from real-time threat containment speeds (MTTR), detection accuracies, and active mitigations.
                </p>
              </div>

              {/* Threat Matrix Bar list */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg space-y-4">
                <h3 className="text-white font-semibold text-sm">Sector Specific Vulnerability Index</h3>
                <div className="space-y-3">
                  {Object.entries(executiveScore.risk_by_sector).map(([sector, risk]) => (
                    <div key={sector}>
                      <div className="flex justify-between text-xs font-semibold mb-1">
                        <span>{sector} Sector</span>
                        <span className="text-cyan-400">{risk}% risk</span>
                      </div>
                      <div className="w-full bg-slate-850 h-2 rounded-full overflow-hidden">
                        <div className="bg-cyan-500 h-2" style={{ width: `${risk * 4}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer copyright */}
      <footer className="h-10 bg-slate-950 border-t border-slate-900 px-6 flex items-center justify-center text-xs text-slate-500">
        <span>© 2026 ACDSF Simulation Framework. All rights reserved.</span>
      </footer>
    </div>
  );
}

export default App;
