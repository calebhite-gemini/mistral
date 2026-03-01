#!/bin/bash
(cd market-ingestion && uv run python main.py) &
(cd prediction-service && uv run python main.py) &
(cd edge-service && uv run python main.py) &
(cd kalshi-service && uv run python main.py) &
(cd web && npm run dev) &
trap "kill 0" EXIT
wait
