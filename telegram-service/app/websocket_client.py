"""WebSocket client for listening to events."""
import asyncio
import logging
from typing import Callable, Any
import websockets
from websockets.client import WebSocketClientProtocol

from app.config import settings

logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket client that listens for events and triggers callbacks."""

    def __init__(self, on_event_callback: Callable[[dict], None]):
        """Initialize the WebSocket client.

        Args:
            on_event_callback: Async callback function to handle incoming events
        """
        self.url = settings.websocket_url
        self.on_event_callback = on_event_callback
        self.websocket: WebSocketClientProtocol | None = None
        self.is_running = False

    async def connect(self) -> None:
        """Establish WebSocket connection and listen for events."""
        self.is_running = True

        while self.is_running:
            try:
                logger.info(f"Connecting to WebSocket: {self.url}")
                async with websockets.connect(self.url) as websocket:
                    self.websocket = websocket
                    logger.info("WebSocket connected successfully")

                    await self._listen()

            except websockets.exceptions.WebSocketException as e:
                logger.error(f"WebSocket error: {e}")
                if self.is_running:
                    logger.info("Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if self.is_running:
                    logger.info("Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)

    async def _listen(self) -> None:
        """Listen for incoming WebSocket messages."""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                logger.debug(f"Received message: {message}")
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")

    async def _handle_message(self, message: str) -> None:
        """Process incoming WebSocket message.

        Args:
            message: Raw message from WebSocket
        """
        try:
            # Parse the message (assuming JSON)
            import json
            event_data = json.loads(message)

            # Trigger the callback
            await self.on_event_callback(event_data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message as JSON: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket disconnected")
