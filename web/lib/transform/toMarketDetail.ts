import type { KalshiMarket } from "../api/kalshi";
// Re-use the same parsing logic from toMarketRow
import { toMarketRow } from "./toMarketRow";

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

function toAbbr(name: string): string {
  const words = name.trim().split(/\s+/);
  if (words.length === 1) return name.slice(0, 3).toUpperCase();
  return words.map((w) => w[0]).join("").toUpperCase().slice(0, 4);
}

function formatGameDate(closeTime: string): string {
  const d = new Date(closeTime);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function formatVolume(v24h: number): [string, string] {
  if (v24h >= 1_000_000) return [`$${(v24h / 1_000_000).toFixed(1)}M`, "HIGH"];
  if (v24h >= 100_000) return [`$${(v24h / 1_000).toFixed(0)}K`, "MED"];
  return [`$${v24h.toLocaleString()}`, "LOW"];
}

function lastPriceToAmericanOdds(lastPrice: number): string {
  const p = lastPrice / 100;
  if (p <= 0 || p >= 1) return "N/A";
  if (p >= 0.5) return `${Math.round(-p / (1 - p) * 100)}`;
  return `+${Math.round((1 - p) / p * 100)}`;
}

export function toMarketDetail(market: KalshiMarket): MarketDetail {
  // Reuse toMarketRow just to get parsed team1/team2/league/type
  const row = toMarketRow(market, { signal: "NO EDGE", edge: 0, ev: 0, kelly_fraction: 0 });
  const [volume, volumeTag] = formatVolume(market.volume_24h ?? 0);

  return {
    ticker: market.ticker,
    lastPrice: market.last_price,
    team1: row.team1,
    team2: row.team2,
    team1Abbr: toAbbr(row.team1),
    team2Abbr: toAbbr(row.team2),
    league: row.league,
    type: row.type,
    gameDate: formatGameDate(market.close_time),
    title: `${row.team1} ${row.type === "MONEYLINE" ? "Moneyline" : row.type === "SPREAD" ? "Spread" : "Total"}`,
    impliedProb: `${market.last_price.toFixed(1)}%`,
    probChange: "+0.0%",
    marketOdds: lastPriceToAmericanOdds(market.last_price),
    oddsBest: "Kalshi",
    volume,
    volumeTag,
    volumePublic: "~50% Public",
    sharpMoney: "50%",
    sharpOn: `On ${row.team1}`,
    drivers: [],
  };
}
