import { useEffect } from "react";
import { runWorkflow, fetchLlm } from "../services/api";
import WorkflowButton from "../components/WorkflowButton";
import DERList from "../components/DERList";
import Timeline from "../components/Timeline";
import Terminal from "../components/Terminal";

export default function Dashboard({
  workflowResult,
  setWorkflowResult,
  loading,
  setLoading,
  error,
  setError
}) {
  const startWorkflow = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runWorkflow();
      setWorkflowResult(res.data);
    } catch (e) {
      console.error(e);
      setError("Failed to run workflow");
    } finally {
      setLoading(false);
    }
  };

  // Poll LLM summaries in the background using session_id
  useEffect(() => {
    if (!workflowResult?.session_id) return;

    let cancelled = false;

    const interval = setInterval(async () => {
      try {
        const res = await fetchLlm(workflowResult.session_id);
        if (cancelled) return;

        const llmData = res.data;

        // Merge LLM into existing workflowResult
        setWorkflowResult((prev) =>
          prev
            ? {
                ...prev,
                llm: {
                  overload: llmData.overload,
                  selection: llmData.selection,
                  confirm: llmData.confirm,
                  status: llmData.status,
                },
              }
            : prev
        );

        if (llmData.complete) {
          clearInterval(interval);
        }
      } catch (e) {
        console.error("Failed to fetch LLM summaries", e);
      }
    }, 1000); // poll every 1s

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [workflowResult?.session_id, setWorkflowResult]);

  return (
    <div className="flex flex-col h-[calc(100vh-60px)] bg-gray-900 text-gray-100">

      {/* Header */}
      <div className="px-6 py-4 flex items-center justify-between border-b border-gray-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Project Reflex — Grid Copilot
          </h1>
          <p className="text-gray-400 text-sm mt-0.5">
            Real-time flexibility orchestration dashboard
          </p>
        </div>

        <WorkflowButton run={startWorkflow} loading={loading} />
      </div>

      {/* Error */}
      {error && (
        <div className="px-6 py-2 bg-red-900 text-sm border-b border-red-800">
          {error}
        </div>
      )}

      {/* Status bar */}
      {workflowResult && (
        <div className="px-6 py-3 flex items-center gap-4 text-sm border-b border-gray-800">
          {/* Mode */}
          <span
            className={`
              px-3 py-1 rounded-full font-semibold 
              ${workflowResult.mode === "emergency"
                ? "bg-red-900/40 text-red-300 border border-red-700/40"
                : "bg-emerald-900/40 text-emerald-300 border border-emerald-700/40"
              }
            `}
          >
            Mode: {workflowResult.mode.toUpperCase()}
          </span>

          {/* Required */}
          <span className="px-3 py-1 rounded-full bg-blue-900/40 text-blue-300 border border-blue-700/40 font-semibold">
            Required: {workflowResult.required_kw} kW
          </span>

          {/* Runtime */}
          <span className="px-3 py-1 rounded-full bg-gray-700 text-gray-200 border border-gray-600 font-semibold">
            Runtime: {workflowResult.performance_seconds}s
          </span>
        </div>
      )}

      {/* Main layout */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 overflow-hidden">

        {/* LEFT COLUMN */}
        <div className="flex flex-col overflow-hidden px-6 py-4">
          {/* TOP */}
          <div className="flex-1 overflow-hidden mb-6">
            <div className="bg-gray-800 rounded-lg p-4 h-full flex flex-col">
              <h2 className="text-lg font-semibold mb-2">Selected DER Windows</h2>
              <div className="flex-1 overflow-auto">
                <DERList selected={workflowResult?.selected} />
              </div>
            </div>
          </div>

          {/* BOTTOM */}
          <div className="flex-1 overflow-hidden">
            <div className="bg-gray-800 rounded-lg p-4 h-full flex flex-col">
              <h2 className="text-lg font-semibold mb-2">Event Timeline</h2>
              <div className="flex-1 overflow-auto">
                <Timeline llm={workflowResult?.llm} sessionId={workflowResult?.session_id} />
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div className="overflow-hidden px-6 py-4">
          <Terminal audit={workflowResult?.audit_log} />
        </div>
      </div>
    </div>
  );
}
