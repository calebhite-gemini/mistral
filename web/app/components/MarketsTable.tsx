"use client";

export interface MarketRow {
  ticker: string;
  team1: string;
  team2: string;
  team1Color: string;
  team2Color: string;
  league: string;
  type: string;
  closesIn: string;
  closingUrgent: boolean;
  marketPrice: string;
  modelProb: string;
  edge: string;
  edgePositive: boolean;
  ev: string;
  evPositive: boolean;
  signal: "YES" | "NO";
  confidence: "High" | "Med" | "Low";
  confidencePercent: number;
}

interface MarketsTableProps {
  markets: MarketRow[];
  loading?: boolean;
  error?: string;
  selectedTicker?: string | null;
  onSelect?: (ticker: string) => void;
  page?: number;
  totalCount?: number;
  onPageChange?: (page: number) => void;
}

function ClockIcon() {
  return (
    <svg width="10" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function SkeletonRow({ idx }: { idx: number }) {
  return (
    <div className={`grid grid-cols-[16%_14%_9%_9%_11%_10%_11%_15%_5%] items-center py-4 ${idx > 0 ? "border-t border-[#27272a]" : ""}`}>
      {Array.from({ length: 9 }).map((_, i) => (
        <div key={i} className="px-6">
          <div className="h-4 bg-[#27272a] rounded animate-pulse" />
        </div>
      ))}
    </div>
  );
}

const PAGE_SIZE = 10;

export default function MarketsTable({ markets, loading, error, selectedTicker, onSelect, page = 1, totalCount, onPageChange }: MarketsTableProps) {
  const total = totalCount ?? markets.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const start = (page - 1) * PAGE_SIZE + 1;
  const end = Math.min(page * PAGE_SIZE, total);
  return (
    <div className="bg-[#18181b] border border-[#27272a] rounded-sm flex flex-col min-h-0 flex-1 overflow-hidden">
      {/* Header */}
      <div className="bg-[#09090b] border-b border-[#27272a] grid grid-cols-[16%_14%_9%_9%_11%_10%_11%_15%_5%] items-center">
        <div className="pl-6 pr-3 py-[18px]">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Matchup</span>
        </div>
        <div className="px-3 py-[18px] text-center">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Closes In</span>
        </div>
        <div className="px-3 py-3 text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase leading-[13px]">Market<br />Price</span>
        </div>
        <div className="px-3 py-3 text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase leading-[13px]">Model<br />Prob</span>
        </div>
        <div className="px-3 py-[18px] text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Edge</span>
        </div>
        <div className="px-3 py-[18px] text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">EV</span>
        </div>
        <div className="px-3 py-[18px] text-center">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Signal</span>
        </div>
        <div className="px-3 py-[18px] text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Confidence</span>
        </div>
        <div />
      </div>

      {/* Body — scrollable */}
      <div className="flex-1 overflow-y-auto">
      {error ? (
        <div className="px-6 py-8 text-center text-[#ef4444] text-xs font-mono">{error}</div>
      ) : loading ? (
        Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} idx={i} />)
      ) : markets.length === 0 ? (
        <div className="px-6 py-8 text-center text-[#64748b] text-xs font-mono">No markets found</div>
      ) : (
        markets.map((market, idx) => (
          <div
            key={market.ticker}
            onClick={() => onSelect?.(market.ticker)}
            className={`grid grid-cols-[16%_14%_9%_9%_11%_10%_11%_15%_5%] items-center py-4 transition-colors cursor-pointer ${
              idx > 0 ? "border-t border-[#27272a]" : ""
            } ${selectedTicker === market.ticker ? "bg-[#27272a]/50" : "hover:bg-[#27272a]/30"}`}
          >
            {/* Matchup */}
            <div className="pl-6 pr-3 flex items-center gap-3">
              <div className="flex items-center gap-1">
                <div className="w-1.5 h-6 rounded-full" style={{ backgroundColor: market.team1Color }} />
                <div className="w-1.5 h-6 rounded-full" style={{ backgroundColor: market.team2Color }} />
              </div>
              <div>
                <p className="text-white text-sm font-semibold leading-5">
                  {market.team1} vs.<br />{market.team2}
                </p>
                <p className="text-[#64748b] text-[10px] font-mono leading-[13px] mt-0.5">
                  {market.league} &bull; {market.type}
                </p>
              </div>
            </div>

            {/* Closes In */}
            <div className="px-3 flex justify-center">
              <div
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-[10px] font-mono ${
                  market.closingUrgent
                    ? "bg-[rgba(124,45,18,0.1)] border border-[rgba(124,45,18,0.2)] text-[#fb923c]"
                    : "bg-[#1e293b] border border-[#27272a] text-[#94a3b8]"
                }`}
              >
                <ClockIcon />
                <span>{market.closesIn}</span>
              </div>
            </div>

            {/* Market Price */}
            <div className="px-3 text-right">
              <span className="text-[#94a3b8] text-sm font-mono">{market.marketPrice}</span>
            </div>

            {/* Model Prob */}
            <div className="px-3 text-right">
              <span className="text-white text-sm font-mono font-bold">{market.modelProb}</span>
            </div>

            {/* Edge */}
            <div className="px-3 flex items-center justify-end gap-1">
              <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
                {market.edgePositive ? (
                  <path d="M4 0L8 8H0L4 0Z" fill="#10b981" />
                ) : (
                  <path d="M4 8L0 0H8L4 8Z" fill="#ef4444" />
                )}
              </svg>
              <span className={`text-sm font-mono font-medium ${market.edgePositive ? "text-[#10b981]" : "text-[#ef4444]"}`}>
                {market.edge}
              </span>
            </div>

            {/* EV */}
            <div className="px-3 text-right">
              <span className={`text-sm font-mono font-medium ${market.evPositive ? "text-[#10b981]" : "text-[#ef4444]"}`}>
                {market.ev}
              </span>
            </div>

            {/* Signal */}
            <div className="px-3 flex justify-center">
              {market.signal === "YES" ? (
                <span className="bg-[#022c22] border border-[rgba(6,78,59,0.5)] text-[#34d399] text-[10px] font-bold tracking-[0.5px] uppercase px-3 py-1 rounded-full">
                  Yes
                </span>
              ) : (
                <span className="bg-[#450a0a] border border-[rgba(127,29,29,0.5)] text-[#f87171] text-[10px] font-bold tracking-[0.5px] uppercase px-3 py-1 rounded-full">
                  No
                </span>
              )}
            </div>

            {/* Confidence */}
            <div className="px-3 flex flex-col items-end gap-1">
              <div className="w-24 h-1.5 bg-[#27272a] rounded-full overflow-hidden">
                <div
                  className={`h-full ${market.confidence === "High" ? "bg-[#10b981]" : "bg-[#f59e0b]"}`}
                  style={{ width: `${market.confidencePercent}%` }}
                />
              </div>
              <span className="text-[#64748b] text-[9px] font-mono uppercase">{market.confidence}</span>
            </div>

            {/* More */}
            <div className="flex justify-center">
              <button className="text-[#64748b] hover:text-white transition-colors p-1" onClick={(e) => e.stopPropagation()}>
                <svg width="3" height="12" viewBox="0 0 3 12" fill="currentColor">
                  <circle cx="1.5" cy="1.5" r="1.5" />
                  <circle cx="1.5" cy="6" r="1.5" />
                  <circle cx="1.5" cy="10.5" r="1.5" />
                </svg>
              </button>
            </div>
          </div>
        ))
      )}

      </div>

      {/* Pagination */}
      <div className="border-t border-[#27272a] flex items-center justify-between px-6 py-3 bg-[#18181b] shrink-0">
        <span className="text-[#64748b] text-[10px] font-mono uppercase">
          {total === 0 ? "0 ENTRIES" : `${start}-${end} / ${total} ENTRIES`}
        </span>
        {onPageChange && totalPages > 1 && (
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              className="bg-[#09090b] border border-[#27272a] text-[#94a3b8] text-[10px] font-bold tracking-[0.25px] uppercase px-2.5 py-1 rounded-sm hover:bg-[#27272a] transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Prev
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter((p) => p === 1 || p === totalPages || Math.abs(p - page) <= 1)
              .reduce<(number | "…")[]>((acc, p, i, arr) => {
                if (i > 0 && p - (arr[i - 1] as number) > 1) acc.push("…");
                acc.push(p);
                return acc;
              }, [])
              .map((p, i) =>
                p === "…" ? (
                  <span key={`ellipsis-${i}`} className="text-[#64748b] text-[10px] px-1">…</span>
                ) : (
                  <button
                    key={p}
                    onClick={() => onPageChange(p as number)}
                    className={`text-[10px] font-mono font-bold px-2.5 py-1 rounded-sm border transition-colors ${
                      page === p
                        ? "bg-[#f1f5f9] border-[#f1f5f9] text-[#09090b]"
                        : "bg-[#09090b] border-[#27272a] text-[#94a3b8] hover:bg-[#27272a]"
                    }`}
                  >
                    {p}
                  </button>
                )
              )}
            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              className="bg-[#09090b] border border-[#27272a] text-[#94a3b8] text-[10px] font-bold tracking-[0.25px] uppercase px-2.5 py-1 rounded-sm hover:bg-[#27272a] transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
