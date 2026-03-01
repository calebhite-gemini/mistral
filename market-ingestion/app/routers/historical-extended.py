import asyncio

from fastapi import APIRouter, Query

from app.routers.events import list_events
from app.routers.historical import get_cutoff, list_historical_markets

router = APIRouter(prefix="/historical-extended", tags=["historical-extended"])

PAGE_DELAY_SECONDS = 5


@router.get("/settled-events")
async def get_settled_events_with_markets(
    series_ticker: str | None = Query(None, description="Filter by series ticker"),
):
    cutoff_data, events_data = await asyncio.gather(
        get_cutoff(),
        list_events(status="settled", series_ticker=series_ticker),
    )

    events = events_data.get("events", [])
    if not events:
        return {"cutoff": cutoff_data, "events": []}

    # Batch event tickers in groups of 10 (Kalshi max for comma-separated event_ticker)
    tickers = [e["event_ticker"] for e in events]
    batches = [tickers[i : i + 10] for i in range(0, len(tickers), 10)]

    all_markets = []
    for batch in batches:
        result = await list_historical_markets(event_ticker=",".join(batch))
        all_markets.extend(result.get("markets", []))
        if batch is not batches[-1]:
            await asyncio.sleep(PAGE_DELAY_SECONDS)

    # Group markets by event_ticker
    markets_by_event: dict[str, list] = {}
    for market in all_markets:
        et = market.get("event_ticker", "")
        markets_by_event.setdefault(et, []).append(market)

    # Attach markets to events, exclude events with no markets
    enriched_events = []
    for event in events:
        et = event["event_ticker"]
        markets = markets_by_event.get(et, [])
        if markets:
            enriched_events.append({**event, "markets": markets})

    return {"cutoff": cutoff_data, "events": enriched_events}
