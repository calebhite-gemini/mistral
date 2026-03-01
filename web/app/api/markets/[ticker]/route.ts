import { NextRequest, NextResponse } from "next/server";
import { getKalshiMarket } from "@/lib/api/kalshi";
import { toMarketDetail } from "@/lib/transform/toMarketDetail";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ ticker: string }> }
) {
  try {
    const { ticker } = await params;
    const data = await getKalshiMarket(ticker);
    const market = data.market ?? data;
    const detail = toMarketDetail(market);
    return NextResponse.json(detail);
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 502 });
  }
}
