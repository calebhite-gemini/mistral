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
  "KXEPLGAME", "KXMLSGAME", "KXUFC",
];

async function fetchAllSportsMarkets(seriesTicker?: string): Promise<KalshiMarket[]> {
  if (seriesTicker) {
    const data = await getKalshiMarkets({ status: "open", limit: 100, series_ticker: seriesTicker });
    return filterToUpcoming(data.markets ?? []);
  }

  const results = await Promise.allSettled(
    SPORTS_SERIES.map((s) =>
      getKalshiMarkets({ status: "open", limit: 100, series_ticker: s })
    )
  );

  const all: KalshiMarket[] = [];
  for (const r of results) {
    if (r.status === "fulfilled") all.push(...(r.value.markets ?? []));
  }

  // Sort by volume descending so highest-volume markets appear first
  all.sort((a, b) => (b.volume_24h ?? 0) - (a.volume_24h ?? 0));

  // Deduplicate by game (strip series prefix from event_ticker).
  // e.g. KXNBAGAME-26MAR01CLEBKN, KXNBASPREAD-26MAR01CLEBKN, KXNBATOTAL-26MAR01CLEBKN
  // all become "26MAR01CLEBKN" — keeping the first (highest-volume) per game.
  const seen = new Set<string>();
  const deduped = all.filter((m) => {
    const eventTicker = m.event_ticker ?? m.ticker;
    const dashIdx = eventTicker.indexOf("-");
    const gameKey = dashIdx >= 0 ? eventTicker.slice(dashIdx + 1) : eventTicker;
    if (seen.has(gameKey)) return false;
    seen.add(gameKey);
    return true;
  });

  return filterToUpcoming(deduped);
}

/** Keep only markets whose game/event expires within 7 days.
 *  Uses `expected_expiration_time` (actual game resolution) rather than
 *  `close_time` (market settlement, often 2 weeks later).
 *  Client-side filtering narrows to Today/Tomorrow/Week. */
function filterToUpcoming(markets: KalshiMarket[]): KalshiMarket[] {
  const now = Date.now();
  const in7d = now + 7 * 24 * 3_600_000;
  return markets.filter((m) => {
    const expiry = m.expected_expiration_time ?? m.close_time;
    const t = new Date(expiry).getTime();
    return t > now && t < in7d;
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
