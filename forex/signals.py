"""Deterministic market features and bounded signal scoring."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MarketBar:
    timestamp: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal = Decimal("0")


@dataclass(frozen=True)
class QuantSignal:
    direction: str
    score: Decimal
    rationale: str


def momentum_signal(bars: list[MarketBar], lookback: int = 3) -> QuantSignal:
    """Return a bounded directional signal from close-to-close momentum."""
    if lookback < 1 or len(bars) <= lookback:
        return QuantSignal("neutral", Decimal("0"), "insufficient market history")
    start = bars[-lookback - 1].close
    end = bars[-1].close
    if start == 0:
        return QuantSignal("neutral", Decimal("0"), "invalid zero reference price")
    raw = (end - start) / start
    score = max(Decimal("-1"), min(Decimal("1"), raw * Decimal("100")))
    direction = "long" if score > 0 else "short" if score < 0 else "neutral"
    return QuantSignal(direction, score, f"{lookback}-bar close momentum")
