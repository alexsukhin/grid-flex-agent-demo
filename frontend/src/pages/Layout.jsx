import { useState } from "react";
import Dashboard from "./Dashboard";
import GridView from "./GridView";

export default function Layout() {
  const [tab, setTab] = useState("dashboard");

  const [workflowResult, setWorkflowResult] = useState(null);

  // MOVE THESE UP
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">

      <nav className="border-b border-gray-700 p-4 flex space-x-6">
        <button
          className={`pb-1 ${
            tab === "dashboard" ? "border-b-2 border-blue-400" : "text-gray-400"
          }`}
          onClick={() => setTab("dashboard")}
        >
          Dashboard
        </button>

        <button
          className={`pb-1 ${
            tab === "grid" ? "border-b-2 border-blue-400" : "text-gray-400"
          }`}
          onClick={() => setTab("grid")}
        >
          Grid View
        </button>
      </nav>

      {tab === "dashboard" && (
        <Dashboard
          workflowResult={workflowResult}
          setWorkflowResult={setWorkflowResult}
          loading={loading}
          setLoading={setLoading}
          error={error}
          setError={setError}
        />
      )}

      {tab === "grid" && (
        <GridView allDERs={workflowResult?.all_windows || []} />
      )}
    </div>
  );
}
