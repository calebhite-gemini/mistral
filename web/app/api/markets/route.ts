import { NextRequest, NextResponse } from "next/server";
import { getKalshiMarkets } from "@/lib/api/kalshi";
import { getEdge } from "@/lib/api/edge";
import { toMarketRow } from "@/lib/transform/toMarketRow";
import type { KalshiMarket } from "@/lib/api/kalshi";

// Fetch single-game markets from each major sports series in parallel
const SPORTS_SERIES = [
  "KXNBAGAME", "KXNBASPREAD", "KXNBATOTAL",
  "KXNFLGAME", "KXNFLSPREAD", "KXNFLTOTAL",
  "KXNHLGAME", "KXMLBGAME",
  "KXNCAABGAME", "KXNCAAFGAME",
  "KXEPLGAME", "KXUFC",
];

async function fetchAllSportsMarkets(seriesTicker?: string): Promise<KalshiMarket[]> {
  if (seriesTicker) {
    const data = await getKalshiMarkets({ status: "open", limit: 50, series_ticker: seriesTicker });
    return data.markets ?? [];
  }

  const results = await Promise.allSettled(
    SPORTS_SERIES.map((s) => getKalshiMarkets({ status: "open", limit: 20, series_ticker: s }))
  );

  const all: KalshiMarket[] = [];
  for (const r of results) {
    if (r.status === "fulfilled") all.push(...(r.value.markets ?? []));
  }

  // Sort by volume descending so highest-volume markets appear first
  all.sort((a, b) => (b.volume_24h ?? 0) - (a.volume_24h ?? 0));

  // Deduplicate by event_ticker — keep first occurrence per game
  const seen = new Set<string>();
  return all.filter((m) => {
    const key = m.event_ticker ?? m.ticker;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl;
    const seriesTicker = searchParams.get("series_ticker") ?? undefined;

    const markets = await fetchAllSportsMarkets(seriesTicker);

    const rows = await Promise.allSettled(
      markets.map(async (market) => {
        try {
          const edge = await getEdge(50, market.last_price / 100);
          return toMarketRow(market, edge);
        } catch {
          return toMarketRow(market, { signal: "NO EDGE", edge: 0, ev: 0, kelly_fraction: 0 });
        }
      })
    );

    const result = rows
      .filter((r): r is PromiseFulfilledResult<ReturnType<typeof toMarketRow>> => r.status === "fulfilled")
      .map((r) => r.value);

    return NextResponse.json({ markets: result, total: result.length });
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 502 });
  }
}
