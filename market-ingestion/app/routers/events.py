import os

from fastapi import APIRouter, Query
import httpx

router = APIRouter(prefix="/events", tags=["events"])

KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
KALSHI_SERIES = os.environ.get("KALSHI_SERIES", "")


@router.get("")
async def list_events(
    limit: int | None = Query(None, ge=1, description="Results per page"),
    cursor: str | None = Query(None, description="Pagination cursor"),
    status: str | None = Query(None, description="open, closed, or settled"),
    series_ticker: str | None = Query(None, description="Filter by series ticker"),
    with_nested_markets: bool | None = Query(None, description="Include nested market data"),
    with_milestones: bool | None = Query(None, description="Include milestones"),
    min_close_ts: int | None = Query(None, description="Events closing after this Unix timestamp"),
):
    params = _strip_none({
        "limit": limit,
        "cursor": cursor,
        "status": status,
        "series_ticker": series_ticker or KALSHI_SERIES or None,
        "with_nested_markets": with_nested_markets,
        "with_milestones": with_milestones,
        "min_close_ts": min_close_ts,
    })
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/events", params=params)
        resp.raise_for_status()
        return resp.json()


@router.get("/multivariate")
async def list_multivariate_events(
    limit: int | None = Query(None, ge=1, description="Results per page"),
    cursor: str | None = Query(None, description="Pagination cursor"),
    series_ticker: str | None = Query(None, description="Filter by series"),
    collection_ticker: str | None = Query(None, description="Filter by collection"),
    with_nested_markets: bool | None = Query(None, description="Include nested market data"),
):
    params = _strip_none({
        "limit": limit,
        "cursor": cursor,
        "series_ticker": series_ticker or KALSHI_SERIES or None,
        "collection_ticker": collection_ticker,
        "with_nested_markets": with_nested_markets,
    })
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/events/multivariate", params=params)
        resp.raise_for_status()
        return resp.json()


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
    return {k: v for k, v in d.items() if v is not None}
