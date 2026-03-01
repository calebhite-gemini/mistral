#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

clear_db() {
  echo "Clearing markets and last_updated tables..."
  uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
r1 = sb.table('markets').delete().neq('ticker', '').execute()
print(f'  Deleted {len(r1.data)} rows from markets')
r2 = sb.table('last_updated').delete().neq('job', '').execute()
print(f'  Deleted {len(r2.data)} rows from last_updated')
"
  echo "Done."
}

sync_open_markets_once() {
  echo "Running sync_once..."
  uv run python -c "
import asyncio
from app.jobs.sync_open_markets import sync_once
asyncio.run(sync_once())
"
  echo "Done."
}

# Run function by name if passed as argument
if [[ $# -gt 0 ]]; then
  "$@"
fi
