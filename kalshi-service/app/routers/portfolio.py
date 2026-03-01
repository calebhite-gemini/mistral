import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.kalshi_client import kalshi_get

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/balance")
async def get_balance():
    try:
        return await kalshi_get("/portfolio/balance")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.get("/positions")
async def get_positions(
    limit: int | None = Query(None, ge=1, description="Results per page"),
    cursor: str | None = Query(None, description="Pagination cursor"),
    event_ticker: str | None = Query(None, description="Filter by event ticker"),
    status: str | None = Query(None, description="open or settled"),
):
    try:
        return await kalshi_get("/portfolio/positions", {
            "limit": limit,
            "cursor": cursor,
            "event_ticker": event_ticker,
            "status": status,
        })
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
