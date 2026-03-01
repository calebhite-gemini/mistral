#!/usr/bin/env python3
"""
Backtesting script for the sports prediction pipeline.

Pulls resolved sports markets from Kalshi, runs research → prediction on each,
then computes accuracy, ROI, and Brier score. Generates a calibration chart.

Services needed (start before running):
    cd research-service  && uv run python main.py   # port 8004
    cd prediction-service && uv run python main.py  # port 8001

Usage:
    python backtest.py [--limit 50] [--output results.json] [--chart calibration.png]
    python backtest.py --skip-research --limit 100   # faster, skips research agent
    python backtest.py --from-file results.json      # re-compute metrics on saved data
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "kalshi-service" / ".env")

# ── Config ──────────────────────────────────────────────────────────────────

KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
RESEARCH_URL    = "http://localhost:8004"
PREDICTION_URL  = "http://localhost:8001"
EDGE_THRESHOLD  = 0.07   # matches edge-service

SPORT_MAP = {
    "KXNBA":   "NBA",   "KXNFL":  "NFL",
    "KXNHL":   "NHL",   "KXMLB":  "MLB",
    "KXNCAAB": "NCAAB", "KXNCAAF": "NCAAF",
    "KXEPL":   "EPL",   "KXMLS":  "MLS",
}


# ── Kalshi helpers ──────────────────────────────────────────────────────────

_MATCHUP_RE = re.compile(
    r"\bvs\.?\b|[ @]vs[ @]|\bbeat\b|\bbeat the\b|@ ",
    re.IGNORECASE,
)

def _is_game_matchup(market: dict) -> bool:
    """
    Return True only for individual game markets, not season-long futures.
    Futures look like "Will the Lakers win the NBA Finals?" — no opponent.
    Matchups contain "vs", "@", or "beat" in the title.
    """
    title = market.get("title", "") or market.get("subtitle", "")
    return bool(_MATCHUP_RE.search(title))


# Traditional team sports to try first — these have real pre-game prices and
# enough research data for the agent to work with.
_PREFERRED_SPORTS = {"NBA", "NFL", "NHL", "MLB", "NCAAB", "NCAAF", "EPL", "MLS"}

async def fetch_sports_series(client: httpx.AsyncClient) -> list[str]:
    """
    Discover all sports series tickers from Kalshi, returning traditional team
    sports (NBA/NFL/NHL/MLB/etc.) first so we don't burn through rate limits
    on esports or novelty series.
    """
    data = await _kalshi_get(client, "/series", {"category": "Sports", "limit": 200})
    if not data:
        return list(SPORT_MAP.keys())

    all_series = data.get("series", [])
    print(f"  Discovered {len(all_series)} sports series from Kalshi API")

    def _priority(s: dict) -> int:
        ticker = s.get("ticker", "")
        tags   = " ".join(s.get("tags") or [])
        title  = s.get("title", "")
        combined = (ticker + " " + tags + " " + title).upper()
        for sport in _PREFERRED_SPORTS:
            if sport in combined:
                return 0   # preferred
        return 1           # deprioritised (esports, novelty, etc.)

    sorted_series = sorted(all_series, key=_priority)
    # Only return the preferred sports; ignore esports/novelty to avoid rate limits
    preferred = [s for s in sorted_series if _priority(s) == 0]
    print(f"  Using {len(preferred)} preferred sports series (skipping {len(all_series) - len(preferred)} others)")
    return [s["ticker"] for s in preferred if s.get("ticker")]


async def _kalshi_get(client: httpx.AsyncClient, path: str, params: dict) -> dict | None:
    """GET with automatic retry on 429 rate-limit responses."""
    for attempt in range(4):
        resp = await client.get(f"{KALSHI_BASE_URL}{path}", params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            wait = 2 ** attempt  # 1s, 2s, 4s, 8s
            print(f"  [rate limit] 429 on {path} — waiting {wait}s…", flush=True)
            await asyncio.sleep(wait)
            continue
        print(f"  [warn] HTTP {resp.status_code} on {path} — skipping")
        return None
    print(f"  [warn] Gave up on {path} after 4 attempts")
    return None


async def fetch_resolved_markets(
    limit: int, debug: bool = False, no_filter: bool = False
) -> list[dict]:
    """
    Pull up to `limit` settled sports markets with YES/NO results.
    Discovers series dynamically from Kalshi's /series API.
    Pass no_filter=True to skip the game-matchup filter and take all binary markets.
    """
    collected: list[dict] = []
    sample_titles: list[str] = []

    async with httpx.AsyncClient(timeout=30) as client:
        series_list = await fetch_sports_series(client)
        await asyncio.sleep(1.0)

        for series in series_list:
            if len(collected) >= limit:
                break
            cursor: str | None = None
            scanned = 0
            series_matched = 0
            while len(collected) < limit and scanned < limit * 10:
                params: dict = {"status": "settled", "series_ticker": series, "limit": 200}
                if cursor:
                    params["cursor"] = cursor

                data = await _kalshi_get(client, "/markets", params)
                if data is None:
                    break

                page = data.get("markets", [])
                scanned += len(page)

                for m in page:
                    if len(sample_titles) < 20:
                        sample_titles.append(
                            f"[{series}] {m.get('title', '')} (result={m.get('result')})"
                        )
                    if m.get("result") in ("yes", "no"):
                        if no_filter or _is_game_matchup(m):
                            collected.append(m)
                            series_matched += 1
                            if len(collected) >= limit:
                                break

                cursor = data.get("cursor") or ""
                if not cursor or not page:
                    break
                await asyncio.sleep(1.0)

            if series_matched:
                print(f"  {series}: matched {series_matched} markets ({scanned} scanned)")

    if not collected:
        print(f"\n[debug] Scanned {len(sample_titles)} market titles, none matched.")
        print("  Sample titles:")
        for t in sample_titles[:20]:
            print(f"    • {t!r}")
        print("\n  → Try running with --no-filter to accept all settled binary markets.")

    return collected[:limit]


# ── Market field parsing ─────────────────────────────────────────────────────

def _presettlement_price(market: dict) -> float:
    """
    Best-effort pre-game market price from the settled market object.

    For settled markets, yes_bid/yes_ask reflect the payout (0 or 100 cents),
    not the trading price. We use `previous_yes_bid` when available — it's the
    bid one tick before the market settled, which is a reasonable proxy for the
    last traded price. Falls back to 0.50 (neutral).

    Note: for the calibration chart this value doesn't matter — only model_prob
    and outcome are used. This only affects the ROI/edge metrics.
    """
    # previous_yes_bid is captured one update before settlement
    for field in ("previous_yes_bid", "previous_price", "last_price"):
        raw = market.get(field)
        if raw is not None and isinstance(raw, (int, float)) and 0 < raw < 100:
            return raw / 100.0
    return 0.50


def _extract_teams(market: dict) -> list[str]:
    """Best-effort team extraction from market title/subtitle."""
    title = market.get("title", "") or market.get("subtitle", "")
    for pat in [
        r"([A-Z][A-Za-z.& ]+?) (?:vs\.?|@|-) ([A-Z][A-Za-z.& ]+?)(?:\s*[\|\(]|$)",
        r"\b([A-Z]{2,5})\b.*?\b(?:vs\.?|@)\b.*?\b([A-Z]{2,5})\b",
    ]:
        m = re.search(pat, title)
        if m:
            return [m.group(1).strip(), m.group(2).strip()]
    return []


def _detect_sport(market: dict) -> str:
    series = market.get("series_ticker", "")
    ticker = market.get("ticker", "")
    for key, sport in SPORT_MAP.items():
        if series.startswith(key) or ticker.startswith(key):
            return sport
    return "Sports"


def _game_date(market: dict) -> str:
    for field in ("close_time", "expiration_time", "end_date"):
        val = market.get(field)
        if val:
            return str(val)[:10]
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ── Pipeline ─────────────────────────────────────────────────────────────────

class _ResearchDown(Exception):
    """Raised when research-service is unreachable (ConnectError)."""

async def call_research(client: httpx.AsyncClient, market: dict) -> dict | None:
    """
    POST /research → research-service.
    Returns brief dict, or None if this specific market failed (500 etc.).
    Raises _ResearchDown if the service is not reachable at all.
    """
    teams = _extract_teams(market)
    if not teams:
        return None   # can't research a non-matchup market — skip silently

    payload = {
        "market_id": market["ticker"],
        "question":  market.get("title", ""),
        "sport":     _detect_sport(market),
        "teams":     teams,
        "game_date": _game_date(market),
    }
    try:
        resp = await client.post(f"{RESEARCH_URL}/research", json=payload, timeout=90)
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError:
        raise _ResearchDown()
    except Exception as exc:
        print(f"\n  [research err] {exc}")
        return None   # per-market failure — keep research enabled for next market


async def call_prediction(
    client: httpx.AsyncClient,
    market: dict,
    brief: dict | None,
    price: float = 0.50,
) -> int | None:
    """POST /predict → prediction-service. Returns model probability (0-100) or None."""
    if brief is None:
        brief = {
            "market_id":    market["ticker"],
            "key_factors":  [],
            "injury_flags": [],
            "rest_advantage": "Unknown — no research data available",
            "recent_form":    "Unknown — no research data available",
            "sources":        [],
        }
    payload = {
        "market": {
            "market_id":  market["ticker"],
            "question":   market.get("title", ""),
            "yes_price":  0.50,   # neutral — model should reason from research, not market price
            "no_price":   0.50,
            "closes_at":  market.get("close_time", ""),
            "sport":      _detect_sport(market),
            "teams":      _extract_teams(market),
            "game_date":  _game_date(market),
            "volume":     int(market.get("volume", 0) or 0),
        },
        "research_brief": brief,
    }
    try:
        resp = await client.post(f"{PREDICTION_URL}/predict", json=payload, timeout=45)
        if resp.status_code != 200:
            print(f"\n  [prediction err] HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        return resp.json().get("probability")
    except httpx.ConnectError:
        print(f"\n  [prediction err] cannot reach {PREDICTION_URL} — is prediction-service running?")
        raise   # re-raise so caller can detect service-down
    except Exception as exc:
        print(f"\n  [prediction err] {type(exc).__name__}: {exc}")
        return None


# ── Metrics ──────────────────────────────────────────────────────────────────

def compute_metrics(results: list[dict]) -> dict:
    valid = [r for r in results if r.get("model_prob") is not None]
    if not valid:
        return {"error": "no valid predictions"}

    # Accuracy at >60% confidence
    high_conf = [r for r in valid if r["model_prob"] > 60]
    if high_conf:
        correct = sum(
            1 for r in high_conf
            if (r["model_prob"] > 50) == (r["outcome"] == 1)
        )
        accuracy = correct / len(high_conf)
    else:
        accuracy = None

    # Simulated ROI: bet $1 on every edge (YES or NO)
    pnl = 0.0
    bets = 0
    for r in valid:
        p     = r["model_prob"] / 100.0
        price = r["market_price"]
        edge  = p - price
        if abs(edge) >= EDGE_THRESHOLD:
            bets += 1
            if edge > 0:                               # BUY YES
                pnl += (1 - price) if r["outcome"] == 1 else -price
            else:                                      # BUY NO
                no_price = 1 - price
                pnl += (1 - no_price) if r["outcome"] == 0 else -no_price

    roi = (pnl / bets) * 100 if bets > 0 else None    # % return per $1 risked

    # Brier score (lower = better calibration, 0 = perfect)
    brier = sum((r["model_prob"] / 100.0 - r["outcome"]) ** 2 for r in valid) / len(valid)

    return {
        "markets_evaluated":    len(results),
        "pipeline_successes":   len(valid),
        "high_conf_bets":       len(high_conf),
        "accuracy_pct":         round(accuracy * 100, 1) if accuracy is not None else "n/a",
        "edge_bets":            bets,
        "roi_per_bet_pct":      round(roi, 2) if roi is not None else "n/a",
        "total_pnl_dollars":    round(pnl, 2),
        "brier_score":          round(brier, 4),
        "note": (
            "Brier score: 0.25 = random, 0.0 = perfect. "
            "ROI > 0 means simulated profit betting flagged edges."
        ),
    }


# ── Calibration chart ────────────────────────────────────────────────────────

def plot_calibration(results: list[dict], output_path: str) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — skipping chart. Run: pip install matplotlib")
        return

    valid = [r for r in results if r.get("model_prob") is not None]
    if not valid:
        print("[chart] No valid predictions to plot.")
        return

    # Build 10 probability buckets (0-9%, 10-19%, …, 90-100%)
    buckets = [(i * 10, (i + 1) * 10) for i in range(10)]
    win_rates: list[float | None] = []
    counts:    list[int]          = []

    for lo, hi in buckets:
        subset = [r for r in valid if lo <= r["model_prob"] < hi]
        counts.append(len(subset))
        win_rates.append(
            sum(r["outcome"] for r in subset) / len(subset) if subset else None
        )

    BG     = "#1a1a2e"
    PANEL  = "#16213e"
    BLUE   = "#4a9eff"
    GRAY   = "#555555"
    WHITE  = "#e0e0e0"

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)

    x      = list(range(len(buckets)))
    colors = [BLUE if wr is not None else GRAY for wr in win_rates]
    ax.bar(x, [wr if wr is not None else 0 for wr in win_rates],
           color=colors, alpha=0.85, zorder=2)

    # Perfect calibration diagonal
    ideal = [(lo + 5) / 100 for lo, _ in buckets]
    ax.plot(x, ideal, "--", color=WHITE, linewidth=1.5, label="Perfect calibration", zorder=3)

    # Sample-size labels on bars
    for i, (wr, n) in enumerate(zip(win_rates, counts)):
        if n > 0:
            ax.text(i, (wr or 0) + 0.015, f"n={n}",
                    ha="center", va="bottom", color=WHITE, fontsize=8)

    labels = [f"{lo}–{hi}%" for lo, hi in buckets]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=40, ha="right", color=WHITE)
    ax.tick_params(colors=WHITE)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Actual win rate", color=WHITE, labelpad=8)
    ax.set_xlabel("Model probability bucket", color=WHITE, labelpad=8)
    ax.set_title("Calibration: Model Probability vs. Actual Win Rate", color=WHITE, fontsize=14, pad=12)
    ax.legend(facecolor=BG, labelcolor=WHITE, framealpha=0.8)
    for spine in ax.spines.values():
        spine.set_color(GRAY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRAY, linewidth=0.5, alpha=0.5, zorder=1)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=BG)
    plt.close()
    print(f"[chart] Saved → {output_path}")


# ── Main ─────────────────────────────────────────────────────────────────────

async def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest the sports prediction pipeline")
    parser.add_argument("--limit",         type=int, default=50,
                        help="Max resolved markets to process (default: 50)")
    parser.add_argument("--output",        default="results.json",
                        help="Where to save raw results JSON (default: results.json)")
    parser.add_argument("--chart",         default="calibration.png",
                        help="Where to save the calibration chart (default: calibration.png)")
    parser.add_argument("--skip-research", action="store_true",
                        help="Skip research agent (use empty brief) — faster but less accurate")
    parser.add_argument("--no-filter",     action="store_true",
                        help="Accept all settled binary markets, not just game matchups")
    parser.add_argument("--from-file",     metavar="PATH",
                        help="Skip data collection and compute metrics from an existing results.json")
    args = parser.parse_args()

    # ── Fast path: re-run metrics on saved data ──────────────────────────────
    if args.from_file:
        data = json.loads(Path(args.from_file).read_text())
        results = data if isinstance(data, list) else data.get("results", data)
        metrics = compute_metrics(results)
        print(json.dumps(metrics, indent=2))
        plot_calibration(results, args.chart)
        return

    # ── Step 1: Fetch resolved markets ───────────────────────────────────────
    print(f"[1/4] Fetching up to {args.limit} resolved sports markets from Kalshi…")
    markets = await fetch_resolved_markets(args.limit, debug=True, no_filter=args.no_filter)
    print(f"      Found {len(markets)} markets with recorded outcomes.\n")

    if not markets:
        sys.exit("No resolved markets found. Exiting.")

    # ── Step 2: Pipeline ─────────────────────────────────────────────────────
    research_available   = True
    prediction_available = True
    results: list[dict]  = []

    print(f"[2/4] Running pipeline ({'' if not args.skip_research else 'no '}research → prediction)…")
    async with httpx.AsyncClient(timeout=90) as client:
        for i, mkt in enumerate(markets, 1):
            ticker  = mkt.get("ticker", "?")
            outcome = 1 if mkt.get("result") == "yes" else 0
            price = _presettlement_price(mkt)

            print(f"  [{i:3}/{len(markets)}] {ticker:<32} price={price:.2f}  outcome={mkt.get('result')}",
                  end="  ", flush=True)

            # Research
            brief = None
            if not args.skip_research and research_available:
                try:
                    brief = await call_research(client, mkt)
                except _ResearchDown:
                    research_available = False
                    print("(research-service unreachable — disabling for run)", flush=True)

            # Prediction
            model_prob = None
            if prediction_available:
                try:
                    model_prob = await call_prediction(client, mkt, brief, price)
                except httpx.ConnectError:
                    prediction_available = False
                    print("prediction-service unreachable — aborting.", flush=True)
                    sys.exit(1)

            if model_prob is not None:
                edge = (model_prob / 100.0) - price
                print(f"model={model_prob:3d}%  edge={edge:+.3f}")
            else:
                print("prediction failed")

            results.append({
                "ticker":       ticker,
                "title":        mkt.get("title", ""),
                "sport":        _detect_sport(mkt),
                "game_date":    _game_date(mkt),
                "market_price": round(price, 4),
                "outcome":      outcome,
                "model_prob":   model_prob,
                "edge":         round((model_prob / 100.0) - price, 4) if model_prob is not None else None,
            })

            # Incremental save so a crash mid-run doesn't lose everything
            Path(args.output).write_text(json.dumps(results, indent=2))
            await asyncio.sleep(0.3)

    # ── Step 3: Metrics ───────────────────────────────────────────────────────
    print(f"\n[3/4] Metrics")
    metrics = compute_metrics(results)
    print(json.dumps(metrics, indent=2))

    # ── Step 4: Chart ─────────────────────────────────────────────────────────
    print(f"\n[4/4] Calibration chart → {args.chart}")
    plot_calibration(results, args.chart)

    print(f"\nDone. Raw results → {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
