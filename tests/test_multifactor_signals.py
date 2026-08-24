from decimal import Decimal

from forex.factors import ensemble_signal
from forex.signals import MarketBar


def bars(values):
    return [MarketBar(str(i), Decimal(v), Decimal(v), Decimal(v), Decimal(v)) for i, v in enumerate(values)]


def test_ensemble_is_bounded_and_exposes_factors():
    result = ensemble_signal(bars([100, 101, 102, 103, 104, 105]))
    assert Decimal("-1") <= result["score"] <= Decimal("1")
    assert {factor["name"] for factor in result["factors"]} == {"momentum", "volatility"}


def test_ensemble_handles_insufficient_history():
    result = ensemble_signal(bars([100, 100]))
    assert result["direction"] == "neutral"
    assert result["score"] == Decimal("0")
