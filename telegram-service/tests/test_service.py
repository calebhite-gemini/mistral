"""Tests for service orchestration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.service import TelegramService


@pytest.mark.asyncio
async def test_service_initialization(mock_env):
    """Test service initializes correctly."""
    service = TelegramService()

    assert service.telegram_notifier is not None
    assert service.kalshi_client is not None
    assert service.is_running is False


@pytest.mark.asyncio
async def test_service_handle_market_created(mock_env):
    """Test service handles market creation events."""
    service = TelegramService()
    service.telegram_notifier.send_notification = AsyncMock()

    event_data = {
        "event_type": "created",
        "market_ticker": "TEST-MARKET-2024"
    }

    await service._handle_market_created(event_data)

    # Verify notification was sent
    service.telegram_notifier.send_notification.assert_called_once_with(event_data)


@pytest.mark.asyncio
async def test_service_start_initializes_components(mock_env):
    """Test service start initializes all components."""
    service = TelegramService()

    # Mock the components
    service.telegram_notifier.start = AsyncMock()
    service.kalshi_client.connect = AsyncMock()

    # Mock signal handling
    with patch("asyncio.get_event_loop") as mock_loop:
        mock_event_loop = MagicMock()
        mock_loop.return_value = mock_event_loop

        # Make connect return immediately to avoid infinite loop
        async def quick_connect():
            service.is_running = False

        service.kalshi_client.connect = quick_connect

        await service.start()

        # Verify components were started
        service.telegram_notifier.start.assert_called_once()


@pytest.mark.asyncio
async def test_service_stop_shuts_down_components(mock_env):
    """Test service stop shuts down all components."""
    service = TelegramService()
    service.is_running = True

    # Mock the components
    service.telegram_notifier.stop = AsyncMock()
    service.kalshi_client.disconnect = AsyncMock()

    await service.stop()

    # Verify components were stopped
    assert service.is_running is False
    service.kalshi_client.disconnect.assert_called_once()
    service.telegram_notifier.stop.assert_called_once()


@pytest.mark.asyncio
async def test_service_stop_when_not_running(mock_env):
    """Test service stop does nothing if not running."""
    service = TelegramService()
    service.is_running = False

    # Mock the components
    service.telegram_notifier.stop = AsyncMock()
    service.kalshi_client.disconnect = AsyncMock()

    await service.stop()

    # Verify components were not called
    service.kalshi_client.disconnect.assert_not_called()
    service.telegram_notifier.stop.assert_not_called()


@pytest.mark.asyncio
async def test_service_handles_callback_errors(mock_env):
    """Test service handles errors in market creation callback."""
    service = TelegramService()

    # Make send_notification raise an error
    service.telegram_notifier.send_notification = AsyncMock(
        side_effect=Exception("Send failed")
    )

    event_data = {
        "event_type": "created",
        "market_ticker": "TEST-MARKET-2024"
    }

    # Should not raise exception
    await service._handle_market_created(event_data)


@pytest.mark.asyncio
async def test_service_full_lifecycle(mock_env):
    """Test full service lifecycle: start -> process event -> stop."""
    service = TelegramService()

    # Mock components
    service.telegram_notifier.start = AsyncMock()
    service.telegram_notifier.stop = AsyncMock()
    service.telegram_notifier.send_notification = AsyncMock()
    service.kalshi_client.disconnect = AsyncMock()

    # Simulate a quick connect that processes one event
    async def simulate_connect():
        service.is_running = True
        # Simulate receiving an event
        event_data = {
            "event_type": "created",
            "market_ticker": "LIFECYCLE-TEST"
        }
        await service._handle_market_created(event_data)
        # Stop the service
        await service.stop()

    service.kalshi_client.connect = simulate_connect

    with patch("asyncio.get_event_loop") as mock_loop:
        mock_event_loop = MagicMock()
        mock_loop.return_value = mock_event_loop

        await service.start()

        # Verify the full lifecycle
        service.telegram_notifier.start.assert_called_once()
        service.telegram_notifier.send_notification.assert_called_once()
        service.kalshi_client.disconnect.assert_called_once()
        service.telegram_notifier.stop.assert_called_once()
