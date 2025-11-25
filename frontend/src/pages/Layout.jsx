import { useState } from "react";
import Dashboard from "./Dashboard";
import GridView from "./GridView";
import OverloadsView from "./OverloadsView";

export default function Layout() {
  const [tab, setTab] = useState("dashboard");

  // workflow result
  const [workflowResult, setWorkflowResult] = useState(null);

  // NEW - loading + error restored
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // new overload history
  const [overloadHistory, setOverloadHistory] = useState([]);

  const updateWorkflow = (res) => {
    setWorkflowResult(res);

    const overloads = res.audit_log?.filter(
      (log) => log.action === "overload_detected"
    ) || [];

    if (overloads.length) {
      setOverloadHistory((prev) => [
        ...prev,
        ...overloads.map((o) => ({
          timestamp: o.timestamp,
          required_kw: o.details?.required_kw || 0,
        })),
      ]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">

      {/* Tabs */}
      <nav className="border-b border-gray-700 p-4 flex space-x-6">
        <button
          className={`pb-1 ${tab === "dashboard" ? "border-b-2 border-blue-400" : "text-gray-400"}`}
          onClick={() => setTab("dashboard")}
        >
          Dashboard
        </button>
        <button
          className={`pb-1 ${tab === "grid" ? "border-b-2 border-blue-400" : "text-gray-400"}`}
          onClick={() => setTab("grid")}
        >
          Grid View
        </button>
        <button
          className={`pb-1 ${tab === "overloads" ? "border-b-2 border-blue-400" : "text-gray-400"}`}
          onClick={() => setTab("overloads")}
        >
          Overloads
        </button>
      </nav>

      {/* Pages */}
      {tab === "dashboard" && (
        <Dashboard
          workflowResult={workflowResult}
          setWorkflowResult={updateWorkflow}
          loading={loading}
          setLoading={setLoading}
          error={error}
          setError={setError}
        />
      )}

      {tab === "grid" && (
        <GridView allDERs={workflowResult?.all_windows || []} />
      )}

      {tab === "overloads" && (
        <OverloadsView items={overloadHistory} />
      )}
    </div>
  );
}
