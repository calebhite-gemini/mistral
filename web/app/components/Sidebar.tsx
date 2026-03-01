"use client";

import { useState } from "react";

const navItems = [
  { label: "Overview", icon: "grid", active: false },
  { label: "Live Markets", icon: "bar-chart", active: true },
  { label: "Positions", icon: "layers", active: false },
  { label: "Analytics", icon: "settings-2", active: false },
];

const utilityItems = [
  { label: "Calculator", icon: "calculator" },
  { label: "History", icon: "clock" },
];

function NavIcon({ name }: { name: string }) {
  const size = 14;
  switch (name) {
    case "grid":
      return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
        </svg>
      );
    case "bar-chart":
      return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="20" x2="12" y2="10" /><line x1="18" y1="20" x2="18" y2="4" /><line x1="6" y1="20" x2="6" y2="16" />
        </svg>
      );
    case "layers":
      return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 2 7 12 12 22 7 12 2" /><polyline points="2 17 12 22 22 17" /><polyline points="2 12 12 17 22 12" />
        </svg>
      );
    case "settings-2":
      return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      );
    case "calculator":
      return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="4" y="2" width="16" height="20" rx="2" /><line x1="8" y1="6" x2="16" y2="6" /><line x1="16" y1="14" x2="16" y2="18" /><line x1="8" y1="10" x2="8" y2="10.01" /><line x1="12" y1="10" x2="12" y2="10.01" /><line x1="16" y1="10" x2="16" y2="10.01" /><line x1="8" y1="14" x2="8" y2="14.01" /><line x1="12" y1="14" x2="12" y2="14.01" /><line x1="8" y1="18" x2="8" y2="18.01" /><line x1="12" y1="18" x2="12" y2="18.01" />
        </svg>
      );
    case "clock":
      return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
        </svg>
      );
    case "cog":
      return (
        <svg width={size + 1} height={size + 1} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      );
    default:
      return null;
  }
}

export default function Sidebar() {
  const [activeNav, setActiveNav] = useState("Live Markets");

  return (
    <aside className="bg-[#09090b] border-r border-[#27272a] flex flex-col justify-between w-64 h-screen shrink-0 px-4 py-4">
      {/* Top section */}
      <div className="flex flex-col gap-6">
        {/* Logo */}
        <div className="flex items-center gap-3 px-2">
          <div className="w-[30px] h-[27px] bg-[#18181b] border border-[#27272a] rounded flex items-center justify-center">
            <svg width="16" height="13" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
            </svg>
          </div>
          <div>
            <p className="text-white text-sm font-bold tracking-[0.7px] uppercase leading-5">MarketEdge</p>
            <p className="text-[#64748b] text-[10px] font-mono leading-[15px]">TERMINAL_V1.0</p>
          </div>
        </div>

        {/* Main Nav */}
        <nav className="flex flex-col gap-0.5">
          {navItems.map((item) => {
            const isDisabled = item.label !== "Live Markets";
            return (
              <button
                key={item.label}
                disabled={isDisabled}
                onClick={() => !isDisabled && setActiveNav(item.label)}
                className={`flex items-center gap-3 px-3 py-2 rounded-sm w-full text-left transition-colors ${
                  isDisabled
                    ? "opacity-30 cursor-not-allowed text-[#94a3b8]"
                    : activeNav === item.label
                      ? "bg-[#27272a] border-l-2 border-white text-white font-bold pl-3.5"
                      : "text-[#94a3b8] hover:bg-[#27272a]/50"
                }`}
              >
                <NavIcon name={item.icon} />
                <span className="text-xs tracking-[0.3px] uppercase">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Divider */}
        <div className="px-2">
          <div className="h-px bg-[#27272a]" />
        </div>

        {/* Utilities */}
        <div className="flex flex-col gap-0.5">
          <p className="text-[#475569] text-[10px] font-mono font-bold tracking-[1px] uppercase px-3 pb-2">
            Utilities
          </p>
          {utilityItems.map((item) => (
            <button
              key={item.label}
              disabled
              className="flex items-center gap-3 px-3 py-2 rounded-sm w-full text-left text-[#94a3b8] opacity-30 cursor-not-allowed transition-colors"
            >
              <NavIcon name={item.icon} />
              <span className="text-xs font-medium tracking-[0.3px] uppercase">{item.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Bottom section */}
      <div className="flex flex-col gap-1">
        <button disabled className="flex items-center gap-3 px-3 py-2 rounded-sm w-full text-left text-[#94a3b8] opacity-30 cursor-not-allowed transition-colors">
          <NavIcon name="cog" />
          <span className="text-xs font-medium tracking-[0.3px] uppercase">Settings</span>
        </button>
        <div className="border-t border-[#27272a] pt-3 mt-2">
          <div className="flex items-center gap-3 px-3">
            <div className="w-7 h-7 rounded bg-[#18181b] border border-[#27272a] opacity-80 flex items-center justify-center text-[10px] text-[#64748b] font-mono">
              AT
            </div>
            <div>
              <p className="text-white text-xs font-medium">Alex Trader</p>
              <p className="text-[#64748b] text-[10px] font-mono">PRO_TIER</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
