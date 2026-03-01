import asyncio
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from supabase import create_client  # noqa: E402

from app.routers.events import list_events  # noqa: E402

SERIES_TICKERS = [
    "KXNBAGAME",
    "KXNFLGAME",
    "KXNCAAFGAME",
    "KXNCAAMBGAME",
]

SYNC_INTERVAL_SECONDS = 60 * 5  # 5 minutes


def get_supabase():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


async def fetch_open_events():
    """Fetch all open events with nested markets for our target series."""
    all_events = []
    for series in SERIES_TICKERS:
        print(f"[sync] fetching open events for {series}...")
        result = await list_events(
            status="open",
            series_ticker=series,
            with_nested_markets=True,
        )
        events = result.get("events", [])
        all_events.extend(events)
        print(f"[sync] {series}: {len(events)} open events")
    return all_events


def upsert_events(supabase, events):
    """Upsert events and their nested markets to Supabase."""
    now = datetime.now(timezone.utc).isoformat()

    event_rows = []
    market_rows = []

    for event in events:
        markets = event.pop("markets", []) or []

        event_rows.append({
            "event_ticker": event["event_ticker"],
            "series_ticker": event.get("series_ticker"),
            "title": event.get("title"),
            "category": event.get("category"),
            "status": event.get("status"),
            "mutually_exclusive": event.get("mutually_exclusive"),
            "data": event,
            "synced_at": now,
        })

        for market in markets:
            market_rows.append({
                "ticker": market["ticker"],
                "event_ticker": market.get("event_ticker"),
                "market_type": market.get("market_type"),
                "title": market.get("title"),
                "subtitle": market.get("subtitle"),
                "status": market.get("status"),
                "result": market.get("result"),
                "yes_bid": market.get("yes_bid"),
                "yes_ask": market.get("yes_ask"),
                "no_bid": market.get("no_bid"),
                "no_ask": market.get("no_ask"),
                "last_price": market.get("last_price"),
                "volume": market.get("volume"),
                "open_interest": market.get("open_interest"),
                "close_time": market.get("close_time"),
                "data": market,
                "synced_at": now,
            })

    if event_rows:
        supabase.table("events").upsert(event_rows, on_conflict="event_ticker").execute()
        print(f"[sync] upserted {len(event_rows)} events")

    if market_rows:
        supabase.table("markets").upsert(market_rows, on_conflict="ticker").execute()
        print(f"[sync] upserted {len(market_rows)} markets")


async def sync_once():
    """Run a single sync cycle."""
    supabase = get_supabase()
    events = await fetch_open_events()
    upsert_events(supabase, events)
    print(f"[sync] cycle complete: {len(events)} events at {datetime.now(timezone.utc).isoformat()}")


async def run_forever():
    """Run sync in a loop."""
    print(f"[sync] starting periodic sync every {SYNC_INTERVAL_SECONDS}s")
    while True:
        try:
            await sync_once()
        except Exception as e:
            print(f"[sync] error: {e}")
        await asyncio.sleep(SYNC_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(run_forever())
