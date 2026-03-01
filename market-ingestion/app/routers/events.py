import asyncio

from fastapi import APIRouter, Query
import httpx

router = APIRouter(prefix="/events", tags=["events"])

KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
PAGE_DELAY_SECONDS = 5


@router.get("")
async def list_events(
    status: str | None = Query(None, description="open, closed, or settled"),
    series_ticker: str | None = Query(None, description="Filter by series ticker"),
    with_nested_markets: bool | None = Query(None, description="Include nested market data"),
    with_milestones: bool | None = Query(None, description="Include milestones"),
    min_close_ts: int | None = Query(None, description="Events closing after this Unix timestamp"),
):
    base_params = _strip_none({
        "limit": 200,
        "status": status,
        "series_ticker": series_ticker,
        "with_nested_markets": with_nested_markets,
        "with_milestones": with_milestones,
        "min_close_ts": min_close_ts,
    })

    all_events = []
    cursor = None
    page = 0

    async with httpx.AsyncClient() as client:
        while True:
            params = {**base_params}
            if cursor:
                params["cursor"] = cursor

            resp = await client.get(f"{KALSHI_BASE_URL}/events", params=params)
            resp.raise_for_status()
            data = resp.json()

            page_events = data.get("events", [])
            all_events.extend(page_events)
            cursor = data.get("cursor", "")
            page += 1
            print(f"[list_events] page {page}: fetched {len(page_events)} events (total: {len(all_events)})")

            if not cursor:
                break

            await asyncio.sleep(PAGE_DELAY_SECONDS)

    print(f"[list_events] done: {len(all_events)} events total across {page} pages")
    return {"events": all_events}


@router.get("/multivariate")
async def list_multivariate_events(
    series_ticker: str | None = Query(None, description="Filter by series"),
    collection_ticker: str | None = Query(None, description="Filter by collection"),
    with_nested_markets: bool | None = Query(None, description="Include nested market data"),
):
    base_params = _strip_none({
        "limit": 200,
        "series_ticker": series_ticker,
        "collection_ticker": collection_ticker,
        "with_nested_markets": with_nested_markets,
    })

    all_events = []
    cursor = None

    async with httpx.AsyncClient() as client:
        while True:
            params = {**base_params}
            if cursor:
                params["cursor"] = cursor

            resp = await client.get(f"{KALSHI_BASE_URL}/events/multivariate", params=params)
            resp.raise_for_status()
            data = resp.json()

            all_events.extend(data.get("events", []))
            cursor = data.get("cursor", "")

            if not cursor:
                break

            await asyncio.sleep(PAGE_DELAY_SECONDS)

    return {"events": all_events}


@router.get("/{event_ticker}")
async def get_event(
    event_ticker: str,
    with_nested_markets: bool | None = Query(None, description="Include nested market data"),
):
    params = _strip_none({
        "with_nested_markets": with_nested_markets,
    })
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/events/{event_ticker}", params=params)
        resp.raise_for_status()
        return resp.json()


def _strip_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if isinstance(v, (str, int, float, bool))}
