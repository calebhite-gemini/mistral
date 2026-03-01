import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.kalshi_client import kalshi_get
from app.services.summary import compute_summary

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("")
async def list_markets(
    limit: int | None = Query(None, ge=1, le=1000, description="Results per page"),
    cursor: str | None = Query(None, description="Pagination cursor"),
    status: str | None = Query(None, description="open, closed, or settled"),
    series_ticker: str | None = Query(None, description="Filter by series ticker"),
    min_close_ts: int | None = Query(None, description="Markets closing after this Unix timestamp"),
):
    try:
        return await kalshi_get("/markets", {
            "limit": limit,
            "cursor": cursor,
            "status": status,
            "series_ticker": series_ticker,
            "min_close_ts": min_close_ts,
        })
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


# Declared before /{ticker} so FastAPI resolves it as a literal path
@router.get("/summary")
async def market_summary(
    series_ticker: str | None = Query(None, description="Filter by series ticker"),
    limit: int = Query(200, ge=1, le=1000, description="Max markets to aggregate"),
):
    """Aggregated stats for the UI header cards."""
    try:
        data = await kalshi_get("/markets", {
            "status": "open",
            "series_ticker": series_ticker,
            "limit": limit,
        })
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

    return compute_summary(data.get("markets", []))


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
