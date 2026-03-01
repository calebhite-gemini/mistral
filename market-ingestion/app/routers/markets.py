import asyncio

from fastapi import APIRouter, Query
import httpx

router = APIRouter(prefix="/markets", tags=["markets"])

KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
PAGE_DELAY_SECONDS = 1


@router.get("")
async def list_markets(
    status: str | None = Query(None, description="unopened, open, paused, closed, or settled"),
    series_ticker: str | None = Query(None, description="Filter by series ticker"),
    event_ticker: str | None = Query(None, description="Filter by event ticker (comma-separated, max 10)"),
    tickers: str | None = Query(None, description="Comma-separated list of market tickers"),
    mve_filter: str | None = Query(None, description="'only' or 'exclude' multivariate events"),
    min_close_ts: int | None = Query(None, description="Markets closing after this Unix timestamp"),
    max_close_ts: int | None = Query(None, description="Markets closing before this Unix timestamp"),
    min_created_ts: int | None = Query(None, description="Markets created after this Unix timestamp"),
    max_created_ts: int | None = Query(None, description="Markets created before this Unix timestamp"),
    min_updated_ts: int | None = Query(None, description="Markets updated after this Unix timestamp"),
    min_settled_ts: int | None = Query(None, description="Markets settled after this Unix timestamp"),
    max_settled_ts: int | None = Query(None, description="Markets settled before this Unix timestamp"),
):
    base_params = _strip_none({
        "limit": 1000,
        "status": status,
        "series_ticker": series_ticker,
        "event_ticker": event_ticker,
        "tickers": tickers,
        "mve_filter": mve_filter,
        "min_close_ts": min_close_ts,
        "max_close_ts": max_close_ts,
        "min_created_ts": min_created_ts,
        "max_created_ts": max_created_ts,
        "min_updated_ts": min_updated_ts,
        "min_settled_ts": min_settled_ts,
        "max_settled_ts": max_settled_ts,
    })

    all_markets = []
    cursor = None
    page = 0

    async with httpx.AsyncClient() as client:
        while True:
            params = {**base_params}
            if cursor:
                params["cursor"] = cursor

            resp = await client.get(f"{KALSHI_BASE_URL}/markets", params=params)
            resp.raise_for_status()
            data = resp.json()

            page_markets = data.get("markets", [])
            all_markets.extend(page_markets)
            cursor = data.get("cursor", "")
            page += 1
            print(f"[list_markets] page {page}: fetched {len(page_markets)} markets (total: {len(all_markets)})")

            if not cursor:
                break

            await asyncio.sleep(PAGE_DELAY_SECONDS)

    print(f"[list_markets] done: {len(all_markets)} markets total across {page} pages")
    return {"markets": all_markets}


@router.get("/{ticker}")
async def get_market(ticker: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/markets/{ticker}")
        resp.raise_for_status()
        return resp.json()


@router.get("/{ticker}/orderbook")
async def get_orderbook(
    ticker: str,
    depth: int | None = Query(None, description="Orderbook depth (0 = all levels, 1-100)"),
):
    params = _strip_none({"depth": depth})
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/markets/{ticker}/orderbook", params=params)
        resp.raise_for_status()
        return resp.json()


def _strip_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if isinstance(v, (str, int, float, bool))}
