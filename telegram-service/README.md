# Kalshi Market Activation Telegram Bot

A Telegram bot service that listens to Kalshi's WebSocket API for market activation events and sends real-time push notifications to subscribed users.

## Features

- 🔌 Kalshi WebSocket integration with market lifecycle v2 channel
- ⚡ Real-time notifications when markets are activated
- 📱 Telegram bot for push notifications with clickable market links
- 👥 User subscription management (start/stop notifications)
- 🔄 Automatic reconnection on WebSocket disconnection
- 🛡️ Graceful shutdown handling

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- A Telegram account
- A Kalshi account with API access

## Setup Guide

### 1. Install Dependencies

First, ensure you have `uv` installed. Then install the project dependencies:

```bash
uv sync
```

### 2. Create a Telegram Bot

You need to create a Telegram bot and get its token:

1. Open Telegram and search for **@BotFather** (official Telegram bot)
2. Start a chat and send the command: `/newbot`
3. Follow the prompts:
   - Enter a **name** for your bot (e.g., "Kalshi Market Alerts")
   - Enter a **username** for your bot (must end in "bot", e.g., "kalshi_markets_bot")
4. BotFather will respond with your bot token that looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```
5. **Save this token** - you'll need it for the `.env` file

### 3. Get Your Kalshi API Key

You need a Kalshi API key to connect to their WebSocket:

1. Log in to [Kalshi](https://kalshi.com)
2. Navigate to your account settings
3. Go to the **API** section
4. Click **Generate New API Key**
5. **Copy the API key** - you'll need it for the `.env` file

> **Note:** Keep your API key secure and never share it publicly

### 4. Configure Environment Variables

Create your environment configuration file:

```bash
cp .env.example .env
```

Open `.env` in your text editor and fill in the required values:

```bash
# Required: Your Telegram bot token from BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789

# Required: Your Kalshi API key
KALSHI_API_KEY=your_kalshi_api_key_here

# Optional: Kalshi WebSocket URL (defaults to production if not set)
KALSHI_WEBSOCKET_URL=wss://api.elections.kalshi.com/trade-api/ws/v2

# Optional: Logging level (INFO, DEBUG, WARNING, ERROR)
LOG_LEVEL=INFO
```

**Required Environment Variables:**

| Variable | Description | Where to Get It |
|----------|-------------|-----------------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot authentication token | @BotFather on Telegram |
| `KALSHI_API_KEY` | Your Kalshi API authentication key | Kalshi account settings → API |

**Optional Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `KALSHI_WEBSOCKET_URL` | Kalshi WebSocket endpoint | `wss://api.elections.kalshi.com/trade-api/ws/v2` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### 5. Run the Service

Start the bot service:

```bash
python main.py
```

You should see output indicating:
- Telegram bot started
- Connected to Kalshi WebSocket
- Subscribed to market_lifecycle_v2 channel

## Usage

### Subscribing to Notifications

1. **Find your bot in Telegram:**
   - Search for the username you created (e.g., @kalshi_markets_bot)
   - Or use the link provided by BotFather

2. **Start the bot:**
   - Send `/start` to subscribe to market activation notifications
   - You'll receive a confirmation message

3. **Receive notifications:**
   - Whenever a market is activated on Kalshi, you'll get a push notification
   - Notifications include the market ticker and a clickable link

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Subscribe to market activation notifications |
| `/stop` | Unsubscribe from notifications |
| `/status` | Check your current subscription status |

### Example Notification

When a market is activated, you'll receive:

```
🎯 New Market Activated!

Market: PRES-2024-DEM

[View on Kalshi](https://kalshi.com/markets/PRES-2024-DEM)
```

Click the link to open the market directly on Kalshi.

## Architecture

- `main.py`: Entry point
- `app/service.py`: Main service orchestration
- `app/telegram_bot.py`: Telegram bot implementation
- `app/kalshi_client.py`: Kalshi WebSocket client for market lifecycle events
- `app/config.py`: Configuration management

## How It Works

1. The service connects to Kalshi's WebSocket API with authentication
2. Subscribes to the `market_lifecycle_v2` channel
3. Listens for `activated` events
4. When a market is activated, sends a Telegram notification to all subscribed users
5. Notification includes the market ticker and a clickable link to view on Kalshi

## Kalshi Event Format

The service receives market activation events in this format:
```json
{
  "type": "market_lifecycle_v2",
  "sid": 13,
  "msg": {
    "event_type": "activated",
    "market_ticker": "EXAMPLE-TICKER"
  }
}
```

## Troubleshooting

### Bot Not Starting

**Error: `telegram_bot_token field required`**
- Make sure you've created a `.env` file with `TELEGRAM_BOT_TOKEN` set
- Check that the token is correct (no extra spaces or quotes)

**Error: `kalshi_api_key field required`**
- Make sure your `.env` file has `KALSHI_API_KEY` set
- Verify the API key is valid and not expired

### WebSocket Connection Issues

**Error: `WebSocket error: 401 Unauthorized`**
- Your Kalshi API key is invalid or expired
- Generate a new API key from your Kalshi account

**Error: `WebSocket connection closed`**
- Normal behavior - the bot will automatically reconnect
- If it keeps failing, check your internet connection and Kalshi API status

### Not Receiving Notifications

1. Make sure you've sent `/start` to the bot
2. Check that the service is running (no errors in the console)
3. Verify the WebSocket connection is active (check logs)
4. Test by checking Kalshi manually for newly activated markets

## Development

### Running Tests
```bash
pytest
```

### Logging

Logs are written to:
- Console output (stdout)
- `telegram_service.log` file

Set `LOG_LEVEL=DEBUG` in `.env` for more detailed logs.

## Production Deployment

For production use, consider:

1. **Persist user subscriptions** - Currently stored in memory, will be lost on restart
2. **Use a process manager** - e.g., systemd, supervisor, or PM2
3. **Set up monitoring** - Track uptime and errors
4. **Secure your API keys** - Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
5. **Rate limiting** - Implement rate limiting for Telegram API calls if you have many users

### Example systemd Service

Create `/etc/systemd/system/kalshi-telegram-bot.service`:

```ini
[Unit]
Description=Kalshi Market Activation Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/telegram-service
Environment=PATH=/path/to/.venv/bin
ExecStart=/path/to/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable kalshi-telegram-bot
sudo systemctl start kalshi-telegram-bot
```

## Notes

- The bot automatically reconnects if the WebSocket connection is lost
- All subscribed users receive notifications for each activated market
- User subscriptions are stored in memory (lost on restart - persist to database for production)
- The service only listens for `activated` events; other lifecycle events (`deactivated`, `settled`, etc.) are ignored
