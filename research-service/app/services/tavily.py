"""Tavily API integration for news search."""

from __future__ import annotations

import os

import httpx

TAVILY_URL = "https://api.tavily.com/search"
_TIMEOUT = 10.0


async def search_news(query: str, days_back: int = 3) -> str:
    """Search for recent news articles using Tavily."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not configured"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                TAVILY_URL,
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": 5,
                    "days": days_back,
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return f"Error searching news: {exc}"

    results = data.get("results", [])
    if not results:
        return f"No recent news found for: {query}"

    lines = []
    for r in results:
        title = r.get("title", "No title")
        content = r.get("content", "")[:200]
        url = r.get("url", "")
        lines.append(f"- {title}: {content}")
        if url:
            lines.append(f"  Source: {url}")
    return "\n".join(lines)
