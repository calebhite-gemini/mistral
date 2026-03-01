import { NextResponse } from "next/server";
import { getKalshiSummary } from "@/lib/api/kalshi";

export async function GET() {
  try {
    const summary = await getKalshiSummary();
    return NextResponse.json(summary);
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 502 });
  }
}
