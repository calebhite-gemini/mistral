import type { KalshiMarket } from "../api/kalshi";
import type { PredictionOutput, ResearchBrief, SourceRef } from "../api/prediction";
import type { EdgeResult } from "../api/edge";
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
  marketOdds: string;
  oddsBest: string;
  volume: string;
  volumeTag: string;
  volumePublic: string;
  sharpMoney: string;
  sharpOn: string;
  modelProb: string;
  confidence: string;
  edge: string;
  ev: string;
  signal: string;
  reasoning: string;
  drivers: {
    tag: string;
    tagColor: string;
    title: string;
    description: string;
    source: string;
    sourceIcon: string;
    sourceColor: string;
    sourceUrl?: string;
    time: string;
  }[];
  sources?: SourceRef[];
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

// ── Driver tag classification ─────────────────────────────────────────────────

const TAG_CONFIG: { pattern: RegExp; tag: string; color: string }[] = [
  { pattern: /injur|out|questionable|day-to-day|doubtful|surgery|soreness/i, tag: "INJURY", color: "#ef4444" },
  { pattern: /back-to-back|rest|fatigue|schedule|b2b/i, tag: "REST", color: "#f59e0b" },
  { pattern: /record|win|loss|form|streak|last \d/i, tag: "FORM", color: "#3b82f6" },
  { pattern: /home|away|road|venue|court/i, tag: "VENUE", color: "#8b5cf6" },
  { pattern: /head-to-head|matchup|h2h|series/i, tag: "H2H", color: "#06b6d4" },
  { pattern: /trade|news|coach|roster|signing/i, tag: "NEWS", color: "#10b981" },
];

function classifyDriver(text: string): { tag: string; color: string } {
  for (const { pattern, tag, color } of TAG_CONFIG) {
    if (pattern.test(text)) return { tag, color };
  }
  return { tag: "INSIGHT", color: "#64748b" };
}

const TAG_TO_SOURCE_TYPE: Record<string, string[]> = {
  INJURY: ["espn_injury"],
  REST: ["espn_schedule"],
  FORM: ["espn_stats"],
  VENUE: ["espn_schedule", "espn_stats"],
  H2H: ["espn_h2h"],
  NEWS: ["tavily"],
  INSIGHT: ["tavily", "espn_stats"],
};

function matchSourceUrl(
  tag: string,
  driverText: string,
  sourceUrls: SourceRef[],
): SourceRef | undefined {
  if (!sourceUrls.length) return undefined;

  const preferredTypes = TAG_TO_SOURCE_TYPE[tag] ?? [];

  // First: try matching by source_type
  for (const st of preferredTypes) {
    const match = sourceUrls.find((s) => s.source_type === st);
    if (match) return match;
  }

  // Fallback: keyword overlap between driver text and source title
  const driverWords = driverText.toLowerCase().split(/\s+/);
  let bestMatch: SourceRef | undefined;
  let bestOverlap = 0;
  for (const src of sourceUrls) {
    const srcWords = src.title.toLowerCase().split(/\s+/);
    const overlap = driverWords.filter(
      (w) => w.length > 3 && srcWords.some((sw) => sw.includes(w))
    ).length;
    if (overlap > bestOverlap) {
      bestOverlap = overlap;
      bestMatch = src;
    }
  }
  return bestOverlap > 0 ? bestMatch : undefined;
}

function buildDrivers(
  prediction?: PredictionOutput,
  research?: ResearchBrief,
): MarketDetail["drivers"] {
  if (!prediction?.key_drivers?.length) return [];

  const now = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  const sourceUrls = research?.source_urls ?? [];

  return prediction.key_drivers.map((driver) => {
    const { tag, color } = classifyDriver(driver);
    // Use first sentence or first 60 chars as title
    const dotIdx = driver.indexOf(".");
    const title = dotIdx > 0 && dotIdx < 80 ? driver.slice(0, dotIdx) : driver.slice(0, 60);
    const description = driver;

    const matched = matchSourceUrl(tag, driver, sourceUrls);

    return {
      tag,
      tagColor: color,
      title: title.length < driver.length ? title : driver,
      description,
      source: matched?.title ?? "AI Research Agent",
      sourceIcon: matched ? "🔗" : "⚡",
      sourceColor: matched ? "#10b981" : "#3b82f6",
      sourceUrl: matched?.url,
      time: now,
    };
  });
}

// ── Main transform ────────────────────────────────────────────────────────────

export function toMarketDetail(
  market: KalshiMarket,
  prediction?: PredictionOutput,
  edgeResult?: EdgeResult,
  research?: ResearchBrief,
): MarketDetail {
  // Reuse toMarketRow just to get parsed team1/team2/league/type
  const row = toMarketRow(market, edgeResult ?? { signal: "NO EDGE", edge: 0, ev: 0, kelly_fraction: 0 });
  const [volume, volumeTag] = formatVolume(market.volume_24h ?? 0);

  const modelProb = prediction ? `${prediction.probability}%` : "—";
  const confidence = prediction
    ? prediction.confidence === "high" ? "High" : prediction.confidence === "medium" ? "Med" : "Low"
    : "—";
  const edge = edgeResult ? `${(edgeResult.edge * 100).toFixed(1)}%` : "—";
  const ev = edgeResult ? `${edgeResult.ev >= 0 ? "+" : ""}${(edgeResult.ev * 100).toFixed(1)}%` : "—";
  const signal = edgeResult
    ? edgeResult.signal === "BUY YES" ? "BUY YES" : edgeResult.signal === "BUY NO" ? "BUY NO" : "NO EDGE"
    : "—";

  return {
    ticker: market.ticker,
    lastPrice: market.last_price,
    team1: row.team1,
    team2: row.team2,
    team1Abbr: toAbbr(row.team1),
    team2Abbr: toAbbr(row.team2),
    league: row.league,
    type: row.type,
    gameDate: formatGameDate(market.expected_expiration_time ?? market.close_time),
    title: `${row.team1} ${row.type === "MONEYLINE" ? "Moneyline" : row.type === "SPREAD" ? "Spread" : "Total"}`,
    impliedProb: `${market.last_price.toFixed(1)}%`,
    marketOdds: lastPriceToAmericanOdds(market.last_price),
    oddsBest: "Kalshi",
    volume,
    volumeTag,
    volumePublic: "~50% Public",
    sharpMoney: "50%",
    sharpOn: `On ${row.team1}`,
    modelProb,
    confidence,
    edge,
    ev,
    signal,
    reasoning: prediction?.reasoning ?? "",
    drivers: buildDrivers(prediction, research),
    sources: research?.source_urls ?? [],
  };
}
