from fastapi import APIRouter, HTTPException

from app.services.prediction import (
    PredictRequest,
    PredictionOutput,
    assemble_context,
    get_prediction,
)

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("", response_model=PredictionOutput)
async def predict(body: PredictRequest) -> PredictionOutput:
    context = assemble_context(body.market, body.research_brief)
    try:
        return await get_prediction(context)
    except EnvironmentError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
