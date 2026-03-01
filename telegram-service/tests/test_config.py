"""Tests for configuration management."""
import pytest
from pydantic import ValidationError

from app.config import Settings


def test_config_with_all_env_vars(mock_env):
    """Test configuration loads correctly with all environment variables."""
    settings = Settings()

    assert settings.telegram_bot_token == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    assert settings.kalshi_api_key == "test_api_key_12345"
    assert settings.kalshi_websocket_url == "wss://test.kalshi.com/ws/v2"
    assert settings.log_level == "DEBUG"


def test_config_with_default_values(monkeypatch):
    """Test configuration uses default values when optional vars not set."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("KALSHI_API_KEY", "test_key")
    monkeypatch.delenv("KALSHI_WEBSOCKET_URL", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = Settings()

    assert settings.telegram_bot_token == "test_token"
    assert settings.kalshi_api_key == "test_key"
    assert settings.kalshi_websocket_url == "wss://api.elections.kalshi.com/market_lifecycle_v2"
    assert settings.log_level == "INFO"


def test_config_missing_required_telegram_token(monkeypatch):
    """Test configuration fails when telegram token is missing."""
    monkeypatch.setenv("KALSHI_API_KEY", "test_key")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test_key")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "telegram_bot_token" in str(exc_info.value)


def test_config_missing_required_kalshi_key(monkeypatch):
    """Test configuration fails when Kalshi API key is missing."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test_key")
    monkeypatch.delenv("KALSHI_API_KEY", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "kalshi_api_key" in str(exc_info.value)


def test_config_case_insensitive(monkeypatch):
    """Test configuration accepts case-insensitive environment variables."""
    monkeypatch.setenv("telegram_bot_token", "test_token_lower")
    monkeypatch.setenv("KALSHI_API_KEY", "test_key_upper")

    settings = Settings()

    assert settings.telegram_bot_token == "test_token_lower"
    assert settings.kalshi_api_key == "test_key_upper"
