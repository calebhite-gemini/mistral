import asyncio
import os

from fastapi import APIRouter, Query
import httpx

router = APIRouter(prefix="/historical", tags=["historical"])

KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
PAGE_DELAY_SECONDS = 5


@router.get("/cutoff")
async def get_cutoff():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/historical/cutoff")
        resp.raise_for_status()
        return resp.json()


@router.get("/markets")
async def list_historical_markets(
    tickers: str | None = Query(None, description="Comma-separated list of market tickers"),
    event_ticker: str | None = Query(None, description="Filter by event ticker (comma-separated, max 10)"),
    mve_filter: str | None = Query(None, description="Multivariate event filter (e.g. 'exclude')"),
):
    base_params = _strip_none({
        "limit": 1000,
        "tickers": tickers,
        "event_ticker": event_ticker,
        "mve_filter": mve_filter,
    })

    all_markets = []
    cursor = None

    async with httpx.AsyncClient() as client:
        while True:
            params = {**base_params}
            if cursor:
                params["cursor"] = cursor

            resp = await client.get(f"{KALSHI_BASE_URL}/historical/markets", params=params)
            resp.raise_for_status()
            data = resp.json()

            all_markets.extend(data.get("markets", []))
            cursor = data.get("cursor", "")

            if not cursor:
                break

            await asyncio.sleep(PAGE_DELAY_SECONDS)

    return {"markets": all_markets}


@router.get("/markets/grouped-by-event")
async def list_historical_markets_grouped_by_event():
    result = await list_historical_markets()
    markets = result.get("markets", [])

    events_map: dict[str, list] = {}
    for market in markets:
        et = market.get("event_ticker", "")
        events_map.setdefault(et, []).append(market)

    return {
        "events": [
            {"event_ticker": et, "markets": mkts}
            for et, mkts in events_map.items()
        ]
    }


@router.get("/markets/{ticker}")
async def get_historical_market(ticker: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/historical/markets/{ticker}")
        resp.raise_for_status()
        return resp.json()


def _strip_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if isinstance(v, (str, int, float, bool))}
