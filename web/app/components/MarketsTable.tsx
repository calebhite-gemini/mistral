"use client";

interface MarketRow {
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

const markets: MarketRow[] = [
  {
    team1: "Lakers",
    team2: "Warriors",
    team1Color: "#552583",
    team2Color: "#1d428a",
    league: "NBA",
    type: "MONEYLINE",
    closesIn: "45:22",
    closingUrgent: true,
    marketPrice: "48.0%",
    modelProb: "56.0%",
    edge: "8.0%",
    edgePositive: true,
    ev: "+12.5%",
    evPositive: true,
    signal: "YES",
    confidence: "High",
    confidencePercent: 80,
  },
  {
    team1: "Chiefs",
    team2: "Bills",
    team1Color: "#e31837",
    team2Color: "#00338d",
    league: "NFL",
    type: "SPREAD",
    closesIn: "02:10:05",
    closingUrgent: false,
    marketPrice: "52.0%",
    modelProb: "45.0%",
    edge: "7.0%",
    edgePositive: false,
    ev: "-3.2%",
    evPositive: false,
    signal: "NO",
    confidence: "Med",
    confidencePercent: 40,
  },
  {
    team1: "Man City",
    team2: "Arsenal",
    team1Color: "#6cabdd",
    team2Color: "#ef0107",
    league: "PL",
    type: "TOTAL GOALS",
    closesIn: "04:00:00",
    closingUrgent: false,
    marketPrice: "30.0%",
    modelProb: "42.0%",
    edge: "12.0%",
    edgePositive: true,
    ev: "+15.4%",
    evPositive: true,
    signal: "YES",
    confidence: "High",
    confidencePercent: 100,
  },
  {
    team1: "Celtics",
    team2: "Heat",
    team1Color: "#007a33",
    team2Color: "#98002e",
    league: "NBA",
    type: "SPREAD",
    closesIn: "30:15",
    closingUrgent: true,
    marketPrice: "55.0%",
    modelProb: "51.0%",
    edge: "4.0%",
    edgePositive: false,
    ev: "-2.1%",
    evPositive: false,
    signal: "NO",
    confidence: "Med",
    confidencePercent: 60,
  },
];

function ClockIcon() {
  return (
    <svg width="10" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

export default function MarketsTable() {
  return (
    <div className="bg-[#18181b] border border-[#27272a] rounded-sm overflow-hidden">
      {/* Header */}
      <div className="bg-[#09090b] border-b border-[#27272a] grid grid-cols-[180px_140px_100px_100px_100px_100px_100px_1fr_50px] items-center">
        <div className="px-6 py-[18px]">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Matchup</span>
        </div>
        <div className="px-6 py-[18px] text-center">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Closes In</span>
        </div>
        <div className="px-6 py-3 text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase leading-[13px]">Market<br />Price</span>
        </div>
        <div className="px-6 py-3 text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase leading-[13px]">Model<br />Prob</span>
        </div>
        <div className="px-6 py-[18px] text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Edge</span>
        </div>
        <div className="px-6 py-[18px] text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">EV</span>
        </div>
        <div className="px-6 py-[18px] text-center">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Signal</span>
        </div>
        <div className="px-6 py-[18px] text-right">
          <span className="text-[#64748b] text-[10px] font-mono font-bold tracking-[1px] uppercase">Confidence</span>
        </div>
        <div />
      </div>

      {/* Body */}
      {markets.map((market, idx) => (
        <div
          key={idx}
          className={`grid grid-cols-[180px_140px_100px_100px_100px_100px_100px_1fr_50px] items-center py-4 hover:bg-[#27272a]/30 transition-colors ${
            idx > 0 ? "border-t border-[#27272a]" : ""
          }`}
        >
          {/* Matchup */}
          <div className="px-6 flex items-center gap-3">
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
          <div className="px-6 flex justify-center">
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
          <div className="px-6 text-right">
            <span className="text-[#94a3b8] text-sm font-mono">{market.marketPrice}</span>
          </div>

          {/* Model Prob */}
          <div className="px-6 text-right">
            <span className="text-white text-sm font-mono font-bold">{market.modelProb}</span>
          </div>

          {/* Edge */}
          <div className="px-6 flex items-center justify-end gap-1">
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
          <div className="px-6 text-right">
            <span className={`text-sm font-mono font-medium ${market.evPositive ? "text-[#10b981]" : "text-[#ef4444]"}`}>
              {market.ev}
            </span>
          </div>

          {/* Signal */}
          <div className="px-6 flex justify-center">
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
          <div className="px-6 flex flex-col items-end gap-1">
            <div className="w-24 h-1.5 bg-[#27272a] rounded-full overflow-hidden">
              <div
                className={`h-full ${
                  market.confidence === "High" ? "bg-[#10b981]" : "bg-[#f59e0b]"
                }`}
                style={{ width: `${market.confidencePercent}%` }}
              />
            </div>
            <span className="text-[#64748b] text-[9px] font-mono uppercase">{market.confidence}</span>
          </div>

          {/* More */}
          <div className="flex justify-center">
            <button className="text-[#64748b] hover:text-white transition-colors p-1">
              <svg width="3" height="12" viewBox="0 0 3 12" fill="currentColor">
                <circle cx="1.5" cy="1.5" r="1.5" />
                <circle cx="1.5" cy="6" r="1.5" />
                <circle cx="1.5" cy="10.5" r="1.5" />
              </svg>
            </button>
          </div>
        </div>
      ))}

      {/* Pagination */}
      <div className="border-t border-[#27272a] flex items-center justify-between px-6 py-3 bg-[#18181b]">
        <span className="text-[#64748b] text-[10px] font-mono uppercase">1-4 / 124 ENTRIES</span>
        <div className="flex items-center gap-2">
          <button className="bg-[#09090b] border border-[#27272a] text-[#94a3b8] text-[10px] font-bold tracking-[0.25px] uppercase px-2.5 py-1 rounded-sm hover:bg-[#27272a] transition-colors">
            Prev
          </button>
          <button className="bg-[#f1f5f9] border border-[#f1f5f9] text-[#09090b] text-[10px] font-mono font-bold px-2.5 py-1 rounded-sm">
            1
          </button>
          <button className="bg-[#09090b] border border-[#27272a] text-[#94a3b8] text-[10px] font-mono font-bold px-2.5 py-1 rounded-sm hover:bg-[#27272a] transition-colors">
            2
          </button>
          <button className="bg-[#09090b] border border-[#27272a] text-[#94a3b8] text-[10px] font-mono font-bold px-2.5 py-1 rounded-sm hover:bg-[#27272a] transition-colors">
            3
          </button>
          <span className="text-[#475569] text-[10px] font-mono px-2">...</span>
          <button className="bg-[#09090b] border border-[#27272a] text-[#94a3b8] text-[10px] font-bold tracking-[0.25px] uppercase px-2.5 py-1 rounded-sm hover:bg-[#27272a] transition-colors">
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
