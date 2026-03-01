import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.agent import run_research_agent, run_research_agent_stream
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


@router.post("/stream")
async def research_stream(body: ResearchRequest):
    async def event_generator():
        try:
            async for event in run_research_agent_stream(body):
                event_type = event["event"]
                data_json = json.dumps(event["data"])
                yield f"event: {event_type}\ndata: {data_json}\n\n"
        except Exception as exc:
            error_data = json.dumps({"message": str(exc)})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
