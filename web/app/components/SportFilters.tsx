"use client";

const sports = ["All Sports", "Football", "Basketball", "Soccer", "UFC"];

interface SportFiltersProps {
  active: string;
  onSelect: (sport: string) => void;
  searchQuery: string;
  onSearch: (q: string) => void;
}

export default function SportFilters({ active, onSelect, searchQuery, onSearch }: SportFiltersProps) {
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
