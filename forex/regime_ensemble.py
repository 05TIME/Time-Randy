"""Regime-aware quantitative signal weighting."""

from decimal import Decimal

from .factors import FactorSignal
from .regime import Regime
from .signals import MarketBar, momentum_signal
from .factors import volatility_signal


def regime_aware_signal(bars: list[MarketBar], regime: Regime) -> dict:
    """Adjust factor weights by temporal regime without changing factor scores."""
    momentum = momentum_signal(bars)
    volatility = volatility_signal(bars)
    weights = {
        "trend": {"momentum": Decimal("0.85"), "volatility": Decimal("0.15")},
        "range": {"momentum": Decimal("0.35"), "volatility": Decimal("0.65")},
        "high_volatility": {"momentum": Decimal("0.50"), "volatility": Decimal("0.50")},
        "insufficient": {"momentum": Decimal("0"), "volatility": Decimal("0")},
    }.get(regime.name, {"momentum": Decimal("0"), "volatility": Decimal("0")})
    factors = [FactorSignal("momentum", momentum.score, weights["momentum"]), FactorSignal("volatility", volatility.score, weights["volatility"])]
    total = sum((factor.weight for factor in factors), Decimal("0"))
    score = Decimal("0") if total == 0 else sum((factor.score * factor.weight for factor in factors), Decimal("0")) / total
    score = max(Decimal("-1"), min(Decimal("1"), score))
    direction = "long" if score > 0 else "short" if score < 0 else "neutral"
    return {"direction": direction, "score": score, "regime": regime.name, "factors": [{"name": f.name, "score": f.score, "weight": f.weight} for f in factors]}
