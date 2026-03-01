# Sports Prediction Market Tool — Mistral AI Hackathon

## Project Overview

An autonomous sports prediction market tool that pulls live markets from Kalshi, researches them using Mistral's function calling, generates calibrated probability estimates, detects edges vs market price, and displays everything in a live dashboard.

## Architecture

```
Kalshi API → [Market Ingestion (8000)] → Supabase
                                      ↘
               [Kalshi Service (8003)] ← authenticated trading
                        ↓
              [Research Agent]  ← ⚠️ NOT IMPLEMENTED
                        ↓
           [Prediction Service (8001)] → Mistral LLM
                        ↓
             [Edge Service (8002)] → signal + EV + Kelly
                        ↓
              [Frontend (3000)] → Next.js dashboard
```

## Tech Stack

| Layer | Tool |
|---|---|
| Markets | Kalshi REST API (authenticated RSA-PSS) |
| Backend | FastAPI (Python), 4 microservices |
| LLM | Mistral Large via `mistralai` SDK |
| Frontend | Next.js 16 + React 19 + Tailwind CSS 4 |
| Storage | Supabase (PostgreSQL) |
| Package Mgmt | `uv` (Python), `npm` (Node) |

## Running the Stack

```bash
# Terminal 1 - Market Ingestion (port 8000, needs SUPABASE_URL + SUPABASE_KEY)
cd market-ingestion && uv sync && uv run python main.py

# Terminal 2 - Kalshi Service (port 8003, needs KALSHI_KEY_ID + KALSHI_PRIVATE_KEY_PEM)
cd kalshi-service && uv sync && uv run python main.py

# Terminal 3 - Prediction Service (port 8001, needs MISTRAL_API_KEY)
cd prediction-service && uv sync && uv run python main.py

# Terminal 4 - Edge Service (port 8002, no env vars needed)
cd edge-service && uv sync && uv run python main.py

# Terminal 5 - Frontend (port 3000)
cd web && npm install && npm run dev
```

---

## Component Status

### DONE - Market Ingestion Service (`market-ingestion/`, port 8000)

Fully working. Proxies Kalshi API for markets, events, and series. Background job syncs open markets to Supabase every 4 hours. Supports filtering by status, series_ticker, time ranges, and pagination.

Key endpoints: `GET /markets`, `GET /markets/{ticker}`, `GET /events`, `GET /series`, `GET /sports/series-tickers`, `GET /sports/event-tickers`.

### DONE - Kalshi Authenticated Service (`kalshi-service/`, port 8003)

Fully working. Wraps Kalshi trade API with RSA-PSS authentication. Handles order placement, portfolio queries, and a summary endpoint that computes aggregate stats (volume_24h, sentiment, active_markets, open_interest).

Key endpoints: `GET /markets`, `GET /markets/summary`, `GET /markets/{ticker}/orderbook`, `POST /orders`, `GET /orders`, `DELETE /orders/{order_id}`, `GET /portfolio/balance`, `GET /portfolio/positions`.

### DONE - Prediction Service (`prediction-service/`, port 8001)

Fully working. Implements both the **Context Assembler** (Component 3) and **Mistral Prediction Call** (Component 4). Takes a market object + research_brief as input, assembles a prompt, calls `mistral-large-latest` at temperature=0.2, returns `{ probability, confidence, key_drivers, reasoning }`. Has retry logic (2 attempts with feedback).

Key endpoint: `POST /predict` — expects `{ market: MarketInput, research_brief: ResearchBriefInput }`.

**Limitation:** Works correctly BUT requires a pre-assembled `research_brief` in the request body. There is currently no service that generates these research briefs automatically.

### DONE - Edge Detection Service (`edge-service/`, port 8002)

Fully working. Compares model probability to market price. Returns signal (BUY YES / BUY NO / NO EDGE at ±7% threshold), edge magnitude, EV on $1 bet, and Kelly criterion fraction.

Key endpoint: `POST /edge` — expects `{ model_prob: int, market_yes_price: float }`.

### DONE - Frontend Dashboard (`web/`, port 3000)

UI is complete and polished. Dark theme. Shows:
- **Header stats cards** — volume 24h, active markets, open interest, sentiment (fed from kalshi-service `/markets/summary`)
- **Markets table** — matchup (with team colors), closes-in countdown, market price, model prob, edge, EV, signal, confidence bar
- **Detail panel** — slide-out on row click showing implied prob, American odds, volume, sharp money, drivers, place bet / watchlist buttons
- **Sport filter tabs** — client-side filtering by league
- **Order placement** — wired up through `POST /api/orders` → kalshi-service

Team color mappings in `web/colors.js` cover NBA, NHL, NFL, MLB, NCAA, EPL (200+ teams).

### DONE - Telegram Notifications (`telegram-service/`)

Working. Listens to Kalshi WebSocket for market activation events, sends Telegram push notifications. Supports /start, /stop, /status commands. Subscriptions are in-memory only (not persisted). Not integrated into the main dashboard flow.

---

## NOT DONE — What Still Needs Building

### 1. Research Agent (CRITICAL — Component 2)

**This is the core missing piece.** The plan calls for a Mistral function-calling agent that autonomously decides what data to gather for each market.

**What needs to be built:**

A new service (or module within prediction-service) that:

