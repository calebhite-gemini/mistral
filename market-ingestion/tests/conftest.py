from unittest.mock import MagicMock

import pytest


def _make_market(ticker: str, event_ticker: str, volume: int | None = 100) -> dict:
    return {
        "ticker": ticker,
        "event_ticker": event_ticker,
        "series_ticker": "KXNBAGAME",
        "market_type": "binary",
        "yes_sub_title": f"{ticker} Yes",
        "no_sub_title": f"{ticker} No",
        "status": "open",
        "result": None,
        "created_time": "2026-02-01T00:00:00Z",
        "updated_time": "2026-02-28T00:00:00Z",
        "open_time": "2026-02-01T12:00:00Z",
        "close_time": "2026-03-15T00:00:00Z",
        "latest_expiration_time": "2026-03-15T00:00:00Z",
        "expected_expiration_time": "2026-03-15T00:00:00Z",
        "settlement_timer_seconds": 3600,
        "yes_bid_dollars": "0.4500",
        "yes_ask_dollars": "0.5500",
        "yes_bid_size_fp": "10.00",
        "yes_ask_size_fp": "15.00",
        "no_bid_dollars": "0.4500",
        "no_ask_dollars": "0.5500",
        "last_price_dollars": "0.5000",
        "previous_yes_bid_dollars": "0.4400",
        "previous_yes_ask_dollars": "0.5400",
        "previous_price_dollars": "0.4900",
        "notional_value_dollars": "1.0000",
        "volume": volume,
        "volume_24h": (volume or 0) // 2,
        "open_interest": 1000,
        "can_close_early": True,
        "fractional_trading_enabled": True,
    }


@pytest.fixture
def sample_markets():
    """25 fake markets with volumes 1..25."""
    return [_make_market(f"MKT-{i}", f"EVT-{i // 3}", volume=i) for i in range(1, 26)]


@pytest.fixture
def mock_supabase():
    """Mock Supabase client that supports chained calls."""
    sb = MagicMock()

    # Make chained methods return the same mock so .table().upsert().execute() works
    chain = MagicMock()
    chain.execute.return_value = MagicMock(data=[])
    sb.table.return_value = chain
    chain.upsert.return_value = chain
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.order.return_value = chain
    chain.limit.return_value = chain

    return sb
