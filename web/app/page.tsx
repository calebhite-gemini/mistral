import Sidebar from "./components/Sidebar";
import StatsCards from "./components/StatsCards";
import MarketsView from "./MarketsView";
import { getKalshiSummary } from "@/lib/api/kalshi";
import type { MarketSummary } from "@/lib/api/kalshi";

async function fetchStats(): Promise<MarketSummary | null> {
  try {
    return await getKalshiSummary();
  } catch {
    return null;
  }
}

export default async function Home() {
  const stats = await fetchStats();

  return (
    <div className="flex h-screen bg-[#09090b] overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="bg-[#09090b] border-b border-[#27272a] flex items-center justify-between px-6 py-4 shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-white text-lg font-bold tracking-[-0.45px] uppercase">Live Markets</h1>
            <span className="bg-[rgba(16,185,129,0.1)] border border-[rgba(16,185,129,0.2)] text-[#10b981] text-[10px] font-mono px-2.5 py-0.5 rounded-sm">
              {stats ? "CONNECTED" : "OFFLINE"}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button className="relative p-2 text-[#94a3b8] hover:text-white transition-colors">
              <svg width="14" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-[#ef4444] rounded-full" />
            </button>
          </div>
        </header>

        {/* Stats cards — fixed, doesn't scroll */}
        <div className="px-6 pt-6 pb-0 shrink-0">
          <StatsCards
            volume24h={stats?.volume_24h}
            activeMarkets={stats?.active_markets}
            openInterest={stats?.open_interest}
            sentiment={stats?.sentiment}
            loading={!stats}
          />
        </div>

        {/* Markets — takes remaining height and scrolls internally */}
        <div className="flex-1 flex flex-col min-h-0 px-6 pb-6 pt-6">
          <MarketsView />
        </div>
      </main>
    </div>
  );
}
