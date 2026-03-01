const KALSHI_URL = process.env.KALSHI_URL ?? "http://localhost:8003";
const EDGE_URL = process.env.EDGE_URL ?? "http://localhost:8002";
const PREDICTION_URL = process.env.PREDICTION_URL ?? "http://localhost:8001";

export async function kalshiFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${KALSHI_URL}${path}`, {
    ...init,
    next: { revalidate: 30 },
  });
  if (!res.ok) throw new Error(`Kalshi ${path} → ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function edgeFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${EDGE_URL}${path}`, {
    ...init,
    next: { revalidate: 0 },
  });
  if (!res.ok) throw new Error(`Edge ${path} → ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function predictionFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${PREDICTION_URL}${path}`, {
    ...init,
    next: { revalidate: 0 },
  });
  if (!res.ok) throw new Error(`Prediction ${path} → ${res.status}: ${await res.text()}`);
  return res.json();
}
