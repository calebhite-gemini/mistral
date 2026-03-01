"""
Component 3: Context Assembler
Component 4: Mistral Prediction Call
"""
from __future__ import annotations

import json
import os
from typing import Literal

from mistralai import Mistral
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Input / output models
# ---------------------------------------------------------------------------

class MarketInput(BaseModel):
    market_id: str
    question: str
    yes_price: float = Field(ge=0.0, le=1.0)
    no_price: float = Field(ge=0.0, le=1.0)
    closes_at: str
    sport: str
    teams: list[str]
    game_date: str
    volume: int = Field(ge=0)


class ResearchBriefInput(BaseModel):
    market_id: str
    key_factors: list[str]
    injury_flags: list[str]
    rest_advantage: str
    recent_form: str
    sources: list[str]


class PredictRequest(BaseModel):
    market: MarketInput
    research_brief: ResearchBriefInput


class PredictionOutput(BaseModel):
    probability: int = Field(ge=0, le=100)
    confidence: Literal["low", "medium", "high"]
    key_drivers: list[str]
    reasoning: str


# ---------------------------------------------------------------------------
# Component 3: Context Assembler
# ---------------------------------------------------------------------------

def assemble_context(market: MarketInput, research_brief: ResearchBriefInput) -> str:
    injury_str = ", ".join(research_brief.injury_flags) or "None reported"
    factors_str = "\n".join(f"  - {f}" for f in research_brief.key_factors)
    return (
        f"Market Question: {market.question}\n"
        f"Current Market Price (YES): {market.yes_price}\n"
        f"\nResearch Brief:\n"
        f"- Rest: {research_brief.rest_advantage}\n"
        f"- Recent Form: {research_brief.recent_form}\n"
        f"- Injuries: {injury_str}\n"
        f"- Key Factors:\n{factors_str}\n"
        f"\nRespond ONLY with a JSON object using exactly these keys: "
        f"probability (integer 0-100), confidence (low/medium/high), "
        f"key_drivers (list of strings), reasoning (2-3 sentence string)."
    )


# ---------------------------------------------------------------------------
# Component 4: Mistral Prediction Call
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are a calibrated sports prediction model. "
    "Always respond in valid JSON with no markdown fences, no commentary outside JSON."
)

_MODEL = "mistral-large-latest"
_TEMPERATURE = 0.2
_MAX_RETRIES = 2


async def get_prediction(context: str) -> PredictionOutput:
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("MISTRAL_API_KEY is not set")

    client = Mistral(api_key=api_key)
    last_error: Exception | None = None
    raw_text = ""

    for attempt in range(1, _MAX_RETRIES + 1):
        response = await client.chat.complete_async(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=_TEMPERATURE,
        )
        raw_text = response.choices[0].message.content.strip()
        cleaned = _strip_fences(raw_text)

        try:
            data = json.loads(cleaned)
            return PredictionOutput(**data)
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            last_error = exc
            if attempt < _MAX_RETRIES:
                context = (
                    context
                    + f"\n\nYour previous response was malformed: {raw_text!r}\n"
                    "Try again. Return ONLY valid JSON."
                )

    raise ValueError(
        f"Mistral returned unparseable JSON after {_MAX_RETRIES} attempts. "
        f"Last raw response: {raw_text!r}. "
        f"Underlying error: {last_error}"
    )


def _strip_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers if present."""
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        return "\n".join(inner).strip()
    return text
