"""Mistral function-calling agent loop for sports research."""

from __future__ import annotations

import json
import os

from mistralai import Mistral

from app.services.schemas import ResearchBriefOutput, ResearchRequest
from app.services.tools import TOOL_DEFINITIONS, execute_tool

_MODEL = "mistral-large-latest"
_TEMPERATURE = 0.3
_MAX_TOOL_CALLS = 8

_SYSTEM_PROMPT = """\
You are an expert sports research analyst. Your job is to gather data about an \
upcoming sports matchup and produce a structured research brief.

You have access to tools for searching news, getting team stats, checking \
injuries, reviewing head-to-head history, and analyzing schedules.

Strategy:
1. Check injury reports for both teams (important for prediction accuracy)
2. Get recent schedule for both teams to assess rest/fatigue
3. Get team stats for both teams (record, PPG, defensive rating)
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

        # Append assistant message to conversation
        messages.append(message)

        # If no tool calls, agent is done
        if not message.tool_calls:
            final_content = message.content or ""
            break

        # Execute each tool call
        for tool_call in message.tool_calls:
            tool_call_count += 1
            fn_name = tool_call.function.name
            fn_args = tool_call.function.arguments

            # Track sources
            if fn_name == "search_news":
                sources_used.add("Tavily news search")
            elif fn_name.startswith("get_"):
                sources_used.add(f"ESPN {fn_name.replace('get_', '').replace('_', ' ')}")

            result = await execute_tool(fn_name, fn_args)

            messages.append({
                "role": "tool",
                "name": fn_name,
                "content": result,
                "tool_call_id": tool_call.id,
            })
    else:
        # Hit max tool calls — force a final response with no tools
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

    return _parse_agent_response(final_content, request.market_id, sources_used)


def _parse_agent_response(
    raw_text: str,
    market_id: str,
    sources_used: set[str],
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
    )


def _strip_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers if present."""
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        return "\n".join(inner).strip()
    return text
