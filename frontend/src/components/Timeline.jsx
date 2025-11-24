export default function Timeline({ llm }) {
  const events = !llm
    ? []
    : [
        { label: "Overload detected", text: llm.overload },
        { label: "Selection made", text: llm.selection },
        { label: "Flex confirmed", text: llm.confirm },
        { label: "Event settled", text: llm.status },
      ];

  return (
    <div className="bg-gray-800 rounded-xl p-4 h-72 flex flex-col">
      <h2 className="text-lg font-semibold mb-2">Event Timeline</h2>
      <div className="flex-1 overflow-auto text-sm space-y-3">
        {events.length === 0 && (
          <p className="text-gray-400">No events yet. Run the workflow.</p>
        )}
        {events.map(
          (e, i) =>
            e.text && (
              <div key={i} className="flex items-start space-x-3">
                <div className="mt-1 h-2 w-2 rounded-full bg-emerald-400" />
                <div>
                  <p className="text-xs font-semibold text-emerald-300">
                    {e.label}
                  </p>
                  <p className="text-gray-200 whitespace-pre-wrap">{e.text}</p>
                </div>
              </div>
            )
        )}
      </div>
    </div>
  );
}
