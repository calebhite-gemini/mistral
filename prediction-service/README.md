# Prediction Service

Takes a structured market object + research brief from Components 1 & 2, assembles a prediction prompt, and makes a single deterministic Mistral call to return a calibrated probability.

**Port:** `8001`

---

## Setup

```bash
cd prediction-service
uv sync
```

Create a `.env` file:

```
MISTRAL_API_KEY=your_key_here
```

---

## Run

```bash
uv run python main.py
```

Swagger UI: `http://localhost:8001/docs`

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/predict` | Assemble context + call Mistral |

---

## Testing

### 1. Smoke test (no server needed)

Runs the full pipeline — assembler + live Mistral call — directly from the CLI:

```bash
uv run python test_predict.py
```

Prints the assembled context first, then the prediction JSON.

---

### 2. Health check

```bash
curl http://localhost:8001/health
# {"status":"ok"}
```

---

### 3. Full prediction via curl

```bash
curl -s -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "market": {
      "market_id": "NBA-LAL-GSW-2026-03-01",
      "question": "Will the Lakers beat the Warriors on March 1?",
      "yes_price": 0.58,
      "no_price": 0.42,
      "closes_at": "2026-03-01T20:00:00Z",
      "sport": "NBA",
      "teams": ["Lakers", "Warriors"],
      "game_date": "2026-03-01",
      "volume": 14200
    },
    "research_brief": {
      "market_id": "NBA-LAL-GSW-2026-03-01",
      "key_factors": [
        "LeBron James listed as questionable with ankle soreness",
        "Warriors on second night of back-to-back after OT loss in Portland",
        "Lakers 8-2 at home this season",
        "Head-to-head: Lakers won 3 of last 4 matchups"
      ],
      "injury_flags": ["LeBron James - questionable (ankle)"],
      "rest_advantage": "Lakers (2 days rest) vs Warriors (0 days rest)",
      "recent_form": "Lakers 7-3 last 10, Warriors 5-5 last 10",
      "sources": ["ESPN injury report", "Rotoworld"]
    }
  }' | python3 -m json.tool
```

Expected response shape:

```json
{
  "probability": 65,
  "confidence": "medium",
  "key_drivers": ["LeBron questionable", "Warriors back-to-back fatigue"],
  "reasoning": "The Lakers hold a meaningful rest advantage and have the better recent form. LeBron's injury status is the key variable — if he plays, the implied probability is higher than the market price suggests."
}
```

---

### 4. Error paths

**Missing API key** — remove `MISTRAL_API_KEY` from `.env` and restart:
```bash
curl -s -X POST http://localhost:8001/predict -H "Content-Type: application/json" -d '{...}'
# HTTP 500: "MISTRAL_API_KEY is not set"
```

**Bad request body:**
```bash
curl -s -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"market": {}, "research_brief": {}}'
# HTTP 422: validation error listing missing fields
```

---

## Response Schema

| Field | Type | Description |
|---|---|---|
| `probability` | `int` (0–100) | Model's estimated YES probability |
| `confidence` | `"low"` \| `"medium"` \| `"high"` | Model's self-reported confidence |
| `key_drivers` | `list[str]` | Top factors driving the estimate |
| `reasoning` | `str` | 2–3 sentence explanation |
