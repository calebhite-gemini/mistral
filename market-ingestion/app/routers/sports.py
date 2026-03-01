import asyncio

from fastapi import APIRouter, Query

from app.routers.events import list_events
from app.routers.series import list_series

router = APIRouter(prefix="/sports", tags=["sports"])

PAGE_DELAY_SECONDS = 5


@router.get("/series-tickers")
async def get_sports_series_tickers(
    tags: str | None = Query(None, description="Filter series by tags (e.g. Basketball, Soccer)"),
):
    series_data = await list_series(category="Sports", tags=tags, include_volume=True)
    series_list = series_data.get("series", [])
    series_list.sort(key=lambda s: s.get("volume", 0), reverse=True)

    return {
        "series_tickers": [
            {
                "series_ticker": s["ticker"],
                "series_title": s.get("title", ""),
                "tags": s.get("tags", []),
                "volume": s.get("volume", 0),
            }
            for s in series_list
        ]
    }


@router.get("/event-tickers")
async def get_sports_event_tickers(
    status: str | None = Query(None, description="open, closed, or settled"),
    tags: str | None = Query(None, description="Filter series by tags (e.g. Basketball, Soccer)"),
):
    series_data = await list_series(category="Sports", tags=tags)
    series_list = series_data.get("series", [])

    if not series_list:
        return {"event_tickers": []}

    all_events = []
    for s in series_list:
        result = await list_events(
            status=status,
            series_ticker=s["ticker"],
        )
        all_events.extend(result.get("events", []))
        await asyncio.sleep(PAGE_DELAY_SECONDS)

    return {
        "event_tickers": [
            {
                "event_ticker": e["event_ticker"],
                "event_description": e.get("title", ""),
            }
            for e in all_events
        ]
    }
