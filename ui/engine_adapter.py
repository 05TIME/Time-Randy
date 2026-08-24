"""Presentation adapter for deterministic TIMEŒ engine outputs."""

from decimal import Decimal

from forex.factors import ensemble_signal
from forex.regime import classify_regime
from forex.signals import MarketBar


def build_market_view(bars: list[MarketBar]) -> dict:
    """Produce JSON-safe dashboard data from the quantitative engine."""
    regime = classify_regime(bars)
    ensemble = ensemble_signal(bars)
    return {
        "regime": {"name": regime.name, "confidence": str(regime.confidence), "rationale": regime.rationale},
        "signal": {"direction": ensemble["direction"], "score": str(ensemble["score"])},
        "factors": [
            {"name": item["name"], "score": str(item["score"]), "weight": str(item["weight"])}
            for item in ensemble["factors"]
        ],
        "last_price": str(bars[-1].close) if bars else None,
    }
