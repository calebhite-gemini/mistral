"""Telegram bot for sending notifications."""
import logging
from datetime import datetime, timezone
from typing import Any
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

from app.config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram bot for sending push notifications."""

    SUBSCRIBERS_TABLE = "telegram_subscribers"

    def __init__(self):
        """Initialize the Telegram bot."""
        self.bot_token = settings.telegram_bot_token
        self.bot: Bot | None = None
        self.application: Application | None = None
        self.user_chat_ids: set[int] = set()
        self.supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

    def _load_subscribers(self) -> None:
        """Load subscribers from Supabase."""
        try:
            result = (
                self.supabase.table(self.SUBSCRIBERS_TABLE)
                .select("chat_id")
                .execute()
            )
            self.user_chat_ids = {row["chat_id"] for row in result.data}
            logger.info(f"Loaded {len(self.user_chat_ids)} subscribers from Supabase")
        except Exception as e:
            logger.error(f"Failed to load subscribers from Supabase: {e}")

    def _add_subscriber(self, chat_id: int) -> None:
        """Add a subscriber to Supabase."""
        try:
            self.supabase.table(self.SUBSCRIBERS_TABLE).upsert(
                {"chat_id": chat_id}, on_conflict="chat_id"
            ).execute()
        except Exception as e:
            logger.error(f"Failed to save subscriber {chat_id} to Supabase: {e}")

    def _remove_subscriber(self, chat_id: int) -> None:
        """Remove a subscriber from Supabase."""
        try:
            self.supabase.table(self.SUBSCRIBERS_TABLE).delete().eq(
                "chat_id", chat_id
            ).execute()
        except Exception as e:
            logger.error(f"Failed to remove subscriber {chat_id} from Supabase: {e}")

    async def start(self) -> None:
        """Start the Telegram bot."""
        # Load existing subscribers from Supabase
        self._load_subscribers()

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
            event_data: Event data from Kalshi market creation

        Returns:
            Formatted notification message
        """
        market_ticker = event_data.get("market_ticker", "Unknown")
        metadata = event_data.get("additional_metadata", {})

        title = metadata.get("title", market_ticker)
        name = metadata.get("name", "")
        yes_sub = metadata.get("yes_sub_title", "")
        no_sub = metadata.get("no_sub_title", "")

        market_url = f"https://kalshi.com/markets/{market_ticker}"

        lines = [f"🎯 *New Market Created!*\n"]

        if name:
            lines.append(f"*{name}*")
        lines.append(f"_{title}_\n")

        if yes_sub or no_sub:
            lines.append(f"✅ Yes: {yes_sub}")
            lines.append(f"❌ No: {no_sub}\n")

        # Strike info
        strike_type = metadata.get("strike_type")
        floor_strike = metadata.get("floor_strike")
        cap_strike = metadata.get("cap_strike")
        if strike_type:
            strike_parts = [f"Strike: {strike_type}"]
            if floor_strike is not None:
                strike_parts.append(f"floor={floor_strike}")
            if cap_strike is not None:
                strike_parts.append(f"cap={cap_strike}")
            lines.append(" | ".join(strike_parts))

        # Timestamps
        open_ts = event_data.get("open_ts")
        close_ts = event_data.get("close_ts")
        if open_ts:
            open_dt = datetime.fromtimestamp(open_ts, tz=timezone.utc).strftime("%b %d, %Y %H:%M UTC")
            lines.append(f"Opens: {open_dt}")
        if close_ts:
            close_dt = datetime.fromtimestamp(close_ts, tz=timezone.utc).strftime("%b %d, %Y %H:%M UTC")
            lines.append(f"Closes: {close_dt}")

        lines.append(f"\n`{market_ticker}`")
        lines.append(f"[View on Kalshi]({market_url})")

        return "\n".join(lines)

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - subscribe user to notifications.

        Args:
            update: Telegram update object
            context: Telegram context
        """
        if update.effective_chat:
            chat_id = update.effective_chat.id
            self.user_chat_ids.add(chat_id)
            self._add_subscriber(chat_id)

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
            self._remove_subscriber(chat_id)

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
