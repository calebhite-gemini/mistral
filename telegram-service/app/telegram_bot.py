"""Telegram bot for sending notifications."""
import logging
from typing import Any
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram bot for sending push notifications."""

    def __init__(self):
        """Initialize the Telegram bot."""
        self.bot_token = settings.telegram_bot_token
        self.bot: Bot | None = None
        self.application: Application | None = None
        self.user_chat_ids: set[int] = set()

    async def start(self) -> None:
        """Start the Telegram bot."""
        # Build the application
        self.application = Application.builder().token(self.bot_token).build()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("stop", self._stop_command))
        self.application.add_handler(CommandHandler("status", self._status_command))

        # Initialize the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        self.bot = self.application.bot
        logger.info("Telegram bot started")

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")

    async def send_notification(self, event_data: dict[str, Any]) -> None:
        """Send notification to all subscribed users.

        Args:
            event_data: Event data from WebSocket
        """
        if not self.bot or not self.user_chat_ids:
            logger.warning("No bot instance or no subscribed users")
            return

        # Format the notification message
        message = self._format_notification(event_data)

        # Send to all subscribed users
        for chat_id in self.user_chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="Markdown"
                )
                logger.info(f"Notification sent to chat_id: {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send notification to {chat_id}: {e}")

    def _format_notification(self, event_data: dict[str, Any]) -> str:
        """Format event data into a notification message.

        Args:
            event_data: Event data from Kalshi market activation

        Returns:
            Formatted notification message
        """
        market_ticker = event_data.get("market_ticker", "Unknown")

        # Create a clickable link to the market
        market_url = f"https://kalshi.com/markets/{market_ticker}"

        return (
            f"🎯 *New Market Activated!*\n\n"
            f"Market: `{market_ticker}`\n\n"
            f"[View on Kalshi]({market_url})"
        )

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - subscribe user to notifications.

        Args:
            update: Telegram update object
            context: Telegram context
        """
        if update.effective_chat:
            chat_id = update.effective_chat.id
            self.user_chat_ids.add(chat_id)

            await update.message.reply_text(
                "✅ You are now subscribed to notifications!\n\n"
                "Commands:\n"
                "/start - Subscribe to notifications\n"
                "/stop - Unsubscribe from notifications\n"
                "/status - Check subscription status"
            )
            logger.info(f"User {chat_id} subscribed to notifications")

    async def _stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stop command - unsubscribe user from notifications.

        Args:
            update: Telegram update object
            context: Telegram context
        """
        if update.effective_chat:
            chat_id = update.effective_chat.id
            self.user_chat_ids.discard(chat_id)

            await update.message.reply_text(
                "❌ You have been unsubscribed from notifications."
            )
            logger.info(f"User {chat_id} unsubscribed from notifications")

    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command - show subscription status.

        Args:
            update: Telegram update object
            context: Telegram context
        """
        if update.effective_chat:
            chat_id = update.effective_chat.id
            is_subscribed = chat_id in self.user_chat_ids

            status = "✅ Subscribed" if is_subscribed else "❌ Not subscribed"
            await update.message.reply_text(
                f"Status: {status}\n\n"
                f"Total subscribers: {len(self.user_chat_ids)}"
            )
