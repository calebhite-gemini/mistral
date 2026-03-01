from fastapi import APIRouter

from app.services.edge import EdgeRequest, EdgeResult, calculate_edge

router = APIRouter(prefix="/edge", tags=["edge"])


@router.post("", response_model=EdgeResult)
def edge(body: EdgeRequest) -> EdgeResult:
    return calculate_edge(body.model_prob, body.market_yes_price)
