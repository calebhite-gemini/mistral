"use client";

import { useState, useEffect, useMemo, useRef } from "react";
import SportFilters, { TIME_RANGES } from "./components/SportFilters";
import MarketsTable from "./components/MarketsTable";
import MarketDetailPanel from "./components/MarketDetailPanel";
import type { AgentStep } from "./components/MarketDetailPanel";
import type { MarketRow } from "@/lib/transform/toMarketRow";
import type { MarketDetail } from "@/lib/transform/toMarketDetail";

const SPORT_LEAGUE_MAP: Record<string, string[]> = {
  "All Sports": [],
  Football: ["NFL", "NCAAF"],
  Basketball: ["NBA", "NCAAB"],
  Hockey: ["NHL"],
  Soccer: ["EPL", "MLS", "UCL"],
  UFC: ["UFC", "MMA"],
};

export default function MarketsView() {
  const [activeSport, setActiveSport] = useState("All Sports");
  const [activeTimeRange, setActiveTimeRange] = useState("24 Hours");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);

  const PAGE_SIZE = 10;
  const [markets, setMarkets] = useState<MarketRow[]>([]);
  const [marketsLoading, setMarketsLoading] = useState(true);
  const [marketsError, setMarketsError] = useState<string | undefined>();

  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<MarketDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const detailCache = useRef<Map<string, MarketDetail>>(new Map());

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

  // Load detail when a row is selected (SSE streaming + cache)
  useEffect(() => {
    if (!selectedTicker) {
      setSelectedDetail(null);
      setAgentSteps([]);
      return;
    }

    // Check cache first
    const cached = detailCache.current.get(selectedTicker);
    if (cached) {
      setSelectedDetail(cached);
      setDetailLoading(false);
      setAgentSteps([]);
      return;
    }

    let cancelled = false;
    setDetailLoading(true);
    setSelectedDetail(null);
    setAgentSteps([]);

    const abortController = new AbortController();

    fetch(`/api/markets/${selectedTicker}?stream=1`, {
      signal: abortController.signal,
    })
      .then(async (res) => {
        if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done || cancelled) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          let currentEvent = "";
          let currentData = "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              currentEvent = line.slice(7);
            } else if (line.startsWith("data: ")) {
              currentData = line.slice(6);
            } else if (line === "" && currentEvent && currentData) {
              try {
                const parsed = JSON.parse(currentData);

                if (currentEvent === "step") {
                  if (!cancelled) {
                    setAgentSteps((prev) => {
                      const updated = prev.map((s) =>
                        s.status === "active" ? { ...s, status: "done" as const } : s
                      );
                      return [
                        ...updated,
                        {
                          phase: parsed.phase,
                          label: parsed.label,
                          tool: parsed.tool,
                          status: "active" as const,
                          timestamp: Date.now(),
                        },
                      ];
                    });
                  }
                } else if (currentEvent === "complete") {
                  if (!cancelled) {
                    detailCache.current.set(selectedTicker, parsed);
                    setSelectedDetail(parsed);
                    setAgentSteps((prev) =>
                      prev.map((s) => ({ ...s, status: "done" as const }))
                    );
                  }
                }
              } catch {
                // ignore malformed JSON
              }
              currentEvent = "";
              currentData = "";
            }
          }
        }
      })
      .catch((err) => {
        if (!cancelled && err.name !== "AbortError") {
          console.error("SSE fetch failed:", err);
        }
      })
      .finally(() => {
        if (!cancelled) setDetailLoading(false);
      });

    return () => {
      cancelled = true;
      abortController.abort();
    };
  }, [selectedTicker]);

  const filteredMarkets = useMemo(() => {
    const leagues = SPORT_LEAGUE_MAP[activeSport] ?? [];
    const q = searchQuery.trim().toLowerCase();

    // Hours-based cumulative cutoff
    const rangeHours = TIME_RANGES.find((r) => r.label === activeTimeRange)?.hours ?? 24;
    const cutoff = Date.now() + rangeHours * 3_600_000;

    return markets.filter((m) => {
      // Time range filter
      if (new Date(m.expiresAt).getTime() > cutoff) return false;

      // Sport filter
      if (leagues.length > 0 && !leagues.includes(m.league)) return false;

      // Search filter
      if (!q) return true;
      return (
        m.ticker.toLowerCase().includes(q) ||
        m.team1.toLowerCase().includes(q) ||
        m.team2.toLowerCase().includes(q) ||
        m.league.toLowerCase().includes(q)
      );
    });
  }, [markets, activeSport, activeTimeRange, searchQuery]);

  // Reset to page 1 whenever filters change
  useEffect(() => { setPage(1); }, [activeSport, activeTimeRange, searchQuery]);

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
      <SportFilters active={activeSport} onSelect={setActiveSport} searchQuery={searchQuery} onSearch={setSearchQuery} activeTimeRange={activeTimeRange} onTimeRangeSelect={setActiveTimeRange} />
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
        agentSteps={agentSteps}
      />
    </div>
  );
}
