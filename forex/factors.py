"""Deterministic multi-factor Forex signal ensemble."""

from dataclasses import dataclass
from decimal import Decimal

from .signals import MarketBar, momentum_signal


@dataclass(frozen=True)
class FactorSignal:
    name: str
    score: Decimal
    weight: Decimal


def volatility_signal(bars: list[MarketBar], lookback: int = 5) -> FactorSignal:
    if len(bars) < lookback or lookback < 2:
        return FactorSignal("volatility", Decimal("0"), Decimal("0.20"))
    moves = [(bars[i].close - bars[i - 1].close) / bars[i - 1].close for i in range(len(bars) - lookback + 1, len(bars)) if bars[i - 1].close]
    if not moves:
        return FactorSignal("volatility", Decimal("0"), Decimal("0.20"))
    mean = sum(moves, Decimal("0")) / Decimal(len(moves))
    variance = sum((x - mean) ** 2 for x in moves) / Decimal(len(moves))
    # Low volatility supports trend signals; high volatility reduces conviction.
    score = max(Decimal("-1"), min(Decimal("1"), Decimal("1") - variance.sqrt() * Decimal("100")))
    return FactorSignal("volatility", score, Decimal("0.20"))


def ensemble_signal(bars: list[MarketBar]) -> dict:
    momentum = momentum_signal(bars)
    volatility = volatility_signal(bars)
    factors = [FactorSignal("momentum", momentum.score, Decimal("0.80")), volatility]
    total_weight = sum((f.weight for f in factors), Decimal("0"))
    score = sum((f.score * f.weight for f in factors), Decimal("0")) / total_weight if total_weight else Decimal("0")
    score = max(Decimal("-1"), min(Decimal("1"), score))
    direction = "long" if score > 0 else "short" if score < 0 else "neutral"
    return {
        "direction": direction,
        "score": score,
        "factors": [{"name": f.name, "score": f.score, "weight": f.weight} for f in factors],
    }
