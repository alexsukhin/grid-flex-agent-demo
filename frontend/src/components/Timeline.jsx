export default function Timeline({ llm, sessionId }) {
  // No workflow run at all
  if (!sessionId) {
    return (
      <p className="text-gray-400 text-sm">
        No events yet. Run the workflow.
      </p>
    );
  }

  // Workflow started but llm not populated yet
  if (!llm) {
    return (
      <p className="text-gray-400 text-sm animate-pulse">
        Generating event summaries…
      </p>
    );
  }

  const events = [
    { label: "Overload detected", text: llm.overload },
    { label: "Selection made", text: llm.selection },
    { label: "Flex confirmed", text: llm.confirm },
    { label: "Event settled", text: llm.status },
  ];

  const allEmpty = events.every((e) => !e.text);

  if (allEmpty) {
    return (
      <p className="text-gray-400 text-sm animate-pulse">
        Generating event summaries…
      </p>
    );
  }

  // Render event list
  return (
    <div className="space-y-4">
      {events.map(
        (e, i) =>
          e.text && (
            <div key={i} className="flex items-start space-x-3">
              <div className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-400 flex-shrink-0" />
              <div>
                <p className="text-xs font-semibold text-emerald-300">
                  {e.label}
                </p>
                <p className="text-gray-200 whitespace-pre-wrap text-sm">
                  {e.text}
                </p>
              </div>
            </div>
          )
      )}
    </div>
  );
}
