export default function DERList({ selected }) {
  if (!selected) {
    return <p className="text-gray-400 text-sm">No selection yet. Run the workflow.</p>;
  }

  return (
    <div className="space-y-3">
      {selected.map((w) => (
        <div
          key={w.id}
          className="p-3 rounded-md bg-gray-900"
        >
          <p className="font-mono text-xs text-gray-400">{w.id}</p>
          <p className="text-gray-200">{w.region} · {w.grid_zone}</p>
          <p className="text-gray-300">{w.window_start} → {w.window_end}</p>
          <p className="text-gray-400 text-xs mt-1">
            Capacity: {w.capacity_kw ?? w.capacity_mw * 1000} kW · RE {w.renewable_mix}% · CO₂ {w.carbon_intensity} g/kWh
          </p>
        </div>
      ))}
    </div>
  );
}
