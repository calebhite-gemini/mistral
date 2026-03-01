from fastapi import APIRouter, HTTPException

from app.services.agent import run_research_agent
from app.services.schemas import ResearchBriefOutput, ResearchRequest

router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchBriefOutput)
async def research(body: ResearchRequest) -> ResearchBriefOutput:
    try:
        return await run_research_agent(body)
    except EnvironmentError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Research agent failed: {exc}")
