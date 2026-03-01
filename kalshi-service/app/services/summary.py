"""
Stats aggregation for the frontend header cards:
volume_24h, active_markets, open_interest, sentiment.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class MarketSummary(BaseModel):
    volume_24h: int
    active_markets: int
    open_interest: int
    sentiment: Literal["BULLISH", "BEARISH", "NEUTRAL"]


def compute_summary(markets: list[dict]) -> MarketSummary:
    # Callers already filter by status=open at the API level; trust that.
    volume_24h = sum(m.get("volume_24h", 0) for m in markets)
    active_markets = len(markets)
    open_interest = sum(m.get("open_interest", 0) for m in markets)

    if markets:
        avg_price = sum(m.get("last_price", 50) for m in markets) / len(markets)
    else:
        avg_price = 50

    if avg_price > 55:
        sentiment: Literal["BULLISH", "BEARISH", "NEUTRAL"] = "BULLISH"
    elif avg_price < 45:
        sentiment = "BEARISH"
    else:
        sentiment = "NEUTRAL"

    return MarketSummary(
        volume_24h=volume_24h,
        active_markets=active_markets,
        open_interest=open_interest,
        sentiment=sentiment,
    )
