export default function Terminal({ audit }) {
  return (
    <div className="bg-black p-4 rounded-lg h-full flex flex-col font-mono text-xs text-gray-200">

      <div className="flex items-center mb-2 space-x-2">
        <div className="h-3 w-3 rounded-full bg-red-500" />
        <div className="h-3 w-3 rounded-full bg-yellow-500" />
        <div className="h-3 w-3 rounded-full bg-green-500" />
        <span className="ml-2 text-gray-400">Audit Log</span>
      </div>

      <div className="flex-1 overflow-auto">
        {!audit && <p className="text-gray-500">No logs yet.</p>}
        {audit?.map((entry, idx) => (
          <pre key={idx} className="whitespace-pre-wrap mb-3">
            {JSON.stringify(entry, null, 2)}
          </pre>
        ))}
      </div>
      
    </div>
  );
}