1. **Implements 5 tool functions:**
   - `search_news(query, days_back)` — Search recent news via Tavily API. Returns titles + summaries.
   - `get_team_stats(team, stat_types)` — Current season stats from ESPN API: W/L record, PPG, defensive rating, home/away splits.
   - `get_injury_report(team)` — Latest injury report from ESPN. Player name, status, body part.
   - `get_head_to_head(team_a, team_b, num_games)` — Historical matchup results (this season + last 3).
   - `get_schedule(team, days_back, days_forward)` — Recent/upcoming schedule. Detects back-to-backs and rest days.

2. **Runs a Mistral agent loop:**
   - System prompt tells the agent it's a sports research analyst
   - Given a market question + teams, agent decides which tools to call
   - Uses Mistral's native function calling (tool_choice: "auto")
   - Loops until agent returns stop (max 8 tool calls as safety limit)
   - Parses output into a structured `ResearchBrief`:
     ```json
     {
       "market_id": "...",
       "key_factors": ["..."],
       "injury_flags": ["..."],
       "rest_advantage": "...",
       "recent_form": "...",
       "sources": ["ESPN", "Tavily"]
     }
     ```

3. **Data sources to integrate:**
   - ESPN API (free, no auth) — for team stats, injury reports, schedules, head-to-head
   - Tavily API (needs `TAVILY_API_KEY`) — for news search

**Where it fits:** The research agent output feeds directly into prediction-service's `POST /predict` as the `research_brief` field.

### 2. Frontend ↔ Prediction Integration (CRITICAL)

**Currently stubbed.** The frontend hardcodes model probability at 50% and confidence at "Low" for every market.

**What needs to be done:**

- In `web/lib/api/prediction.ts` — replace the stub with an actual call to `POST http://localhost:8001/predict`
- In `web/app/api/markets/route.ts` — for each market, call the research agent → then call prediction service → use real probability for edge calculation
- In `web/lib/transform/toMarketRow.ts` — remove hardcoded `modelProb: "50.0%"` and `confidence: "Low"`, use real values
- In `web/lib/transform/toMarketDetail.ts` — populate `drivers[]` from prediction key_drivers, populate `probChange`

**Note:** This depends on the Research Agent being built first, since prediction-service needs a research_brief to produce meaningful results.

### 3. Backtesting Framework (Component 6 — Demo Centerpiece)

**Not started at all.**

**What needs to be built:**

1. **Data collection script:**
   - Pull 50-100 resolved Kalshi sports markets via `GET /markets?status=resolved`
   - For each, run the full pipeline: research agent → prediction → edge detection
   - Record: `model_probability`, `market_price`, `actual_outcome`

2. **Metrics computation:**
   - **Accuracy** — when model says >60%, how often correct?
   - **ROI** — simulated returns if betting every flagged edge
   - **Brier Score** — calibration metric (lower = better)

3. **Calibration chart:**
   - X axis: model probability buckets (0-10%, 10-20%, ..., 90-100%)
   - Y axis: actual win rate per bucket
   - Well-calibrated model = bars match the diagonal

4. **Output:** Either a script that generates charts (matplotlib) or a page in the frontend.

### 4. Market Drivers & News in Detail Panel

The market detail panel (`web/components/MarketDetailPanel.tsx`) has a "Market Drivers & News" section that is currently empty. Once the research agent exists, pipe its `key_factors` and `sources` into the detail view so judges can see the agent's reasoning.

### 5. Portfolio Dashboard (Nice-to-have)

API endpoints exist (`GET /portfolio/balance`, `GET /portfolio/positions`) but there's no UI for them. Would be useful to show current positions, P&L, and account balance in the dashboard.

---

## Priority Order for Remaining Work

1. **Research Agent** — build the 5 tool functions + Mistral agent loop. This unblocks everything else.
2. **Frontend prediction integration** — wire up real predictions to replace stubs.
3. **Market drivers in detail panel** — pipe research findings into the UI.
4. **Backtesting** — run against resolved markets, generate calibration chart.
5. **Portfolio dashboard** — show positions and balance (nice-to-have).

---

## Environment Variables Needed

```
# Kalshi (already configured)
KALSHI_KEY_ID=...
KALSHI_PRIVATE_KEY_PEM=...

# Supabase (already configured)
SUPABASE_URL=...
SUPABASE_KEY=...

# Mistral (already configured)
MISTRAL_API_KEY=...

# Still needed for Research Agent:
TAVILY_API_KEY=...          # for search_news()
```

ESPN API is free and requires no auth.

## Key File Locations

| What | Where |
|---|---|
| Market ingestion router | `market-ingestion/app/routers/markets.py` |
| Kalshi auth logic | `kalshi-service/app/services/kalshi_auth.py` |
| Prediction context assembly | `prediction-service/app/services/prediction.py` |
| Edge calculation | `edge-service/app/services/edge.py` |
| Frontend API clients | `web/lib/api/clients.ts` |
| Prediction API stub (needs replacing) | `web/lib/api/prediction.ts` |
| Market row transform (has hardcoded stubs) | `web/lib/transform/toMarketRow.ts` |
| Market detail transform (empty drivers) | `web/lib/transform/toMarketDetail.ts` |
| Markets API route (orchestrates services) | `web/app/api/markets/route.ts` |
| Market detail API route | `web/app/api/markets/[ticker]/route.ts` |
| Team colors | `web/colors.js` |
