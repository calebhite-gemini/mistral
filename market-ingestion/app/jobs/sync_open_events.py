import asyncio
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from supabase import create_client  # noqa: E402

from app.routers.events import get_event  # noqa: E402


def get_supabase():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def get_unique_event_tickers(supabase) -> list[str]:
    """Get distinct event_tickers from the markets table."""
    result = (
        supabase.table("markets")
        .select("event_ticker")
        .execute()
    )
    return list({row["event_ticker"] for row in result.data if row.get("event_ticker")})


def preprocess_markets(markets: list[dict]) -> list[dict]:
    """Reduce nested markets to [{ticker, status}]."""
    return [{"ticker": m["ticker"], "status": m.get("status")} for m in markets]


def build_event_row(event: dict) -> dict:
    """Build a row for the events table from an API event response."""
    nested = event.get("markets") or []
    return {
        "event_ticker": event["event_ticker"],
        "series_ticker": event.get("series_ticker"),
        "title": event.get("title"),
        "sub_title": event.get("sub_title"),
        "collateral_return_type": event.get("collateral_return_type"),
        "mutually_exclusive": event.get("mutually_exclusive"),
        "available_on_brokers": event.get("available_on_brokers"),
        "product_metadata": event.get("product_metadata"),
        "strike_date": event.get("strike_date"),
        "strike_period": event.get("strike_period"),
        "last_updated_ts": event.get("last_updated_ts"),
        "markets": preprocess_markets(nested),
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }


def upsert_events(supabase, rows: list[dict]):
    """Upsert event rows to Supabase."""
    if rows:
        supabase.table("events").upsert(rows, on_conflict="event_ticker").execute()
        print(f"[sync-events] upserted {len(rows)} events")


async def sync_once():
    """Fetch events for all unique event_tickers in the markets table."""
    supabase = get_supabase()

    event_tickers = get_unique_event_tickers(supabase)
    print(f"[sync-events] found {len(event_tickers)} unique event_tickers in markets table")

    rows = []
    for ticker in event_tickers:
        try:
            data = await get_event(ticker, with_nested_markets=True)
            event = data.get("event", data)
            rows.append(build_event_row(event))
        except Exception as e:
            print(f"[sync-events] error fetching {ticker}: {e}")

    print(f"[sync-events] fetched {len(rows)} events")
    upsert_events(supabase, rows)
    print(f"[sync-events] done at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    asyncio.run(sync_once())
