"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import AsyncMock, Mock, MagicMock, patch
import os


# Set up environment variables before any imports
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
os.environ.setdefault("KALSHI_API_KEY", "test_api_key_12345")
os.environ.setdefault("KALSHI_WEBSOCKET_URL", "wss://test.kalshi.com/ws/v2")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test_supabase_key")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables for the entire test session."""
    os.environ["TELEGRAM_BOT_TOKEN"] = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    os.environ["KALSHI_API_KEY"] = "test_api_key_12345"
    os.environ["KALSHI_WEBSOCKET_URL"] = "wss://test.kalshi.com/ws/v2"
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_KEY"] = "test_supabase_key"
    os.environ["LOG_LEVEL"] = "DEBUG"
    yield
    # Cleanup after tests
    for key in ["TELEGRAM_BOT_TOKEN", "KALSHI_API_KEY", "KALSHI_WEBSOCKET_URL", "SUPABASE_URL", "SUPABASE_KEY", "LOG_LEVEL"]:
        os.environ.pop(key, None)


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    monkeypatch.setenv("KALSHI_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("KALSHI_WEBSOCKET_URL", "wss://test.kalshi.com/ws/v2")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test_supabase_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture(autouse=True)
def mock_supabase():
    """Mock Supabase client for all tests."""
    mock_client = MagicMock()
    # Mock table().select().execute() chain for _load_subscribers
    mock_client.table.return_value.select.return_value.execute.return_value.data = []
    # Mock table().upsert().execute() chain for _add_subscriber
    mock_client.table.return_value.upsert.return_value.execute.return_value = None
    # Mock table().delete().eq().execute() chain for _remove_subscriber
    mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = None

    with patch("app.telegram_bot.create_client", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.close = AsyncMock()
    ws.__aiter__ = Mock(return_value=iter([]))
    return ws


@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram Bot instance."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot


@pytest.fixture
def mock_telegram_application():
    """Mock Telegram Application instance."""
    app = MagicMock()
    app.bot = MagicMock()
    app.bot.send_message = AsyncMock()
    app.initialize = AsyncMock()
    app.start = AsyncMock()
    app.stop = AsyncMock()
    app.shutdown = AsyncMock()
    app.updater = MagicMock()
    app.updater.start_polling = AsyncMock()
    app.updater.stop = AsyncMock()
    app.add_handler = Mock()
    return app


@pytest.fixture
def sample_kalshi_created_event():
    """Sample Kalshi market creation event."""
    return {
        "type": "market_lifecycle_v2",
        "sid": 13,
        "msg": {
            "event_type": "created",
            "market_ticker": "TEST-MARKET-2024",
            "open_ts": 1694635200,
            "close_ts": 1694721600,
            "additional_metadata": {
                "name": "S&P 500 daily return on Sep 14",
                "title": "S&P 500 closes up by 0.02% or more",
                "yes_sub_title": "S&P 500 closes up 0.02%+",
                "no_sub_title": "S&P 500 closes up <0.02%",
                "rules_primary": "The S&P 500 index level at 4:00 PM ET...",
                "rules_secondary": "",
                "can_close_early": True,
                "event_ticker": "INXD-23SEP14",
                "expected_expiration_ts": 1694721600,
                "strike_type": "greater",
                "floor_strike": 4487
            }
        }
    }


@pytest.fixture
def sample_kalshi_deactivated_event():
    """Sample Kalshi market deactivation event."""
    return {
        "type": "market_lifecycle_v2",
        "sid": 14,
        "msg": {
            "event_type": "deactivated",
            "market_ticker": "TEST-MARKET-2024"
        }
    }


@pytest.fixture
def sample_kalshi_subscription_response():
    """Sample Kalshi subscription confirmation response."""
    return {
        "id": 1,
        "type": "subscription_ack",
        "status": "success"
    }
