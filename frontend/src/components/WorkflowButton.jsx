export default function WorkflowButton({ run, loading }) {
  return (
    <button
      onClick={run}
      disabled={loading}
      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow w-full"
    >
      {loading ? "Running workflow..." : "Run Grid Flexibility Workflow"}
    </button>
  );
}
