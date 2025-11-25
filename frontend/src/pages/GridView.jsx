import { useState } from "react";

export default function GridView({ allDERs = [] }) {
  const [sortBy, setSortBy] = useState("capacity_desc");
  const [expanded, setExpanded] = useState({});

  const sorted = [...allDERs].sort((a, b) => {
    const capA = a.capacity_kw ?? (a.capacity_mw || 0) * 1000;
    const capB = b.capacity_kw ?? (b.capacity_mw || 0) * 1000;

    switch (sortBy) {
      case "capacity_desc":
        return capB - capA;
      case "capacity_asc":
        return capA - capB;

      case "re_desc":
        return (b.renewable_mix || 0) - (a.renewable_mix || 0);
      case "re_asc":
        return (a.renewable_mix || 0) - (b.renewable_mix || 0);

      case "co2_asc":
        return (a.carbon_intensity || 9999) - (b.carbon_intensity || 9999);
      case "co2_desc":
        return (b.carbon_intensity || 9999) - (a.carbon_intensity || 9999);

      default:
        return 0;
    }
  });

  const getCap = (d) =>
    d.capacity_kw ?? (d.capacity_mw || 0) * 1000;

  const toggle = (id) =>
    setExpanded((e) => ({ ...e, [id]: !e[id] }));

  return (
    <div className="h-[calc(100vh-60px)] p-6 overflow-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">DER Explorer</h2>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-gray-800 border border-gray-600 text-gray-200 rounded-lg px-3 py-2 text-sm"
        >
          <option value="capacity_desc">Capacity (High → Low)</option>
          <option value="capacity_asc">Capacity (Low → High)</option>

          <option value="re_desc">Renewable Mix (High → Low)</option>
          <option value="re_asc">Renewable Mix (Low → High)</option>

          <option value="co2_asc">CO₂ Intensity (Low → High)</option>
          <option value="co2_desc">CO₂ Intensity (High → Low)</option>
        </select>
      </div>

      {!sorted.length && (
        <p className="text-gray-400">Run the workflow to see DERs.</p>
      )}

      {/* Masonry layout to prevent expansion overlap */}
      <div className="columns-1 md:columns-2 gap-4 space-y-4">
        {sorted.map((d) => (
          <div
            key={d.id}
            className={`
              break-inside-avoid 
              p-4 rounded-lg border border-gray-700 bg-gray-800
            `}
          >
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <p className="font-mono text-xs text-gray-400">{d.id}</p>
                <p className="text-gray-200 font-semibold">{d.region}</p>
                <p className="text-gray-300">Zone: {d.grid_zone}</p>
              </div>

              {d.selected && (
                <span className="text-emerald-400 text-xs font-bold">
                  SELECTED
                </span>
              )}
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mt-3 text-xs">
              <span className="px-2 py-1 bg-gray-700 rounded-md text-gray-200">
                ⚡ {getCap(d)} kW
              </span>
              <span className="px-2 py-1 bg-gray-700 rounded-md text-gray-200">
                🌿 {d.renewable_mix}% RE
              </span>
              <span className="px-2 py-1 bg-gray-700 rounded-md text-gray-200">
                🏭 {d.carbon_intensity} g/kWh
              </span>
            </div>

            {/* Expand button */}
            <button
              onClick={() => toggle(d.id)}
              className="mt-3 text-sm text-blue-300 hover:text-blue-400"
            >
              {expanded[d.id] ? "Hide details ▲" : "Show details ▼"}
            </button>

            {/* Expanded section */}
            {expanded[d.id] && (
              <div className="mt-3 space-y-1 text-sm text-gray-300 border-t border-gray-700 pt-3">
                <p><strong>Window:</strong> {d.window_start} → {d.window_end}</p>
                <p><strong>Duration:</strong> {d.window_duration || "N/A"}</p>
                <p><strong>Response time:</strong> {d.response_time_s || "N/A"}s</p>
                <p><strong>Comfort penalty:</strong> {d.comfort_penalty ?? "N/A"}</p>
                <p><strong>Availability score:</strong> {d.availability_score ?? "N/A"}</p>
                <p><strong>Price:</strong> {d.price_kw ? `${d.price_kw} ${d.price_currency}` : "N/A"}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
