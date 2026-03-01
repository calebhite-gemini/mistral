"""Mistral function-calling agent loop for sports research."""

from __future__ import annotations

import json
import os
import re
from typing import AsyncGenerator

from mistralai import Mistral

from app.services.espn import get_espn_web_url
from app.services.schemas import ResearchBriefOutput, ResearchRequest, SourceRef
from app.services.tools import TOOL_DEFINITIONS, execute_tool

_MODEL = "mistral-large-latest"
_TEMPERATURE = 0.3
_MAX_TOOL_CALLS = 8

_SYSTEM_PROMPT = """\
You are an expert sports research analyst. Your job is to gather data about an \
upcoming sports matchup and produce a structured research brief.

You have access to tools for searching news, getting team stats, checking \
injuries, reviewing head-to-head history, and analyzing schedules. The ESPN \
tools support NBA, NFL, NHL, and MLB — always pass the correct "sport" \
parameter based on the league of the market you are researching.

Strategy:
1. Check injury reports for both teams (important for prediction accuracy)
2. Get recent schedule for both teams to assess rest/fatigue
3. Get team stats for both teams (record, scoring, defensive performance)
4. Search for relevant recent news if needed (trades, coaching changes, momentum)
5. Optionally check head-to-head if the matchup is close

Be efficient. Skip tools if the information would not meaningfully affect a \
prediction. Do not call the same tool twice with identical arguments.

When you have gathered enough information, respond with a JSON object \
(no markdown fences) using exactly these keys:
- key_factors: list of 3-6 strings, each a concise factor affecting the outcome
- injury_flags: list of strings formatted as "Player Name - status (injury)", or empty list
- rest_advantage: string describing rest situation, e.g. "Lakers (2 days rest) vs Warriors (back-to-back)"
- recent_form: string summarizing recent performance, e.g. "Lakers 7-3 last 10, Warriors 5-5 last 10"
- sources: list of data sources used, e.g. ["ESPN injury report", "ESPN team stats", "Tavily news"]

Respond ONLY with the JSON object when you are ready to give your final answer.\
"""


# ── Source URL extraction helpers ─────────────────────────────────────────────

_URL_RE = re.compile(r"https?://\S+")

_SOURCE_TYPE_MAP: dict[str, str] = {
    "get_injury_report": "espn_injury",
    "get_team_stats": "espn_stats",
    "get_schedule": "espn_schedule",
    "get_head_to_head": "espn_h2h",
}

_FN_LABEL_MAP: dict[str, str] = {
    "get_injury_report": "Injury Report",
    "get_team_stats": "Team Stats",
    "get_schedule": "Schedule",
    "get_head_to_head": "Head-to-Head",
}


def _extract_tavily_urls(result_text: str) -> list[SourceRef]:
    """Parse 'Source: URL' lines from Tavily's plain-text output."""
    refs: list[SourceRef] = []
    lines = result_text.split("\n")
    prev_line = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Source: "):
            url = stripped[len("Source: "):].strip()
            if url.startswith("http"):
                # Extract title from the preceding article line ("- Title: content")
                title = "News article"
                clean = prev_line.lstrip("- ").strip()
                colon_pos = clean.find(":")
                if colon_pos > 0:
                    title = clean[:colon_pos].strip()
                refs.append(SourceRef(title=title, url=url, source_type="tavily"))
        prev_line = stripped
    return refs


def _build_espn_ref(fn_name: str, parsed_args: dict, sport: str) -> SourceRef | None:
    """Build a SourceRef with an ESPN web URL for a given tool call."""
    team_hint = parsed_args.get("team", parsed_args.get("team_a", ""))
    if not team_hint:
        return None
    url = get_espn_web_url(fn_name, team_hint, sport)
    if not url:
        return None
    label = _FN_LABEL_MAP.get(fn_name, fn_name.replace("get_", "").replace("_", " ").title())
    return SourceRef(
        title=f"{team_hint.title()} - ESPN {label}",
        url=url,
        source_type=_SOURCE_TYPE_MAP.get(fn_name, "espn"),
    )


# ── Agent loops ───────────────────────────────────────────────────────────────

