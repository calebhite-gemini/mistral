"""Configuration management for the Telegram service."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Telegram configuration
    telegram_bot_token: str

    # Kalshi WebSocket configuration
    kalshi_websocket_url: str = "wss://api.elections.kalshi.com/trade-api/ws/v2"
    kalshi_api_key: str

    # Optional settings
    log_level: str = "INFO"


settings = Settings()
