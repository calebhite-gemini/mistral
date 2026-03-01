"use client";

import { useEffect, useState } from "react";
import StatsCards from "./StatsCards";
import type { MarketSummary } from "@/lib/api/kalshi";

export default function StatsCardsLoader() {
  const [stats, setStats] = useState<MarketSummary | null>(null);

  useEffect(() => {
    fetch("/api/stats")
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});
  }, []);

  return (
    <StatsCards
      volume24h={stats?.volume_24h}
      activeMarkets={stats?.active_markets}
      openInterest={stats?.open_interest}
      sentiment={stats?.sentiment}
      loading={!stats}
    />
  );
}
