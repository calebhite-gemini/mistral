import asyncio

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.kalshi_client import kalshi_get
from app.services.summary import compute_summary

router = APIRouter(prefix="/markets", tags=["markets"])

# Same series the frontend table displays
_SPORTS_SERIES = [
    "KXNBAGAME", "KXNBASPREAD", "KXNBATOTAL",
    "KXNFLGAME", "KXNFLSPREAD", "KXNFLTOTAL",
    "KXNHLGAME", "KXMLBGAME",
    "KXNCAABGAME", "KXNCAAFGAME",
    "KXEPLGAME", "KXUFC",
]


@router.get("")
async def list_markets(
    limit: int | None = Query(None, ge=1, le=1000, description="Results per page"),
    cursor: str | None = Query(None, description="Pagination cursor"),
    status: str | None = Query(None, description="open, closed, or settled"),
    series_ticker: str | None = Query(None, description="Filter by series ticker"),
    min_close_ts: int | None = Query(None, description="Markets closing after this Unix timestamp"),
    max_close_ts: int | None = Query(None, description="Markets closing before this Unix timestamp"),
):
    try:
        return await kalshi_get("/markets", {
            "limit": limit,
            "cursor": cursor,
            "status": status,
            "series_ticker": series_ticker,
            "min_close_ts": min_close_ts,
            "max_close_ts": max_close_ts,
        })
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


# Declared before /{ticker} so FastAPI resolves it as a literal path
@router.get("/summary")
async def market_summary(
    series_ticker: str | None = Query(None, description="Filter by series ticker"),
):
    """Aggregated stats for the UI header cards."""
    try:
        if series_ticker:
            series_list = [series_ticker]
        else:
            series_list = _SPORTS_SERIES

        results = await asyncio.gather(
            *[
                kalshi_get("/markets", {"status": "open", "limit": 20, "series_ticker": s})
                for s in series_list
            ],
            return_exceptions=True,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

    all_markets: list[dict] = []
    for r in results:
        if isinstance(r, Exception):
            continue
        all_markets.extend(r.get("markets", []))

    return compute_summary(all_markets)


@router.get("/{ticker}")
async def get_market(ticker: str):
    try:
        return await kalshi_get(f"/markets/{ticker}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.get("/{ticker}/orderbook")
async def get_orderbook(
    ticker: str,
    depth: int | None = Query(None, ge=0, le=100, description="Orderbook depth per side"),
):
    try:
        return await kalshi_get(f"/markets/{ticker}/orderbook", {"depth": depth})
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
