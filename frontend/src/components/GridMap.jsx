export default function GridMap({ selected }) {
  const first = selected && selected[0];

  return (
    <div className="bg-gray-800 rounded-xl p-4 h-72 flex flex-col">
      <h2 className="text-lg font-semibold mb-2">Grid View</h2>
      <div className="flex-1 border border-gray-700 rounded-lg relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-sky-500/10 via-emerald-500/10 to-purple-500/10" />
        <div className="relative p-4 text-sm">
          {!first && <p className="text-gray-400">Run the workflow to see a window.</p>}
          {first && (
            <>
              <p className="text-gray-300 mb-1">
                <span className="font-semibold">Selected window:</span> {first.id}
              </p>
              <p className="text-gray-300 mb-1">
                Region: <span className="font-mono">{first.region}</span>
              </p>
              <p className="text-gray-300 mb-1">
                Zone: <span className="font-mono">{first.grid_zone}</span>
              </p>
              <p className="text-gray-300 mb-1">
                Capacity:{" "}
                <span className="font-mono">
                  {first.capacity_kw ?? first.capacity_mw * 1000} kW
                </span>
              </p>
              <p className="text-gray-300 mb-1">
                Renewable mix: <span className="font-mono">{first.renewable_mix}%</span>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
