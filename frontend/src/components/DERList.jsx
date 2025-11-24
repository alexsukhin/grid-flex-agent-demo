export default function DERList({ selected }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 h-72 flex flex-col">
      <h2 className="text-lg font-semibold mb-2">Selected DER Windows</h2>
      <div className="flex-1 overflow-auto text-sm">
        {!selected && (
          <p className="text-gray-400">No selection yet. Run the workflow.</p>
        )}
        {selected &&
          selected.map((w) => (
            <div
              key={w.id}
              className="border border-gray-700 rounded-lg p-3 mb-2 bg-gray-900/60"
            >
              <p className="font-mono text-xs text-gray-400">{w.id}</p>
              <p className="text-gray-200">
                {w.region} · {w.grid_zone}
              </p>
              <p className="text-gray-300">
                {w.window_start} → {w.window_end}
              </p>
              <p className="text-gray-400 text-xs mt-1">
                Capacity: {w.capacity_kw ?? w.capacity_mw * 1000} kW · RE{" "}
                {w.renewable_mix}% · CO₂ {w.carbon_intensity} g/kWh
              </p>
            </div>
          ))}
      </div>
    </div>
  );
}