async def run_research_agent(request: ResearchRequest) -> ResearchBriefOutput:
    """Run the Mistral research agent loop for a given market."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("MISTRAL_API_KEY is not set")

    client = Mistral(api_key=api_key)

    user_message = (
        f"Research this market for a prediction:\n"
        f"Question: {request.question}\n"
        f"Sport: {request.sport}\n"
        f"Teams: {', '.join(request.teams)}\n"
        f"Game Date: {request.game_date}\n"
        f"Market ID: {request.market_id}"
    )

    messages: list[dict] = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    tool_call_count = 0
    sources_used: set[str] = set()
    collected_urls: list[SourceRef] = []
    final_content = ""

    while tool_call_count < _MAX_TOOL_CALLS:
        response = await client.chat.complete_async(
            model=_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=_TEMPERATURE,
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            final_content = message.content or ""
            break

        for tool_call in message.tool_calls:
            tool_call_count += 1
            fn_name = tool_call.function.name
            fn_args = tool_call.function.arguments

            if fn_name == "search_news":
                sources_used.add("Tavily news search")
            elif fn_name.startswith("get_"):
                sources_used.add(f"ESPN {fn_name.replace('get_', '').replace('_', ' ')}")

            result = await execute_tool(fn_name, fn_args)

            # Collect structured URLs
            try:
                parsed_args = json.loads(fn_args) if isinstance(fn_args, str) else fn_args
            except json.JSONDecodeError:
                parsed_args = {}

            if fn_name == "search_news":
                collected_urls.extend(_extract_tavily_urls(result))
            elif fn_name.startswith("get_"):
                ref = _build_espn_ref(fn_name, parsed_args, request.sport)
                if ref:
                    collected_urls.append(ref)

            messages.append({
                "role": "tool",
                "name": fn_name,
                "content": result,
                "tool_call_id": tool_call.id,
            })
    else:
        messages.append({
            "role": "user",
            "content": (
                "You have used all available tool calls. Provide your final "
                "research brief JSON now based on the data gathered so far."
            ),
        })
        response = await client.chat.complete_async(
            model=_MODEL,
            messages=messages,
            temperature=_TEMPERATURE,
        )
        final_content = response.choices[0].message.content or ""

    return _parse_agent_response(final_content, request.market_id, sources_used, collected_urls)


_TOOL_LABELS: dict[str, str] = {
    "get_injury_report": "Checking {team} injury report...",
    "get_team_stats": "Getting {team} team stats...",
    "get_schedule": "Fetching {team} schedule...",
    "get_head_to_head": "Looking up head-to-head history...",
    "search_news": "Searching recent news...",
}


async def run_research_agent_stream(
    request: ResearchRequest,
) -> AsyncGenerator[dict, None]:
    """Run the Mistral research agent loop, yielding SSE events for each tool call."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("MISTRAL_API_KEY is not set")

    client = Mistral(api_key=api_key)

    user_message = (
        f"Research this market for a prediction:\n"
        f"Question: {request.question}\n"
        f"Sport: {request.sport}\n"
        f"Teams: {', '.join(request.teams)}\n"
        f"Game Date: {request.game_date}\n"
        f"Market ID: {request.market_id}"
    )

    messages: list[dict] = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    tool_call_count = 0
    sources_used: set[str] = set()
    collected_urls: list[SourceRef] = []
    final_content = ""

    while tool_call_count < _MAX_TOOL_CALLS:
        response = await client.chat.complete_async(
            model=_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=_TEMPERATURE,
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            final_content = message.content or ""
            break

        for tool_call in message.tool_calls:
            tool_call_count += 1
            fn_name = tool_call.function.name
            fn_args = tool_call.function.arguments

            # Parse args to extract team name for the label
            try:
                parsed_args = json.loads(fn_args) if isinstance(fn_args, str) else fn_args
            except json.JSONDecodeError:
                parsed_args = {}

            team_hint = parsed_args.get(
                "team",
                parsed_args.get("team_a", parsed_args.get("query", "")),
            )
            label_template = _TOOL_LABELS.get(fn_name, f"Running {fn_name}...")
            label = (
                label_template.format(team=team_hint)
                if "{team}" in label_template
                else label_template
            )

            # Emit step event BEFORE executing the tool
            yield {
                "event": "step",
                "data": {
                    "phase": "research",
                    "tool": fn_name,
                    "label": label,
                    "index": tool_call_count,
                },
            }

            # Track sources
            if fn_name == "search_news":
                sources_used.add("Tavily news search")
            elif fn_name.startswith("get_"):
                sources_used.add(f"ESPN {fn_name.replace('get_', '').replace('_', ' ')}")

            result = await execute_tool(fn_name, fn_args)

            # Collect structured URLs
            if fn_name == "search_news":
                collected_urls.extend(_extract_tavily_urls(result))
            elif fn_name.startswith("get_"):
                ref = _build_espn_ref(fn_name, parsed_args, request.sport)
                if ref:
                    collected_urls.append(ref)

            messages.append({
                "role": "tool",
                "name": fn_name,
                "content": result,
                "tool_call_id": tool_call.id,
            })
    else:
        # Hit max tool calls — force a final response
        yield {
            "event": "step",
            "data": {"phase": "research", "tool": None, "label": "Compiling research brief..."},
        }

        messages.append({
            "role": "user",
            "content": (
                "You have used all available tool calls. Provide your final "
                "research brief JSON now based on the data gathered so far."
            ),
        })
        response = await client.chat.complete_async(
            model=_MODEL,
            messages=messages,
            temperature=_TEMPERATURE,
        )
        final_content = response.choices[0].message.content or ""

    brief = _parse_agent_response(final_content, request.market_id, sources_used, collected_urls)
    yield {
        "event": "research_complete",
        "data": brief.model_dump(),
    }


# ── Response parsing ──────────────────────────────────────────────────────────

def _parse_agent_response(
    raw_text: str,
    market_id: str,
    sources_used: set[str],
    collected_urls: list[SourceRef] | None = None,
) -> ResearchBriefOutput:
    """Parse the agent's final JSON response into a ResearchBriefOutput."""
    cleaned = _strip_fences(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return ResearchBriefOutput(
            market_id=market_id,
            key_factors=[raw_text[:500] if raw_text else "Research agent produced no output"],
            injury_flags=[],
            rest_advantage="Unknown",
            recent_form="Unknown",
            sources=list(sources_used) or ["none"],
            source_urls=collected_urls or [],
        )

    agent_sources = data.get("sources", [])
    all_sources = list(sources_used | set(agent_sources))

    return ResearchBriefOutput(
        market_id=market_id,
        key_factors=data.get("key_factors", []),
        injury_flags=data.get("injury_flags", []),
        rest_advantage=data.get("rest_advantage", "Unknown"),
        recent_form=data.get("recent_form", "Unknown"),
        sources=all_sources if all_sources else ["none"],
        source_urls=collected_urls or [],
    )


def _strip_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers if present."""
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        return "\n".join(inner).strip()
    return text
