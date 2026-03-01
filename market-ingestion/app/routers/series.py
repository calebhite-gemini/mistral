from fastapi import APIRouter, Query
import httpx

router = APIRouter(prefix="/series", tags=["series"])

KALSHI_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"


@router.get("")
async def list_series(
    category: str | None = Query(None, description="Filter by category"),
    tags: str | None = Query(None, description="Filter by tags"),
    include_product_metadata: bool | None = Query(None, description="Include internal product metadata"),
    include_volume: bool | None = Query(None, description="Include total volume traded across all events"),
    min_updated_ts: int | None = Query(None, description="Series updated after this Unix timestamp"),
):
    params = _strip_none({
        "category": category,
        "tags": tags,
        "include_product_metadata": include_product_metadata,
        "include_volume": include_volume,
        "min_updated_ts": min_updated_ts,
    })
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/series", params=params)
        resp.raise_for_status()
        data = resp.json()
    series_list = data.get("series", [])
    print(f"[list_series] done: fetched {len(series_list)} series")
    return data


@router.get("/{series_ticker}")
async def get_series(
    series_ticker: str,
    include_volume: bool | None = Query(None, description="Include total volume traded across all events"),
):
    params = _strip_none({
        "include_volume": include_volume,
    })
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{KALSHI_BASE_URL}/series/{series_ticker}", params=params)
        resp.raise_for_status()
        return resp.json()


def _strip_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if isinstance(v, (str, int, float, bool))}
