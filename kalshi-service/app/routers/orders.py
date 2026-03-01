from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.kalshi_client import kalshi_delete, kalshi_get, kalshi_post

router = APIRouter(prefix="/orders", tags=["orders"])


class PlaceOrderRequest(BaseModel):
    ticker: str
    side: Literal["yes", "no"]
    action: Literal["buy", "sell"] = "buy"
    type: Literal["limit", "market"]
    count: int = Field(ge=1, description="Number of contracts")
    yes_price: int | None = Field(None, ge=1, le=99, description="Limit price in cents (1-99). Required for limit orders.")


@router.post("")
async def place_order(body: PlaceOrderRequest):
    payload: dict = {
        "ticker": body.ticker,
        "side": body.side,
        "action": body.action,
        "type": body.type,
        "count": body.count,
    }
    if body.yes_price is not None:
        payload["yes_price"] = body.yes_price
    try:
        return await kalshi_post("/portfolio/orders", payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.get("")
async def list_orders(
    ticker: str | None = Query(None, description="Filter by market ticker"),
    status: str | None = Query(None, description="resting, canceled, executed"),
    limit: int | None = Query(None, ge=1, description="Results per page"),
    cursor: str | None = Query(None, description="Pagination cursor"),
):
    try:
        return await kalshi_get("/portfolio/orders", {
            "ticker": ticker,
            "status": status,
            "limit": limit,
            "cursor": cursor,
        })
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


@router.delete("/{order_id}")
async def cancel_order(order_id: str):
    try:
        return await kalshi_delete(f"/portfolio/orders/{order_id}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
