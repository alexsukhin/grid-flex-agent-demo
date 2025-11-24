import { useState } from "react";
import { runWorkflow } from "../services/api";

import WorkflowButton from "../components/WorkflowButton";
import GridMap from "../components/GridMap";
import DERList from "../components/DERList";
import Timeline from "../components/Timeline";
import Terminal from "../components/Terminal";

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const startWorkflow = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runWorkflow();
      setResult(res.data);
    } catch (e) {
      console.error(e);
      setError("Failed to run workflow");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Project Reflex — Grid Copilot</h1>
        <WorkflowButton run={startWorkflow} loading={loading} />
      </div>

      {error && (
        <div className="rounded bg-red-900/60 border border-red-500 px-4 py-2 text-sm">
          {error}
        </div>
      )}

      {result && (
        <p className="text-sm text-gray-300">
          Mode: <span className="font-semibold">{result.mode.toUpperCase()}</span> ·
          Required: <span className="font-semibold">{result.required_kw} kW</span> ·
          Runtime:{" "}
          <span className="font-semibold">
            {result.performance_seconds}s
          </span>
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <GridMap selected={result?.selected} />
        <DERList selected={result?.selected} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Timeline llm={result?.llm} />
        <Terminal audit={result?.audit_log} />
      </div>
    </div>
  );
}
