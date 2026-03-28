function FilterBar({ filters, options, onChange, onClear }) {
  return (
    <div className="rounded-xl2 border border-cardBorder bg-white p-4 shadow-soft">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <select
          value={filters.floor}
          onChange={(e) => onChange("floor", e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 focus:border-primary focus:outline-none"
        >
          <option value="">All Floors</option>
          {options.floors.map((floor) => (
            <option key={floor} value={floor}>
              {floor}
            </option>
          ))}
        </select>
        <select
          value={filters.issueType}
          onChange={(e) => onChange("issueType", e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 focus:border-primary focus:outline-none"
        >
          <option value="">All Issue Types</option>
          {options.issueTypes.map((issueType) => (
            <option key={issueType} value={issueType}>
              {issueType}
            </option>
          ))}
        </select>
        <select
          value={filters.status}
          onChange={(e) => onChange("status", e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 focus:border-primary focus:outline-none"
        >
          <option value="">All Status</option>
          {options.statuses.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={onClear}
          className="rounded-lg border border-primary px-3 py-2 font-medium text-primary transition hover:bg-primary hover:text-white"
        >
          Clear Filters
        </button>
      </div>
    </div>
  );
}

export default FilterBar;
