import asyncio
import json
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from app.routers.historical import list_historical_markets  # noqa: E402


JSON_FILE = "settled_sports_events_20260301_031142.json"
BATCH_SIZE = 10
BATCH_DELAY_SECONDS = 1

async def main():
    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    event_tickers = [e["event_ticker"] for e in data.get("event_tickers", [])]
    print(f"Loaded {len(event_tickers)} event tickers from {JSON_FILE}")

    all_markets = []
    failed_batches = []

    for i in range(0, len(event_tickers), BATCH_SIZE):
        batch = event_tickers[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(event_tickers) + BATCH_SIZE - 1) // BATCH_SIZE

        try:
            print(f"[batch {batch_num}/{total_batches}] fetching markets for {len(batch)} event tickers...")
            result = await list_historical_markets(event_ticker=",".join(batch))
            markets = result.get("markets", [])
            all_markets.extend(markets)
            print(f"[batch {batch_num}/{total_batches}] got {len(markets)} markets (total: {len(all_markets)})")
        except Exception as e:
            print(f"[batch {batch_num}/{total_batches}] FAILED: {e}")
            failed_batches.append({"batch": batch_num, "event_tickers": batch, "error": str(e)})
            _write_partial(all_markets, failed_batches)
            print(f"Wrote partial results ({len(all_markets)} markets) due to failure. Continuing...")

        if i + BATCH_SIZE < len(event_tickers):
            await asyncio.sleep(BATCH_DELAY_SECONDS)

    _write_partial(all_markets, failed_batches)

    if failed_batches:
        print(f"Done with {len(failed_batches)} failed batch(es). Check output for details.")
    else:
        print(f"Done. {len(all_markets)} markets exported.")


def _write_partial(markets, failed_batches):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"settled_sports_markets_{timestamp}.json"

    output = {"markets": markets}
    if failed_batches:
        output["failed_batches"] = failed_batches

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(markets)} markets to {filename}")


if __name__ == "__main__":
    asyncio.run(main())
