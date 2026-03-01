"""
Authenticated httpx wrapper for the Kalshi trade API.
"""
from __future__ import annotations

import httpx

from app.services.kalshi_auth import build_auth_headers

import os
# Trading API (may be demo for paper trading)
BASE_URL = os.environ.get("KALSHI_BASE_URL", "https://api.elections.kalshi.com/trade-api/v2")
# Public production API — always used for read-only market data so stats reflect real volume
PUBLIC_BASE_URL = os.environ.get("KALSHI_PUBLIC_BASE_URL", "https://api.elections.kalshi.com/trade-api/v2")
_API_PREFIX = "/trade-api/v2"


async def kalshi_get(path: str, params: dict | None = None, authenticated: bool = False) -> dict:
    # Non-authenticated reads (market data, stats) always use the public production API
    # so that volume/open_interest reflect real activity even when BASE_URL is a demo env.
    base = BASE_URL if authenticated else PUBLIC_BASE_URL
    headers = build_auth_headers("GET", f"{_API_PREFIX}{path}") if authenticated else {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{base}{path}",
            params=_strip_none(params or {}),
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()


async def kalshi_post(path: str, body: dict) -> dict:
    headers = build_auth_headers("POST", f"{_API_PREFIX}{path}")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}{path}",
            json=body,
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()


async def kalshi_delete(path: str) -> dict:
    headers = build_auth_headers("DELETE", f"{_API_PREFIX}{path}")
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{BASE_URL}{path}",
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()


def _strip_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}
