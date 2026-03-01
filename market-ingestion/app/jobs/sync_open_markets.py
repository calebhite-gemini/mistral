import asyncio
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from supabase import create_client  # noqa: E402

from app.routers.markets import list_markets  # noqa: E402

SERIES_TICKERS = [
    "KXNBAGAME",
    "KXNFLGAME",
    "KXNCAAFGAME",
    "KXNCAAMBGAME",
]

SYNC_INTERVAL_SECONDS = 60 * 60 * 4  # 4 hours
TOP_N = 20


def get_supabase():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def get_last_updated_ts(supabase) -> int | None:
    """Get the most recent sync timestamp from last_updated table. Returns Unix ts or None."""
    result = (
        supabase.table("last_updated")
        .select("updated_at")
        .eq("job", "sync_open_markets")
        .order("updated_at", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        ts_str = result.data[0]["updated_at"]
        dt = datetime.fromisoformat(ts_str)
        return int(dt.timestamp())
    return None


def set_last_updated(supabase):
    """Upsert the current timestamp into last_updated table."""
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("last_updated").upsert(
        {"job": "sync_open_markets", "updated_at": now},
        on_conflict="job",
    ).execute()
    print(f"[sync-markets] updated last_updated to {now}")


async def fetch_open_markets(min_created_ts: int | None = None):
    """Fetch open markets for our target series, optionally filtering by creation time."""
    all_markets = []
    for series in SERIES_TICKERS:
        print(f"[sync-markets] fetching open markets for {series} (min_created_ts={min_created_ts})...")
        result = await list_markets(
            status="open",
            series_ticker=series,
            min_created_ts=min_created_ts,
        )
        markets = result.get("markets", [])
        # Tag each market with the series_ticker we queried
        for m in markets:
            m["series_ticker"] = series
        all_markets.extend(markets)
        print(f"[sync-markets] {series}: {len(markets)} open markets")
    return all_markets


def top_by_volume(markets, n=TOP_N):
    """Return the top N markets sorted by volume descending."""
    sorted_markets = sorted(markets, key=lambda m: m.get("volume", 0) or 0, reverse=True)
    return sorted_markets[:n]


def upsert_markets(supabase, markets):
    """Upsert top markets to Supabase."""
    now = datetime.now(timezone.utc).isoformat()

    rows = []
    for market in markets:
        rows.append({
            "ticker": market["ticker"],
            "series_ticker": market.get("series_ticker"),
            "event_ticker": market.get("event_ticker"),
            "market_type": market.get("market_type"),
            "yes_sub_title": market.get("yes_sub_title"),
            "no_sub_title": market.get("no_sub_title"),
            "status": market.get("status"),
            "result": market.get("result"),
            "created_time": market.get("created_time"),
            "updated_time": market.get("updated_time"),
            "open_time": market.get("open_time"),
            "close_time": market.get("close_time"),
            "latest_expiration_time": market.get("latest_expiration_time"),
            "expected_expiration_time": market.get("expected_expiration_time"),
            "settlement_timer_seconds": market.get("settlement_timer_seconds"),
            "yes_bid_dollars": market.get("yes_bid_dollars"),
            "yes_ask_dollars": market.get("yes_ask_dollars"),
            "yes_bid_size_fp": market.get("yes_bid_size_fp"),
            "yes_ask_size_fp": market.get("yes_ask_size_fp"),
            "no_bid_dollars": market.get("no_bid_dollars"),
            "no_ask_dollars": market.get("no_ask_dollars"),
            "last_price_dollars": market.get("last_price_dollars"),
            "previous_yes_bid_dollars": market.get("previous_yes_bid_dollars"),
            "previous_yes_ask_dollars": market.get("previous_yes_ask_dollars"),
            "previous_price_dollars": market.get("previous_price_dollars"),
            "notional_value_dollars": market.get("notional_value_dollars"),
            "volume": market.get("volume"),
            "volume_24h": market.get("volume_24h"),
            "open_interest": market.get("open_interest"),
            "can_close_early": market.get("can_close_early"),
            "fractional_trading_enabled": market.get("fractional_trading_enabled"),
            "data": market,
            "synced_at": now,
        })

    if rows:
        supabase.table("markets").upsert(rows, on_conflict="ticker").execute()
        print(f"[sync-markets] upserted {len(rows)} markets")


async def sync_once():
    """Run a single sync cycle."""
    supabase = get_supabase()

    last_ts = get_last_updated_ts(supabase)
    if last_ts is None:
        print("[sync-markets] no previous sync found, fetching all open markets")
    else:
        print(f"[sync-markets] last sync at {last_ts}, fetching markets created since then")

    markets = await fetch_open_markets(min_created_ts=last_ts)
    top = top_by_volume(markets)
    print(f"[sync-markets] {len(markets)} total open markets, upserting top {len(top)} by volume")

    upsert_markets(supabase, top)
    set_last_updated(supabase)

    print(f"[sync-markets] cycle complete at {datetime.now(timezone.utc).isoformat()}")


async def run_forever():
    """Run sync in a loop every 4 hours."""
    print(f"[sync-markets] starting periodic sync every {SYNC_INTERVAL_SECONDS}s")
    while True:
        try:
            await sync_once()
        except Exception as e:
            print(f"[sync-markets] error: {e}")
        await asyncio.sleep(SYNC_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(run_forever())
