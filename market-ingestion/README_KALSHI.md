# Kalshi API Reference

## Base URLs

| Environment | URL |
|---|---|
| Production REST | `https://api.elections.kalshi.com/trade-api/v2` |
| Demo REST | `https://demo-api.kalshi.co/trade-api/v2` |
| Production WebSocket | `wss://api.elections.kalshi.com/trade-api/ws/v2` |
| Demo WebSocket | `wss://demo-api.kalshi.co/trade-api/ws/v2` |

> **Note:** Despite the "elections" subdomain, the production URL provides access to **all** Kalshi markets — not just election-related ones.

---

## Rate Limits

| Tier | Read | Write | Qualification |
|---|---|---|---|
| Basic | 20/sec | 10/sec | Complete signup |
| Advanced | 30/sec | 30/sec | Apply via [form](https://kalshi.typeform.com/advanced-api) |
| Premier | 100/sec | 100/sec | 3.75% of exchange volume/month + technical review |
| Prime | 400/sec | 400/sec | 7.5% of exchange volume/month + technical review |

Write-limited endpoints: `CreateOrder`, `CancelOrder`, `AmendOrder`, `DecreaseOrder`, `BatchCreateOrders`, `BatchCancelOrders`. For batch APIs, each item counts as 1 transaction (except `BatchCancelOrders` where each cancel = 0.2 transactions).

Exceeding limits returns HTTP `429`. Implement exponential backoff.

---

## Public Endpoints (No API Key Required)

Available on both production and demo environments.

### GET /markets

List and discover markets. Returns paginated results.

| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | Optional | Results per page (1–1000, default 100) |
| `cursor` | string | Optional | Pagination cursor from previous response |
| `event_ticker` | string | Optional | Filter by event ticker (comma-separated, max 10) |
| `series_ticker` | string | Optional | Filter by series ticker |
| `status` | string | Optional | `open`, `closed`, `settled` |
| `tickers` | string | Optional | Comma-separated list of specific market tickers |
| `max_close_ts` | int | Optional | Markets closing before this Unix timestamp |
| `min_close_ts` | int | Optional | Markets closing after this Unix timestamp |

### GET /markets/{ticker}

Get detailed data for a single market by its ticker.

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | **Required** | Market ticker (path param) |

### GET /markets/{ticker}/orderbook

Get the current order book for a specific market.

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | **Required** | Market ticker (path param) |
| `depth` | int | Optional | Orderbook depth (0 = all levels, 1–100 for specific depth) |

### GET /markets/{ticker}/candlesticks

Get OHLC candlestick data for a market.

| Param | Type | Required | Description |
|---|---|---|---|
| `ticker` | string | **Required** | Series ticker (path param) |
| `market_ticker` | string | **Required** | Market ticker |
| `start_ts` | int | Optional | Start Unix timestamp |
| `end_ts` | int | Optional | End Unix timestamp |
| `period_interval` | string | Optional | Interval (e.g. `1m`, `5m`, `1h`, `1d`) |

### GET /markets/candlesticks

Get candlestick data for multiple markets in a single call. Supports up to 10,000 candlesticks total.

### GET /events

List and discover events. Returns paginated results.

| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | Optional | Results per page (default 100) |
| `cursor` | string | Optional | Pagination cursor |
| `status` | string | Optional | `open`, `closed`, `settled` |
| `series_ticker` | string | Optional | Filter by series ticker |
| `with_nested_markets` | bool | Optional | Include full market data nested in each event |
| `with_milestones` | bool | Optional | Include milestones |
| `min_close_ts` | int | Optional | Events closing after this Unix timestamp |

### GET /events/{event_ticker}

Get detailed data for a single event.

| Param | Type | Required | Description |
|---|---|---|---|
| `event_ticker` | string | **Required** | Event ticker (path param) |
| `with_nested_markets` | bool | Optional | Include full market data for all markets in the event |

### GET /events/multivariate

Retrieve multivariate (combo) events.

| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | Optional | Results per page |
| `cursor` | string | Optional | Pagination cursor |
| `series_ticker` | string | Optional | Filter by series |
| `collection_ticker` | string | Optional | Filter by collection |
| `with_nested_markets` | bool | Optional | Include nested market data |

### GET /series/{series_ticker}

Get data about a specific series (recurring event template).

| Param | Type | Required | Description |
|---|---|---|---|
| `series_ticker` | string | **Required** | Series ticker (path param) |

### GET /trades

Get all public trades across all markets. Returns paginated results.

| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | Optional | Results per page (1–1000, default 100) |
| `cursor` | string | Optional | Pagination cursor |
| `ticker` | string | Optional | Filter by market ticker |
| `min_ts` | int | Optional | Trades after this Unix timestamp |
| `max_ts` | int | Optional | Trades before this Unix timestamp |

### GET /historical/cutoff

Returns cutoff timestamps defining the boundary between live and historical data tiers.

### GET /historical/markets

Get historical market data (markets settled before the cutoff timestamp).

### GET /historical/markets/{ticker}/candlesticks

Get historical candlestick data for settled markets.

---

## Authenticated Endpoints (API Key Required)

Require `KALSHI-ACCESS-KEY`, `KALSHI-ACCESS-SIGNATURE`, and `KALSHI-ACCESS-TIMESTAMP` headers. Available on both production and demo.

### Portfolio — Read

#### GET /portfolio/balance

Get account balance. Supports optional `subaccount` query param.

#### GET /portfolio/positions

Get your current positions.

| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | Optional | Results per page |
| `cursor` | string | Optional | Pagination cursor |
| `event_ticker` | string | Optional | Filter by event ticker |
| `status` | string | Optional | Filter by position status |

#### GET /portfolio/orders

Get your orders.

| Param | Type | Required | Description |
|---|---|---|---|
| `limit` | int | Optional | Results per page |
| `cursor` | string | Optional | Pagination cursor |
| `event_ticker` | string | Optional | Filter by event ticker (comma-separated) |
| `ticker` | string | Optional | Filter by market ticker |
| `status` | string | Optional | Filter by order status |

#### GET /portfolio/fills

Get your fill history.

#### GET /portfolio/settlements

Get your settlement history. Includes sum of trade fees paid.

### Portfolio — Write

These endpoints count against the **write** rate limit.

#### POST /portfolio/orders

Place a new order.

#### DELETE /portfolio/orders/{order_id}

Cancel a specific order.

#### PUT /portfolio/orders/{order_id}/amend

Amend an existing order.

#### PUT /portfolio/orders/{order_id}/decrease

Decrease an existing order's size.

#### POST /portfolio/orders/batched

Batch create multiple orders. Each item counts as 1 write transaction.

#### DELETE /portfolio/orders/batched

Batch cancel multiple orders. Each cancel counts as 0.2 write transactions.

---

## WebSocket Channels (API Key Required)

All WebSocket connections require authentication via API key headers during the handshake. Available on both production and demo.

### Subscribing

```json
{
  "id": 1,
  "cmd": "subscribe",
  "params": {
    "channels": ["orderbook_delta"],
    "market_ticker": "CPI-22DEC-TN0.1"
  }
}
```

### Available Channels

| Channel | Description | Market-Specific |
|---|---|---|
| `orderbook_delta` | Real-time orderbook changes | Yes |
| `ticker` | Market price/volume updates | Yes |
| `trade` | Public trade notifications | Optional (omit for all trades) |
| `fill` | Your personal order fills | Optional (omit for all fills) |
| `market_positions` | Your position updates | Yes |
| `market_lifecycle` | Market/event status changes (open, closed, settled, determined) | Yes |
| `multivariate_lookups` | Multivariate event lookups | — |
| `communications` | RFQ and quote notifications | No (receives all) |
| `order_group_updates` | Order group status updates | — |
| `user_orders` | Your order updates | — |

### Managing Subscriptions

```json
// Add markets to existing subscription
{
  "id": 124,
  "cmd": "update_subscription",
  "params": {
    "sids": [456],
    "market_tickers": ["NEW-MARKET-1", "NEW-MARKET-2"],
    "action": "add_markets"
  }
}

// List current subscriptions
{ "id": 3, "cmd": "list_subscriptions" }

// Unsubscribe
{ "id": 124, "cmd": "unsubscribe", "params": { "sids": [1, 2] } }
```

> **Note:** There is no WebSocket channel for streaming new events or markets being created. To discover new events, poll `GET /events?status=open` via REST.

---

## Authentication

For authenticated endpoints, every request must include three headers:

| Header | Description |
|---|---|
| `KALSHI-ACCESS-KEY` | Your API key ID |
| `KALSHI-ACCESS-SIGNATURE` | RSA-PSS signature of the request |
| `KALSHI-ACCESS-TIMESTAMP` | Request timestamp in milliseconds |

The signature is computed over `timestamp + method + path` using your RSA private key with PSS padding and SHA-256.

---

## Market Data Model

Each market object returned from the API includes:

**Identity:** `ticker`, `event_ticker`, `market_type`, `title`, `subtitle`, `yes_sub_title`, `no_sub_title`, `status`, `result`

**Timestamps:** `created_time`, `updated_time`, `open_time`, `close_time`, `expiration_time`, `latest_expiration_time`, `settlement_timer_seconds`

**Pricing:** `yes_bid` / `yes_bid_dollars`, `yes_ask` / `yes_ask_dollars`, `no_bid` / `no_bid_dollars`, `no_ask` / `no_ask_dollars`, `last_price` / `last_price_dollars`

**Volume:** `volume` / `volume_fp`, `volume_24h` / `volume_24h_fp`, `open_interest`

**Features:** `can_close_early`, `fractional_trading_enabled`, `response_price_units`

> **Deprecation notes:**
> - `liquidity` and `liquidity_dollars` fields are deprecated (return 0).
> - Integer count fields with an `_fp` equivalent are being phased out. Prefer `_fp` (fixed-point) fields.
> - Dollar-denominated string fields (e.g. `yes_bid_dollars`) provide sub-penny precision at 4 decimal places.