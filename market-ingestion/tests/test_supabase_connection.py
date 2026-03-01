import os

from dotenv import load_dotenv

load_dotenv()

from supabase import create_client  # noqa: E402


def test_supabase_connection():
    """Verify we can connect and authenticate with Supabase."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    sb = create_client(url, key)

    # Query a built-in auth schema to verify connection without needing custom tables
    result = sb.auth.get_session()
    # If we get here without an exception, connection + auth succeeded
    print(f"Connection OK — session: {result}")


def test_supabase_tables_exist():
    """Verify our required tables exist in Supabase."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    sb = create_client(url, key)

    for table in ("markets", "last_updated"):
        result = sb.table(table).select("*").limit(1).execute()
        assert result.data is not None, f"Table '{table}' not accessible"
        print(f"Table '{table}' OK — {len(result.data)} rows")


def test_supabase_markets_schema():
    """Verify the markets table has all expected columns by inserting and reading back a test row."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    sb = create_client(url, key)

    test_row = {
        "ticker": "__TEST_SCHEMA_CHECK__",
        "series_ticker": "TEST",
        "event_ticker": "TEST-EVT",
        "market_type": "binary",
        "yes_sub_title": "Yes",
        "no_sub_title": "No",
        "status": "open",
        "result": None,
        "created_time": "2026-01-01T00:00:00Z",
        "updated_time": "2026-01-01T00:00:00Z",
        "open_time": "2026-01-01T00:00:00Z",
        "close_time": "2026-01-01T00:00:00Z",
        "latest_expiration_time": "2026-01-01T00:00:00Z",
        "expected_expiration_time": "2026-01-01T00:00:00Z",
        "settlement_timer_seconds": 3600,
        "yes_bid_dollars": "0.5000",
        "yes_ask_dollars": "0.5500",
        "yes_bid_size_fp": "10.00",
        "yes_ask_size_fp": "10.00",
        "no_bid_dollars": "0.4500",
        "no_ask_dollars": "0.5000",
        "last_price_dollars": "0.5000",
        "previous_yes_bid_dollars": "0.4900",
        "previous_yes_ask_dollars": "0.5400",
        "previous_price_dollars": "0.4900",
        "notional_value_dollars": "1.0000",
        "volume": 100,
        "volume_24h": 50,
        "open_interest": 200,
        "can_close_early": True,
        "fractional_trading_enabled": True,
        "data": {"test": True},
        "synced_at": "2026-01-01T00:00:00Z",
    }

    try:
        sb.table("markets").upsert(test_row, on_conflict="ticker").execute()
        result = sb.table("markets").select("*").eq("ticker", "__TEST_SCHEMA_CHECK__").execute()
        assert len(result.data) == 1
        row = result.data[0]
        for col in test_row:
            assert col in row, f"Column '{col}' missing from markets table"
        print("Markets schema OK — all columns present")
    finally:
        sb.table("markets").delete().eq("ticker", "__TEST_SCHEMA_CHECK__").execute()
