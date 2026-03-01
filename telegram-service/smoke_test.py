"""Smoke test: sends a fake market notification to your real Telegram bot.

Usage:
    uv run python smoke_test.py

Then open Telegram and send /start to your bot. You'll receive a test notification.
Press Ctrl+C to stop.
"""
import asyncio
import logging

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import settings
from app.telegram_bot import TelegramNotifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SAMPLE_EVENT = {
    "event_type": "created",
    "market_ticker": "INXD-23SEP14-B4487",
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
        "floor_strike": 4487,
    },
}


async def main():
    notifier = TelegramNotifier()

    # Patch the start command to also send a test notification
    original_start = notifier._start_command

    async def start_and_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await original_start(update, context)
        chat_id = update.effective_chat.id
        logger.info(f"User {chat_id} subscribed — sending test notification...")
        await notifier.send_notification(SAMPLE_EVENT)
        logger.info("Test notification sent! Check your Telegram.")

    notifier._start_command = start_and_test

    await notifier.start()

    # Override the handler with our patched version
    notifier.application.handlers[0].clear()
    notifier.application.add_handler(CommandHandler("start", start_and_test))

    logger.info("Bot is running. Send /start to your bot in Telegram to receive a test notification.")
    logger.info("Press Ctrl+C to stop.")

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await notifier.stop()


if __name__ == "__main__":
    asyncio.run(main())
