import { NextRequest, NextResponse } from "next/server";
import { getKalshiMarket } from "@/lib/api/kalshi";
import { getEdge } from "@/lib/api/edge";
import { getPrediction } from "@/lib/api/prediction";
import type { ResearchBrief } from "@/lib/api/prediction";
import { toMarketDetail } from "@/lib/transform/toMarketDetail";
import { toMarketRow } from "@/lib/transform/toMarketRow";

export const dynamic = "force-dynamic";

const RESEARCH_URL = process.env.RESEARCH_URL ?? "http://localhost:8004";

// Re-use toMarketRow's team/league parsing to extract info for the research request.
function parseMarketMeta(market: Parameters<typeof toMarketRow>[0]) {
  const row = toMarketRow(market, { signal: "NO EDGE", edge: 0, ev: 0, kelly_fraction: 0 });
  return { team1: row.team1, team2: row.team2, league: row.league };
}

function toNickname(fullName: string): string {
  const parts = fullName.trim().split(/\s+/);
  return parts[parts.length - 1];
}

function toGameDate(closeTime: string): string {
  return new Date(closeTime).toISOString().slice(0, 10);
}

// ---------- Non-streaming path (original) ----------

async function handleJSON(ticker: string) {
  const data = await getKalshiMarket(ticker);
  const market = data.market ?? data;
  const { team1, team2, league } = parseMarketMeta(market);
  const gameDate = toGameDate(market.close_time);

  try {
    const researchRes = await fetch(`${RESEARCH_URL}/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        market_id: market.ticker,
        question: market.title,
        sport: league,
        teams: [toNickname(team1), toNickname(team2)],
        game_date: gameDate,
      }),
    });
    if (!researchRes.ok) throw new Error(`Research ${researchRes.status}`);
    const researchBrief: ResearchBrief = await researchRes.json();

    const prediction = await getPrediction({
      market: {
        market_id: market.ticker,
        question: market.title,
        yes_price: (market.last_price ?? 50) / 100,
        no_price: 1 - (market.last_price ?? 50) / 100,
        closes_at: market.close_time,
        sport: league,
        teams: [toNickname(team1), toNickname(team2)],
        game_date: gameDate,
        volume: market.volume ?? 0,
      },
      research_brief: researchBrief,
    });

    const edgeResult = await getEdge(prediction.probability, market.last_price / 100);
    return NextResponse.json(toMarketDetail(market, prediction, edgeResult, researchBrief));
  } catch {
    return NextResponse.json(toMarketDetail(market));
  }
}

// ---------- Streaming (SSE) path ----------

async function handleSSE(ticker: string) {
  const encoder = new TextEncoder();

  const readable = new ReadableStream({
    async start(controller) {
      function send(event: string, data: object) {
        controller.enqueue(
          encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`)
        );
      }

      try {
        // 1. Fetch Kalshi market (fast)
        const rawData = await getKalshiMarket(ticker);
        const market = rawData.market ?? rawData;
        const { team1, team2, league } = parseMarketMeta(market);
        const gameDate = toGameDate(market.close_time);

        // 2. Stream research phase via SSE proxy
        const researchReq = {
          market_id: market.ticker,
          question: market.title,
          sport: league,
          teams: [toNickname(team1), toNickname(team2)],
          game_date: gameDate,
        };

        const researchRes = await fetch(`${RESEARCH_URL}/research/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(researchReq),
        });

        if (!researchRes.ok || !researchRes.body) {
          throw new Error(`Research service failed: ${researchRes.status}`);
        }

        // Parse SSE from research service and forward to client
        let researchBrief: ResearchBrief | null = null;
        const reader = researchRes.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

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
              const parsed = JSON.parse(currentData);

              if (currentEvent === "research_complete") {
                researchBrief = parsed as ResearchBrief;
              } else if (currentEvent === "step") {
                send("step", parsed);
              } else if (currentEvent === "error") {
                send("error", parsed);
              }
              currentEvent = "";
              currentData = "";
            }
          }
        }

        if (!researchBrief) {
          throw new Error("Research service did not produce a result");
        }

        // 3. Prediction phase
        send("step", { phase: "prediction", label: "Generating AI prediction..." });

        const prediction = await getPrediction({
          market: {
            market_id: market.ticker,
            question: market.title,
            yes_price: (market.last_price ?? 50) / 100,
            no_price: 1 - (market.last_price ?? 50) / 100,
            closes_at: market.close_time,
            sport: league,
            teams: [toNickname(team1), toNickname(team2)],
            game_date: gameDate,
            volume: market.volume ?? 0,
          },
          research_brief: researchBrief,
        });

        // 4. Edge phase
        send("step", { phase: "edge", label: "Calculating edge..." });

        const edgeResult = await getEdge(prediction.probability, market.last_price / 100);

        // 5. Final result
        const detail = toMarketDetail(market, prediction, edgeResult, researchBrief);
        send("complete", detail);
      } catch (err) {
        send("error", { message: String(err) });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(readable, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string }> }
) {
  try {
    const { ticker } = await params;
    const stream = request.nextUrl.searchParams.get("stream") === "1";

    if (stream) {
      return handleSSE(ticker);
    }
    return handleJSON(ticker);
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 502 });
  }
}
