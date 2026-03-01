"use client";

import { useEffect, useState } from "react";
import StatsCards from "./StatsCards";

interface MarketStats {
  volume24h: number;
  gameCount: number;
}

export default function StatsCardsLoader() {
  const [stats, setStats] = useState<MarketStats | null>(null);

  useEffect(() => {
    fetch("/api/markets")
      .then((r) => r.json())
      .then((data) => {
        const markets = data.markets ?? [];
        setStats({
          gameCount: markets.length,
          volume24h: 0, // Volume comes from the summary endpoint
        });
      })
      .catch(() => {});

    // Also fetch volume from stats endpoint
    fetch("/api/stats")
      .then((r) => r.json())
      .then((summary) => {
        setStats((prev) => ({
          gameCount: prev?.gameCount ?? 0,
          volume24h: summary.volume_24h ?? 0,
        }));
      })
      .catch(() => {});
  }, []);

  return (
    <StatsCards
      volume={stats?.volume24h}
      activeMarkets={stats?.gameCount}
      loading={!stats}
    />
  );
}
