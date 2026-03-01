"""Tests for Telegram bot."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from telegram import Update, Chat, Message, User

from app.telegram_bot import TelegramNotifier


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update object."""
    update = MagicMock(spec=Update)
    update.effective_chat = MagicMock(spec=Chat)
    update.effective_chat.id = 12345
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_telegram_bot_initialization(mock_env):
    """Test Telegram bot initializes correctly."""
    notifier = TelegramNotifier()

    assert notifier.bot_token == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    assert notifier.bot is None
    assert notifier.application is None
    assert notifier.user_chat_ids == set()


@pytest.mark.asyncio
async def test_telegram_bot_start(mock_env, mock_telegram_application):
    """Test Telegram bot starts correctly."""
    notifier = TelegramNotifier()

    with patch("app.telegram_bot.Application.builder") as mock_builder:
        mock_builder.return_value.token.return_value.build.return_value = mock_telegram_application

        await notifier.start()

        assert notifier.application == mock_telegram_application
        assert notifier.bot == mock_telegram_application.bot

        # Verify initialization sequence
        mock_telegram_application.initialize.assert_called_once()
        mock_telegram_application.start.assert_called_once()
        mock_telegram_application.updater.start_polling.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_bot_stop(mock_env, mock_telegram_application):
    """Test Telegram bot stops correctly."""
    notifier = TelegramNotifier()
    notifier.application = mock_telegram_application

    await notifier.stop()

    # Verify shutdown sequence
    mock_telegram_application.updater.stop.assert_called_once()
    mock_telegram_application.stop.assert_called_once()
    mock_telegram_application.shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_start_command_subscribes_user(mock_env, mock_update):
    """Test /start command subscribes user to notifications."""
    notifier = TelegramNotifier()
    context = MagicMock()

    await notifier._start_command(mock_update, context)

    # Verify user was added to subscribers
    assert 12345 in notifier.user_chat_ids

    # Verify reply was sent
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "subscribed" in call_args.lower()


@pytest.mark.asyncio
async def test_stop_command_unsubscribes_user(mock_env, mock_update):
    """Test /stop command unsubscribes user from notifications."""
    notifier = TelegramNotifier()
    notifier.user_chat_ids.add(12345)
    context = MagicMock()

    await notifier._stop_command(mock_update, context)

    # Verify user was removed from subscribers
    assert 12345 not in notifier.user_chat_ids

    # Verify reply was sent
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "unsubscribed" in call_args.lower()


@pytest.mark.asyncio
async def test_status_command_shows_subscribed(mock_env, mock_update):
    """Test /status command shows subscribed status."""
    notifier = TelegramNotifier()
    notifier.user_chat_ids.add(12345)
    context = MagicMock()

    await notifier._status_command(mock_update, context)

    # Verify status reply was sent
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Subscribed" in call_args


@pytest.mark.asyncio
async def test_status_command_shows_not_subscribed(mock_env, mock_update):
    """Test /status command shows not subscribed status."""
    notifier = TelegramNotifier()
    context = MagicMock()

    await notifier._status_command(mock_update, context)

    # Verify status reply was sent
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Not subscribed" in call_args


@pytest.mark.asyncio
async def test_format_notification(mock_env):
    """Test notification formatting for market creation."""
    notifier = TelegramNotifier()

    event_data = {
        "event_type": "created",
        "market_ticker": "INXD-23SEP14-B4487",
        "open_ts": 1694635200,
        "close_ts": 1694721600,
        "additional_metadata": {
            "name": "S&P 500 daily return on Sep 14",
            "title": "S&P 500 closes up by 0.02% or more",
            "yes_sub_title": "S&P 500 closes up 0.02%+",
            "no_sub_title": "S&P 500 closes up <0.02%",
            "event_ticker": "INXD-23SEP14",
            "strike_type": "greater",
            "floor_strike": 4487
        }
    }

    message = notifier._format_notification(event_data)

    assert "New Market Created" in message
    assert "INXD-23SEP14-B4487" in message
    assert "kalshi.com/markets/INXD-23SEP14-B4487" in message
    assert "S&P 500 daily return on Sep 14" in message
    assert "S&P 500 closes up by 0.02% or more" in message
    assert "S&P 500 closes up 0.02%+" in message
    assert "greater" in message
    assert "4487" in message


@pytest.mark.asyncio
async def test_send_notification_to_subscribers(mock_env, mock_telegram_bot):
    """Test sending notifications to all subscribed users."""
    notifier = TelegramNotifier()
    notifier.bot = mock_telegram_bot
    notifier.user_chat_ids = {111, 222, 333}

    event_data = {
        "event_type": "activated",
        "market_ticker": "TEST-MARKET"
    }

    await notifier.send_notification(event_data)

    # Verify send_message was called for each subscriber
    assert mock_telegram_bot.send_message.call_count == 3

    # Verify each subscriber got the message
    call_chat_ids = [
        call.kwargs["chat_id"]
        for call in mock_telegram_bot.send_message.call_args_list
    ]
    assert set(call_chat_ids) == {111, 222, 333}


@pytest.mark.asyncio
async def test_send_notification_no_subscribers(mock_env, mock_telegram_bot):
    """Test sending notification with no subscribers doesn't crash."""
    notifier = TelegramNotifier()
    notifier.bot = mock_telegram_bot
    notifier.user_chat_ids = set()

    event_data = {
        "event_type": "activated",
        "market_ticker": "TEST-MARKET"
    }

    await notifier.send_notification(event_data)

    # Verify no messages were sent
    mock_telegram_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_notification_no_bot_instance(mock_env):
    """Test sending notification without bot instance doesn't crash."""
    notifier = TelegramNotifier()
    notifier.bot = None
    notifier.user_chat_ids = {111}

    event_data = {
        "event_type": "activated",
        "market_ticker": "TEST-MARKET"
    }

    # Should not raise exception
    await notifier.send_notification(event_data)


@pytest.mark.asyncio
async def test_send_notification_handles_send_failure(mock_env, mock_telegram_bot):
    """Test notification sending handles failures gracefully."""
    notifier = TelegramNotifier()
    notifier.bot = mock_telegram_bot
    notifier.user_chat_ids = {111, 222}

    # Make send_message fail for one user
    async def send_with_error(chat_id, **kwargs):
        if chat_id == 111:
            raise Exception("Send failed")

    mock_telegram_bot.send_message.side_effect = send_with_error

    event_data = {
        "event_type": "activated",
        "market_ticker": "TEST-MARKET"
    }

    # Should not raise exception, should continue to next user
    await notifier.send_notification(event_data)

    # Verify both attempts were made
    assert mock_telegram_bot.send_message.call_count == 2
