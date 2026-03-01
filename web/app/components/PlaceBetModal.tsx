"use client";

import { useState } from "react";

interface PlaceBetModalProps {
  ticker: string;
  title: string;
  lastPrice: number; // 0-99 cents
  onClose: () => void;
}

type Side = "yes" | "no";
type OrderType = "market" | "limit";
type Status = "idle" | "loading" | "success" | "error";

export default function PlaceBetModal({ ticker, title, lastPrice, onClose }: PlaceBetModalProps) {
  const [side, setSide] = useState<Side>("yes");
  const [orderType, setOrderType] = useState<OrderType>("market");
  const [contracts, setContracts] = useState(1);
  const [limitPrice, setLimitPrice] = useState(lastPrice || 50);
  const [status, setStatus] = useState<Status>("idle");
  const [errorMsg, setErrorMsg] = useState("");

  const price = orderType === "limit" ? limitPrice : (side === "yes" ? lastPrice : 100 - lastPrice);
  const totalCost = ((price / 100) * contracts).toFixed(2);
  const maxGain = (((100 - price) / 100) * contracts).toFixed(2);

  async function handleSubmit() {
    setStatus("loading");
    setErrorMsg("");
    try {
      const body: Record<string, unknown> = { ticker, side, type: orderType, count: contracts };
      if (orderType === "limit") body.yes_price = side === "yes" ? limitPrice : 100 - limitPrice;
      const res = await fetch("/api/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const raw = data.error ?? "";
        // Parse nested Kalshi error JSON if present
        let msg = raw;
        try {
          const inner = JSON.parse(raw.replace(/^[^{]*/, ""));
          msg = inner?.error?.message ?? inner?.detail ?? raw;
        } catch { /* not JSON */ }
        if (res.status === 401) msg = "Order rejected by Kalshi: API key lacks trading permissions. Enable trading access in your Kalshi account settings.";
        throw new Error(msg || `HTTP ${res.status}`);
      }
      setStatus("success");
    } catch (e) {
      setStatus("error");
      setErrorMsg(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/70 z-60"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-70 w-[420px] rounded-sm border flex flex-col"
        style={{ background: "#0c0c0e", borderColor: "#27272a" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b" style={{ borderColor: "#27272a" }}>
          <div>
            <p className="text-white text-sm font-bold">{title}</p>
            <p className="text-[#64748b] text-[10px] font-mono mt-0.5">{ticker}</p>
          </div>
          <button onClick={onClose} className="text-[#64748b] hover:text-white transition-colors">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {status === "success" ? (
          <div className="flex flex-col items-center gap-4 px-5 py-10">
            <div className="w-12 h-12 rounded-full bg-[#022c22] border border-[rgba(6,78,59,0.5)] flex items-center justify-center">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <p className="text-white text-sm font-bold">Order Placed</p>
            <p className="text-[#64748b] text-xs text-center font-mono">
              {contracts} contract{contracts !== 1 ? "s" : ""} on {side.toUpperCase()} at {price}¢ each
            </p>
            <button
              onClick={onClose}
              className="mt-2 w-full border border-[#27272a] text-white text-xs font-bold tracking-[0.5px] uppercase py-2.5 rounded-sm hover:bg-[#27272a]/50 transition-colors"
            >
              Close
            </button>
          </div>
        ) : (
          <div className="px-5 py-5 flex flex-col gap-5">
            {/* Side */}
            <div>
              <p className="text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase mb-2">Side</p>
              <div className="grid grid-cols-2 gap-2">
                {(["yes", "no"] as Side[]).map((s) => (
                  <button
                    key={s}
                    onClick={() => setSide(s)}
                    className="py-2.5 rounded-sm border text-xs font-bold tracking-[0.5px] uppercase transition-colors"
                    style={
                      side === s
                        ? s === "yes"
                          ? { background: "#022c22", borderColor: "rgba(6,78,59,0.5)", color: "#34d399" }
                          : { background: "#450a0a", borderColor: "rgba(127,29,29,0.5)", color: "#f87171" }
                        : { background: "transparent", borderColor: "#27272a", color: "#64748b" }
                    }
                  >
                    {s === "yes" ? "YES" : "NO"}
                  </button>
                ))}
              </div>
            </div>

            {/* Order type */}
            <div>
              <p className="text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase mb-2">Order Type</p>
              <div className="grid grid-cols-2 gap-2">
                {(["market", "limit"] as OrderType[]).map((t) => (
                  <button
                    key={t}
                    onClick={() => setOrderType(t)}
                    className="py-2.5 rounded-sm border text-xs font-bold tracking-[0.5px] uppercase transition-colors"
                    style={
                      orderType === t
                        ? { background: "#18181b", borderColor: "#e2e8f0", color: "#ffffff" }
                        : { background: "transparent", borderColor: "#27272a", color: "#64748b" }
                    }
                  >
                    {t.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* Limit price */}
            {orderType === "limit" && (
              <div>
                <p className="text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase mb-2">
                  Limit Price (¢) &nbsp;<span className="normal-case font-normal">Current: {lastPrice}¢</span>
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min={1}
                    max={99}
                    value={limitPrice}
                    onChange={(e) => setLimitPrice(Number(e.target.value))}
                    className="flex-1 accent-white"
                  />
                  <div className="w-16 bg-[#18181b] border border-[#27272a] rounded-sm px-2 py-1.5 text-white text-sm font-mono text-center">
                    {limitPrice}¢
                  </div>
                </div>
              </div>
            )}

            {/* Contracts */}
            <div>
              <p className="text-[#64748b] text-[10px] font-mono font-bold tracking-[0.5px] uppercase mb-2">Contracts</p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setContracts((c) => Math.max(1, c - 1))}
                  className="w-9 h-9 rounded-sm border border-[#27272a] text-white text-lg font-bold hover:bg-[#27272a]/50 transition-colors flex items-center justify-center"
                >
                  −
                </button>
                <input
                  type="number"
                  min={1}
                  value={contracts}
                  onChange={(e) => setContracts(Math.max(1, parseInt(e.target.value) || 1))}
                  className="flex-1 bg-[#18181b] border border-[#27272a] rounded-sm px-3 py-2 text-white text-sm font-mono text-center outline-none"
                />
                <button
                  onClick={() => setContracts((c) => c + 1)}
                  className="w-9 h-9 rounded-sm border border-[#27272a] text-white text-lg font-bold hover:bg-[#27272a]/50 transition-colors flex items-center justify-center"
                >
                  +
                </button>
              </div>
            </div>

            {/* Order summary */}
            <div className="rounded-sm border p-4 space-y-2" style={{ background: "#18181b", borderColor: "#27272a" }}>
              <div className="flex justify-between text-xs font-mono">
                <span style={{ color: "#64748b" }}>Price per contract</span>
                <span className="text-white">{price}¢</span>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span style={{ color: "#64748b" }}>Total cost</span>
                <span className="text-white">${totalCost}</span>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span style={{ color: "#64748b" }}>Max gain</span>
                <span style={{ color: "#34d399" }}>${maxGain}</span>
              </div>
            </div>

            {status === "error" && (
              <p className="text-[#f87171] text-xs font-mono">{errorMsg}</p>
            )}

            {/* Submit */}
            <button
              onClick={handleSubmit}
              disabled={status === "loading"}
              className="w-full bg-white text-[#09090b] text-xs font-bold tracking-[0.5px] uppercase py-3 rounded-sm hover:bg-[#e2e8f0] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {status === "loading" ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-[#09090b]/30 border-t-[#09090b] rounded-full animate-spin" />
                  Placing...
                </>
              ) : (
                `Place ${side.toUpperCase()} Order`
              )}
            </button>
          </div>
        )}
      </div>
    </>
  );
}
