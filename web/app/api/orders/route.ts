import { NextRequest, NextResponse } from "next/server";
import { kalshiFetch } from "@/lib/api/clients";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const result = await kalshiFetch("/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return NextResponse.json(result);
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 502 });
  }
}
