"use client";

const sports = ["All Sports", "Football", "Basketball", "Hockey", "Soccer", "UFC"];

export const TIME_RANGES = [
  { label: "24 Hours", hours: 24 },
  { label: "48 Hours", hours: 48 },
  { label: "This Week", hours: 7 * 24 },
];

interface SportFiltersProps {
  active: string;
  onSelect: (sport: string) => void;
  searchQuery: string;
  onSearch: (q: string) => void;
  activeTimeRange: string;
  onTimeRangeSelect: (range: string) => void;
}

export default function SportFilters({ active, onSelect, searchQuery, onSearch, activeTimeRange, onTimeRangeSelect }: SportFiltersProps) {
  return (
    <div className="flex items-center gap-2">
      {sports.map((sport) => (
        <button
          key={sport}
          onClick={() => onSelect(sport)}
          className={`px-4 py-[7px] rounded-sm text-xs tracking-[0.3px] uppercase transition-colors border ${
            active === sport
              ? "bg-[#f1f5f9] border-[#f1f5f9] text-[#09090b] font-bold"
              : "border-[#27272a] text-[#94a3b8] font-medium hover:bg-[#27272a]/50"
          }`}
        >
          {sport}
        </button>
      ))}
      <div className="flex-1" />
      <select
        value={activeTimeRange}
        onChange={(e) => onTimeRangeSelect(e.target.value)}
        className="bg-[#18181b] border border-[#27272a] rounded-sm text-[#94a3b8] text-xs font-mono tracking-[0.3px] uppercase px-3 py-[7px] outline-none cursor-pointer hover:border-[#3f3f46] transition-colors appearance-none pr-7"
        style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L5 5L9 1' stroke='%2364748b' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")`, backgroundRepeat: "no-repeat", backgroundPosition: "right 8px center" }}
      >
        {TIME_RANGES.map((r) => (
          <option key={r.label} value={r.label}>{r.label}</option>
        ))}
      </select>
      <div className="bg-[#18181b] border border-[#27272a] rounded-sm flex items-center px-3 py-[7px] w-56">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearch(e.target.value)}
          placeholder="SEARCH TICKER/EVENT..."
          className="bg-transparent border-none outline-none text-[#475569] text-xs font-mono w-full ml-2 placeholder:text-[#475569]"
        />
      </div>
    </div>
  );
}
