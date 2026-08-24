"""Deterministic temporal market-regime classification."""

from dataclasses import dataclass
from decimal import Decimal

from .signals import MarketBar


@dataclass(frozen=True)
class Regime:
    name: str
    confidence: Decimal
    rationale: str


def classify_regime(bars: list[MarketBar], lookback: int = 6) -> Regime:
    if lookback < 3 or len(bars) < lookback:
        return Regime("insufficient", Decimal("0"), "insufficient temporal history")
    closes = [bar.close for bar in bars[-lookback:]]
    returns = []
    for previous, current in zip(closes, closes[1:]):
        if previous == 0:
            return Regime("insufficient", Decimal("0"), "invalid zero reference price")
        returns.append((current - previous) / previous)
    mean = sum(returns, Decimal("0")) / Decimal(len(returns))
    variance = sum((item - mean) ** 2 for item in returns) / Decimal(len(returns))
    volatility = variance.sqrt()
    directional = abs(mean)
    if volatility > Decimal("0.01"):
        name = "high_volatility"
    elif directional > Decimal("0.001"):
        name = "trend"
    else:
        name = "range"
    confidence = min(Decimal("1"), max(Decimal("0"), directional * Decimal("500") + volatility * Decimal("25")))
    return Regime(name, confidence, f"{lookback}-bar temporal return structure")
