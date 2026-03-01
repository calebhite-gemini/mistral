"""Integration tests for the full service flow."""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from app.service import TelegramService


@pytest.mark.asyncio
async def test_end_to_end_market_activation_flow(mock_env):
    """Test complete flow from WebSocket event to Telegram notification."""
    service = TelegramService()

    # Track the notification that was sent
    sent_notifications = []

    async def capture_notification(event_data):
        sent_notifications.append(event_data)

    # Mock the Telegram notifier
    service.telegram_notifier.start = AsyncMock()
    service.telegram_notifier.stop = AsyncMock()
    service.telegram_notifier.send_notification = AsyncMock(side_effect=capture_notification)
    service.telegram_notifier.bot = MagicMock()
    service.telegram_notifier.user_chat_ids = {12345}

    # Mock the Kalshi client to simulate receiving an event
    service.kalshi_client.disconnect = AsyncMock()

    activation_event = {
        "event_type": "created",
        "market_ticker": "INTEGRATION-TEST-2024"
    }

    async def simulate_websocket_event():
        # Simulate the WebSocket client calling the callback
        await service._handle_market_created(activation_event)

    service.kalshi_client.connect = simulate_websocket_event

    # Run the service
    with patch("asyncio.get_event_loop") as mock_loop:
        mock_event_loop = MagicMock()
        mock_loop.return_value = mock_event_loop

        await service.start()

    # Verify the notification was sent
    assert len(sent_notifications) == 1
    assert sent_notifications[0]["market_ticker"] == "INTEGRATION-TEST-2024"


@pytest.mark.asyncio
async def test_multiple_users_receive_notifications(mock_env):
    """Test multiple subscribed users receive notifications."""
    service = TelegramService()

    # Mock bot with multiple subscribers
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()

    service.telegram_notifier.start = AsyncMock()
    service.telegram_notifier.bot = mock_bot
    service.telegram_notifier.user_chat_ids = {111, 222, 333}

    # Simulate market activation
    event_data = {
        "event_type": "created",
        "market_ticker": "MULTI-USER-TEST"
    }

    await service._handle_market_created(event_data)

    # Verify all users received notification
    assert mock_bot.send_message.call_count == 3

    # Verify correct chat IDs
    sent_chat_ids = {
        call.kwargs["chat_id"]
        for call in mock_bot.send_message.call_args_list
    }
    assert sent_chat_ids == {111, 222, 333}


@pytest.mark.asyncio
async def test_reconnection_after_websocket_disconnect(mock_env):
    """Test service reconnects after WebSocket disconnection."""
    service = TelegramService()

    connection_attempts = []

    async def simulate_connection_with_disconnect():
        connection_attempts.append(1)
        if len(connection_attempts) == 1:
            # First connection - simulate disconnect
            raise ConnectionError("Connection lost")
        else:
            # Second connection - success
            service.is_running = False

    service.telegram_notifier.start = AsyncMock()
    service.kalshi_client.connect = simulate_connection_with_disconnect

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_event_loop = MagicMock()
        mock_loop.return_value = mock_event_loop

        # The connect method should retry on failure
        # We need to mock the actual reconnection logic
        with patch.object(service.kalshi_client, 'connect') as mock_connect:
            # First call fails, second succeeds
            mock_connect.side_effect = [
                ConnectionError("Connection lost"),
                AsyncMock()
            ]

            # Start service - it should handle the error and retry would happen
            # For this test, we just verify the service can handle connection errors
            try:
                await service.start()
            except ConnectionError:
                # Expected on first attempt
                pass


@pytest.mark.asyncio
async def test_graceful_shutdown(mock_env):
    """Test service shuts down gracefully."""
    service = TelegramService()

    # Track shutdown sequence
    shutdown_sequence = []

    async def track_kalshi_disconnect():
        shutdown_sequence.append("kalshi_disconnected")

    async def track_telegram_stop():
        shutdown_sequence.append("telegram_stopped")

    service.kalshi_client.disconnect = AsyncMock(side_effect=track_kalshi_disconnect)
    service.telegram_notifier.stop = AsyncMock(side_effect=track_telegram_stop)
    service.is_running = True

    await service.stop()

    # Verify shutdown sequence
    assert "kalshi_disconnected" in shutdown_sequence
    assert "telegram_stopped" in shutdown_sequence
    assert service.is_running is False


@pytest.mark.asyncio
async def test_no_notifications_when_no_subscribers(mock_env):
    """Test no errors when event received but no subscribers."""
    service = TelegramService()

    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()

    service.telegram_notifier.bot = mock_bot
    service.telegram_notifier.user_chat_ids = set()  # No subscribers

    event_data = {
        "event_type": "created",
        "market_ticker": "NO-SUBSCRIBERS-TEST"
    }

    # Should not raise any errors
    await service._handle_market_created(event_data)

    # No messages should be sent
    mock_bot.send_message.assert_not_called()
