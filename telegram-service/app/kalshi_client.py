"""Kalshi WebSocket client for market lifecycle events."""
import asyncio
import json
import logging
import ssl
from typing import Callable, Any
import certifi
import websockets

from app.config import settings

logger = logging.getLogger(__name__)


class KalshiWebSocketClient:
    """WebSocket client for Kalshi market lifecycle events."""

    def __init__(self, on_market_created: Callable[[dict], None]):
        """Initialize the Kalshi WebSocket client.

        Args:
            on_market_created: Async callback for market creation events
        """
        self.url = settings.kalshi_websocket_url
        self.api_key = settings.kalshi_api_key
        self.on_market_created = on_market_created
        self.websocket: websockets.ClientConnection | None = None
        self.is_running = False
        self.message_id = 0

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for WebSocket connection.

        Returns:
            Dictionary of headers for authentication
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    async def connect(self) -> None:
        """Establish WebSocket connection and listen for events."""
        self.is_running = True

        while self.is_running:
            try:
                logger.info(f"Connecting to Kalshi WebSocket: {self.url}")

                # Connect with authentication headers
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                async with websockets.connect(
                    self.url,
                    additional_headers=self._get_auth_headers(),
                    ssl=ssl_context,
                ) as websocket:
                    self.websocket = websocket
                    logger.info("Kalshi WebSocket connected successfully")

                    # Subscribe to market lifecycle channel
                    await self._subscribe_to_market_lifecycle()

                    # Listen for events
                    await self._listen()

            except websockets.exceptions.WebSocketException as e:
                logger.error(f"Kalshi WebSocket error: {e}")
                if self.is_running:
                    logger.info("Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                if self.is_running:
                    logger.info("Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)

    async def _subscribe_to_market_lifecycle(self) -> None:
        """Subscribe to the market_lifecycle_v2 channel."""
        if not self.websocket:
            return

        self.message_id += 1
        subscribe_message = {
            "id": self.message_id,
            "cmd": "subscribe",
            "params": {
                "channels": ["market_lifecycle_v2"]
            }
        }

        await self.websocket.send(json.dumps(subscribe_message))
        logger.info("Subscribed to market_lifecycle_v2 channel")

    async def _listen(self) -> None:
        """Listen for incoming WebSocket messages."""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                logger.debug(f"Received message: {message}")
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Kalshi WebSocket connection closed")

    async def _handle_message(self, message: str) -> None:
        """Process incoming WebSocket message.

        Args:
            message: Raw message from WebSocket
        """
        try:
            data = json.loads(message)

            # Check if this is a market lifecycle event
            if data.get("type") == "market_lifecycle_v2":
                msg = data.get("msg", {})
                event_type = msg.get("event_type")

                logger.info(f"Market lifecycle event: {event_type} for {msg.get('market_ticker')}")

                # Handle market creation events
                if event_type == "created":
                    await self.on_market_created(msg)

            # Log subscription confirmations
            elif "id" in data and "type" in data:
                logger.debug(f"Response to command {data.get('id')}: {data}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message as JSON: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Kalshi WebSocket disconnected")
