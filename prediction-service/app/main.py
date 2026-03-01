from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routers import predict

app = FastAPI(title="Prediction Service", version="0.1.0")
app.include_router(predict.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
