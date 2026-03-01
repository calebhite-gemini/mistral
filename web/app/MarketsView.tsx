"use client";

import { useState, useEffect, useMemo } from "react";
import SportFilters from "./components/SportFilters";
import MarketsTable from "./components/MarketsTable";
import MarketDetailPanel from "./components/MarketDetailPanel";
import type { MarketRow } from "@/lib/transform/toMarketRow";
import type { MarketDetail } from "@/lib/transform/toMarketDetail";

const SPORT_LEAGUE_MAP: Record<string, string[]> = {
  "All Sports": [],
  Football: ["NFL", "NCAAF"],
  Basketball: ["NBA", "NCAAB"],
  Soccer: ["EPL", "MLS", "UCL"],
  UFC: ["UFC", "MMA"],
};

export default function MarketsView() {
  const [activeSport, setActiveSport] = useState("All Sports");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);

  const PAGE_SIZE = 10;
  const [markets, setMarkets] = useState<MarketRow[]>([]);
  const [marketsLoading, setMarketsLoading] = useState(true);
  const [marketsError, setMarketsError] = useState<string | undefined>();

  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<MarketDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Load markets on mount and poll every 30s
  useEffect(() => {
    let cancelled = false;

    async function loadMarkets() {
      try {
        setMarketsLoading(true);
        setMarketsError(undefined);
        const res = await fetch("/api/markets");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) {
          setMarkets(data.markets ?? []);
        }
      } catch (err) {
        if (!cancelled) setMarketsError(String(err));
      } finally {
        if (!cancelled) setMarketsLoading(false);
      }
    }

    loadMarkets();
    const interval = setInterval(loadMarkets, 30_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  // Load detail when a row is selected
  useEffect(() => {
    if (!selectedTicker) {
      setSelectedDetail(null);
      return;
    }
    let cancelled = false;
    setDetailLoading(true);
    setSelectedDetail(null);
    fetch(`/api/markets/${selectedTicker}`)
      .then((r) => r.json())
      .then((data) => { if (!cancelled) setSelectedDetail(data); })
      .catch(() => { if (!cancelled) setDetailLoading(false); })
      .finally(() => { if (!cancelled) setDetailLoading(false); });
    return () => { cancelled = true; };
  }, [selectedTicker]);

  const filteredMarkets = useMemo(() => {
    const leagues = SPORT_LEAGUE_MAP[activeSport] ?? [];
    const q = searchQuery.trim().toLowerCase();
    return markets.filter((m) => {
      if (leagues.length > 0 && !leagues.includes(m.league)) return false;
      if (!q) return true;
      return (
        m.ticker.toLowerCase().includes(q) ||
        m.team1.toLowerCase().includes(q) ||
        m.team2.toLowerCase().includes(q) ||
        m.league.toLowerCase().includes(q)
      );
    });
  }, [markets, activeSport, searchQuery]);

  // Reset to page 1 whenever filters change
  useEffect(() => { setPage(1); }, [activeSport, searchQuery]);

  const pagedMarkets = useMemo(
    () => filteredMarkets.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    [filteredMarkets, page]
  );

  function handleSelect(ticker: string) {
    setSelectedTicker((prev) => (prev === ticker ? null : ticker));
  }

  function handleClose() {
    setSelectedTicker(null);
    setSelectedDetail(null);
  }

  return (
    <div className="flex flex-col min-h-0 h-full gap-4">
      <SportFilters active={activeSport} onSelect={setActiveSport} searchQuery={searchQuery} onSearch={setSearchQuery} />
      <MarketsTable
        markets={pagedMarkets}
        loading={marketsLoading}
        error={marketsError}
        selectedTicker={selectedTicker}
        onSelect={handleSelect}
        page={page}
        totalCount={filteredMarkets.length}
        onPageChange={setPage}
      />
      <MarketDetailPanel
        market={selectedDetail}
        loading={detailLoading}
        isOpen={selectedTicker !== null}
        onClose={handleClose}
      />
    </div>
  );
}
