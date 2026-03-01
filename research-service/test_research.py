"""
End-to-end test for the research agent.
Requires MISTRAL_API_KEY and TAVILY_API_KEY in environment (or .env file).

Run:
    uv run python test_research.py
"""

import asyncio
import json

from app.services.agent import run_research_agent
from app.services.schemas import ResearchRequest

SAMPLE_REQUEST = ResearchRequest(
    market_id="NBA-LAL-GSW-2026-03-01",
    question="Will the Lakers beat the Warriors on March 1?",
    sport="NBA",
    teams=["Lakers", "Warriors"],
    game_date="2026-03-01",
)


async def main():
    from dotenv import load_dotenv

    load_dotenv()

    print("=== Running Research Agent ===")
    print(f"Market: {SAMPLE_REQUEST.question}")
    print(f"Teams: {', '.join(SAMPLE_REQUEST.teams)}")
    print()

    result = await run_research_agent(SAMPLE_REQUEST)

    print("=== Research Brief ===")
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
