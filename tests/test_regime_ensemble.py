from decimal import Decimal

from forex.regime import Regime
from forex.regime_ensemble import regime_aware_signal
from forex.signals import MarketBar


def bars(values):
    return [MarketBar(str(i), Decimal(v), Decimal(v), Decimal(v), Decimal(v)) for i, v in enumerate(values)]


def test_trend_regime_favors_momentum():
    result = regime_aware_signal(bars([100, 101, 102, 103, 104, 105]), Regime("trend", Decimal("0.8"), "trend"))
    weights = {f["name"]: f["weight"] for f in result["factors"]}
    assert weights["momentum"] == Decimal("0.85")
    assert result["direction"] == "long"


def test_range_regime_favors_volatility_factor():
    result = regime_aware_signal(bars([100, 100.01, 99.99, 100.01, 100, 99.99]), Regime("range", Decimal("0.5"), "range"))
    weights = {f["name"]: f["weight"] for f in result["factors"]}
    assert weights["volatility"] == Decimal("0.65")


def test_insufficient_regime_is_neutral():
    result = regime_aware_signal(bars([100, 101]), Regime("insufficient", Decimal("0"), "insufficient"))
    assert result["direction"] == "neutral"
    assert result["score"] == Decimal("0")
