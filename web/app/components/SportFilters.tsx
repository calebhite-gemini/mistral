"use client";

import { useState } from "react";

const sports = ["All Sports", "Football", "Basketball", "Soccer", "UFC"];

export default function SportFilters() {
  const [active, setActive] = useState("All Sports");

  return (
    <div className="flex items-center gap-2">
      {sports.map((sport) => (
        <button
          key={sport}
          onClick={() => setActive(sport)}
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
      <button className="flex items-center gap-1 px-3 py-[7px] rounded-sm border border-[#27272a] text-[#64748b] hover:bg-[#27272a]/50 transition-colors">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="4" y1="21" x2="4" y2="14" /><line x1="4" y1="10" x2="4" y2="3" /><line x1="12" y1="21" x2="12" y2="12" /><line x1="12" y1="8" x2="12" y2="3" /><line x1="20" y1="21" x2="20" y2="16" /><line x1="20" y1="12" x2="20" y2="3" /><line x1="1" y1="14" x2="7" y2="14" /><line x1="9" y1="8" x2="15" y2="8" /><line x1="17" y1="16" x2="23" y2="16" />
        </svg>
        <span className="text-xs font-medium tracking-[0.3px] uppercase">Filter</span>
      </button>
    </div>
  );
}
