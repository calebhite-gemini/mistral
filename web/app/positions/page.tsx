"use client";

import { useState, useRef, useEffect } from "react";
import Sidebar from "../components/Sidebar";

/* ───── Types ───── */

interface Position {
  id: string;
  team1: string;
  team2: string;
  team1Color: string;
  team2Color: string;
  league: string;
  type: string;
  entryPrice: number;
  currentPrice: number;
  stake: number;
  units: number;
  unrealizedPL: number;
  unrealizedPLPercent: number;
  status: "Live" | "Open" | "Settled" | "Pending";
}

/* ───── Mock Data ───── */

const MOCK_POSITIONS: Position[] = [
  {
    id: "1",
    team1: "LAL",
    team2: "GSW",
    team1Color: "#552583",
    team2Color: "#FFC72C",
    league: "NBA",
    type: "OVER 224.5",
    entryPrice: 1.92,
    currentPrice: 2.05,
    stake: 500.0,
    units: 260.4,
    unrealizedPL: 67.7,
    unrealizedPLPercent: 13.5,
    status: "Live",
  },
  {
    id: "2",
    team1: "KC",
    team2: "BUF",
    team1Color: "#E31837",
    team2Color: "#00338D",
    league: "NFL",
    type: "MONEYLINE",
    entryPrice: 1.8,
    currentPrice: 1.72,
    stake: 1200.0,
    units: 666.7,
    unrealizedPL: -53.4,
    unrealizedPLPercent: -4.4,
    status: "Open",
  },
  {
    id: "3",
    team1: "BOS",
    team2: "MIA",
    team1Color: "#007A33",
    team2Color: "#98002E",
    league: "NBA",
    type: "SPREAD -4.5",
    entryPrice: 2.1,
    currentPrice: 2.45,
    stake: 2000.0,
    units: 952.4,
    unrealizedPL: 333.33,
    unrealizedPLPercent: 16.7,
    status: "Live",
  },
];

const TOTAL_POSITIONS = 14;
const TOTAL_STAKE = 12450.0;
const UNREALIZED_PL = 842.15;
const UNREALIZED_PL_PERCENT = 6.8;
const TOTAL_REALIZED_PL = 4821.5;

/* ───── Stat Card ───── */

function StatCard({
  label,
  value,
  subValue,
  subColor,
}: {
  label: string;
  value: string;
  subValue?: string;
  subColor?: string;
}) {
  return (
    <div className="bg-[#18181b]/50 border border-[#27272a] rounded-sm p-4 flex-1 flex flex-col justify-between min-h-[100px]">
      <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">
        {label}
      </span>
      <div className="flex items-baseline gap-2">
        <span className="text-white text-2xl font-mono font-bold">{value}</span>
        {subValue && (
          <span className={`text-xs font-mono font-medium ${subColor || "text-[#64748b]"}`}>
            {subValue}
          </span>
        )}
      </div>
    </div>
  );
}

/* ───── Status Badge ───── */

function StatusBadge({ status }: { status: Position["status"] }) {
  if (status === "Live") {
    return (
      <span className="inline-flex items-center gap-1.5 border border-[#10b981] text-[#10b981] text-[10px] font-mono font-bold tracking-[0.5px] uppercase px-3 py-1 rounded-sm">
        <span className="w-1.5 h-1.5 bg-[#10b981] rounded-full animate-pulse" />
        LIVE
      </span>
    );
  }
  if (status === "Open") {
    return (
      <span className="inline-flex items-center border border-[#94a3b8] text-[#94a3b8] text-[10px] font-mono font-bold tracking-[0.5px] uppercase px-3 py-1 rounded-sm">
        OPEN
      </span>
    );
  }
  if (status === "Settled") {
    return (
      <span className="inline-flex items-center border border-[#64748b] text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase px-3 py-1 rounded-sm">
        SETTLED
      </span>
    );
  }
  return (
    <span className="inline-flex items-center border border-[#f59e0b] text-[#f59e0b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase px-3 py-1 rounded-sm">
      PENDING
    </span>
  );
}

/* ───── Main Page ───── */

type TabFilter = "Open" | "Settled" | "Pending";

