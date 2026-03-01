import { edgeFetch } from "./clients";

export interface EdgeResult {
  signal: "BUY YES" | "BUY NO" | "NO EDGE";
  edge: number;
  ev: number;
  kelly_fraction: number;
}

export async function getEdge(
  modelProb: number,       // int 0-100
  marketYesPrice: number   // float 0.0-1.0
): Promise<EdgeResult> {
  return edgeFetch("/edge", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model_prob: modelProb, market_yes_price: marketYesPrice }),
  });
}
