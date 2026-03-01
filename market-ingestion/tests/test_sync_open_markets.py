from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.jobs.sync_open_markets import (
    get_last_updated_ts,
    set_last_updated,
    fetch_open_markets,
    top_by_volume,
    upsert_markets,
    sync_once,
    SERIES_TICKERS,
    TOP_N_PER_SERIES,
)


# --- top_by_volume (pure function) ---


def test_top_by_volume(sample_markets):
    result = top_by_volume(sample_markets)
    assert len(result) == TOP_N_PER_SERIES
    volumes = [m["volume"] for m in result]
    assert volumes == sorted(volumes, reverse=True)
    assert volumes[0] == 25


def test_top_by_volume_fewer_than_n():
    markets = [{"ticker": f"M-{i}", "volume": i} for i in range(5)]
    result = top_by_volume(markets)
    assert len(result) == 5


def test_top_by_volume_with_missing_volume():
    markets = [
        {"ticker": "A", "volume": 100},
        {"ticker": "B", "volume": None},
        {"ticker": "C"},  # no volume key
        {"ticker": "D", "volume": 50},
    ]
    result = top_by_volume(markets, n=3)
    assert len(result) == 3
    assert result[0]["ticker"] == "A"
    assert result[1]["ticker"] == "D"
    # None and missing should both sort as 0
    assert result[2]["ticker"] in ("B", "C")


# --- get_last_updated_ts ---


def test_get_last_updated_ts_empty(mock_supabase):
    # .execute() returns empty data
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

    result = get_last_updated_ts(mock_supabase)
    assert result is None
    mock_supabase.table.assert_called_with("last_updated")


def test_get_last_updated_ts_with_data(mock_supabase):
    ts = "2026-02-28T12:00:00+00:00"
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"updated_at": ts}]
    )

    result = get_last_updated_ts(mock_supabase)
    expected = int(datetime.fromisoformat(ts).timestamp())
    assert result == expected


# --- set_last_updated ---


def test_set_last_updated(mock_supabase):
    set_last_updated(mock_supabase)
    mock_supabase.table.assert_called_with("last_updated")
    mock_supabase.table.return_value.upsert.assert_called_once()
    call_args = mock_supabase.table.return_value.upsert.call_args
    row = call_args[0][0]
    assert row["job"] == "sync_open_markets"
    assert "updated_at" in row


# --- upsert_markets ---


def test_upsert_markets_builds_correct_rows(mock_supabase, sample_markets):
    top = sample_markets[:3]
    upsert_markets(mock_supabase, top)

    mock_supabase.table.assert_called_with("markets")
    call_args = mock_supabase.table.return_value.upsert.call_args
    rows = call_args[0][0]
    assert len(rows) == 3

    row = rows[0]
    assert row["ticker"] == top[0]["ticker"]

    # Verify all expected columns are present
    expected_keys = {
        "ticker", "series_ticker", "event_ticker", "market_type",
        "yes_sub_title", "no_sub_title", "status", "result",
        "created_time", "updated_time", "open_time", "close_time",
        "latest_expiration_time", "expected_expiration_time", "settlement_timer_seconds",
        "yes_bid_dollars", "yes_ask_dollars", "yes_bid_size_fp", "yes_ask_size_fp",
        "no_bid_dollars", "no_ask_dollars", "last_price_dollars",
        "previous_yes_bid_dollars", "previous_yes_ask_dollars", "previous_price_dollars",
        "notional_value_dollars",
        "volume", "volume_24h", "open_interest",
        "can_close_early", "fractional_trading_enabled",
        "data", "synced_at",
    }
    assert set(row.keys()) == expected_keys

    # Verify no deprecated integer price fields leak in
    for deprecated in ("yes_bid", "yes_ask", "no_bid", "no_ask", "last_price", "title", "subtitle", "expiration_time"):
        assert deprecated not in row


def test_upsert_markets_empty(mock_supabase):
    upsert_markets(mock_supabase, [])
    mock_supabase.table.return_value.upsert.assert_not_called()


# --- fetch_open_markets ---


@pytest.mark.asyncio
async def test_fetch_open_markets_calls_all_series():
    # 15 markets per series, should be trimmed to TOP_N_PER_SERIES each
    fake_markets = [{"ticker": f"MKT-{i}", "volume": i} for i in range(15)]
    mock_list = AsyncMock(return_value={"markets": fake_markets})

    with patch("app.jobs.sync_open_markets.list_markets", mock_list):
        result = await fetch_open_markets()

    assert mock_list.call_count == len(SERIES_TICKERS)
    # Each series returns top TOP_N_PER_SERIES
    assert len(result) == TOP_N_PER_SERIES * len(SERIES_TICKERS)

    # First run: no min_created_ts
    for call in mock_list.call_args_list:
        assert call.kwargs["status"] == "open"
        assert call.kwargs["min_created_ts"] is None


@pytest.mark.asyncio
async def test_fetch_open_markets_with_min_created_ts():
    mock_list = AsyncMock(return_value={"markets": []})
    ts = 1709100000

    with patch("app.jobs.sync_open_markets.list_markets", mock_list):
        await fetch_open_markets(min_created_ts=ts)

    for call in mock_list.call_args_list:
        assert call.kwargs["min_created_ts"] == ts


# --- sync_once (integration of all pieces) ---


@pytest.mark.asyncio
async def test_sync_once_first_run(mock_supabase, sample_markets):
    """First run: last_updated is empty, should fetch all, upsert top 10 per series, update last_updated."""
    # last_updated returns empty
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

    mock_list = AsyncMock(return_value={"markets": sample_markets})

    with (
        patch("app.jobs.sync_open_markets.get_supabase", return_value=mock_supabase),
        patch("app.jobs.sync_open_markets.list_markets", mock_list),
    ):
        await sync_once()

    # Should have called list_markets for each series with no min_created_ts
    assert mock_list.call_count == len(SERIES_TICKERS)
    for call in mock_list.call_args_list:
        assert call.kwargs["min_created_ts"] is None

    # Should have upserted markets (top 20) and updated last_updated
    upsert_calls = [
        c for c in mock_supabase.table.call_args_list if c[0][0] == "markets"
    ]
    assert len(upsert_calls) > 0

    last_updated_calls = [
        c for c in mock_supabase.table.call_args_list if c[0][0] == "last_updated"
    ]
    assert len(last_updated_calls) > 0


@pytest.mark.asyncio
async def test_sync_once_subsequent_run(mock_supabase):
    """Subsequent run: last_updated has a timestamp, should pass it as min_created_ts."""
    ts = "2026-02-28T08:00:00+00:00"
    expected_unix = int(datetime.fromisoformat(ts).timestamp())

    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"updated_at": ts}]
    )

    mock_list = AsyncMock(return_value={"markets": [{"ticker": "X", "volume": 5}]})

    with (
        patch("app.jobs.sync_open_markets.get_supabase", return_value=mock_supabase),
        patch("app.jobs.sync_open_markets.list_markets", mock_list),
    ):
        await sync_once()

    for call in mock_list.call_args_list:
        assert call.kwargs["min_created_ts"] == expected_unix
