# kalshi-service

Authenticated service layer between the MARKETEDGE frontend and the Kalshi trade API. Runs on port **8003**.

## Setup

```bash
uv sync
cp .env.example .env   # fill in your credentials
uv run python main.py
```

## Environment Variables

Create a `.env` file in this directory:

```
KALSHI_KEY_ID=your-key-id
KALSHI_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----
<your RSA private key content>
-----END PRIVATE KEY-----"
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/markets` | List markets (`limit`, `cursor`, `status`, `series_ticker`, `min_close_ts`) |
| GET | `/markets/summary` | Header card stats: volume, active markets, open interest, sentiment |
| GET | `/markets/{ticker}` | Single market detail |
| GET | `/markets/{ticker}/orderbook` | Orderbook depth |
| POST | `/orders` | Place order |
| GET | `/orders` | List orders |
| DELETE | `/orders/{order_id}` | Cancel order |
| GET | `/portfolio/balance` | Account balance |
| GET | `/portfolio/positions` | Current positions |

## Place Order

```json
POST /orders
{
  "ticker": "KXNBA-25FEB28-LAL",
  "side": "yes",
  "type": "limit",
  "count": 10,
  "yes_price": 48
}
```

`yes_price` (1–99 cents) is required for limit orders; omit for market orders.

## Swagger UI

`http://localhost:8003/docs`
