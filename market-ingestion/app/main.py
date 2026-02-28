from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import events  # noqa: E402

app = FastAPI(title="Market Ingestion Service", version="0.1.0")
app.include_router(events.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
