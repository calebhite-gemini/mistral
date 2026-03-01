"""
Component 5: Edge Detection & EV Calculator

Compares the model's probability estimate against the current market price
and returns an actionable signal with EV and Kelly stake sizing.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

_EDGE_THRESHOLD = 0.07  # minimum edge to generate a BUY signal


class EdgeRequest(BaseModel):
    model_prob: int = Field(ge=0, le=100, description="Model probability (0-100)")
    market_yes_price: float = Field(ge=0.0, le=1.0, description="Current Kalshi YES price (0-1)")


class EdgeResult(BaseModel):
    signal: Literal["BUY YES", "BUY NO", "NO EDGE"]
    edge: float = Field(description="model_prob_decimal - market_yes_price")
    ev: float = Field(description="Expected value of a $1 YES bet")
    kelly_fraction: float = Field(description="Fraction of bankroll to bet per Kelly criterion")


def calculate_edge(model_prob: int, market_yes_price: float) -> EdgeResult:
    p = model_prob / 100
    edge = p - market_yes_price

    # EV on a $1 YES bet: win (1 - price) with prob p, lose price with prob (1-p)
    ev_yes = (p * (1 - market_yes_price)) - ((1 - p) * market_yes_price)

    # Full Kelly: edge / odds_received; zero if no positive edge
    kelly = edge / (1 - market_yes_price) if edge > 0 else 0.0

    if edge > _EDGE_THRESHOLD:
        signal: Literal["BUY YES", "BUY NO", "NO EDGE"] = "BUY YES"
    elif edge < -_EDGE_THRESHOLD:
        signal = "BUY NO"
    else:
        signal = "NO EDGE"

    return EdgeResult(
        signal=signal,
        edge=round(edge, 3),
        ev=round(ev_yes, 3),
        kelly_fraction=round(kelly, 3),
    )
