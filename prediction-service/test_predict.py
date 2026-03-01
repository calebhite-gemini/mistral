"""
End-to-end test for POST /predict.
Requires MISTRAL_API_KEY in environment (or .env file).

Run:
    uv run python test_predict.py
"""
import asyncio
import json

from app.services.prediction import (
    MarketInput,
    ResearchBriefInput,
    PredictRequest,
    assemble_context,
    get_prediction,
)

SAMPLE_REQUEST = PredictRequest(
    market=MarketInput(
        market_id="NBA-LAL-GSW-2026-03-01",
        question="Will the Lakers beat the Warriors on March 1?",
        yes_price=0.58,
        no_price=0.42,
        closes_at="2026-03-01T20:00:00Z",
        sport="NBA",
        teams=["Lakers", "Warriors"],
        game_date="2026-03-01",
        volume=14200,
    ),
    research_brief=ResearchBriefInput(
        market_id="NBA-LAL-GSW-2026-03-01",
        key_factors=[
            "LeBron James listed as questionable with ankle soreness",
            "Warriors on second night of back-to-back after OT loss in Portland",
            "Lakers 8-2 at home this season",
            "Head-to-head: Lakers won 3 of last 4 matchups",
        ],
        injury_flags=["LeBron James - questionable (ankle)"],
        rest_advantage="Lakers (2 days rest) vs Warriors (0 days rest)",
        recent_form="Lakers 7-3 last 10, Warriors 5-5 last 10",
        sources=["ESPN injury report", "Rotoworld", "Beat reporter tweet"],
    ),
)


async def main():
    from dotenv import load_dotenv
    load_dotenv()

    print("=== Assembled Context ===")
    context = assemble_context(SAMPLE_REQUEST.market, SAMPLE_REQUEST.research_brief)
    print(context)

    print("\n=== Prediction ===")
    result = await get_prediction(context)
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
