from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import research

app = FastAPI(title="Research Agent Service", version="0.1.0")
app.include_router(research.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
