from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import markets, orders, portfolio

app = FastAPI(title="Kalshi Service", version="0.1.0")
app.include_router(markets.router)
app.include_router(orders.router)
app.include_router(portfolio.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
