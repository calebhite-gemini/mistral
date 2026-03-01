"""Main entry point for the Telegram service."""
import asyncio
import logging

from app.service import TelegramService
from app.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("telegram_service.log")
        ]
    )


async def main() -> None:
    """Run the Telegram service."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Initializing Telegram Service")

    service = TelegramService()

    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Service error: {e}", exc_info=True)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
