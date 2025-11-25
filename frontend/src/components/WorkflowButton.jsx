export default function WorkflowButton({ run, loading }) {
  return (
    <button
      onClick={run}
      disabled={loading}
      className={`
        px-4 py-2 rounded-md text-sm font-medium
        bg-blue-600 hover:bg-blue-500 
        disabled:bg-blue-900/50 disabled:text-gray-400
        transition-all duration-200
      `}
    >
      {loading ? "Running…" : "Run Workflow"}
    </button>
  );
}
