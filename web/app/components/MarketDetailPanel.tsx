"use client";

import { useEffect, useState } from "react";
import PlaceBetModal from "./PlaceBetModal";

export interface MarketDetail {
  ticker: string;
  lastPrice: number;
  team1: string;
  team2: string;
  team1Abbr: string;
  team2Abbr: string;
  league: string;
  type: string;
  gameDate: string;
  title: string;
  impliedProb: string;
  probChange: string;
  marketOdds: string;
  oddsBest: string;
  volume: string;
  volumeTag: string;
  volumePublic: string;
  sharpMoney: string;
  sharpOn: string;
  drivers: {
    tag: string;
    tagColor: string;
    title: string;
    description: string;
    source: string;
    sourceIcon: string;
    sourceColor: string;
    time: string;
  }[];
}

interface MarketDetailPanelProps {
  market: MarketDetail | null;
  onClose: () => void;
  isOpen?: boolean;
  loading?: boolean;
}

export default function MarketDetailPanel({ market, onClose, isOpen, loading }: MarketDetailPanelProps) {
  const open = isOpen ?? !!market;
  const [betOpen, setBetOpen] = useState(false);

  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (open) {
      document.addEventListener("keydown", handleEsc);
      return () => document.removeEventListener("keydown", handleEsc);
    }
  }, [open, onClose]);

  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 bg-black/50 z-40 transition-opacity duration-300 ${
          open ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
        onClick={onClose}
      />

      {/* Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-[380px] bg-[#0c0c0e] border-l border-[#27272a] z-50 flex flex-col transition-transform duration-300 ease-in-out ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {loading && !market ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3">
              <div className="w-6 h-6 border-2 border-[#27272a] border-t-white rounded-full animate-spin" />
              <span className="text-[#64748b] text-xs font-mono">Loading market...</span>
            </div>
          </div>
        ) : market && (
          <>
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-[#27272a] shrink-0">
              <div className="flex items-center gap-3">
                <button
                  onClick={onClose}
                  className="text-[#94a3b8] hover:text-white transition-colors"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
                <span className="bg-[#1e293b] border border-[#27272a] text-[#94a3b8] text-[10px] font-mono font-bold px-2 py-0.5 rounded-sm uppercase">
                  {market.league}
                </span>
                <span className="text-[#94a3b8] text-xs font-mono">
                  {market.team1Abbr} vs {market.team2Abbr} &bull; {market.gameDate}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button className="text-[#64748b] hover:text-white transition-colors p-1">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" /><line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
                  </svg>
                </button>
                <button className="text-[#64748b] hover:text-white transition-colors p-1">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
                  </svg>
                </button>
                <button className="bg-white text-[#09090b] p-2 rounded-sm hover:bg-[#e2e8f0] transition-colors ml-1">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="7" y1="17" x2="17" y2="7" /><polyline points="7 7 17 7 17 17" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Scrollable content */}
            <div className="flex-1 overflow-y-auto">
              {/* Title */}
              <div className="px-5 pt-5 pb-4">
                <h2 className="text-white text-xl font-bold">{market.title}</h2>
              </div>

              {/* Stats Grid */}
              <div className="px-5 grid grid-cols-2 gap-3">
                {/* Implied Probability */}
                <div className="bg-[#18181b]/50 border border-[#27272a] rounded-sm p-4">
                  <p className="text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase mb-2">Implied Probability</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-white text-2xl font-mono font-bold">{market.impliedProb}</span>
                    <span className="text-[#10b981] text-xs font-mono font-medium">{market.probChange}</span>
                  </div>
                  <p className="text-[#64748b] text-[10px] font-mono mt-1">vs Opening Line</p>
                </div>

                {/* Market Odds */}
                <div className="bg-[#18181b]/50 border border-[#27272a] rounded-sm p-4">
                  <p className="text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase mb-2">Market Odds</p>
                  <span className="text-white text-2xl font-mono font-bold">{market.marketOdds}</span>
                  <p className="text-[#64748b] text-[10px] font-mono mt-1">Best: {market.oddsBest}</p>
                </div>

                {/* Volume */}
                <div className="bg-[#18181b]/50 border border-[#27272a] rounded-sm p-4">
                  <p className="text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase mb-2">Volume (24H)</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-white text-2xl font-mono font-bold">{market.volume}</span>
                    <span className="bg-[#022c22] border border-[rgba(6,78,59,0.5)] text-[#34d399] text-[8px] font-bold tracking-[0.5px] uppercase px-1.5 py-0.5 rounded-sm">
                      {market.volumeTag}
                    </span>
                  </div>
                  <p className="text-[#64748b] text-[10px] font-mono mt-1">{market.volumePublic}</p>
                </div>

                {/* Sharp Money */}
                <div className="bg-[#18181b]/50 border border-[#27272a] rounded-sm p-4">
                  <p className="text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase mb-2">Sharp Money</p>
                  <span className="text-white text-2xl font-mono font-bold">{market.sharpMoney}</span>
                  <p className="text-[#64748b] text-[10px] font-mono mt-1">{market.sharpOn}</p>
                </div>
              </div>

              {/* Market Drivers & News */}
              <div className="px-5 pt-6 pb-4">
                <div className="flex items-center gap-2 mb-4">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                  </svg>
                  <span className="text-white text-xs font-bold tracking-[0.5px] uppercase">Market Drivers & News</span>
                </div>

                <div className="flex flex-col">
                  {(market.drivers ?? []).map((driver, idx) => (
                    <div
                      key={idx}
                      className={`py-4 ${idx > 0 ? "border-t border-[#27272a]" : ""}`}
                    >
                      <div className="flex items-start justify-between mb-1.5">
                        <span
                          className="text-[9px] font-bold tracking-[0.5px] uppercase px-1.5 py-0.5 rounded-sm border"
                          style={{
                            color: driver.tagColor,
                            borderColor: `${driver.tagColor}33`,
                            backgroundColor: `${driver.tagColor}15`,
                          }}
                        >
                          {driver.tag}
                        </span>
                        <span className="text-[#64748b] text-[10px] font-mono">{driver.time}</span>
                      </div>
                      <h4 className="text-white text-sm font-semibold mb-1.5">{driver.title}</h4>
                      <p className="text-[#94a3b8] text-xs leading-[18px] mb-3">{driver.description}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span
                            className="w-5 h-5 rounded flex items-center justify-center text-[9px] font-bold text-white"
                            style={{ backgroundColor: driver.sourceColor }}
                          >
                            {driver.sourceIcon}
                          </span>
                          <span className="text-[#94a3b8] text-[11px]">{driver.source}</span>
                        </div>
                        <button className="text-[#64748b] hover:text-white transition-colors">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" /><polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="px-5 py-4 border-t border-[#27272a] shrink-0 flex flex-col gap-2.5">
              <button
                onClick={() => setBetOpen(true)}
                className="w-full bg-white text-[#09090b] text-xs font-bold tracking-[0.5px] uppercase py-3 rounded-sm hover:bg-[#e2e8f0] transition-colors"
              >
                Place Bet
              </button>
              <button className="w-full border border-[#27272a] text-white text-xs font-bold tracking-[0.5px] uppercase py-3 rounded-sm hover:bg-[#27272a]/50 transition-colors">
                Add to Watchlist
              </button>
            </div>
          </>
        )}
      </div>

      {betOpen && market && (
        <PlaceBetModal
          ticker={market.ticker}
          title={market.title}
          lastPrice={market.lastPrice}
          onClose={() => setBetOpen(false)}
        />
      )}
    </>
  );
}
