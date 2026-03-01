import { kalshiFetch } from "./clients";

export interface KalshiMarket {
  ticker: string;
  title: string;
  subtitle?: string;
  series_ticker?: string;
  event_ticker?: string;
  status: string;
  last_price: number;
  yes_bid?: number;
  yes_ask?: number;
  no_bid?: number;
  no_ask?: number;
  volume: number;
  volume_24h: number;
  open_interest?: number;
  close_time: string;
  expected_expiration_time?: string;
  result?: string;
}

export interface KalshiMarketsResponse {
  markets: KalshiMarket[];
  cursor?: string;
}

export interface MarketSummary {
  volume_24h: number;
  active_markets: number;
  open_interest: number;
  sentiment: "BULLISH" | "BEARISH" | "NEUTRAL";
}

export async function getKalshiMarkets(params?: {
  status?: string;
  limit?: number;
  series_ticker?: string;
  cursor?: string;
  min_close_ts?: number;
  max_close_ts?: number;
}): Promise<KalshiMarketsResponse> {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.limit) qs.set("limit", String(params.limit));
  if (params?.series_ticker) qs.set("series_ticker", params.series_ticker);
  if (params?.cursor) qs.set("cursor", params.cursor);
  if (params?.min_close_ts) qs.set("min_close_ts", String(params.min_close_ts));
  if (params?.max_close_ts) qs.set("max_close_ts", String(params.max_close_ts));
  const query = qs.toString() ? `?${qs}` : "";
  return kalshiFetch(`/markets${query}`);
}

export async function getKalshiMarket(ticker: string): Promise<{ market: KalshiMarket }> {
  return kalshiFetch(`/markets/${ticker}`);
}

export async function getKalshiSummary(seriesTicker?: string): Promise<MarketSummary> {
  const query = seriesTicker ? `?series_ticker=${seriesTicker}` : "";
  return kalshiFetch(`/markets/summary${query}`);
}
