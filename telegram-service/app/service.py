"""Main service orchestration."""
import asyncio
import logging
import signal
from typing import Any

from app.telegram_bot import TelegramNotifier
from app.kalshi_client import KalshiWebSocketClient
from app.config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Main service that coordinates Kalshi WebSocket and Telegram bot."""

    def __init__(self):
        """Initialize the service."""
        self.telegram_notifier = TelegramNotifier()
        self.kalshi_client = KalshiWebSocketClient(on_market_created=self._handle_market_created)
        self.is_running = False

    async def _handle_market_created(self, event_data: dict[str, Any]) -> None:
        """Handle market creation events from Kalshi.

        Args:
            event_data: Market creation event data
        """
        market_ticker = event_data.get("market_ticker", "Unknown")
        logger.info(f"Market created: {market_ticker}")

        # Send notification via Telegram
        try:
            await self.telegram_notifier.send_notification(event_data)
        except Exception as e:
            logger.error(f"Failed to send notification for {market_ticker}: {e}", exc_info=True)

    async def start(self) -> None:
        """Start the service."""
        self.is_running = True
        logger.info("Starting Telegram Service for Kalshi Markets...")

        # Start Telegram bot
        await self.telegram_notifier.start()

        # Start Kalshi WebSocket client
        kalshi_task = asyncio.create_task(self.kalshi_client.connect())

        # Set up graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))

        try:
            await kalshi_task
        except asyncio.CancelledError:
            logger.info("Kalshi WebSocket task cancelled")

    async def stop(self) -> None:
        """Stop the service gracefully."""
        if not self.is_running:
            return

        logger.info("Stopping Telegram Service...")
        self.is_running = False

        # Stop Kalshi WebSocket client
        await self.kalshi_client.disconnect()

        # Stop Telegram bot
        await self.telegram_notifier.stop()

        logger.info("Telegram Service stopped")
