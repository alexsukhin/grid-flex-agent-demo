export default function OverloadsView({ items = [] }) {
  const formatTime = (ts) =>
    new Date(ts).toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      timeZoneName: "short",
    });

  const severityColor = (kw) => {
    if (kw > 10000) return "text-red-400 bg-red-900/30";
    if (kw > 5000) return "text-yellow-300 bg-yellow-900/20";
    return "text-green-300 bg-green-900/20";
  };

  return (
    <div className="h-[calc(100vh-60px)] p-6 overflow-auto">
      <h2 className="text-xl font-semibold mb-4">Previous Overloads</h2>

      {!items.length && (
        <p className="text-gray-400">No overloads recorded yet.</p>
      )}

      <div className="space-y-3">
        {items
          .slice()
          .reverse()
          .map((o, i) => {
            const sevClass = severityColor(o.required_kw);
            return (
              <div
                key={i}
                className="bg-gray-800 border border-gray-700 p-4 rounded-lg space-y-2"
              >
                {/* TOP ROW */}
                <div className="flex justify-between items-center">
                  <span
                    className={`px-2 py-1 rounded-md text-xs font-medium ${sevClass}`}
                  >
                    {o.required_kw > 10000
                      ? "Severe Overload"
                      : o.required_kw > 5000
                      ? "Moderate Overload"
                      : "Minor Overload"}
                  </span>

                  {/* Mode */}
                  {o.mode && (
                    <span
                      className={`px-2 py-1 rounded-md text-xs font-medium ${
                        o.mode === "emergency"
                          ? "text-red-300 bg-red-900/30"
                          : "text-blue-300 bg-blue-900/30"
                      }`}
                    >
                      {o.mode.toUpperCase()}
                    </span>
                  )}
                </div>

                {/* REQUIRED KW */}
                <p className="text-gray-200 text-lg font-semibold">
                  {o.required_kw.toLocaleString()} kW required
                </p>

                {/* SELECTED CAPACITY + COUNT */}
                {o.selected_kw !== undefined && (
                  <p className="text-gray-300 text-sm">
                    <strong>Selected capacity:</strong>{" "}
                    {o.selected_kw.toLocaleString()} kW
                  </p>
                )}

                {o.selected_count !== undefined && (
                  <p className="text-gray-300 text-sm">
                    <strong>DERs activated:</strong> {o.selected_count}
                  </p>
                )}

                {/* TIMESTAMP */}
                <p className="text-gray-400 text-sm">{formatTime(o.timestamp)}</p>
              </div>
            );
          })}
      </div>
    </div>
  );
}
