/*
 * React component for analyzing the execution history and agent usage statistics of workflow graphs.
 * Purpose:
 * - Allows users to select a workflow graph and view detailed analytics about its executions and agent performance.
 * Features:
 * - Fetches and displays a list of available graphs for the authenticated user.
 * - For the selected graph, loads and displays:
 *   - Execution history (individual runs, duration, tokens, execution path).
 *   - Detailed audit trail for each execution (step-by-step agent actions, inputs, outputs, timing).
 *   - Manager decisions for each execution.
 *   - Visual timeline of agent durations within a run.
 *   - Agent usage statistics (call frequency, average execution times, most used agent, total executions).
 * - Allows the user to inspect details of any execution run.
 * Usage:
 * - Place this component on a page where you want to provide analytics and insights for workflow graphs.
 * - Requires the user to be authenticated (uses `useAuth` for token).
 * Props: none
 */
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../../services/authContext";
import '../../css/Settings.css';

interface Graph {
  id: number;
  name: string;
}

interface AgentUsageStats {
  total_executions: number;
  agent_call_frequency: Record<string, number>;
  average_execution_times_ms: Record<string, number>;
  most_used_agent: string | null;
}

interface AuditTrailEntry {
  agent: string;
  duration_ms: number;
  tokens_used: number;
  input: any;
  output: any;
  timestamp: string;
}

interface FlowStep {
  from: string;
  to: string;
  timestamp: string;
}

interface ExecutionHistoryItem {
  id: number;
  execution_timestamp: string;
  total_duration_ms: number;
  tokens_used: number | null;
  execution_path: string[];
  node_outputs: Record<string, {
    content: string;
    timestamp: string;
    duration_ms: number;
    tokens_used: number;
  }>;
  manager_decisions: any[];
  audit_trail: AuditTrailEntry[];
  flow_steps: FlowStep[];
}


