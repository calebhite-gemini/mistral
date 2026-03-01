# Database Schema

All tables live in Supabase. Run these in the SQL Editor when setting up a new project.

```sql
create table last_updated (
  job text primary key,
  updated_at timestamptz not null
);

create table markets (
  ticker text primary key,
  series_ticker text,
  event_ticker text,
  market_type text,
  yes_sub_title text,
  no_sub_title text,
  status text,
  result text,
  created_time timestamptz,
  updated_time timestamptz,
  open_time timestamptz,
  close_time timestamptz,
  latest_expiration_time timestamptz,
  expected_expiration_time timestamptz,
  settlement_timer_seconds integer,
  yes_bid_dollars text,
  yes_ask_dollars text,
  yes_bid_size_fp text,
  yes_ask_size_fp text,
  no_bid_dollars text,
  no_ask_dollars text,
  last_price_dollars text,
  previous_yes_bid_dollars text,
  previous_yes_ask_dollars text,
  previous_price_dollars text,
  notional_value_dollars text,
  volume integer,
  volume_24h integer,
  open_interest integer,
  can_close_early boolean,
  fractional_trading_enabled boolean,
  data jsonb,
  synced_at timestamptz
);

create table events (
  event_ticker text primary key,
  series_ticker text,
  title text,
  sub_title text,
  collateral_return_type text,
  mutually_exclusive boolean,
  available_on_brokers boolean,
  product_metadata jsonb,
  strike_date timestamptz,
  strike_period text,
  last_updated_ts timestamptz,
  markets jsonb,
  synced_at timestamptz
);

create table telegram_subscribers (
  chat_id bigint primary key
);
```
