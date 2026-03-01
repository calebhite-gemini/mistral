from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import edge

app = FastAPI(title="Edge Detection Service", version="0.1.0")
app.include_router(edge.router)


@app.get("/health")
def health():
    return {"status": "ok"}
