"""Tool definitions for Mistral function calling and dispatch table."""

from __future__ import annotations

import json

from app.services.espn import (
    get_head_to_head,
    get_injury_report,
    get_schedule,
    get_team_stats,
)
from app.services.tavily import search_news

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": (
                "Search recent sports news articles. Use for breaking news, "
                "roster changes, coaching updates, or any current events "
                "affecting a team or matchup."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query, e.g. 'Lakers injury updates March 2026'",
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "How many days back to search (default 3, max 7)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_stats",
            "description": (
                "Get current season statistics for an NBA team: win-loss record, "
                "points per game, defensive rating, home/away splits."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "Team nickname, e.g. 'Lakers', 'Warriors', '76ers'",
                    },
                    "stat_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Which stats to retrieve: 'record', 'ppg', "
                            "'defensive_rating', 'home_away'. Omit for all."
                        ),
                    },
                },
                "required": ["team"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_injury_report",
            "description": (
                "Get the current injury report for an NBA team. Returns player "
                "names, injury status (Out/Doubtful/Questionable/Day-to-Day), "
                "and injury description."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "Team nickname, e.g. 'Lakers', 'Warriors'",
                    },
                },
                "required": ["team"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_head_to_head",
            "description": (
                "Get historical head-to-head results between two NBA teams. "
                "Returns recent matchup outcomes, scores, and series record."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team_a": {
                        "type": "string",
                        "description": "First team nickname",
                    },
                    "team_b": {
                        "type": "string",
                        "description": "Second team nickname",
                    },
                    "num_games": {
                        "type": "integer",
                        "description": "Number of recent matchups to retrieve (default 5, max 10)",
                    },
                },
                "required": ["team_a", "team_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_schedule",
            "description": (
                "Get recent and upcoming schedule for an NBA team. Detects "
                "back-to-back games and rest days. Use to assess fatigue and "
                "rest advantages."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "Team nickname",
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "Days of past schedule to include (default 7)",
                    },
                    "days_forward": {
                        "type": "integer",
                        "description": "Days of future schedule to include (default 3)",
                    },
                },
                "required": ["team"],
            },
        },
    },
]

_TOOL_DISPATCH: dict[str, object] = {
    "search_news": search_news,
    "get_team_stats": get_team_stats,
    "get_injury_report": get_injury_report,
    "get_head_to_head": get_head_to_head,
    "get_schedule": get_schedule,
}


async def execute_tool(name: str, arguments_json: str) -> str:
    """Execute a tool by name with JSON-encoded arguments. Returns string result."""
    func = _TOOL_DISPATCH.get(name)
    if not func:
        return f"Error: Unknown tool '{name}'"
    try:
        args = json.loads(arguments_json) if isinstance(arguments_json, str) else arguments_json
        result = await func(**args)
        return result
    except Exception as exc:
        return f"Error calling {name}: {exc}"
