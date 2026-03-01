from __future__ import annotations

from pydantic import BaseModel


class SourceRef(BaseModel):
    title: str
    url: str
    source_type: str  # "tavily" | "espn_injury" | "espn_stats" | "espn_schedule" | "espn_h2h"


class ResearchRequest(BaseModel):
    market_id: str
    question: str
    sport: str
    teams: list[str]
    game_date: str


class ResearchBriefOutput(BaseModel):
    market_id: str
    key_factors: list[str]
    injury_flags: list[str]
    rest_advantage: str
    recent_form: str
    sources: list[str]
    source_urls: list[SourceRef] = []
