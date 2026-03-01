import asyncio
import json
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from app.routers.sports import get_sports_event_tickers  # noqa: E402


SPORTS_TAGS = ["Basketball","Football"]


async def main():
    data = await get_sports_event_tickers(status="settled", tags=",".join(SPORTS_TAGS))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"settled_sports_events_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Wrote {len(data.get('event_tickers', []))} events to {filename}")


if __name__ == "__main__":
    asyncio.run(main())