export default function PositionsPage() {
  const [activeTab, setActiveTab] = useState<TabFilter>("Open");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    }
    if (notifOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [notifOpen]);

  const tabs: TabFilter[] = ["Open", "Settled", "Pending"];
  const PAGE_SIZE = 3;
  const totalPages = Math.ceil(TOTAL_POSITIONS / PAGE_SIZE);

  // Filter positions (mock: all show under "Open")
  const filtered = MOCK_POSITIONS.filter((p) => {
    if (search) {
      const q = search.toLowerCase();
      const matchup = `${p.team1} vs ${p.team2}`.toLowerCase();
      if (!matchup.includes(q) && !p.league.toLowerCase().includes(q) && !p.type.toLowerCase().includes(q)) {
        return false;
      }
    }
    return true;
  });

  return (
    <div className="flex h-screen bg-[#09090b] overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="bg-[#09090b] border-b border-[#27272a] flex items-center justify-between px-6 py-4 shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-white text-lg font-bold tracking-[-0.45px] uppercase">
              Positions Dashboard
            </h1>
            <span className="bg-[rgba(16,185,129,0.1)] border border-[rgba(16,185,129,0.2)] text-[#10b981] text-[10px] font-mono px-2.5 py-0.5 rounded-sm">
              LIVE FEED ACTIVE
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative" ref={notifRef}>
              <button
                onClick={() => setNotifOpen((v) => !v)}
                className="relative p-2 text-[#94a3b8] hover:text-white transition-colors"
              >
                <svg width="14" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                  <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                </svg>
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-[#ef4444] rounded-full" />
              </button>
              {notifOpen && (
                <div className="absolute right-0 top-full mt-2 w-72 bg-[#18181b] border border-[#27272a] rounded-md shadow-xl z-50">
                  <div className="px-4 py-3 border-b border-[#27272a]">
                    <p className="text-white text-xs font-bold tracking-[0.3px] uppercase">Notifications</p>
                  </div>
                  <div className="px-4 py-8 flex flex-col items-center gap-2">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                    </svg>
                    <p className="text-[#64748b] text-xs font-mono">No new notifications</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 flex flex-col min-h-0 overflow-y-auto px-6 pt-6 pb-6 gap-6">
          {/* Stats Cards */}
          <div className="flex gap-4 shrink-0">
            <StatCard label="Active Positions" value={TOTAL_POSITIONS.toString()} />
            <StatCard label="Total Stake" value={`$${TOTAL_STAKE.toLocaleString("en-US", { minimumFractionDigits: 2 })}`} />
            <StatCard
              label="Unrealized P/L"
              value={`+$${UNREALIZED_PL.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
              subValue={`+${UNREALIZED_PL_PERCENT}%`}
              subColor="text-[#10b981]"
            />
            <StatCard
              label="Total Realized P/L"
              value={`$${TOTAL_REALIZED_PL.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
            />
          </div>

          {/* Filters Row */}
          <div className="flex items-center justify-between shrink-0">
            {/* Tabs */}
            <div className="flex items-center gap-0">
              {tabs.map((tab) => (
                <button
                  key={tab}
                  onClick={() => { setActiveTab(tab); setPage(1); }}
                  className={`px-5 py-2 text-xs font-bold tracking-[0.5px] uppercase transition-colors border border-[#27272a] ${
                    activeTab === tab
                      ? "bg-white text-black"
                      : "bg-transparent text-[#94a3b8] hover:bg-[#27272a]/50"
                  } ${tab === "Open" ? "rounded-l-sm" : ""} ${tab === "Pending" ? "rounded-r-sm" : ""} ${tab !== "Open" ? "-ml-px" : ""}`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Search + Filter */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-[#64748b]"
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search positions..."
                  className="bg-[#18181b] border border-[#27272a] text-white text-xs font-mono pl-9 pr-4 py-2 rounded-sm w-56 placeholder:text-[#64748b] focus:outline-none focus:border-[#3f3f46]"
                />
              </div>
              <button className="flex items-center gap-2 bg-[#18181b] border border-[#27272a] text-[#94a3b8] text-xs font-bold tracking-[0.5px] uppercase px-4 py-2 rounded-sm hover:bg-[#27272a]/50 transition-colors">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="4" y1="21" x2="4" y2="14" />
                  <line x1="4" y1="10" x2="4" y2="3" />
                  <line x1="12" y1="21" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12" y2="3" />
                  <line x1="20" y1="21" x2="20" y2="16" />
                  <line x1="20" y1="12" x2="20" y2="3" />
                  <line x1="1" y1="14" x2="7" y2="14" />
                  <line x1="9" y1="8" x2="15" y2="8" />
                  <line x1="17" y1="16" x2="23" y2="16" />
                </svg>
                Filter
              </button>
            </div>
          </div>

          {/* Positions Table */}
          <div className="bg-[#18181b] border border-[#27272a] rounded-sm flex flex-col">
            {/* Table Header */}
            <div className="bg-[#09090b] border-b border-[#27272a] grid grid-cols-[22%_11%_11%_14%_13%_11%_18%] items-center">
              <div className="pl-6 pr-3 py-[18px]">
                <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">
                  Matchup
                </span>
              </div>
              <div className="px-3 py-3 text-center">
                <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase leading-[13px]">
                  Entry<br />Price
                </span>
              </div>
              <div className="px-3 py-3 text-center">
                <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase leading-[13px]">
                  Current<br />Price
                </span>
              </div>
              <div className="px-3 py-3 text-right">
                <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase leading-[13px]">
                  Size/Stake
                </span>
              </div>
              <div className="px-3 py-3 text-right">
                <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase leading-[13px]">
                  Unrealized<br />P/L
                </span>
              </div>
              <div className="px-3 py-[18px] text-center">
                <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">
                  Status
                </span>
              </div>
              <div className="px-3 py-[18px] text-center">
                <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">
                  Actions
                </span>
              </div>
            </div>

            {/* Table Rows */}
            {filtered.map((pos, idx) => (
              <div
                key={pos.id}
                className={`grid grid-cols-[22%_11%_11%_14%_13%_11%_18%] items-center hover:bg-[#27272a]/30 transition-colors ${
                  idx > 0 ? "border-t border-[#27272a]" : ""
                }`}
              >
                {/* Matchup */}
                <div className="pl-6 pr-3 py-5 flex items-center gap-3">
                  <div className="flex flex-col gap-0.5">
                    <div
                      className="w-[3px] h-[10px] rounded-full"
                      style={{ backgroundColor: pos.team1Color }}
                    />
                    <div
                      className="w-[3px] h-[10px] rounded-full"
                      style={{ backgroundColor: pos.team2Color }}
                    />
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold">
                      {pos.team1} vs {pos.team2}
                    </p>
                    <p className="text-[#64748b] text-[10px] font-mono">
                      {pos.league} &bull; {pos.type}
                    </p>
                  </div>
                </div>

                {/* Entry Price */}
                <div className="px-3 py-5 text-center">
                  <span className="text-white text-sm font-mono">
                    {pos.entryPrice.toFixed(2)}
                  </span>
                </div>

                {/* Current Price */}
                <div className="px-3 py-5 text-center">
                  <span className="text-white text-sm font-mono">
                    {pos.currentPrice.toFixed(2)}
                  </span>
                </div>

                {/* Size/Stake */}
                <div className="px-3 py-5 text-right">
                  <p className="text-white text-sm font-mono">
                    ${pos.stake.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </p>
                  <p className="text-[#64748b] text-[10px] font-mono">
                    {pos.units.toFixed(1)} UNITS
                  </p>
                </div>

                {/* Unrealized P/L */}
                <div className="px-3 py-5 text-right">
                  <p
                    className={`text-sm font-mono font-semibold ${
                      pos.unrealizedPL >= 0 ? "text-[#10b981]" : "text-[#ef4444]"
                    }`}
                  >
                    {pos.unrealizedPL >= 0 ? "+" : ""}${Math.abs(pos.unrealizedPL).toFixed(2)}
                  </p>
                  <p
                    className={`text-[10px] font-mono ${
                      pos.unrealizedPLPercent >= 0 ? "text-[#10b981]" : "text-[#ef4444]"
                    }`}
                  >
                    {pos.unrealizedPLPercent >= 0 ? "+" : ""}
                    {pos.unrealizedPLPercent.toFixed(1)}%
                  </p>
                </div>

                {/* Status */}
                <div className="px-3 py-5 flex justify-center">
                  <StatusBadge status={pos.status} />
                </div>

                {/* Actions */}
                <div className="px-3 py-5 flex justify-center">
                  <button className="border border-[#27272a] text-white text-[10px] font-mono font-bold tracking-[0.5px] uppercase px-4 py-1.5 rounded-sm hover:bg-[#27272a] transition-colors">
                    Close
                  </button>
                </div>
              </div>
            ))}

            {/* Pagination Footer */}
            <div className="border-t border-[#27272a] flex items-center justify-between px-6 py-4">
              <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">
                Showing 1-{filtered.length} of {TOTAL_POSITIONS} Active Positions
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="border border-[#27272a] text-white text-[10px] font-mono font-bold tracking-[0.5px] uppercase px-3 py-1.5 rounded-sm hover:bg-[#27272a] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Prev
                </button>
                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map((p) => (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={`border border-[#27272a] text-[10px] font-mono font-bold px-2.5 py-1.5 rounded-sm transition-colors ${
                      page === p
                        ? "bg-white text-black"
                        : "text-white hover:bg-[#27272a]"
                    }`}
                  >
                    {p}
                  </button>
                ))}
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="border border-[#27272a] text-white text-[10px] font-mono font-bold tracking-[0.5px] uppercase px-3 py-1.5 rounded-sm hover:bg-[#27272a] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
