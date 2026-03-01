import importlib

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import events, historical, markets, series, sports  # noqa: E402

historical_extended = importlib.import_module("app.routers.historical-extended")

app = FastAPI(title="Market Ingestion Service", version="0.1.0")
app.include_router(events.router)
app.include_router(historical.router)
app.include_router(markets.router)
app.include_router(historical_extended.router)
app.include_router(series.router)
app.include_router(sports.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
