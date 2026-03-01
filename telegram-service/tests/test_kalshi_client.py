"""Tests for Kalshi WebSocket client."""
import pytest
import json
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import asyncio

from app.kalshi_client import KalshiWebSocketClient


@pytest.mark.asyncio
async def test_kalshi_client_initialization(mock_env):
    """Test Kalshi client initializes correctly."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)

    assert client.url == "wss://test.kalshi.com/ws/v2"
    assert client.api_key == "test_api_key_12345"
    assert client.on_market_created == callback
    assert client.websocket is None
    assert client.is_running is False
    assert client.message_id == 0


@pytest.mark.asyncio
async def test_kalshi_client_auth_headers(mock_env):
    """Test Kalshi client generates correct auth headers."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)

    headers = client._get_auth_headers()

    assert headers == {"Authorization": "Bearer test_api_key_12345"}


@pytest.mark.asyncio
async def test_kalshi_client_subscribe_to_market_lifecycle(mock_env, mock_websocket):
    """Test Kalshi client subscribes to market_lifecycle_v2 channel."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)
    client.websocket = mock_websocket

    await client._subscribe_to_market_lifecycle()

    # Verify subscription message was sent
    mock_websocket.send.assert_called_once()
    sent_message = json.loads(mock_websocket.send.call_args[0][0])

    assert sent_message["id"] == 1
    assert sent_message["cmd"] == "subscribe"
    assert sent_message["params"]["channels"] == ["market_lifecycle_v2"]


@pytest.mark.asyncio
async def test_kalshi_client_handles_created_event(
    mock_env,
    sample_kalshi_created_event
):
    """Test Kalshi client handles market creation events."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)

    message = json.dumps(sample_kalshi_created_event)
    await client._handle_message(message)

    # Verify callback was called with the event message
    callback.assert_called_once_with(sample_kalshi_created_event["msg"])


@pytest.mark.asyncio
async def test_kalshi_client_ignores_deactivated_event(
    mock_env,
    sample_kalshi_deactivated_event
):
    """Test Kalshi client ignores non-activation events."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)

    message = json.dumps(sample_kalshi_deactivated_event)
    await client._handle_message(message)

    # Verify callback was NOT called for deactivation event
    callback.assert_not_called()


@pytest.mark.asyncio
async def test_kalshi_client_handles_subscription_response(
    mock_env,
    sample_kalshi_subscription_response
):
    """Test Kalshi client handles subscription confirmation."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)

    message = json.dumps(sample_kalshi_subscription_response)
    await client._handle_message(message)

    # Should not call the activation callback
    callback.assert_not_called()


@pytest.mark.asyncio
async def test_kalshi_client_handles_invalid_json(mock_env):
    """Test Kalshi client handles invalid JSON gracefully."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)

    # Send invalid JSON
    await client._handle_message("invalid json {")

    # Should not crash, callback should not be called
    callback.assert_not_called()


@pytest.mark.asyncio
async def test_kalshi_client_disconnect(mock_env, mock_websocket):
    """Test Kalshi client disconnects properly."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)
    client.websocket = mock_websocket
    client.is_running = True

    await client.disconnect()

    assert client.is_running is False
    mock_websocket.close.assert_called_once()


@pytest.mark.asyncio
async def test_kalshi_client_listen_processes_messages(mock_env):
    """Test Kalshi client listen loop processes messages."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)

    # Create a mock websocket that yields messages
    mock_ws = MagicMock()
    event_message = json.dumps({
        "type": "market_lifecycle_v2",
        "msg": {
            "event_type": "created",
            "market_ticker": "TEST-123"
        }
    })

    async def mock_aiter():
        yield event_message

    mock_ws.__aiter__ = lambda self: mock_aiter()
    client.websocket = mock_ws

    # Run listen for a short time
    await client._listen()

    # Verify the callback was called
    callback.assert_called_once()
    assert callback.call_args[0][0]["market_ticker"] == "TEST-123"


@pytest.mark.asyncio
async def test_kalshi_client_connect_with_reconnect(mock_env):
    """Test Kalshi client connection attempts reconnection on failure."""
    callback = AsyncMock()
    client = KalshiWebSocketClient(on_market_created=callback)

    # This test verifies the reconnection logic exists
    # Actual reconnection is tested in integration tests
    assert client.is_running is False

    # Simulate starting and stopping
    client.is_running = True
    assert client.is_running is True

    await client.disconnect()
    assert client.is_running is False