const GraphAnalysis: React.FC = () => {
  const { token } = useAuth();
  const [graphs, setGraphs] = useState<Graph[]>([]);
  const [selectedGraphId, setSelectedGraphId] = useState<number | null>(null);
  const [stats, setStats] = useState<AgentUsageStats | null>(null);
  const [history, setHistory] = useState<ExecutionHistoryItem[]>([]);
  const [loadingGraphs, setLoadingGraphs] = useState(true);
  const [loadingStats, setLoadingStats] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState<ExecutionHistoryItem | null>(null);


  useEffect(() => {
    if (!token) return;
    const fetchGraphs = async () => {
      setLoadingGraphs(true);
      try {
        const res = await axios.get("http://127.0.0.1:8000/graphs", {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setGraphs(res.data);
        if (res.data.length > 0) {
          setSelectedGraphId(res.data[0].id);
        }
      } catch (err) {
        setGraphs([]);
      }
      setLoadingGraphs(false);
    };
    fetchGraphs();
  }, [token]);


  useEffect(() => {
    if (!selectedGraphId || !token) return;
    
    const fetchStats = async () => {
      setLoadingStats(true);
      try {
        const res = await axios.get(`http://127.0.0.1:8000/analytics/agent-usage/${selectedGraphId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setStats(res.data);
      } catch (err) {
        setStats(null);
      }
      setLoadingStats(false);
    };

    const fetchHistory = async () => {
      setLoadingHistory(true);
      try {
        const res = await axios.get(`http://127.0.0.1:8000/analytics/execution-history/${selectedGraphId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setHistory(res.data);
      } catch (err) {
        setHistory([]);
      }
      setLoadingHistory(false);
    };

    fetchStats();
    fetchHistory();
    setSelectedDetail(null);
  }, [selectedGraphId, token]);

  const handleGraphChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedGraphId(Number(e.target.value));
  };

  if (loadingGraphs) return <div>Načítám seznam grafů...</div>;

  return (
    <div className="graph-analysis">
      <h2><i className="bx bx-bar-chart"></i> Analýza běhů grafu</h2>
      <div className="graph-selector">
        <label htmlFor="graph-select">Vyberte graf:</label>
        <select className="graph-select" value={selectedGraphId || ""} onChange={handleGraphChange}>
          {graphs.map((graph) => (
            <option key={graph.id} value={graph.id}>{graph.name}</option>
          ))}
        </select>
      </div>

      <h3>Historie běhů grafu</h3>
      {loadingHistory ? (
        <div>Načítám historii...</div>
      ) : history.length === 0 ? (
        <div>Pro tento graf nejsou žádné běhy.</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Čas spuštění</th>
              <th>Trvání (ms)</th>
              <th>Použité tokeny</th>
              <th>Tok spolupráce</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {history.map(item => (
              <tr key={item.id}>
                <td>{new Date(item.execution_timestamp).toLocaleString()}</td>
                <td>{item.total_duration_ms}</td>
                <td>{item.tokens_used ?? "-"}</td>
                <td>{item.execution_path.join(" → ")}</td>
                <td><button onClick={() => setSelectedDetail(item)}>Detail</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

    {selectedDetail && (
        <div className="execution-detail">
          <div className="execution-manager">
            <h5>Rozhodnutí manažera:</h5>
            <pre style={{ whiteSpace: "pre-wrap" }}>
              {JSON.stringify(selectedDetail.manager_decisions, null, 2)}
            </pre>
          </div>
        </div>
      )}

    {selectedDetail && (
        <div className="execution-detail">
          <h5>Časová osa běhu ({selectedDetail.total_duration_ms} ms)</h5>
          <div className="timeline-container">
            {selectedDetail.audit_trail?.map((entry, index) => {
              const percentage = selectedDetail.total_duration_ms > 0 
                ? (entry.duration_ms / selectedDetail.total_duration_ms) * 100 
                : 0;
              return (
                <div 
                  key={index} 
                  className="timeline-bar"
                  style={{ width: `${percentage}%` }}
                  title={`${entry.agent}: ${entry.duration_ms} ms`}
                >
                  <span className="timeline-label">{entry.agent}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {selectedDetail && (
        <div className="execution-detail">
          {selectedDetail.audit_trail && selectedDetail.audit_trail.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Agent</th>
                  <th>Trvání (ms)</th>
                  <th>Tokeny</th>
                  <th>Zadání</th>
                  <th>Výstup</th>
                  <th>Čas</th>
                </tr>
              </thead>
              <tbody>
                {selectedDetail.audit_trail.map((entry, index) => (
                  <tr key={index}>
                    <td>{entry.agent}</td>
                    <td>{entry.duration_ms}</td>
                    <td>{entry.tokens_used}</td>
                    <td><pre>{JSON.stringify(entry.input, null, 2)}</pre></td>
                    <td><pre>{typeof entry.output === 'object' ? JSON.stringify(entry.output, null, 2) : String(entry.output)}</pre></td>
                    <td>{new Date(entry.timestamp).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Audit log není k dispozici.</p>
          )}
        </div>
      )}
      
      <h3>Statistiky využití agentů</h3>
        {loadingStats ? (
            <div>Načítám analýzu...</div>
        ) : stats && stats.total_executions > 0 ? (
            <div className="stats-container">
                <div><h5>Počet exekucí: <strong>{stats.total_executions}</strong></h5></div>
                <div>
                    <h5>Frekvence volání agentů</h5>
                    <ul>{Object.entries(stats.agent_call_frequency).map(([agent, count]) => <li key={agent}>{agent}: <strong>{count}×</strong></li>)}</ul>
                </div>
                <div>
                    <h5>Průměrné časy vykonání (ms)</h5>
                    <ul>{Object.entries(stats.average_execution_times_ms).map(([agent, ms]) => <li key={agent}>{agent}: <strong>{ms.toFixed(1)} ms</strong></li>)}</ul>
                </div>
            </div>
        ) : (
            <div>Pro tento graf nejsou žádné běhy k analýze.</div>
        )}
      </div>
  );
};

export default GraphAnalysis;